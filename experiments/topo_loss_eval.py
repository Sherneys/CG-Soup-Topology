# experiments/topo_loss_eval.py
# Phase-3 stages 3c/3d: the C-matrix runner (PHASE3_PLAN.md §6).
#
# Thin sibling of topo_resampling_eval.py — reuses its venv/scene/env plumbing
# and (for C5) the Phase-2 field builder. Conditions:
#   C0  baseline (photometric only)
#   C1  + matched topological loss (rho, ramp default 0.2:0.5)
#   C2  + gradient-norm-matched repulsion on the SAME samples (the control)
#   C3  C1 WITHOUT curriculum (constant lambda from step 1: ramp "0:0")
#   C5  C1 + the B4 spread resampling prior (Phase-2 best; channel stacking)
#   C6  C1 WITHOUT recruitment (pure matching+diagonal; --topo_recruit 0)
#   C7  C1 + sensor noise on the plan's cloud, sigma=0.5% of the diagonal
#   C7h C1 + sensor noise, sigma=1% (~= one median sample spacing at M=2048)
#   (C4 curvature-weighted spatial mask: DEFERRED — needs a weight-mask input
#    on TopoLossState; wire it before the decisive-shape extension runs.)
#
# Deviation from §6 noted in Appendix C: C0 is re-run fresh instead of reusing
# Phase-2 B0 trajectories — a 2,500-step run here is ~1-3 min, and re-running
# keeps the traj schedule and code state identical across arms.
#
# Tags: {shape}_{cond}_r{rho}_s{seed} (rho omitted for C0) under
# output/synth/<exp_name>/. Resumable: runs whose final dump exists are skipped.
#
# 3c rho sweep:
#   python experiments/topo_loss_eval.py --shapes sphere --seeds 0 \
#       --conditions C0 C1 --rhos 0.03 0.1 0.3 --steps 2500 --max_faces 1200
#   python experiments/topo_loss_eval.py --quicklook --shapes sphere \
#       --conditions C0 C1 C2 --rhos 0.03 0.1 0.3

from __future__ import annotations

