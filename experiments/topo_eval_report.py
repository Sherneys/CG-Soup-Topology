# experiments/topo_eval_report.py
# Phase-2 deliverable 4: evaluation + plots + summary, reusing topology/ unchanged.
#
# For every (shape, condition, seed) trajectory dumped by topo_resampling_eval.py:
#   * PRIMARY   — bottleneck-to-target in the DISCRIMINATING dimension over training
#                 (topology.metrics.topology_stability_series vs the target's
#                 persistence_from_target diagram), averaged over seeds.
#   * Betti     — count of SIGNIFICANT features in the disc. dim over training:
#                 when does the correct topology emerge, and does it persist?
#   * PARITY    — Chamfer / Hausdorff95 over training (eval_geometry conventions):
#                 is B2 COMPARABLE to B0? (the claim is "correct topology at equal
#                 geometry", NOT better geometry).
#
# Outputs (under <exp_root>/report/):
#   <shape>_bottleneck.png, <shape>_betti.png, <shape>_geometry.png
#   summary.md  (headline comparison table)  +  results.json
#
# Honest reporting: a null result (B2 does not beat B0/B1) is printed plainly.
#
# Run:  python experiments/topo_eval_report.py --shapes torus --conditions B0 B2

from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

_TOPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _TOPO_ROOT not in sys.path:
    sys.path.insert(0, _TOPO_ROOT)
from methods._paths import load_topology

topology = load_topology()
meshes = topology.meshes
metrics = topology.metrics
persistence_from_target = topology.persistence_from_target

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

DENTISTRY = os.environ.get("CGSOUP_ROOT", r"D:\Project\CG-Soup-for-Digital-Dentistry")
EXP_ROOT = os.path.join(DENTISTRY, "output", "synth", "topo2")
SHAPE_DIM = {"torus": 1, "two_spheres": 0, "sphere": 2, "cube": 2, "cylinder": 2,
             "double_torus": 1, "three_spheres": 0, "thick_shell": 2,
             "tomyum": 1}
# tomyum: genus 9 mesh, but the SIGNIFICANT cloud reading at eval densities is
# the metal solid's chimney cycle only — (1,1,0) holds for M in [2048, 30000];
# the full handlebody rank (1,9,0) needs M~50000 (see scripts/make_tomyum_asset).
CORRECT_BETTI = {"torus": (1, 2, 1), "two_spheres": (2, 0, 2), "sphere": (1, 0, 1),
                 "cube": (1, 0, 1), "cylinder": (1, 0, 1),
                 "double_torus": (1, 4, 1), "three_spheres": (3, 0, 3), "thick_shell": (1, 0, 1),
                 "tomyum": (1, 1, 0)}
COND_COLOR = {"B0": "#555555", "B1": "#1f77b4", "B2": "#d62728", "B3": "#2ca02c",
              "B4": "#ff7f0e", "B5": "#9467bd"}
COND_LABEL = {"B0": "B0 baseline", "B1": "B1 topo@init", "B2": "B2 topo concentrate",
              "B3": "B3 non-topo in-loop", "B4": "B4 topo spread",
              "B5": "B5 non-topo width-matched"}
N_GEOM = 30_000


# ── geometry parity (eval_geometry conventions: normalize by GT bbox diag) ──

def _geom_metrics(P_recon, P_ref, diag):
    from scipy.spatial import cKDTree
    d_s2r, _ = cKDTree(P_ref).query(P_recon)
    d_r2s, _ = cKDTree(P_recon).query(P_ref)
    return (float((d_s2r.mean() + d_r2s.mean()) / diag * 100),
            float(max(np.percentile(d_s2r, 95), np.percentile(d_r2s, 95)) / diag * 100))


def geom_series(recons, steps, gt_pts, diag, seed=0):
    rng = np.random.default_rng(seed)
    out = []
    for st, rc in zip(steps, recons):
        P = meshes.soup_cloud(rc, N_GEOM, rng)
        cham, haus = _geom_metrics(P, gt_pts, diag)
        out.append({"step": int(st), "chamfer_pct": cham, "hausdorff95_pct": haus})
    return out


