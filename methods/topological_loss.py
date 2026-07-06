# methods/topological_loss.py
# Phase-3 deliverable 1 (stage 3a): the DIFFERENTIABLE TOPOLOGICAL LOSS.
#
# Pulls a live point cloud's persistence diagram toward a fixed TARGET diagram
# (PHASE3_PLAN.md §3). Split into two halves so the training loop can freeze
# the combinatorics between refreshes (§3.5):
#
#   plan_topo_loss(P, bundle)  -> LossPlan     forward, NON-differentiable:
#       GUDHI alpha complex + persistence_pairs(), significance filter,
#       optimal partial matching to the target diagram, recruitment for
#       missing target features. Records, per loss term, the birth/death
#       simplex VERTEX INDICES.
#   eval_topo_loss(X, plan)    -> torch scalar  differentiable:
#       recomputes each recorded simplex's circumradius from the live torch
#       positions (closed form; alpha filtration value = squared circumradius
#       for Gabriel simplices) and assembles the matched-Wasserstein loss.
#
# The pairing is treated as locally constant (pair-frozen backward). Non-Gabriel
# simplices — whose alpha value is inherited from a coface, so the recomputed
# circumradius would NOT equal the diagram value — are DETACHED: they contribute
# their value but no gradient (gate + counts in LossPlan.info; PHASE3_PLAN.md
# §3.2).
#
# Term kinds (all squared, diagram units = circumradius / target scale):
#   match    live significant bar <-> target bar     (b-b*)^2 + (d-d*)^2
#   diag     live significant bar unmatched          ((d-b)/2)^2   push to diagonal
#   recruit  target bar unmatched: nearest live bar (sub-threshold allowed) is
#            pulled toward it. DELIBERATE deviation from pure Wasserstein:
#            optimal matching prefers diagonalizing a far-apart (live, target)
#            pair, which zeroes the gradient exactly in the most important
#            failure mode (a missing component/void). Recruitment restores a
#            gradient path; its known pathology (satisfying the diagram at the
#            wrong LOCATION) is probed by toy T4 in tests/test_topo_loss.py.
#
# Scale-locking: every value is normalized by the BUNDLE's scale (the target
# sample's bbox diagonal), never by the live cloud's own extent. Density
# matching: build the bundle at the SAME sample count M the training loop will
# use (PHASE3_PLAN.md §4).
#
# No DiffSoup / renderer imports here — this file must stay runnable standalone
# (stage 3a gate) and CPU-only.

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, field as _dc_field
from typing import Optional, Sequence

import numpy as np
import torch
from scipy.optimize import linear_sum_assignment
from scipy.spatial import cKDTree

import gudhi

from . import _paths

_topology = _paths.load_topology()
persistence_from_points = _topology.persistence_from_points
meshes = _topology.meshes
DEFAULT_SIG_K = _topology.persistence.DEFAULT_SIG_K


# ── differentiable circumradii (closed forms; float64 recommended) ────────

_EPS = 1e-30


def circumradius_edge(p: torch.Tensor) -> torch.Tensor:
    """(...,2,3) -> (...,): half the edge length."""
    return 0.5 * torch.linalg.norm(p[..., 1, :] - p[..., 0, :], dim=-1)


def circumradius_triangle(p: torch.Tensor) -> torch.Tensor:
    """(...,3,3) -> (...,): R = |u||v||u-v| / (2|u x v|)."""
    u = p[..., 1, :] - p[..., 0, :]
    v = p[..., 2, :] - p[..., 0, :]
    cross = torch.cross(u, v, dim=-1)
    denom = (2.0 * torch.linalg.norm(cross, dim=-1)).clamp_min(_EPS)
    return (torch.linalg.norm(u, dim=-1) * torch.linalg.norm(v, dim=-1)
            * torch.linalg.norm(u - v, dim=-1)) / denom


def circumradius_tetra(p: torch.Tensor) -> torch.Tensor:
    """(...,4,3) -> (...,): solve A y = diag(A A^T)/2 with A rows p_i - p_0;
    the circumcenter is p_0 + y, so R = |y|."""
    A = p[..., 1:, :] - p[..., :1, :]                    # (...,3,3)
    rhs = 0.5 * (A * A).sum(dim=-1)                      # (...,3)
    y = torch.linalg.solve(A, rhs.unsqueeze(-1)).squeeze(-1)
    return torch.linalg.norm(y, dim=-1)


_CIRCUM = {2: circumradius_edge, 3: circumradius_triangle, 4: circumradius_tetra}


