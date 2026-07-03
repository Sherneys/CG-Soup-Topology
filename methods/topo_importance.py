# methods/topo_importance.py
# Phase-2 deliverable 1: a DETERMINISTIC spatial *topological importance field*
# built from a fixed TARGET shape's significant persistent features.
#
# WHAT IT IS (and is not): a precomputed scalar field imp: R^3 -> [0, 1] that is
# HIGH near the geometry that carries the target's topology (the tube around a
# loop, the shell bounding a void, the neck between two components) and ~0 on
# topologically inert regions. Phase 2 uses it ONLY to bias sampling/resampling.
# There is no differentiable persistent homology and no gradient through it.
#
# HOW A 3D QUERY POINT -> SCALAR WEIGHT  (the documented mapping):
#   1. Sample the target surface -> point cloud P (original/world coords, the same
#      frame the trained soup lives in for synthetic scenes).
#   2. Persistence of P via the alpha complex (REUSES topology.persistence_from_target
#      for the diagram, scale and the self-calibrating significance threshold).
#   3. LOCALIZE each SIGNIFICANT feature with GUDHI's persistence_pairs() +
#      AlphaComplex.get_point():
#        - H1 (loop)      birth = an edge, death = the triangle that fills the loop;
#        - H2 (void)      death = the tetrahedron that fills the void (coarse: it
#                          sits on the bounding shell, not the void centre);
#        - H0 (component)  a significant FINITE bar dies on the edge that merges two
#                          components -> its midpoint is the fragile neck/gap.
#      Each feature f contributes Gaussian "kernels" centred at the 3D coordinates
#      of its birth- and death-simplex vertices, weighted by w_f = normalized
#      persistence (lifetime / bbox-diagonal), with radius sigma_f = the feature's
#      own death scale sqrt(death) = its circumradius (clamped to a spacing floor
#      and a bbox-fraction ceiling). sigma sized to the feature is the key trick:
#      it is ~loop radius / void radius / gap, so the kernel covers the feature.
#   4. (Option B, surface-splat) evaluate the kernel sum at a DENSE set of target
#      surface samples Q, normalize to [0, 1]. A query point x then takes the
#      importance of its nearest Q sample (cKDTree). Tying importance to surface
#      proximity keeps the bias on the manifold the soup must reproduce.
#
# Per-dimension fields (imp_H0/H1/H2) are kept so the evaluation can attribute any
# gain to a specific homology dimension; the combined field is their max.
#
# This module needs gudhi (via topology) + scipy + numpy; it is OFFLINE (run once
# per target). The trained loop never imports it — it consumes the saved .npz.

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass, field as _dc_field
from typing import Optional, Sequence

import numpy as np
from scipy.spatial import cKDTree

from . import _paths

_topology = _paths.load_topology()
persistence_from_target = _topology.persistence_from_target
meshes = _topology.meshes

import gudhi  # noqa: E402  (topology import has already validated availability)


# ── target -> point cloud (mirrors topology._to_points conventions) ──────

def sample_target_points(target, n: int, seed: int) -> np.ndarray:
    """(N,3) surface samples of a target given as a mesh path / (V,F) / ndarray."""
    rng = np.random.default_rng(seed)
    if isinstance(target, np.ndarray):
        return np.ascontiguousarray(target, dtype=np.float64)
    if isinstance(target, (tuple, list)) and len(target) == 2:
        V, F = target
        return meshes.sample_surface(np.asarray(V), np.asarray(F), n, rng)
    if isinstance(target, str):
        import trimesh
        m = trimesh.load(target, process=False, force="mesh")
        return meshes.sample_surface(np.asarray(m.vertices), np.asarray(m.faces), n, rng)
    raise TypeError(f"cannot sample target of type {type(target)}")


# ── feature localization via persistence_pairs + get_point ───────────────

@dataclass
class _Feature:
    dim: int
    centers: np.ndarray   # (k,3) kernel centres (simplex vertex coords, orig units)
    sigma: float          # kernel radius (orig units)
    weight: float         # normalized persistence (lifetime / scale)
    birth: float          # normalized birth
    death: float          # normalized death


