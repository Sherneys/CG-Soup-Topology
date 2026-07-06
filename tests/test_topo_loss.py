# tests/test_topo_loss.py
# Verification gate for Phase-3 stage 3a (PHASE3_PLAN.md §5). The differentiable
# topological loss must, BEFORE any DiffSoup integration:
#   1. have exact gradients (closed-form circumradii + frozen-plan loss vs
#      finite differences),
#   2. satisfy the alpha-complex assumptions on our shapes (vertex ids map 1:1
#      to input indices; significant pairs are Gabriel so the recomputed
#      circumradius IS the diagram value),
#   3. actually repair topological defects when optimized (toys T1-T3), with
#      the recruitment pathology probe T4 reported (not gated).
#
# Runs under pytest, OR standalone:  python tests\test_topo_loss.py
# Deterministic: every cloud is seeded; optimizers are CPU float64.
#
# Toy constants were probed empirically (2026-07-06) at M=2048 / sig_k=4.0 so
# every defect bar clears the significance threshold with margin:
#   T1 punctured sphere   hole .45          live H2 [0.122,0.269] thr 0.069
#   T2 handle sphere      h=1.0 tr=.08 a=.6 live H1 [0.018,0.106] (spurious)
#   T3 far two_spheres    live gap 1.0      live H0 [0,0.209] vs target 0.145
#   T4 bridged spheres    gap .5 bridge     live H0 sub-threshold -> recruit

from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from methods._paths import load_topology
topology = load_topology()

import gudhi  # noqa: E402

from methods.topological_loss import (  # noqa: E402
    LossPlan, _Term, TargetBundle,
    build_target_bundle, circumradius_edge, circumradius_tetra,
    circumradius_triangle, eval_topo_loss, live_pairs, matched_topo_loss,
    plan_topo_loss)

meshes = topology.meshes
persistence_from_points = topology.persistence_from_points

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(REPO, "figures", "phase3_toy")

M = 2048
SIG_K = 4.0
_rng = lambda s: np.random.default_rng(s)


def _bbox_diag(P: np.ndarray) -> float:
    return float(np.linalg.norm(P.max(axis=0) - P.min(axis=0)))


def _bottleneck(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) == 0 and len(b) == 0:
        return 0.0
    return float(gudhi.bottleneck_distance(np.asarray(a).tolist(),
                                           np.asarray(b).tolist()))


# ── 1. gradients ──────────────────────────────────────────────────────


def test_circumradius_values():
    """Closed forms against textbook values, under a random rigid motion."""
    rng = _rng(7)
    A = np.linalg.qr(rng.normal(size=(3, 3)))[0]          # random rotation
    t = rng.normal(size=3)

    def tt(pts):                                          # rigid-transform + tensor
        return torch.tensor((np.asarray(pts) @ A.T) + t, dtype=torch.float64)

    r = circumradius_edge(tt([[0, 0, 0], [2, 0, 0]]).unsqueeze(0))
    assert torch.allclose(r, torch.tensor([1.0], dtype=torch.float64)), r

    eq = [[0, 0, 0], [1, 0, 0], [0.5, np.sqrt(3) / 2, 0]]  # side 1 -> R=1/sqrt(3)
    r = circumradius_triangle(tt(eq).unsqueeze(0))
    assert torch.allclose(r, torch.tensor([1 / np.sqrt(3)], dtype=torch.float64)), r

    right = [[0, 0, 0], [3, 0, 0], [0, 4, 0]]              # hypotenuse 5 -> R=2.5
    r = circumradius_triangle(tt(right).unsqueeze(0))
    assert torch.allclose(r, torch.tensor([2.5], dtype=torch.float64)), r

    tet = [[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]]  # edge 2√2 -> R=√3
    r = circumradius_tetra(tt(tet).unsqueeze(0))
    assert torch.allclose(r, torch.tensor([np.sqrt(3.0)], dtype=torch.float64)), r
    print("[PASS] circumradius closed forms (rigid-motion invariant)")


def test_circumradius_gradcheck():
    """Autograd vs finite differences, float64, well-conditioned simplices."""
    rng = _rng(11)
    for fn, k in ((circumradius_edge, 2), (circumradius_triangle, 3),
                  (circumradius_tetra, 4)):
        p = torch.tensor(rng.normal(size=(5, k, 3)), dtype=torch.float64,
                         requires_grad=True)
        assert torch.autograd.gradcheck(fn, (p,), eps=1e-6, atol=1e-8), fn
    print("[PASS] circumradius gradcheck (edge/triangle/tetra)")