def simplex_values(X: torch.Tensor, simplices: Sequence[Sequence[int]],
                   scale: float) -> torch.Tensor:
    """Normalized alpha filtration values sqrt(alpha)/scale = circumradius/scale
    of `simplices` (vertex-index tuples into X), differentiable w.r.t. X.
    Single vertices have value exactly 0 (their alpha value), gradient-free.
    Valid as the diagram value only for GABRIEL simplices — the caller detaches
    the rest."""
    vals = X.new_zeros(len(simplices))
    by_size: dict[int, list[int]] = {}
    for i, s in enumerate(simplices):
        by_size.setdefault(len(s), []).append(i)
    for size, idxs in by_size.items():
        if size == 1:
            continue                                     # vertices: alpha = 0
        if size not in _CIRCUM:
            raise ValueError(f"unsupported simplex size {size}")
        vidx = torch.as_tensor([list(simplices[i]) for i in idxs],
                               dtype=torch.long, device=X.device)
        r = _CIRCUM[size](X[vidx])                       # (K,)
        vals = vals.index_put((torch.as_tensor(idxs, device=X.device),), r / scale)
    return vals


# ── forward: live pairing (GUDHI, non-differentiable) ─────────────────────

@dataclass
class LiveBar:
    dim: int
    birth: float                 # normalized (sqrt(filtration)/scale)
    death: float
    birth_verts: tuple           # vertex indices into the live cloud
    death_verts: tuple
    gabriel_birth: bool          # recomputed circumradius == filtration value
    gabriel_death: bool
    significant: bool            # lifetime > sig_thr


def live_pairs(P: np.ndarray, scale: float, *, dims: Sequence[int] = (0, 1, 2),
               sig_thr: Optional[float] = None, gabriel_rtol: float = 1e-6,
               check_mapping: bool = True) -> tuple[dict, dict]:
    """All FINITE persistence pairs of P's alpha complex in `dims`, with their
    birth/death simplices and Gabriel flags. Essential bars (death=inf) are
    skipped — they have no death simplex to differentiate through.

    Returns ({dim: [LiveBar,...]}, info). Raises if the alpha-complex vertex ids
    do not map 1:1 onto input-cloud indices (the §3.2 mapping gate)."""
    P = np.ascontiguousarray(P, dtype=np.float64)
    scale = max(float(scale), 1e-12)
    try:
        ac = gudhi.AlphaComplex(points=P)
    except TypeError:                                    # very old gudhi
        ac = gudhi.AlphaComplex(points=P.tolist())
    st = ac.create_simplex_tree()
    st.compute_persistence(persistence_dim_max=False, min_persistence=0.0)
    pairs = st.persistence_pairs()

    if sig_thr is None:
        d, _ = cKDTree(P).query(P, k=2)
        sig_thr = DEFAULT_SIG_K * float(np.median(d[:, 1])) / scale

    records = []                                         # (dim, bp, dp, b, dth)
    used_verts: set[int] = set()
    for bp, dp in pairs:
        d = len(bp) - 1
        if d not in dims or not dp:                      # essential: dp == []
            continue
        b = float(np.sqrt(max(st.filtration(bp), 0.0))) / scale
        dth = float(np.sqrt(max(st.filtration(dp), 0.0))) / scale
        records.append((d, tuple(bp), tuple(dp), b, dth))
        used_verts.update(bp)
        used_verts.update(dp)

    if check_mapping and used_verts:
        vs = sorted(used_verts)
        got = np.array([ac.get_point(v) for v in vs], dtype=np.float64)
        err = float(np.max(np.abs(got - P[vs]))) if len(vs) else 0.0
        if err > 1e-9:
            raise RuntimeError(
                f"alpha-complex vertex ids do not map to input indices "
                f"(max |get_point(v) - P[v]| = {err:.3e}); a vertex-map fallback "
                f"is required for this cloud")

    # Gabriel gate: recompute every birth/death simplex circumradius (torch,
    # no grad) and compare to the official filtration value.
    simps = [r[1] for r in records] + [r[2] for r in records]
    if simps:
        with torch.no_grad():
            tv = simplex_values(torch.from_numpy(P), simps, scale).numpy()
    n = len(records)
    bars: dict[int, list[LiveBar]] = {d: [] for d in dims}
    n_gab_fail = 0
    for i, (d, bp, dp, b, dth) in enumerate(records):
        gb = abs(tv[i] - b) <= gabriel_rtol * max(b, 1e-9)
        gd = abs(tv[n + i] - dth) <= gabriel_rtol * max(dth, 1e-9)
        n_gab_fail += (not gb) + (not gd)
        bars[d].append(LiveBar(dim=d, birth=b, death=dth, birth_verts=bp,
                               death_verts=dp, gabriel_birth=gb, gabriel_death=gd,
                               significant=(dth - b) > sig_thr))
    info = {
        "n_finite_pairs": n,
        "n_significant": {d: sum(x.significant for x in bars[d]) for d in dims},
        "n_gabriel_fail": n_gab_fail,
        "sig_thr": float(sig_thr),
    }
    return bars, info