# ── per-run series (topology + geometry) ─────────────────────────────────

def run_series(traj_dir, target, gt_pts, diag, dims=(0, 1, 2)):
    steps, recons = metrics.load_trajectory(traj_dir)
    if not steps:
        return None
    topo = metrics.topology_stability_series(recons, target, steps=steps, dims=dims)
    geom = geom_series(recons, steps, gt_pts, diag)
    rows = []
    for t, g in zip(topo, geom):
        r = dict(t)
        r["chamfer_pct"] = g["chamfer_pct"]
        r["hausdorff95_pct"] = g["hausdorff95_pct"]
        rows.append(r)
    return rows


def _avg_over_seeds(per_seed_rows):
    """Align rows by step and average each numeric field across seeds."""
    if not per_seed_rows:
        return []
    common = set(r["step"] for r in per_seed_rows[0])
    for rows in per_seed_rows[1:]:
        common &= set(r["step"] for r in rows)
    steps = sorted(common)
    by_step = [{rows_i["step"]: rows_i for rows_i in rows} for rows in per_seed_rows]
    keys = [k for k in per_seed_rows[0][0] if k != "step"]
    out = []
    for st in steps:
        row = {"step": st}
        for k in keys:
            vals = [bs[st][k] for bs in by_step if k in bs[st]]
            row[k] = float(np.mean(vals))
            row[k + "_sd"] = float(np.std(vals))
        out.append(row)
    return out


# ── plotting (conditions overlaid; reuse topology.plots colours/idiom) ───

def _plot_metric(ax, cond_rows, key, ylabel, title, ref=None, ref_label=None):
    for cond, rows in cond_rows.items():
        if not rows:
            continue
        st = [r["step"] for r in rows]
        y = [r.get(key, np.nan) for r in rows]
        sd = [r.get(key + "_sd", 0.0) for r in rows]
        ax.plot(st, y, "-o", ms=3, color=COND_COLOR.get(cond, "k"), label=COND_LABEL.get(cond, cond))
        if any(s > 0 for s in sd):
            ax.fill_between(st, np.array(y) - np.array(sd), np.array(y) + np.array(sd),
                            color=COND_COLOR.get(cond, "k"), alpha=0.12)
    if ref is not None:
        ax.axhline(ref, ls="--", color="0.4", lw=1, label=ref_label)
    ax.set_xlabel("training step"); ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=10); ax.grid(alpha=0.25); ax.legend(fontsize=8)