import argparse
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_TOPO_ROOT = os.path.dirname(_HERE)
for _p in (_HERE, _TOPO_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from topo_resampling_eval import (  # noqa: E402  (the Phase-2 harness plumbing)
    DENTISTRY, PY, TRAIN, scene_dir, _run,
    ensure_fields, field_path, spread_kind, SHAPE_DIM, traj_schedule)


def exp_root(name: str) -> str:
    return os.path.join(DENTISTRY, "output", "synth", name)


# ── target bundle (density-matched; PHASE3_PLAN.md §4) ───────────────────

def ensure_bundle(shape: str, root: str, *, n: int = 2048, seed: int = 0,
                  rebuild: bool = False) -> str:
    from methods.topological_loss import build_target_bundle
    p = os.path.join(root, "fields", f"{shape}_diag.npz")
    if rebuild or not os.path.exists(p):
        gt = os.path.join(scene_dir(shape), "gt_mesh.ply")
        if not os.path.exists(gt):
            raise FileNotFoundError(gt)
        print(f"[bundle] {shape}: target diagram, M={n} …")
        b = build_target_bundle(gt, n=n, seed=seed)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        b.save(p)
        for d in b.dims:
            print(f"  H{d}: {len(b.diagrams[d])} significant bar(s), "
                  f"thr={b.sig_thr:.4f}")
    return p


# ── condition -> diffsoup_train flags ─────────────────────────────────────

def condition_flags(cond: str, shape: str, bundle: str, rho: float, ramp: str,
                    spread: float, lam_prior: float, loss_dims: int = -1) -> list:
    c1 = ["--topo_loss_npz", bundle, "--topo_rho", str(rho), "--topo_ramp", ramp]
    if loss_dims >= 0:                                   # e.g. torus: H1 only (its
        c1 += ["--topo_loss_dims", str(loss_dims)]       # H2 bar is sub-thr at M)
    if cond == "C0":
        return []
    if cond == "C1":
        return c1
    if cond == "C2":
        return c1 + ["--topo_loss_mode", "control_repulsion"]
    if cond == "C2g":                                    # gentler control (r0 = 1 spacing)
        return c1 + ["--topo_loss_mode", "control_repulsion",
                     "--topo_rep_scale", "1.0"]
    if cond == "C3":                                     # no curriculum
        return c1[:2] + ["--topo_rho", str(rho), "--topo_ramp", "0:0"] \
            + (["--topo_loss_dims", str(loss_dims)] if loss_dims >= 0 else [])
    if cond == "C5":                                     # loss + B4 spread prior
        return c1 + ["--resample_mode", "topo",
                     "--importance_npz", field_path(shape, spread_kind(spread)),
                     "--lambda_topo", str(lam_prior),
                     "--topo_dim", str(SHAPE_DIM[shape])]
    if cond == "C6":                                     # no recruitment (ablation)
        return c1 + ["--topo_recruit", "0"]
    if cond == "C7":                                     # sensor-noise stress, mild
        return c1 + ["--topo_noise", "0.005"]
    if cond == "C7h":                                    # sensor-noise stress, strong
        return c1 + ["--topo_noise", "0.01"]
    raise ValueError(cond)


def tag_of(shape: str, cond: str, rho: float, seed: int) -> str:
    if cond == "C0":
        return f"{shape}_{cond}_s{seed}"
    return f"{shape}_{cond}_r{rho:g}_s{seed}"


# ── quicklook: tail-mean disc-dim bottleneck + Chamfer parity ─────────────

def _chamfer_norm(P: "np.ndarray", Q: "np.ndarray", scale: float) -> float:
    """Symmetric mean nearest-neighbour distance / scale (mirrors the
    eval_geometry normalization closely enough for a parity check)."""
    from scipy.spatial import cKDTree
    d_pq, _ = cKDTree(Q).query(P, k=1)
    d_qp, _ = cKDTree(P).query(Q, k=1)
    return float((d_pq.mean() + d_qp.mean()) / 2.0 / scale)


def quicklook(args, root: str) -> int:
    import numpy as np
    from methods._paths import load_topology
    topology = load_topology()
    meshes, metrics = topology.meshes, topology.metrics

    out_rows = []
    for shape in args.shapes:
        disc = SHAPE_DIM[shape]
        gt = os.path.join(scene_dir(shape), "gt_mesh.ply")
        tgt = topology.persistence_from_target(gt, n_samples=20_000, seed=0)
        import trimesh
        m = trimesh.load(gt, process=False, force="mesh")
        gt_cloud = meshes.sample_surface(np.asarray(m.vertices),
                                         np.asarray(m.faces), 20_000,
                                         np.random.default_rng(0))
        print(f"\n=== {shape} (disc dim H{disc}, target scale {tgt.scale:.4f}) ===")
        print(f"{'tag':34s} {'tail bott':>10s} {'final nsig':>10s} {'chamfer%':>9s}")
        for cond in args.conditions:
            for rho in ([None] if cond == "C0" else args.rhos):
                for s in args.seeds:
                    tag = tag_of(shape, cond, rho, s)
                    traj = os.path.join(root, tag)
                    if not os.path.isdir(traj):
                        continue
                    steps, dumps = metrics.load_trajectory(traj)
                    series = metrics.topology_stability_series(
                        dumps, tgt, steps=steps, n_samples=20_000, seed=0,
                        dims=(disc,))
                    tail = series[-args.tail:]
                    bott = float(np.mean([r[f"bottleneck_H{disc}"] for r in tail]))
                    nsig = int(series[-1][f"nsig_H{disc}"])
                    soup = meshes.soup_cloud(dumps[-1], 20_000,
                                             np.random.default_rng(0))
                    cham = 100.0 * _chamfer_norm(soup, gt_cloud, tgt.scale)
                    print(f"{tag:34s} {bott:10.4f} {nsig:10d} {cham:9.3f}")
                    out_rows.append({"shape": shape, "cond": cond,
                                     "rho": rho, "seed": s, "tag": tag,
                                     f"tail_bottleneck_H{disc}": bott,
                                     f"nsig_H{disc}": nsig, "chamfer_pct": cham})
    path = os.path.join(root, "quicklook.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out_rows, fh, indent=2)
    print(f"\n[quicklook] {len(out_rows)} rows → {path}")
    return 0


# ── main sweep ────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description="Phase-3 C-matrix runner")
    ap.add_argument("--shapes", nargs="+", default=["sphere"])
    ap.add_argument("--seeds", nargs="+", type=int, default=[0])
    ap.add_argument("--conditions", nargs="+", default=["C0", "C1", "C2"],
                    choices=["C0", "C1", "C2", "C2g", "C3", "C5", "C6", "C7", "C7h"])
    ap.add_argument("--rhos", nargs="+", type=float, default=[0.1])
    ap.add_argument("--ramp", default="0.2:0.5")
    ap.add_argument("--steps", type=int, default=2500)
    ap.add_argument("--max_faces", type=int, default=1200)
    ap.add_argument("--downscale", type=int, default=1)
    ap.add_argument("--batch_size", type=int, default=4)
    ap.add_argument("--init", default="random", choices=["random", "curvature"])
    ap.add_argument("--exp_name", default="topo3")
    ap.add_argument("--spread", type=float, default=3.0, help="C5's B4 field spread")
    ap.add_argument("--lambda_prior", type=float, default=1.0, help="C5's prior strength")
    ap.add_argument("--loss_dims", type=int, default=-1,
                    help="restrict the loss to one homology dim (-1 = all bundle dims)")
    ap.add_argument("--bundle_n", type=int, default=2048)
    ap.add_argument("--rebuild_bundle", action="store_true")
    ap.add_argument("--quicklook", action="store_true",
                    help="analyze existing runs instead of training")
    ap.add_argument("--tail", type=int, default=3,
                    help="quicklook: dumps in the tail mean")
    args = ap.parse_args()

    root = exp_root(args.exp_name)
    os.makedirs(root, exist_ok=True)
    if args.quicklook:
        return quicklook(args, root)

    sched = traj_schedule(args.steps)
    for shape in args.shapes:
        bundle = ensure_bundle(shape, root, n=args.bundle_n,
                               rebuild=args.rebuild_bundle)
        if "C5" in args.conditions:                      # Phase-2 B4 field
            ensure_fields(shape, ["B4"], "random", spread=args.spread)
        scene = scene_dir(shape)
        for cond in args.conditions:
            for rho in ([None] if cond == "C0" else args.rhos):
                for s in args.seeds:
                    tag = tag_of(shape, cond, rho, s)
                    traj = os.path.join(root, tag)
                    if os.path.exists(os.path.join(traj, f"step_{args.steps:05d}.pt")):
                        print(f"[skip] {tag}")
                        continue
                    cmd = [PY, TRAIN, "--scene_root", scene,
                           "--downscale", str(args.downscale),
                           "--max_faces", str(args.max_faces),
                           "--steps", str(args.steps),
                           "--batch_size", str(args.batch_size),
                           "--seed", str(s), "--init", args.init,
                           "--out_dir", os.path.join(root, "_train", tag),
                           "--traj_dir", traj, "--traj_schedule", sched]
                    cmd += condition_flags(cond, shape, bundle, rho, args.ramp,
                                           args.spread, args.lambda_prior,
                                           loss_dims=args.loss_dims)
                    print(f"[run ] {tag}")
                    if not _run(cmd):
                        print(f"[FAIL] {tag} — stopping")
                        return 1
    print("\n[done] runs complete. Analyze: topo_loss_eval.py --quicklook …")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