def _localize_features(P: np.ndarray, scale: float, sig_thr: float,
                       med_orig: float, dims: Sequence[int],
                       sigma_floor_mult: float, sigma_ceil_frac: float,
                       spread: float = 1.0) -> list[_Feature]:
    """Significant features of P's alpha complex, each with 3D kernel centres."""
    pts = np.ascontiguousarray(P, dtype=np.float64)
    try:
        ac = gudhi.AlphaComplex(points=pts)
    except TypeError:
        ac = gudhi.AlphaComplex(points=pts.tolist())
    st = ac.create_simplex_tree()
    st.compute_persistence(persistence_dim_max=False, min_persistence=0.0)
    pairs = st.persistence_pairs()

    sigma_floor = sigma_floor_mult * med_orig          # original units
    sigma_ceil = sigma_ceil_frac * scale
    feats: list[_Feature] = []
    for bp, dp in pairs:
        d = len(bp) - 1
        if d not in dims or not dp:                    # skip essential (death=[])
            continue
        b_orig = float(np.sqrt(max(st.filtration(bp), 0.0)))
        d_orig = float(np.sqrt(max(st.filtration(dp), 0.0)))
        life_norm = (d_orig - b_orig) / scale
        if life_norm <= sig_thr:                       # not a real feature
            continue
        verts = sorted(set(bp) | set(dp))
        centers = np.array([ac.get_point(v) for v in verts], dtype=np.float64)
        # CONCENTRATE <-> SPREAD knob (dimensional-crossover follow-up):
        # widen the per-feature kernel by `spread` while HOLDING the injected
        # surface mass fixed. Option-B splats on a 2-D surface sample set, so a
        # kernel's surface integral ~ w * sigma**2; thus sigma -> s*sigma and
        # w -> w / s**2 preserves total mass and changes ONLY the spatial spread.
        # spread == 1.0 is numerically identical to the concentrated field (B2).
        sigma_base = float(np.clip(d_orig, sigma_floor, sigma_ceil))
        sigma = spread * sigma_base
        weight = life_norm / (spread ** 2)
        feats.append(_Feature(dim=d, centers=centers, sigma=sigma, weight=weight,
                              birth=b_orig / scale, death=d_orig / scale))
    return feats


# ── the importance field ─────────────────────────────────────────────────

@dataclass
class ImportanceField:
    """Surface-splatted topological importance, queryable at any 3D point.

    points       : (S,3) target surface samples carrying the field (orig coords).
    importance   : (S,)  combined importance in [0,1] (max over dims).
    by_dim       : {dim: (S,) importance in [0,1]} per-homology-dimension field.
    scale,center : the target's bbox-diagonal and centroid (bookkeeping/alignment).
    meta         : provenance + feature summary.
    """
    points: np.ndarray
    importance: np.ndarray
    by_dim: dict
    scale: float
    center: np.ndarray
    meta: dict = _dc_field(default_factory=dict)
    _tree: Optional[cKDTree] = None

    def _kdtree(self) -> cKDTree:
        if self._tree is None:
            self._tree = cKDTree(self.points)
        return self._tree

    def query(self, X: np.ndarray, dim: Optional[int] = None) -> np.ndarray:
        """Importance in [0,1] at each query point (nearest surface sample).
        dim=None -> combined field; dim in {0,1,2} -> that dimension's field."""
        X = np.ascontiguousarray(np.asarray(X, dtype=np.float64).reshape(-1, 3))
        if len(self.points) == 0:
            return np.zeros(len(X))
        _, idx = self._kdtree().query(X)
        src = self.importance if dim is None else self.by_dim.get(dim, self.importance)
        return np.asarray(src)[idx]

    # -- persistence --
    def save(self, path: str) -> str:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        payload = dict(points=self.points.astype(np.float32),
                       importance=self.importance.astype(np.float32),
                       scale=np.float64(self.scale), center=self.center.astype(np.float64))
        for d, v in self.by_dim.items():
            payload[f"by_dim_{d}"] = v.astype(np.float32)
        payload["meta_json"] = np.frombuffer(_json_bytes(self.meta), dtype=np.uint8)
        np.savez_compressed(path, **payload)
        return path

    @staticmethod
    def load(path: str) -> "ImportanceField":
        z = np.load(path, allow_pickle=False)
        by_dim = {int(k.split("_")[-1]): z[k] for k in z.files if k.startswith("by_dim_")}
        meta = _json_from_bytes(bytes(z["meta_json"])) if "meta_json" in z.files else {}
        return ImportanceField(points=z["points"].astype(np.float64),
                               importance=z["importance"].astype(np.float64),
                               by_dim={d: v.astype(np.float64) for d, v in by_dim.items()},
                               scale=float(z["scale"]), center=z["center"].astype(np.float64),
                               meta=meta)


def _json_bytes(obj) -> bytes:
    import json
    return json.dumps(obj, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)).encode("utf-8")


def _json_from_bytes(b: bytes):
    import json
    try:
        return json.loads(b.decode("utf-8"))
    except Exception:
        return {}


def _normalize01(x: np.ndarray, pct: float = 99.5) -> np.ndarray:
    if len(x) == 0:
        return x
    hi = float(np.percentile(x, pct))
    if hi <= 0:
        return np.zeros_like(x)
    return np.clip(x / hi, 0.0, 1.0)