# ── optimal partial matching (exact 2-Wasserstein assignment) ─────────────

_INF = 1e18


def match_partial(live: np.ndarray, target: np.ndarray):
    """Hungarian assignment on the standard augmented matrix: every live bar
    either matches a target bar (cost = squared L2 in the diagram plane) or its
    own diagonal projection (cost = (life/2)^2), and symmetrically for target.

    Returns (matches [(i_live, j_target)], unmatched_live, unmatched_target)."""
    n, m = len(live), len(target)
    if n == 0 or m == 0:
        return [], list(range(n)), list(range(m))
    C = np.full((n + m, n + m), 0.0)
    C[:n, :m] = ((live[:, None, :] - target[None, :, :]) ** 2).sum(axis=-1)
    C[:n, m:] = _INF
    C[:n, m:][np.arange(n), np.arange(n)] = ((live[:, 1] - live[:, 0]) / 2.0) ** 2
    C[n:, :m] = _INF
    C[n:, :m][np.arange(m), np.arange(m)] = ((target[:, 1] - target[:, 0]) / 2.0) ** 2
    rows, cols = linear_sum_assignment(C)
    matches, um_live, um_tgt = [], [], []
    for r, c in zip(rows, cols):
        if r < n and c < m:
            matches.append((int(r), int(c)))
        elif r < n:
            um_live.append(int(r))
        elif c < m:
            um_tgt.append(int(c))
    return matches, um_live, um_tgt


# ── target bundle (density-matched, scale-locked; PHASE3_PLAN.md §4) ──────

# Shapes buildable straight from topology.meshes (training-scene targets like
# cube/cylinder come in later via a mesh path — sample_target_points handles it).
SHAPES = {
    "sphere":        lambda n, rng: meshes.sphere_cloud(n, rng=rng),
    "torus":         lambda n, rng: meshes.torus_cloud(n, rng=rng),
    "two_spheres":   lambda n, rng: meshes.two_spheres_cloud(n, rng=rng),
    "double_torus":  lambda n, rng: meshes.double_torus_cloud(n, rng=rng),
    "three_spheres": lambda n, rng: meshes.three_spheres_cloud(n, rng=rng),
    "thick_shell":   lambda n, rng: meshes.thick_shell_cloud(n, rng=rng),
}


def _resolve_points(target, n: int, seed: int) -> np.ndarray:
    if isinstance(target, np.ndarray):
        return np.ascontiguousarray(target, dtype=np.float64)
    if isinstance(target, str) and target in SHAPES:
        return SHAPES[target](n, np.random.default_rng(seed))
    from .topo_importance import sample_target_points   # mesh path / (V,F)
    return sample_target_points(target, n, seed)


@dataclass
class TargetBundle:
    """The loss's constant: per-dim SIGNIFICANT FINITE target bars, plus the
    normalization contract (scale, significance threshold, sample count)."""
    diagrams: dict               # dim -> (m,2) normalized [birth, death]
    scale: float                 # target bbox diagonal (original units)
    sig_thr: float               # normalized lifetime threshold
    n_points: int                # density-matching M
    dims: tuple
    meta: dict = _dc_field(default_factory=dict)

    def save(self, path: str) -> str:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        arrays = {f"diag_{d}": self.diagrams.get(d, np.zeros((0, 2)))
                  for d in self.dims}
        np.savez(
            path, **arrays,
            scale=np.float64(self.scale), sig_thr=np.float64(self.sig_thr),
            n_points=np.int64(self.n_points),
            dims=np.asarray(self.dims, dtype=np.int64),
            meta=np.frombuffer(json.dumps(self.meta).encode("utf-8"), dtype=np.uint8),
        )
        return path

    @staticmethod
    def load(path: str) -> "TargetBundle":
        z = np.load(path, allow_pickle=False)
        dims = tuple(int(d) for d in z["dims"])
        return TargetBundle(
            diagrams={d: z[f"diag_{d}"].reshape(-1, 2) for d in dims},
            scale=float(z["scale"]), sig_thr=float(z["sig_thr"]),
            n_points=int(z["n_points"]), dims=dims,
            meta=json.loads(bytes(z["meta"]).decode("utf-8")),
        )