def test_eval_loss_gradcheck_synthetic():
    """eval_topo_loss gradient on a hand-built plan covering every term kind.
    The pairing is piecewise constant in X, so the frozen-plan gradient is the
    true gradient a.e. The non-Gabriel detach path is checked separately — it
    is DESIGNED to differ from the numerical Jacobian (value kept, gradient
    blocked), so it must not sit inside a gradcheck."""
    rng = _rng(13)
    P = rng.normal(size=(24, 3))
    terms = [
        _Term("match", 1, (0, 1), (2, 3, 4), False, False, (0.10, 0.40), 1.0),
        _Term("match", 2, (5, 6, 7), (8, 9, 10, 11), False, False, (0.05, 0.30), 1.0),
        _Term("diag", 1, (12, 13), (14, 15, 16), False, False, None, 0.7),
        _Term("recruit", 0, (17,), (18, 19), False, False, (0.0, 0.25), 1.3),
    ]
    plan = LossPlan(terms=terms, scale=1.7, live_diagrams={}, info={})
    X = torch.tensor(P, dtype=torch.float64, requires_grad=True)
    assert torch.autograd.gradcheck(lambda x: eval_topo_loss(x, plan), (X,),
                                    eps=1e-6, atol=1e-8)

    # detach path: same value as the free term, zero gradient on the detached
    # simplex's exclusive vertices, live gradient on the free simplex.
    mk = lambda detach_death: LossPlan(
        terms=[_Term("match", 2, (5, 6, 7), (20, 21, 22, 23), False,
                     detach_death, (0.05, 0.30), 1.0)],
        scale=1.7, live_diagrams={}, info={})
    Xd = torch.tensor(P, dtype=torch.float64, requires_grad=True)
    ld = eval_topo_loss(Xd, mk(True))
    lf = eval_topo_loss(torch.tensor(P, dtype=torch.float64), mk(False))
    assert abs(float(ld.detach()) - float(lf.detach())) < 1e-12
    ld.backward()
    assert torch.all(Xd.grad[[20, 21, 22, 23]] == 0), "detached simplex leaked grad"
    assert torch.any(Xd.grad[[5, 6, 7]] != 0), "free simplex lost grad"
    print("[PASS] eval_topo_loss gradcheck (term kinds) + detach semantics")


def test_frozen_plan_gradcheck_real():
    """Same, but the plan comes from a REAL pairing: sphere seed 5 against the
    seed-0 bundle (every bar significant and matched, small offsets)."""
    n = 700
    bundle = build_target_bundle(meshes.sphere_cloud(n, rng=_rng(0)), n=n,
                                 sig_k=3.5, stability_seeds=())
    Q = meshes.sphere_cloud(n, rng=_rng(5))
    plan = plan_topo_loss(Q, bundle)
    kinds = sorted(t.kind for t in plan.terms)
    assert "match" in kinds, f"expected a matched term, got {kinds}"
    X = torch.tensor(Q, dtype=torch.float64, requires_grad=True)
    assert torch.autograd.gradcheck(lambda x: eval_topo_loss(x, plan), (X,),
                                    eps=1e-6, atol=1e-8)
    print(f"[PASS] frozen-plan gradcheck on a real pairing ({len(plan.terms)} terms)")


# ── 2. alpha-complex assumption gates ─────────────────────────────────


def test_mapping_and_gabriel_gate():
    """§3.2 gates across the 6 registry shapes at the working density M:
    live_pairs raises if vertex ids don't map to input indices; here we also
    require that ≥50% of significant-bar simplex values are Gabriel-exact
    (recomputed circumradius == filtration value) so the pair-frozen backward
    has gradient paths to work with. Empirical rates are printed per shape."""
    shapes = {
        "sphere": meshes.sphere_cloud(M, rng=_rng(0)),
        "torus": meshes.torus_cloud(M, rng=_rng(0)),
        "two_spheres": meshes.two_spheres_cloud(M, rng=_rng(0)),
        "double_torus": meshes.double_torus_cloud(M, rng=_rng(0)),
        "three_spheres": meshes.three_spheres_cloud(M, rng=_rng(0)),
        "thick_shell": meshes.thick_shell_cloud(M, rng=_rng(0)),
    }
    tot_checks = tot_gabriel = 0
    for name, P in shapes.items():
        bars, info = live_pairs(P, _bbox_diag(P))          # mapping gate inside
        n_sig = g_ok = g_all = 0
        for d, xs in bars.items():
            for x in xs:
                if not x.significant:
                    continue
                n_sig += 1
                g_ok += int(x.gabriel_birth) + int(x.gabriel_death)
                g_all += 2
        rate = g_ok / max(g_all, 1)
        tot_checks += g_all
        tot_gabriel += g_ok
        print(f"  {name:14s} sig bars {n_sig:2d}  gabriel-exact {g_ok}/{g_all} "
              f"({100 * rate:.0f}%)  finite pairs {info['n_finite_pairs']}")
    frac = tot_gabriel / max(tot_checks, 1)
    assert frac >= 0.5, (
        f"only {100 * frac:.0f}% of significant-bar simplex values are Gabriel-"
        f"exact; the pair-frozen backward is starved — switch to the weighted-"
        f"Rips fallback (PHASE3_PLAN.md §3.2)")
    print(f"[PASS] mapping + Gabriel gates: {tot_gabriel}/{tot_checks} "
          f"({100 * frac:.0f}%) Gabriel-exact across 6 shapes @M={M}")