def build_importance_field(
    target,
    *,
    n_persist: int = 20_000,
    n_field: int = 60_000,
    seed: int = 0,
    k: Optional[float] = None,
    dims: Sequence[int] = (0, 1, 2),
    sigma_floor_mult: float = 3.0,
    sigma_ceil_frac: float = 0.5,
    spread: float = 1.0,
) -> ImportanceField:
    """Build the deterministic topological importance field for a target.

    target     : mesh path / (V,F) / (N,3) point cloud.
    n_persist  : samples for persistence + localization (alpha complex).
    n_field    : DENSE samples carrying the queryable field (Option B splat).
    k          : significance multiplier (default DEFAULT_SIG_K via topology).
    dims       : homology dimensions to include.
    spread     : kernel-width multiplier. 1.0 = concentrated field (B2; sigma=
                 sqrt(death)). >1 spreads the SAME mass over a wider region
                 (mass-preserving: w -> w/spread**2). Used for condition B4
                 (topology-localized but SPREAD) in the dimensional crossover.
    """
    P = sample_target_points(target, n_persist, seed)
    # diagram + scale + self-calibrating significance threshold (REUSE Phase-1)
    res = persistence_from_target(P, n_samples=len(P), seed=seed, max_dim=max(dims))
    scale = float(res.scale)
    center = np.asarray(res.center, dtype=np.float64)
    sig_thr = float(res.significance_threshold(k))     # normalized units
    med_orig = float(res.median_nn) * scale            # original-unit spacing

    feats = _localize_features(P, scale, sig_thr, med_orig, dims,
                               sigma_floor_mult, sigma_ceil_frac, spread=spread)

    # Option B: evaluate kernels on a dense surface sample Q, splat per dimension.
    Q = sample_target_points(target, n_field, seed + 1)
    treeQ = cKDTree(Q)
    raw_by_dim = {d: np.zeros(len(Q)) for d in dims}
    for f in feats:
        # only touch field points within 4 sigma of a kernel centre (cheap + local)
        for c in f.centers:
            near = treeQ.query_ball_point(c, r=4.0 * f.sigma)
            if not near:
                continue
            near = np.asarray(near, dtype=np.int64)
            dist2 = np.sum((Q[near] - c) ** 2, axis=1)
            raw_by_dim[f.dim][near] += f.weight * np.exp(-dist2 / (2.0 * f.sigma ** 2))

    by_dim = {d: _normalize01(raw_by_dim[d]) for d in dims}
    combined = np.zeros(len(Q))
    for d in dims:
        combined = np.maximum(combined, by_dim[d])

    meta = {
        "n_persist": int(len(P)), "n_field": int(len(Q)), "seed": int(seed),
        "scale": scale, "sig_thr": sig_thr, "median_nn_norm": float(res.median_nn),
        "betti": list(res.betti_numbers()),
        "n_features": {int(d): int(sum(1 for f in feats if f.dim == d)) for d in dims},
        "features": [{"dim": int(f.dim), "weight": float(f.weight),
                      "birth": float(f.birth), "death": float(f.death),
                      "sigma": float(f.sigma),
                      "center": np.mean(f.centers, axis=0).round(5).tolist()} for f in feats],
        "option": "B_surface_splat", "sigma_rule": "sqrt(death) clamped",
        "spread": float(spread),
    }
    return ImportanceField(points=Q, importance=combined, by_dim=by_dim,
                           scale=scale, center=center, meta=meta)


# ── NON-TOPOLOGICAL control fields (for experiment B3) ───────────────────
#   Same ImportanceField format + .npz, so methods/topo_resampling.py consumes
#   them identically. They isolate the question "is any gain TOPOLOGICAL, or just
#   from biasing resampling at all?".

def _import_curvature_density(src_dir: Optional[str]):
    import importlib.util as _il
    if src_dir is None:
        src_dir = os.path.join(os.path.dirname(_paths.DIFFSOUP_ROOT),
                               "CG-Soup-for-Digital-Dentistry", "src")
    path = os.path.join(src_dir, "curvature_density.py")
    spec = _il.spec_from_file_location("curvature_density", path)
    mod = _il.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_curvature_field(target_mesh: str, *, n_field: int = 60_000, seed: int = 0,
                          src_dir: Optional[str] = None) -> ImportanceField:
    """Non-topological control: per-vertex curvedness+QEM density (REUSES CG-Soup's
    curvature_density.density_map), splatted to surface samples by nearest vertex."""
    import trimesh
    cd = _import_curvature_density(src_dir)
    m = trimesh.load(target_mesh, process=True, force="mesh")
    V = np.asarray(m.vertices, dtype=np.float64)
    density, _, _ = cd.density_map(m, n_rings=2)        # per-vertex in [0,1]
    rng = np.random.default_rng(seed + 1)
    Q = meshes.sample_surface(V, np.asarray(m.faces), n_field, rng)
    _, vidx = cKDTree(V).query(Q)
    imp = _normalize01(np.asarray(density)[vidx])
    scale = float(np.linalg.norm(V.max(0) - V.min(0)))
    meta = {"option": "curvature", "n_field": int(len(Q)), "seed": int(seed),
            "signal": "0.5*curvedness + 0.5*QEM (non-topological)"}
    return ImportanceField(points=Q, importance=imp, by_dim={}, scale=scale,
                           center=Q.mean(0), meta=meta)