def build_target_bundle(target, *, n: int = 2048, seed: int = 0,
                        dims: Sequence[int] = (0, 1, 2),
                        sig_k: Optional[float] = None,
                        stability_seeds: Sequence[int] = (1, 2)) -> TargetBundle:
    """Density-matched target diagram: computed at the SAME sample count M the
    live loss will see (alpha birth/death values shift with point spacing).
    The bundle's diagram uses one reference seed; `stability_seeds` re-sample
    the target and record the per-dim bottleneck spread in meta (honest noise
    floor for interpreting live-vs-target distances)."""
    P = _resolve_points(target, n, seed)
    res = persistence_from_points(P)                     # scale = P's bbox diagonal
    thr = res.significance_threshold(k=sig_k)

    def _sig_finite(r, d):
        dg = r.diagram(d)
        if not len(dg):
            return np.zeros((0, 2))
        keep = np.isfinite(dg[:, 1]) & ((dg[:, 1] - dg[:, 0]) > thr)
        return np.ascontiguousarray(dg[keep], dtype=np.float64)

    diagrams = {d: _sig_finite(res, d) for d in dims}

    stability = {}
    for s in stability_seeds:
        Ps = _resolve_points(target, n, int(s))
        rs = persistence_from_points(Ps, scale=res.scale)        # scale-locked
        for d in dims:
            a, b = diagrams[d], _sig_finite(rs, d)
            if len(a) == 0 and len(b) == 0:
                bd = 0.0
            else:
                bd = float(gudhi.bottleneck_distance(a.tolist(), b.tolist()))
            stability.setdefault(d, []).append(bd)

    name = target if isinstance(target, str) else type(target).__name__
    return TargetBundle(
        diagrams=diagrams, scale=float(res.scale), sig_thr=float(thr),
        n_points=int(n), dims=tuple(int(d) for d in dims),
        meta={"target": str(name), "seed": int(seed), "sig_k": sig_k or DEFAULT_SIG_K,
              "betti_significant": {str(d): int(len(diagrams[d])) for d in dims},
              "stability_bottleneck": {str(d): v for d, v in stability.items()},
              "median_nn": float(res.median_nn)},
    )


# ── the loss: plan (forward pairing) + eval (differentiable) ──────────────

@dataclass
class _Term:
    kind: str                    # "match" | "diag" | "recruit"
    dim: int
    birth_verts: tuple
    death_verts: tuple
    detach_birth: bool           # non-Gabriel -> value contributes, gradient doesn't
    detach_death: bool
    target: Optional[tuple]      # (b*, d*) for match/recruit
    weight: float


@dataclass
class LossPlan:
    """Frozen combinatorics of one loss evaluation. Reusable across steps until
    the cloud changes enough to warrant a refresh (or any resample invalidates
    the vertex indices — PHASE3_PLAN.md §3.5)."""
    terms: list
    scale: float
    live_diagrams: dict          # dim -> (k,2) significant finite live bars
    info: dict


