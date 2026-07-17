# experiments/topo_loss_report.py
# Phase-3 stage 3d: the full report over the C-matrix runs (PHASE3_PLAN.md §6).
#
# Auto-discovers run directories under output/synth/<exp_name>/ whose names
# parse as {shape}_{cond}[_r{rho}]_s{seed}, computes the per-step topology
# stability series in the shape's discriminating dimension (cached — the alpha
# complexes at 20k samples are the slow part), and writes into <exp>/report/:
#
#   results.json        per-run tails + per-condition aggregates + verdicts
#   summary.md          tables + verdict lines (the human-readable artifact)
#   {shape}_series.png  bottleneck-vs-step, per-condition mean + seed band
#   {shape}_tail.png    per-seed tail dots + condition means
#   {shape}_nsig.png    significant-feature-count trajectory (phantom check)
#
# Verdict rule (mirrors Phase 2's topo_eval_report discipline): C1 PASSES on a
# shape iff mean(C1) < mean(C0) AND mean(C1) < mean(every control arm present:
# C2, C2g) on the tail bottleneck, AND C1's Chamfer stays within PARITY_MULT of
# C0's. Welch sigma for the C0-C1 separation is reported alongside.
#
# Usage:  python experiments/topo_loss_report.py            # everything found
#         python experiments/topo_loss_report.py --shapes sphere torus

from __future__ import annotations