# ── 3. loss semantics ─────────────────────────────────────────────────


def test_loss_zero_on_target():
    """The loss must be exactly satisfiable: evaluated on the bundle's own
    cloud, every significant bar matches its identical target bar at zero cost
    and nothing is recruited or pushed."""
    P = meshes.sphere_cloud(M, rng=_rng(0))
    bundle = build_target_bundle(P, n=M, sig_k=SIG_K, stability_seeds=())
    X = torch.tensor(P, dtype=torch.float64, requires_grad=True)
    loss, plan = matched_topo_loss(X, bundle)
    assert float(loss.detach()) < 1e-12, float(loss.detach())
    for d, c in plan.info["per_dim"].items():
        assert c["matched"] == c["target"], (d, c)
        assert c["diag"] == 0 and c["recruit"] == 0 and c["target_unreached"] == 0, (d, c)

    Q = meshes.sphere_with_hole_cloud(M, hole_half_angle=0.45, rng=_rng(0))
    loss_bad, _ = matched_topo_loss(torch.tensor(Q, dtype=torch.float64), bundle)
    assert float(loss_bad) > 1e-4, float(loss_bad)
    print(f"[PASS] loss==0 on the target cloud; {float(loss_bad):.4f} on the "
          f"punctured defect")


# ── 4. toy recovery (the scientific gate) ─────────────────────────────


def _betti(P: np.ndarray, bundle: TargetBundle) -> tuple:
    res = persistence_from_points(P, scale=bundle.scale)
    return res.betti_numbers(abs_thr=bundle.sig_thr)


def run_toy(name: str, P0: np.ndarray, bundle: TargetBundle, disc_dim: int, *,
            iters: int, lr: float, refresh_every: int = 1) -> dict:
    X = torch.tensor(P0, dtype=torch.float64, requires_grad=True)
    opt = torch.optim.Adam([X], lr=lr)
    plan = None
    series = []                                            # (iter, bottleneck)
    t0 = time.perf_counter()
    for it in range(iters):
        if plan is None or it % refresh_every == 0:
            plan = plan_topo_loss(X.detach().numpy(), bundle)
            bd = _bottleneck(plan.live_diagrams[disc_dim],
                             bundle.diagrams.get(disc_dim, np.zeros((0, 2))))
            series.append((it, bd))
        if not plan.terms:
            break                                          # fully satisfied
        loss = eval_topo_loss(X, plan)
        opt.zero_grad()
        loss.backward()
        opt.step()
    P1 = X.detach().numpy()
    plan = plan_topo_loss(P1, bundle)
    bd_final = _bottleneck(plan.live_diagrams[disc_dim],
                           bundle.diagrams.get(disc_dim, np.zeros((0, 2))))
    series.append((iters, bd_final))
    out = {
        "name": name, "disc_dim": disc_dim, "iters": iters, "lr": lr,
        "bottleneck_initial": series[0][1], "bottleneck_final": bd_final,
        "factor": series[0][1] / max(bd_final, 1e-12),
        "betti_initial": _betti(P0, bundle), "betti_final": _betti(P1, bundle),
        "betti_target": tuple(
            (1 if d == 0 else 0) + len(bundle.diagrams.get(d, ()))
            for d in (0, 1, 2)),                           # +1: essential H0
        "seconds": time.perf_counter() - t0,
        "series": series,
    }
    _save_toy_artifacts(out, P0, P1)
    print(f"  {name}: H{disc_dim} bottleneck {out['bottleneck_initial']:.4f} -> "
          f"{bd_final:.4f} ({out['factor']:.1f}x)  betti {out['betti_initial']} -> "
          f"{out['betti_final']} (target {out['betti_target']})  "
          f"[{out['seconds']:.0f}s]")
    return out


def _save_toy_artifacts(out: dict, P0: np.ndarray, P1: np.ndarray) -> None:
    os.makedirs(FIG_DIR, exist_ok=True)
    slug = out["name"].split()[0].lower()
    with open(os.path.join(FIG_DIR, f"{slug}.json"), "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in out.items() if k != "series"} |
                  {"series": [[int(i), float(b)] for i, b in out["series"]]},
                  f, indent=2, default=str)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return                                             # plots are optional
    fig = plt.figure(figsize=(12, 4))
    for i, (P, title) in enumerate(((P0, "before"), (P1, "after"))):
        ax = fig.add_subplot(1, 3, i + 1, projection="3d")
        ax.scatter(P[:, 0], P[:, 1], P[:, 2], s=1)
        ax.set_title(f"{out['name']} — {title}")
        ax.set_box_aspect((np.ptp(P[:, 0]), np.ptp(P[:, 1]), np.ptp(P[:, 2])))
    ax = fig.add_subplot(1, 3, 3)
    s = np.asarray(out["series"], dtype=float)
    ax.plot(s[:, 0], s[:, 1])
    ax.set_xlabel("iteration")
    ax.set_ylabel(f"bottleneck H{out['disc_dim']} to target")
    ax.set_title(f"{out['factor']:.1f}x reduction")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, f"{slug}.png"), dpi=110)
    plt.close(fig)