def plan_topo_loss(P: np.ndarray, bundle: TargetBundle, *,
                   dims: Optional[Sequence[int]] = None, recruit: bool = True,
                   w_match: float = 1.0, w_diag: float = 1.0,
                   w_recruit: float = 1.0, gabriel_rtol: float = 1e-6) -> LossPlan:
    """Pair the live cloud's diagram against the bundle and emit loss terms."""
    dims = tuple(bundle.dims if dims is None else dims)
    bars, info = live_pairs(P, bundle.scale, dims=dims, sig_thr=bundle.sig_thr,
                            gabriel_rtol=gabriel_rtol)

    terms: list[_Term] = []
    live_diagrams: dict[int, np.ndarray] = {}
    counts = {}
    for d in dims:
        allbars = bars[d]
        sig_idx = [k for k, x in enumerate(allbars) if x.significant]
        D_live = np.array([[allbars[k].birth, allbars[k].death] for k in sig_idx],
                          dtype=np.float64).reshape(-1, 2)
        live_diagrams[d] = D_live
        tgt = bundle.diagrams.get(d, np.zeros((0, 2)))
        # matches/um_live index into sig_idx; um_tgt indexes into tgt
        matches, um_live, um_tgt = match_partial(D_live, tgt)

        for i, j in matches:
            x = allbars[sig_idx[i]]
            terms.append(_Term("match", d, x.birth_verts, x.death_verts,
                               not x.gabriel_birth, not x.gabriel_death,
                               (float(tgt[j, 0]), float(tgt[j, 1])), w_match))

        # Recruitment BEFORE diagonal terms: a missing target feature claims the
        # nearest not-yet-matched live bar — an unmatched significant one or any
        # sub-threshold bar. Longest-lived target features recruit first.
        matched_all = {sig_idx[i] for i, _ in matches}
        recruited: set[int] = set()
        n_recruit = 0
        if recruit and len(um_tgt):
            candidates = [k for k in range(len(allbars)) if k not in matched_all]
            for j in sorted(um_tgt, key=lambda jj: -(tgt[jj, 1] - tgt[jj, 0])):
                if not candidates:
                    break
                costs = [(allbars[k].birth - tgt[j, 0]) ** 2
                         + (allbars[k].death - tgt[j, 1]) ** 2 for k in candidates]
                pick = candidates.pop(int(np.argmin(costs)))
                recruited.add(pick)
                n_recruit += 1
                x = allbars[pick]
                terms.append(_Term("recruit", d, x.birth_verts, x.death_verts,
                                   not x.gabriel_birth, not x.gabriel_death,
                                   (float(tgt[j, 0]), float(tgt[j, 1])), w_recruit))

        n_diag = 0
        for i in um_live:
            k = sig_idx[i]
            if k in recruited:
                continue
            n_diag += 1
            x = allbars[k]
            terms.append(_Term("diag", d, x.birth_verts, x.death_verts,
                               not x.gabriel_birth, not x.gabriel_death,
                               None, w_diag))

        counts[d] = {"live_sig": len(sig_idx), "target": int(len(tgt)),
                     "matched": len(matches), "diag": n_diag, "recruit": n_recruit,
                     "target_unreached": max(0, len(um_tgt) - n_recruit)}

    info.update({"per_dim": counts})
    return LossPlan(terms=terms, scale=bundle.scale,
                    live_diagrams=live_diagrams, info=info)


def eval_topo_loss(X: torch.Tensor, plan: LossPlan) -> torch.Tensor:
    """Differentiable evaluation of a frozen plan at live positions X (M,3)."""
    if not plan.terms:
        return X.new_zeros(())
    simps = []
    for t in plan.terms:
        simps.append(t.birth_verts)
        simps.append(t.death_verts)
    vals = simplex_values(X, simps, plan.scale)
    loss = X.new_zeros(())
    for i, t in enumerate(plan.terms):
        b = vals[2 * i].detach() if t.detach_birth else vals[2 * i]
        d = vals[2 * i + 1].detach() if t.detach_death else vals[2 * i + 1]
        if t.kind in ("match", "recruit"):
            loss = loss + t.weight * ((b - t.target[0]) ** 2 + (d - t.target[1]) ** 2)
        else:                                            # diag
            loss = loss + t.weight * ((d - b) / 2.0) ** 2
    return loss


def matched_topo_loss(X: torch.Tensor, bundle: TargetBundle, *,
                      P: Optional[np.ndarray] = None, **plan_kw):
    """Convenience one-shot: plan on X's detached positions, then evaluate.
    Training code should instead cache the plan and refresh on its own schedule
    (PHASE3_PLAN.md §3.5)."""
    if P is None:
        P = X.detach().cpu().double().numpy()
    plan = plan_topo_loss(P, bundle, **plan_kw)
    return eval_topo_loss(X, plan), plan


# ── CLI: build + inspect a target bundle ──────────────────────────────────

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build a Phase-3 target-diagram bundle")
    ap.add_argument("--shape", choices=sorted(SHAPES), help="synthetic target")
    ap.add_argument("--mesh", help="or: a mesh file path")
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=2048, help="density-matching sample count")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--dims", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--sig_k", type=float, default=None)
    a = ap.parse_args(argv)
    if bool(a.shape) == bool(a.mesh):
        ap.error("exactly one of --shape / --mesh")
    bundle = build_target_bundle(a.shape or a.mesh, n=a.n, seed=a.seed,
                                 dims=tuple(a.dims), sig_k=a.sig_k)
    bundle.save(a.out)
    print(f"[topological_loss] wrote {a.out}")
    print(f"  scale={bundle.scale:.6g}  sig_thr={bundle.sig_thr:.6g}  M={bundle.n_points}")
    for d in bundle.dims:
        dg = bundle.diagrams[d]
        bars = ", ".join(f"[{b:.4f},{dd:.4f}]" for b, dd in dg) or "-"
        stab = bundle.meta["stability_bottleneck"].get(str(d), [])
        print(f"  H{d}: {len(dg)} significant finite bar(s): {bars}   "
              f"cross-seed bottleneck {['%.4f' % s for s in stab]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