import argparse
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_TOPO_ROOT = os.path.dirname(_HERE)
for _p in (_HERE, _TOPO_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np

from topo_resampling_eval import SHAPE_DIM, scene_dir  # noqa: E402
from topo_loss_eval import exp_root, _chamfer_norm     # noqa: E402
from methods._paths import load_topology               # noqa: E402

topology = load_topology()
meshes, metrics = topology.meshes, topology.metrics

TAG_RE = re.compile(r"^(?P<shape>[a-z_]+?)_(?P<cond>C\w+?)(?:_r(?P<rho>[0-9.]+))?_s(?P<seed>\d+)$")

COLORS = {"C0": "#7f7f7f", "C1": "#1f77b4", "C2": "#d62728", "C2g": "#ff7f0e",
          "C3": "#17becf", "C5": "#9467bd", "C6": "#e377c2",
          "C7": "#bcbd22", "C7h": "#8c564b"}
LABELS = {"C0": "C0 baseline", "C1": "C1 topo loss",
          "C2": "C2 repulsion control", "C2g": "C2g gentle control",
          "C3": "C3 no-curriculum", "C5": "C5 loss + B4 prior",
          "C6": "C6 no-recruitment",
          "C7": "C7 noise 0.5%", "C7h": "C7h noise 1%"}
CONTROLS = ("C2", "C2g")
PARITY_MULT = 1.15                   # C1 Chamfer must stay within this of C0


def discover(root: str, shapes=None):
    """{shape: {cond: {seed: tag}}} from directory names."""
    out: dict = {}
    for name in sorted(os.listdir(root)):
        m = TAG_RE.match(name)
        if not m or not os.path.isdir(os.path.join(root, name)):
            continue
        shape, cond, seed = m["shape"], m["cond"], int(m["seed"])
        if shape not in SHAPE_DIM or (shapes and shape not in shapes):
            continue
        # rho is part of the condition identity: non-default-rho runs (the 3c
        # sweep extras) become their own arms instead of clobbering seeds.
        if m["rho"] is not None and m["rho"] != "0.1":
            cond = f"{cond}_r{m['rho']}"
        out.setdefault(shape, {}).setdefault(cond, {})[seed] = name
    return out


def run_series(root: str, tag: str, shape: str, tgt, cache_dir: str) -> dict:
    """Cached per-run series: steps, bottleneck/wasserstein/nsig in the disc
    dim, and final-dump Chamfer%."""
    cpath = os.path.join(cache_dir, f"{tag}.json")
    if os.path.exists(cpath):
        with open(cpath, encoding="utf-8") as fh:
            return json.load(fh)
    disc = SHAPE_DIM[shape]
    steps, dumps = metrics.load_trajectory(os.path.join(root, tag))
    rows = metrics.topology_stability_series(
        dumps, tgt, steps=steps, n_samples=20_000, seed=0, dims=(disc,))
    soup = meshes.soup_cloud(dumps[-1], 20_000, np.random.default_rng(0))
    gt_cloud = _GT_CLOUDS[shape]
    rec = {
        "tag": tag, "shape": shape, "disc": disc,
        "steps": [r["step"] for r in rows],
        "bottleneck": [r[f"bottleneck_H{disc}"] for r in rows],
        "wasserstein": [r[f"wasserstein_H{disc}"] for r in rows],
        "nsig": [r[f"nsig_H{disc}"] for r in rows],
        "chamfer_pct": 100.0 * _chamfer_norm(soup, gt_cloud, tgt.scale),
    }
    os.makedirs(cache_dir, exist_ok=True)
    with open(cpath, "w", encoding="utf-8") as fh:
        json.dump(rec, fh)
    return rec


_GT_CLOUDS: dict = {}


def _prep_target(shape: str):
    gt = os.path.join(scene_dir(shape), "gt_mesh.ply")
    tgt = topology.persistence_from_target(gt, n_samples=20_000, seed=0)
    import trimesh
    m = trimesh.load(gt, process=False, force="mesh")
    _GT_CLOUDS[shape] = meshes.sample_surface(
        np.asarray(m.vertices), np.asarray(m.faces), 20_000,
        np.random.default_rng(0))
    return tgt


def welch_sigma(a: list, b: list) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 2 or len(b) < 2:
        return float("nan")
    se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return float(abs(a.mean() - b.mean()) / se) if se > 0 else float("inf")


def make_plots(shape: str, series: dict, agg: dict, out_dir: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    disc = SHAPE_DIM[shape]

    fig, ax = plt.subplots(figsize=(7, 4.2))
    for cond, runs in sorted(series.items()):
        curves = np.array([r["bottleneck"] for r in runs.values()])
        steps = runs[min(runs)]["steps"]
        c = COLORS.get(cond, "k")
        ax.plot(steps, curves.mean(0), color=c, label=LABELS.get(cond, cond))
        ax.fill_between(steps, curves.min(0), curves.max(0), color=c, alpha=0.15)
    ax.set_xlabel("step")
    ax.set_ylabel(f"bottleneck H{disc} to target")
    ax.set_title(f"{shape}: topology error over training")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, f"{shape}_series.png"), dpi=130)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    for i, (cond, a) in enumerate(sorted(agg.items())):
        c = COLORS.get(cond, "k")
        xs = np.full(len(a["tails"]), i, dtype=float)
        ax.scatter(xs + np.linspace(-0.08, 0.08, len(xs)), a["tails"],
                   color=c, s=28, zorder=3)
        ax.hlines(a["mean"], i - 0.22, i + 0.22, color=c, lw=3)
    ax.set_xticks(range(len(agg)))
    ax.set_xticklabels([LABELS.get(c, c) for c in sorted(agg)], rotation=20,
                       ha="right", fontsize=8)
    ax.set_ylabel(f"tail bottleneck H{disc}")
    ax.set_title(f"{shape}: per-seed tails")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, f"{shape}_tail.png"), dpi=130)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 3.6))
    peak = 0.0
    for cond, runs in sorted(series.items()):
        curves = np.array([r["nsig"] for r in runs.values()], dtype=float)
        steps = runs[min(runs)]["steps"]
        peak = max(peak, float(curves.max()))
        ax.plot(steps, curves.mean(0), color=COLORS.get(cond, "k"),
                label=LABELS.get(cond, cond))
    tgt_n = {"sphere": 1, "cube": 1, "torus": 2, "two_spheres": 1,
             "double_torus": 2, "spot": 1, "bob": 2, "fandisk": 1,
             # open-surface probe bowls: staircase-certified 1 significant
             # H2 bar each (OPEN_SURFACE_PROBE_PLAN.md, 2026-07-17)
             "bowl_narrow": 1, "bowl_wide": 1}.get(shape)
    if tgt_n is not None:
        ax.axhline(tgt_n, color="k", ls="--", lw=0.8, alpha=0.6)
    # The random-init transient (hundreds of sub-scale bars at step 0) swamps
    # the ±1-around-target region the phantom check is about: clip the axis
    # and annotate the peak rather than hide that the transient exists.
    cap = max(8, (tgt_n or 0) + 6)
    if peak > cap:
        ax.set_ylim(-0.3, cap)
        ax.annotate(f"init transient peaks at ~{int(round(peak))} (off-scale)",
                    xy=(0.98, 0.92), xycoords="axes fraction", ha="right",
                    fontsize=7, color="0.35")
    ax.set_xlabel("step")
    ax.set_ylabel(f"#sig H{SHAPE_DIM[shape]}")
    ax.set_title(f"{shape}: significant-feature count (phantom check)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, f"{shape}_nsig.png"), dpi=130)
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase-3 C-matrix report")
    ap.add_argument("--exp_name", default="topo3")
    ap.add_argument("--shapes", nargs="+", default=None)
    ap.add_argument("--tail", type=int, default=3)
    a = ap.parse_args()

    root = exp_root(a.exp_name)
    out_dir = os.path.join(root, "report")
    cache_dir = os.path.join(out_dir, "cache")
    os.makedirs(out_dir, exist_ok=True)

    found = discover(root, a.shapes)
    if not found:
        print("no runs found");  return 1

    results, md = {}, []
    md.append("# Phase 3 — C-matrix report (topological loss)\n")
    md.append(f"Tail = mean over the last {a.tail} trajectory dumps of the "
              f"discriminating-dimension bottleneck to the GT diagram "
              f"(20k samples, target-normalized). Verdict rule: C1 < C0 and "
              f"C1 < every control (Chamfer within {PARITY_MULT}x of C0).\n")

    for shape, conds in found.items():
        disc = SHAPE_DIM[shape]
        tgt = _prep_target(shape)
        series = {c: {s: run_series(root, tag, shape, tgt, cache_dir)
                      for s, tag in sorted(runs.items())}
                  for c, runs in conds.items()}
        agg = {}
        for cond, runs in series.items():
            tails = [float(np.mean(r["bottleneck"][-a.tail:]))
                     for r in runs.values()]
            chams = [r["chamfer_pct"] for r in runs.values()]
            nsig_final = [int(r["nsig"][-1]) for r in runs.values()]
            agg[cond] = {"tails": tails, "mean": float(np.mean(tails)),
                         "sd": float(np.std(tails, ddof=1)) if len(tails) > 1 else 0.0,
                         "chamfer_mean": float(np.mean(chams)),
                         "nsig_final": nsig_final, "n_seeds": len(tails)}

        verdict, why = None, []
        if "C0" in agg and "C1" in agg:
            ok = agg["C1"]["mean"] < agg["C0"]["mean"]
            why.append(f"C1 {agg['C1']['mean']:.4f} vs C0 {agg['C0']['mean']:.4f} "
                       f"({welch_sigma(agg['C0']['tails'], agg['C1']['tails']):.1f} sigma)")
            for ctrl in CONTROLS:
                if ctrl in agg:
                    ok &= agg["C1"]["mean"] < agg[ctrl]["mean"]
                    why.append(f"vs {ctrl} {agg[ctrl]['mean']:.4f}")
            parity = agg["C1"]["chamfer_mean"] <= PARITY_MULT * agg["C0"]["chamfer_mean"]
            ok &= parity
            why.append(f"Chamfer {agg['C1']['chamfer_mean']:.3f} vs C0 "
                       f"{agg['C0']['chamfer_mean']:.3f} (parity {'OK' if parity else 'FAIL'})")
            verdict = "PASS" if ok else "FAIL"

        make_plots(shape, series, agg, out_dir)
        results[shape] = {"disc_dim": disc, "aggregate": agg, "verdict": verdict,
                          "why": why}

        md.append(f"\n## {shape} (H{disc})\n")
        md.append("| cond | seeds | tail bottleneck (mean±sd) | Chamfer% | final #sig |")
        md.append("|---|---|---|---|---|")
        for cond in sorted(agg):
            g = agg[cond]
            md.append(f"| {LABELS.get(cond, cond)} | {g['n_seeds']} "
                      f"| {g['mean']:.4f} ± {g['sd']:.4f} "
                      f"| {g['chamfer_mean']:.3f} | {g['nsig_final']} |")
        if verdict:
            md.append(f"\n**Verdict: {verdict}** — {'; '.join(why)}")

    with open(os.path.join(out_dir, "results.json"), "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2)
    with open(os.path.join(out_dir, "summary.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    print(f"[report] {len(found)} shape(s) → {out_dir}")
    for shape, r in results.items():
        print(f"  {shape:14s} H{r['disc_dim']}  verdict={r['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