def build_random_field(target, *, n_field: int = 60_000, seed: int = 0,
                       n_blobs: int = 6, sigma_frac: float = 0.22,
                       sigma_abs: Optional[float] = None) -> ImportanceField:
    """Non-topological control: random Gaussian importance blobs on the surface —
    comparable spatial STRUCTURE to the topo field but at RANDOM locations.

    sigma_abs: if given, use this ABSOLUTE kernel width instead of sigma_frac*scale
    (used to WIDTH-MATCH the B3-spread control to B4's spread sigma); the per-blob
    weight is mass-preserved relative to the narrow default so the control differs
    from plain B3 only in width."""
    rng = np.random.default_rng(seed + 12_345)
    Q = sample_target_points(target, n_field, seed + 1)
    scale = float(np.linalg.norm(Q.max(0) - Q.min(0)))
    if sigma_abs is not None:                    # width-matched control (e.g. to B4's spread sigma)
        sigma = float(sigma_abs)
        wscale = (sigma_frac * scale / sigma) ** 2   # mass-preserving vs the narrow default
    else:
        sigma = sigma_frac * scale
        wscale = 1.0
    ctr_idx = rng.choice(len(Q), size=min(n_blobs, len(Q)), replace=False)
    centers, weights = Q[ctr_idx], rng.uniform(0.5, 1.0, size=len(ctr_idx)) * wscale
    treeQ = cKDTree(Q)
    raw = np.zeros(len(Q))
    for c, w in zip(centers, weights):
        near = np.asarray(treeQ.query_ball_point(c, r=4.0 * sigma), dtype=np.int64)
        if near.size:
            raw[near] += w * np.exp(-np.sum((Q[near] - c) ** 2, axis=1) / (2.0 * sigma ** 2))
    meta = {"option": "random", "n_field": int(len(Q)), "seed": int(seed),
            "n_blobs": int(len(ctr_idx)), "sigma": float(sigma),
            "signal": "random blobs (non-topological)"}
    return ImportanceField(points=Q, importance=_normalize01(raw), by_dim={},
                           scale=scale, center=Q.mean(0), meta=meta)


# ── CLI: precompute a field from a target mesh -> npz ────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description="Build an importance field from a target mesh.")
    ap.add_argument("--target", required=True, help="mesh path (.ply/.obj) or .npy point cloud")
    ap.add_argument("--out", required=True, help="output .npz")
    ap.add_argument("--mode", choices=["topo", "curvature", "random"], default="topo")
    ap.add_argument("--n_persist", type=int, default=20_000)
    ap.add_argument("--n_field", type=int, default=60_000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--k", type=float, default=None, help="significance multiplier (default 6.0)")
    ap.add_argument("--dims", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--spread", type=float, default=1.0,
                    help="kernel widen factor (1=concentrated B2; >1=spread B4, mass-preserving)")
    args = ap.parse_args()

    target = np.load(args.target) if args.target.endswith(".npy") else args.target
    if args.mode == "topo":
        fld = build_importance_field(target, n_persist=args.n_persist, n_field=args.n_field,
                                     seed=args.seed, k=args.k, dims=tuple(args.dims),
                                     spread=args.spread)
    elif args.mode == "curvature":
        fld = build_curvature_field(target, n_field=args.n_field, seed=args.seed)
    else:
        fld = build_random_field(target, n_field=args.n_field, seed=args.seed)
    fld.save(args.out)

    m = fld.meta
    print(f"[importance:{args.mode}] target={args.target}")
    if args.mode == "topo":
        print(f"  betti={m['betti']}  significant features per dim={m['n_features']}")
        for fe in m["features"]:
            print(f"    H{fe['dim']}  persistence={fe['weight']:.4f}  sigma={fe['sigma']:.4f}  "
                  f"center={fe['center']}")
    nz = float((fld.importance > 0.05).mean())
    print(f"  field: {m['n_field']} surface pts, {nz*100:.1f}% with importance>0.05")
    print(f"[save] {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