def make_plots(shape, cond_rows, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    dim = SHAPE_DIM[shape]
    dname = {0: "H0", 1: "H1", 2: "H2"}[dim]
    # 1) PRIMARY: bottleneck-to-target (disc dim)
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    _plot_metric(ax, cond_rows, f"bottleneck_H{dim}",
                 f"bottleneck→target ({dname})", f"{shape}: topology error ({dname}) over training")
    fig.tight_layout(); p1 = os.path.join(out_dir, f"{shape}_bottleneck.png")
    fig.savefig(p1, dpi=130); plt.close(fig)
    # 2) significant Betti (disc dim) with correct-count reference
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    _plot_metric(ax, cond_rows, f"nsig_H{dim}", f"# significant {dname}",
                 f"{shape}: significant {dname} count over training",
                 ref=CORRECT_BETTI[shape][dim], ref_label=f"correct b{dim}={CORRECT_BETTI[shape][dim]}")
    fig.tight_layout(); p2 = os.path.join(out_dir, f"{shape}_betti.png")
    fig.savefig(p2, dpi=130); plt.close(fig)
    # 3) geometry parity (Chamfer)
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    _plot_metric(ax, cond_rows, "chamfer_pct", "Chamfer→target (%)",
                 f"{shape}: geometry parity (Chamfer) — expect B2 ≈ B0")
    fig.tight_layout(); p3 = os.path.join(out_dir, f"{shape}_geometry.png")
    fig.savefig(p3, dpi=130); plt.close(fig)
    return [p1, p2, p3]


# ── summary statistics ───────────────────────────────────────────────────

def _tail_stats(rows, key, tail_frac=0.3):
    """Mean & std of `key` over the last tail_frac of steps (steady-state)."""
    if not rows:
        return float("nan"), float("nan")
    n = max(1, int(round(len(rows) * tail_frac)))
    vals = [r.get(key, np.nan) for r in rows[-n:]]
    return float(np.nanmean(vals)), float(np.nanstd(vals))


def summarize(shape, cond_rows):
    dim = SHAPE_DIM[shape]
    rec = {}
    for cond, rows in cond_rows.items():
        if not rows:
            continue
        bott_key = f"bottleneck_H{dim}"
        tail_mean, tail_sd = _tail_stats(rows, bott_key)
        cham_mean, _ = _tail_stats(rows, "chamfer_pct")
        best = float(np.nanmin([r.get(bott_key, np.nan) for r in rows]))
        final_betti = rows[-1].get(f"nsig_H{dim}", float("nan"))
        rec[cond] = {"bott_tail_mean": tail_mean, "bott_tail_sd": tail_sd,
                     "bott_best": best, "chamfer_tail_mean": cham_mean,
                     "final_nsig": final_betti, "n_steps": len(rows)}
    return rec


def verdict(shape, rec):
    """B2 wins if its tail bottleneck is lower than BOTH B0 and B1, at Chamfer
    within tolerance of B0; B3 should NOT show the same topological gain."""
    if "B2" not in rec or "B0" not in rec:
        return {"note": "need at least B0 and B2 to judge"}
    b0, b2 = rec["B0"], rec["B2"]
    lower_than_b0 = b2["bott_tail_mean"] < b0["bott_tail_mean"]
    lower_than_b1 = ("B1" not in rec) or (b2["bott_tail_mean"] < rec["B1"]["bott_tail_mean"])
    more_stable = b2["bott_tail_sd"] <= b0["bott_tail_sd"]
    cham_tol = 0.15  # 15% relative Chamfer tolerance
    cham_ok = b2["chamfer_tail_mean"] <= b0["chamfer_tail_mean"] * (1 + cham_tol)
    b3_isolates = ("B3" not in rec) or (b2["bott_tail_mean"] < rec["B3"]["bott_tail_mean"])
    # A genuine topological win must beat baseline, beat the one-shot/washout B1,
    # hold Chamfer parity, AND beat the non-topological B3 control (otherwise the
    # gain is "biased resampling", not topology).
    return {"B2_lower_than_B0": bool(lower_than_b0), "B2_lower_than_B1": bool(lower_than_b1),
            "B2_more_stable_than_B0": bool(more_stable), "chamfer_parity": bool(cham_ok),
            "gain_is_topological_vs_B3": bool(b3_isolates),
            "PASS": bool(lower_than_b0 and lower_than_b1 and cham_ok and b3_isolates)}


# ── main ─────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--shapes", nargs="+", default=["torus", "two_spheres", "sphere"])
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    ap.add_argument("--conditions", nargs="+", default=["B0", "B1", "B2", "B3"])
    ap.add_argument("--n_target", type=int, default=20_000)
    ap.add_argument("--exp_name", default="topo2", help="output subdir under output/synth/")
    args = ap.parse_args()

    global EXP_ROOT
    EXP_ROOT = os.path.join(DENTISTRY, "output", "synth", args.exp_name)
    out_dir = os.path.join(EXP_ROOT, "report")
    os.makedirs(out_dir, exist_ok=True)
    all_results, all_summ, all_verdict, fig_index = {}, {}, {}, {}

    for shape in args.shapes:
        gt = os.path.join(DENTISTRY, "output", "synth", shape, "gt_mesh.ply")
        target = persistence_from_target(gt, n_samples=args.n_target, seed=0)
        gt_pts = meshes.sample_surface(*_load_mesh(gt), N_GEOM, np.random.default_rng(123))
        diag = float(np.linalg.norm(gt_pts.max(0) - gt_pts.min(0)))
        print(f"\n=== {shape}  (target betti={target.betti_numbers()}, disc dim H{SHAPE_DIM[shape]}) ===")

        cond_rows = {}
        for cond in args.conditions:
            per_seed = []
            for s in args.seeds:
                traj = os.path.join(EXP_ROOT, f"{shape}_{cond}_s{s}")
                rows = run_series(traj, target, gt_pts, diag) if os.path.isdir(traj) else None
                if rows:
                    per_seed.append(rows)
                else:
                    print(f"  [miss] {shape}_{cond}_s{s}")
            cond_rows[cond] = _avg_over_seeds(per_seed)
            if cond_rows[cond]:
                print(f"  [ok] {cond}: {len(per_seed)} seed(s), {len(cond_rows[cond])} steps")

        figs = make_plots(shape, cond_rows, out_dir)
        summ = summarize(shape, cond_rows)
        verd = verdict(shape, summ)
        all_results[shape] = cond_rows
        all_summ[shape] = summ
        all_verdict[shape] = verd
        fig_index[shape] = [os.path.basename(f) for f in figs]

    _write_summary(out_dir, args, all_summ, all_verdict, fig_index)
    with open(os.path.join(out_dir, "results.json"), "w") as f:
        json.dump({"summary": all_summ, "verdict": all_verdict}, f, indent=2)
    print(f"\n[save] {out_dir}/summary.md  +  results.json  + figures")
    return 0


def _load_mesh(path):
    import trimesh
    m = trimesh.load(path, process=False, force="mesh")
    return np.asarray(m.vertices), np.asarray(m.faces)


def _write_summary(out_dir, args, all_summ, all_verdict, fig_index):
    dname = {0: "H0", 1: "H1", 2: "H2"}
    L = ["# Phase 2 — Topology-aware Adaptive Resampling: results\n",
         "Controlled comparison: all conditions share seed, target, triangle budget "
         "N=max_faces, optimizer, steps — only the resampling importance differs.\n",
         "- **B0** baseline · **B1** topology@init (F1 washout test) · "
         "**B2** topology in-loop (the method) · **B3** non-topological in-loop (control)",
         "- PRIMARY metric: bottleneck-to-target in the discriminating dimension, "
         "tail = mean over the last 30% of steps (steady state). Lower = better.\n"]
    for shape, summ in all_summ.items():
        d = SHAPE_DIM[shape]
        L.append(f"## {shape} — discriminating dim {dname[d]} "
                 f"(correct b{d}={CORRECT_BETTI[shape][d]})\n")
        L.append(f"| cond | bottleneck {dname[d]} (tail mean±sd) | best | "
                 f"Chamfer% (tail) | final #sig {dname[d]} |")
        L.append("|------|------------------------------:|-----:|---------------:|--------------:|")
        for cond in args.conditions:
            if cond not in summ:
                continue
            r = summ[cond]
            L.append(f"| {cond} | {r['bott_tail_mean']:.4f} ± {r['bott_tail_sd']:.4f} | "
                     f"{r['bott_best']:.4f} | {r['chamfer_tail_mean']:.3f} | {r['final_nsig']:.1f} |")
        v = all_verdict[shape]
        L.append("")
        if "PASS" in v:
            L.append(f"**Verdict:** B2 lower than B0: `{v['B2_lower_than_B0']}` · "
                     f"lower than B1: `{v['B2_lower_than_B1']}` · "
                     f"more stable than B0: `{v['B2_more_stable_than_B0']}` · "
                     f"Chamfer parity: `{v['chamfer_parity']}` · "
                     f"gain is topological (vs B3): `{v['gain_is_topological_vs_B3']}` "
                     f"→ **{'PASS' if v['PASS'] else 'NOT a win — reported honestly'}**")
        else:
            L.append(f"**Verdict:** {v.get('note','')}")
        L.append("\nFigures: " + ", ".join(f"`{f}`" for f in fig_index[shape]) + "\n")
    path = os.path.join(out_dir, "summary.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    # echo to stdout
    print("\n" + "\n".join(L))


if __name__ == "__main__":
    raise SystemExit(main())