def test_toy_t1_punctured_sphere():
    """Matched-pair BIRTH pull: close the hole so the void encloses on time."""
    bundle = build_target_bundle(meshes.sphere_cloud(M, rng=_rng(0)), n=M,
                                 sig_k=SIG_K, stability_seeds=())
    P0 = meshes.sphere_with_hole_cloud(M, hole_half_angle=0.45, rng=_rng(0))
    out = run_toy("T1 punctured-sphere->sphere (H2)", P0, bundle, 2,
                  iters=500, lr=8e-3)
    assert out["factor"] >= 5.0, out
    assert out["betti_final"] == (1, 0, 1), out
    return out


def test_toy_t2_handle_sphere():
    """Diagonal push: kill the spurious handle loop (the Phase-2 phantom-handle
    failure mode, now attacked by metric pressure instead of resampling)."""
    bundle = build_target_bundle(meshes.sphere_cloud(M, rng=_rng(0)), n=M,
                                 sig_k=SIG_K, stability_seeds=())
    P0 = meshes.sphere_with_handle_cloud(M, height=1.0, tube_r=0.08,
                                         attach_angle=0.6, rng=_rng(0))
    out = run_toy("T2 handle-sphere->sphere (H1)", P0, bundle, 1,
                  iters=400, lr=8e-3)
    assert out["factor"] >= 5.0, out
    assert out["betti_final"] == (1, 0, 1), out
    return out


def test_toy_t3_far_two_spheres():
    """Matched-pair DEATH pull on H0: drag the components toward the target
    separation (sparse-tug mechanics: expect a drawn 'antenna', not a rigid
    translation — the diagram is what must land, and does)."""
    bundle = build_target_bundle(meshes.two_spheres_cloud(M, gap=0.7, rng=_rng(0)),
                                 n=M, sig_k=SIG_K, stability_seeds=())
    P0 = meshes.two_spheres_cloud(M, gap=1.0, rng=_rng(0))
    out = run_toy("T3 far-two-spheres->gap0.7 (H0)", P0, bundle, 0,
                  iters=250, lr=1e-2)
    assert out["factor"] >= 5.0, out
    assert out["betti_final"] == (2, 0, 2), out
    return out


def test_toy_t4_bridged_spheres_probe():
    """RECRUITMENT probe (reported, not gated): the bridge merges the components
    below the noise floor, so no significant live H0 bar exists and pure
    Wasserstein matching would return zero gradient. Recruitment restores one —
    but it is location-blind (grabs the largest sub-threshold merge anywhere),
    so this may satisfy the diagram by tearing the WRONG points apart, or stall.
    Whatever happens is the documented §3.1 pathology probe."""
    bundle = build_target_bundle(meshes.two_spheres_cloud(M, gap=0.5, rng=_rng(0)),
                                 n=M, sig_k=SIG_K, stability_seeds=())
    P0 = meshes.bridged_spheres_cloud(M, gap=0.5, rng=_rng(0))
    out = run_toy("T4 bridged-spheres->two-spheres (H0, recruitment)", P0,
                  bundle, 0, iters=600, lr=1e-2)
    verdict = ("RECOVERED" if out["factor"] >= 5.0 and out["betti_final"][0] == 2
               else "PARTIAL/STALLED")
    print(f"  T4 verdict: {verdict} (informational probe, no hard gate)")
    return out


# ── standalone runner ─────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_circumradius_values,
        test_circumradius_gradcheck,
        test_eval_loss_gradcheck_synthetic,
        test_frozen_plan_gradcheck_real,
        test_mapping_and_gabriel_gate,
        test_loss_zero_on_target,
        test_toy_t1_punctured_sphere,
        test_toy_t2_handle_sphere,
        test_toy_t3_far_two_spheres,
        test_toy_t4_bridged_spheres_probe,
    ]
    failed = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            failed += 1
            print(f"[FAIL] {t.__name__}: {e}")
        except Exception as e:                             # noqa: BLE001
            failed += 1
            print(f"[ERROR] {t.__name__}: {type(e).__name__}: {e}")
    total = len(tests)
    print(f"\n{total - failed}/{total} PASS")
    sys.exit(1 if failed else 0)
