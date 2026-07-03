# experiments/crossover_report.py
# Phase-2 follow-up: evaluation + plots for the DIMENSIONAL-CROSSOVER experiment,
# reusing topology/ and experiments/topo_eval_report.py UNCHANGED.
#
# The thesis: the sign of (bottleneck_SPREAD - bottleneck_CONCENTRATE) should FLIP
# with the dimension of the topological feature:
#   H2 (voids)  -> CONCENTRATE (B2) better -> delta = bott(B4)-bott(B2) > 0
#   H1 (loops)  -> SPREAD (B4) better/tie  -> delta <= 0  (and B2 inflates phantom features)
#   H0 (comps)  -> SPREAD (B4) better/tie  -> delta <= 0
#
# Each shape is read at its OWN HEADROOM budget (the pilot showed one N can't give
# all feature classes headroom). The shape->budget mapping mirrors
# experiments/dimensional_crossover.py's PLAN.
#
# Outputs (under output/synth/<exp_name>/crossover_report/):
#   crossover.png        signed delta per shape, grouped by feature dimension
#   phantom.png          significant-feature count vs true Betti (B0/B2/B4), low-dim shapes
#   parity.png           Chamfer per condition (gain must be at COMPARABLE geometry)
#   bottleneck_vs_N.png  H1 baseline budget-dependence + where concentrate backfires
#   summary.md + results.json   crossover table + honest verdict
#
#   python experiments/crossover_report.py --seeds 0 1 2 3 4

from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

_TOPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_EXP_DIR = os.path.dirname(os.path.abspath(__file__))
for p in (_TOPO_ROOT, _EXP_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

import topo_eval_report as rep          # reuse run_series/_avg_over_seeds/_tail_stats/maps

import matplotlib                       # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt         # noqa: E402

DENTISTRY = rep.DENTISTRY
DIM_NAME = {0: "H0", 1: "H1", 2: "H2"}
DIM_COLOR = {2: "#d62728", 1: "#1f77b4", 0: "#2ca02c"}   # H2 red, H1 blue, H0 green
CONDS = ["B0", "B2", "B4", "B3"]
COND_LABEL = {"B0": "B0 baseline", "B2": "B2 concentrate", "B4": "B4 spread", "B3": "B3 non-topo"}
CC = {"B0": "#555555", "B2": "#d62728", "B4": "#ff7f0e", "B3": "#2ca02c"}

# shape -> (exp_name holding its HEADROOM run, budget N). Mirrors dimensional_crossover.PLAN.
DEFAULT_PLAN = {
    "sphere":        ("crossover_N1200", 1200),
    "cube":          ("crossover_N1200", 1200),
    "torus":         ("crossover",        700),
    "double_torus":  ("crossover_N2000", 2000),
    "two_spheres":   ("crossover",        700),
    "three_spheres": ("crossover",        700),
}
# shape -> {N: exp_name} for the bottleneck-vs-N curves (H1 shapes).
NSWEEP_PLAN = {
    "torus":        {400: "crossover_N400", 700: "crossover", 1200: "crossover_N1200"},
    "double_torus": {2000: "crossover_N2000"},
}


# ── per-(exp,shape) analysis (reuses topo_eval_report) ────────────────────

def analyze_one(exp_name, shape, conds, seeds, n_target):
    """Per-condition tail-mean bottleneck (decisive dim), final significant-feature
    count, and Chamfer for ONE shape read from output/synth/<exp_name>/."""
    exp_root = os.path.join(DENTISTRY, "output", "synth", exp_name)
    gt = os.path.join(DENTISTRY, "output", "synth", shape, "gt_mesh.ply")
    if not os.path.exists(gt):
        return None
    dim = rep.SHAPE_DIM[shape]
    target = rep.persistence_from_target(gt, n_samples=n_target, seed=0)
    gt_pts = rep.meshes.sample_surface(*rep._load_mesh(gt), rep.N_GEOM, np.random.default_rng(123))
    diag = float(np.linalg.norm(gt_pts.max(0) - gt_pts.min(0)))
    bott_key, nsig_key = f"bottleneck_H{dim}", f"nsig_H{dim}"

    rec = {"dim": dim, "true_betti": rep.CORRECT_BETTI[shape][dim], "exp": exp_name, "conds": {}}
    for cond in conds:
        per_seed = []
        for s in seeds:
            traj = os.path.join(exp_root, f"{shape}_{cond}_s{s}")
            rows = rep.run_series(traj, target, gt_pts, diag) if os.path.isdir(traj) else None
            if rows:
                per_seed.append(rows)
        if not per_seed:
            continue
        avg = rep._avg_over_seeds(per_seed)
        bt_m, bt_sd = rep._tail_stats(avg, bott_key)
        cham_m, _ = rep._tail_stats(avg, "chamfer_pct")
        haus_m, _ = rep._tail_stats(avg, "hausdorff95_pct")
        nsig = float(np.mean([rows[-1].get(nsig_key, np.nan) for rows in per_seed]))
        rec["conds"][cond] = {"bott": bt_m, "bott_sd": bt_sd, "cham": cham_m,
                              "haus": haus_m, "nsig": nsig, "nseeds": len(per_seed)}
    return rec if rec["conds"] else None


def analyze_plan(plan, conds, seeds, n_target):
    out = {}
    for shape, (exp_name, N) in plan.items():
        rec = analyze_one(exp_name, shape, conds, seeds, n_target)
        if rec is None:
            print(f"  [skip] {shape}: no runs in {exp_name}")
            continue
        rec["N"] = N
        out[shape] = rec
        cs = rec["conds"]
        line = "  ".join(f"{c}={cs[c]['bott']:.4f}(n{cs[c]['nseeds']})" for c in conds if c in cs)
        print(f"  {shape:14s} H{rec['dim']} @N={N}: {line}")
    return out


def crossover_stats(rec_by_shape):
    rows = []
    for shape, rec in rec_by_shape.items():
        cs = rec["conds"]
        if "B2" not in cs or "B4" not in cs:
            continue
        b2, b4 = cs["B2"], cs["B4"]
        delta = b4["bott"] - b2["bott"]
        cham_par = abs(b4["cham"] - b2["cham"]) <= 0.15 * max(b2["cham"], 1e-9)
        rows.append({
            "shape": shape, "dim": rec["dim"], "dname": DIM_NAME[rec["dim"]], "N": rec["N"],
            "true_betti": rec["true_betti"],
            "B0": cs.get("B0", {}).get("bott"), "B2": b2["bott"], "B4": b4["bott"],
            "B3": cs.get("B3", {}).get("bott"),
            "delta_spread_minus_conc": delta,
            "winner": "concentrate(B2)" if delta > 0 else "spread(B4)",
            "nsig_B2": b2["nsig"], "nsig_B4": b4["nsig"], "nsig_B0": cs.get("B0", {}).get("nsig"),
            "cham_B2": b2["cham"], "cham_B4": b4["cham"], "cham_parity": bool(cham_par),
        })
    return rows


def verdict(cross_rows):
    hi = [r for r in cross_rows if r["dim"] == 2]
    lo = [r for r in cross_rows if r["dim"] in (0, 1)]
    hi_conc = [r["delta_spread_minus_conc"] > 0 for r in hi]
    lo_spread = [r["delta_spread_minus_conc"] <= 0 for r in lo]
    phantom = []
    for r in lo:
        phantom.append({"shape": r["shape"], "true": r["true_betti"],
                        "nsig_conc": r["nsig_B2"], "nsig_spread": r["nsig_B4"],
                        "concentrate_inflates_more": (r["nsig_B2"] - r["true_betti"]) >
                                                     (r["nsig_B4"] - r["true_betti"]) + 1e-9})
    return {"n_H2": len(hi), "H2_concentrate_wins": hi_conc,
            "n_lowdim": len(lo), "lowdim_spread_wins_or_ties": lo_spread, "phantom": phantom,
            "CROSSOVER_HOLDS": bool(hi and lo and all(hi_conc) and all(lo_spread)),
            "all_chamfer_parity": all(r["cham_parity"] for r in cross_rows)}


# ── figures ───────────────────────────────────────────────────────────────

def fig_crossover(cross_rows, path):
    rows = sorted(cross_rows, key=lambda r: (-r["dim"], r["shape"]))
    if not rows:
        return None
    xs = np.arange(len(rows))
    deltas = [r["delta_spread_minus_conc"] for r in rows]
    colors = [DIM_COLOR[r["dim"]] for r in rows]
    fig, ax = plt.subplots(figsize=(max(7, 1.4 * len(rows)), 4.8))
    ax.bar(xs, deltas, color=colors, edgecolor="k", linewidth=0.6)
    ax.axhline(0, color="k", lw=1)
    ax.set_xticks(xs)
    ax.set_xticklabels([f"{r['shape']}\n({r['dname']}, N={r['N']})" for r in rows], fontsize=8.5)
    ax.set_ylabel(r"$\Delta$ = bottleneck(spread B4) $-$ bottleneck(concentrate B2)")
    ax.set_title("Dimensional crossover: >0 → CONCENTRATE wins (expect H2);  <0 → SPREAD wins (expect H1/H0)",
                 fontsize=10)
    top = max((abs(d) for d in deltas), default=1e-6) or 1e-6
    ax.text(0.01, 0.96, "concentrate better ↑", transform=ax.transAxes, fontsize=8, va="top", color="0.3")
    ax.text(0.01, 0.04, "spread better ↓", transform=ax.transAxes, fontsize=8, va="bottom", color="0.3")
    ax.set_ylim(-1.3 * top, 1.3 * top); ax.grid(axis="y", alpha=0.25)
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)
    return path


def fig_phantom(rec_by_shape, path):
    lo = [(s, r) for s, r in rec_by_shape.items() if r["dim"] in (0, 1)]
    if not lo:
        return None
    fig, ax = plt.subplots(figsize=(max(7, 1.7 * len(lo)), 4.8))
    width, base = 0.22, np.arange(len(lo))
    for i, cond in enumerate(["B0", "B2", "B4"]):
        vals = [rec["conds"].get(cond, {}).get("nsig", np.nan) for _, rec in lo]
        ax.bar(base + (i - 1) * width, vals, width, label=COND_LABEL[cond],
               color={"B0": "#555555", "B2": "#d62728", "B4": "#ff7f0e"}[cond],
               edgecolor="k", linewidth=0.5)
    for j, (_, rec) in enumerate(lo):
        ax.hlines(rec["true_betti"], base[j] - 2 * width, base[j] + 2 * width, color="k", ls="--",
                  lw=1.2, label="true Betti" if j == 0 else None)
    ax.set_xticks(base)
    ax.set_xticklabels([f"{s}\n({DIM_NAME[rec['dim']]}, true b={rec['true_betti']})" for s, rec in lo], fontsize=8.5)
    ax.set_ylabel("# significant features (decisive dim)")
    ax.set_title("Phantom features: does CONCENTRATE (B2) inflate the count above true Betti, vs SPREAD (B4)?",
                 fontsize=9.5)
    ax.legend(fontsize=8); ax.grid(axis="y", alpha=0.25)
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)
    return path


def fig_parity(rec_by_shape, path):
    shapes = sorted(rec_by_shape, key=lambda s: (-rec_by_shape[s]["dim"], s))
    if not shapes:
        return None
    fig, ax = plt.subplots(figsize=(max(7, 1.5 * len(shapes)), 4.6))
    width, base = 0.2, np.arange(len(shapes))
    for i, cond in enumerate(CONDS):
        vals = [rec_by_shape[s]["conds"].get(cond, {}).get("cham", np.nan) for s in shapes]
        ax.bar(base + (i - 1.5) * width, vals, width, label=COND_LABEL[cond],
               color=CC[cond], edgecolor="k", linewidth=0.5)
    ax.set_xticks(base)
    ax.set_xticklabels([f"{s}\n({DIM_NAME[rec_by_shape[s]['dim']]})" for s in shapes], fontsize=8.5)
    ax.set_ylabel("Chamfer→target (%, tail mean)")
    ax.set_title("Geometry parity — concentrate/spread differences must be at COMPARABLE Chamfer", fontsize=9.5)
    ax.legend(fontsize=8); ax.grid(axis="y", alpha=0.25)
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)
    return path


def fig_bottleneck_vs_N(conds, seeds, n_target, path):
    series = {}                                   # shape -> cond -> {N: bott}
    for shape, nmap in NSWEEP_PLAN.items():
        for N, exp_name in nmap.items():
            rec = analyze_one(exp_name, shape, conds, seeds, n_target)
            if rec is None:
                continue
            for cond, d in rec["conds"].items():
                series.setdefault(shape, {}).setdefault(cond, {})[N] = d["bott"]
    series = {s: cd for s, cd in series.items() if any(len(v) >= 2 for v in cd.values())}
    if not series:
        return None
    fig, axes = plt.subplots(1, len(series), figsize=(5.2 * len(series), 4.4), squeeze=False)
    for ax, (shape, cd) in zip(axes[0], series.items()):
        for cond in conds:
            if cond not in cd:
                continue
            Ns = sorted(cd[cond])
            ax.plot(Ns, [cd[cond][n] for n in Ns], "-o", ms=4, color=CC.get(cond, "k"),
                    label=COND_LABEL.get(cond, cond))
        ax.set_xlabel("triangle budget N"); ax.set_ylabel(f"bottleneck→target (H{rep.SHAPE_DIM[shape]})")
        ax.set_title(f"{shape} (H{rep.SHAPE_DIM[shape]})", fontsize=10)
        ax.grid(alpha=0.25); ax.legend(fontsize=8)
    fig.suptitle("Bottleneck vs budget for H1 shapes (baseline budget-dependence; concentrate backfire at tight N)",
                 fontsize=10)
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)
    return path


# ── summary ───────────────────────────────────────────────────────────────

def write_summary(out_dir, rec_by_shape, cross_rows, verd, figs):
    L = ["# Phase-2 follow-up — Dimensional crossover (concentrate vs spread by feature dimension)\n",
         "Budget-neutral, paired seeds. B2 (CONCENTRATE, spread s=1) and B4 (SPREAD, s>1) differ ONLY in "
         "the importance field's kernel width (mass-preserving, Σwσ² invariant); B0 baseline and B3 "
         "non-topological anchor the comparison. Each shape is run at its OWN headroom budget N.\n",
         "PRIMARY metric: bottleneck-to-target in each shape's decisive dimension (tail mean over the last "
         "30% of steps; lower = better).\n",
         "## Crossover table\n",
         "| shape | dim | N | true b | B0 | B2 concentrate | B4 spread | B3 | Δ=B4−B2 | winner | Cham parity |",
         "|---|---|---:|---:|---:|---:|---:|---:|---:|---|:--:|"]
    for r in sorted(cross_rows, key=lambda r: (-r["dim"], r["shape"])):
        def f(x): return f"{x:.4f}" if isinstance(x, (int, float)) else "—"
        L.append(f"| {r['shape']} | {r['dname']} | {r['N']} | {r['true_betti']} | {f(r['B0'])} | "
                 f"{f(r['B2'])} | {f(r['B4'])} | {f(r['B3'])} | {r['delta_spread_minus_conc']:+.4f} | "
                 f"{r['winner']} | {'yes' if r['cham_parity'] else 'NO'} |")
    L.append("\n## Phantom-feature check (low-dim shapes: does concentrate over-tessellate?)\n")
    L.append("| shape | true Betti | #sig B0 | #sig B2 concentrate | #sig B4 spread |")
    L.append("|---|---:|---:|---:|---:|")
    for s, rec in rec_by_shape.items():
        if rec["dim"] not in (0, 1):
            continue
        cs = rec["conds"]
        def g(c): return f"{cs[c]['nsig']:.1f}" if c in cs else "—"
        L.append(f"| {s} | {rec['true_betti']} | {g('B0')} | {g('B2')} | {g('B4')} |")
    cv = verd
    L.append("\n## Verdict\n")
    L.append(f"- H2 (voids) — concentrate (B2) better than spread (B4)?  `{cv['H2_concentrate_wins']}`  (Δ>0 expected)")
    L.append(f"- H1/H0 (loops/components) — spread (B4) better-or-tie?  `{cv['lowdim_spread_wins_or_ties']}`  (Δ≤0 expected)")
    L.append(f"- Chamfer parity across all shapes: `{cv['all_chamfer_parity']}`")
    for p in cv["phantom"]:
        L.append(f"- phantom[{p['shape']}]: true b={p['true']}, concentrate #sig={p['nsig_conc']:.1f}, "
                 f"spread #sig={p['nsig_spread']:.1f} → concentrate inflates more: `{p['concentrate_inflates_more']}`")
    L.append(f"\n**CROSSOVER {'HOLDS' if cv['CROSSOVER_HOLDS'] else 'does NOT fully hold'}** "
             f"(sign of Δ flips between high-dim and low-dim classes: `{cv['CROSSOVER_HOLDS']}`). "
             f"Reported honestly — partial/non-crossover is a valid result.")
    L.append("\nFigures: " + ", ".join(f"`{os.path.basename(x)}`" for x in figs if x) + "\n")
    path = os.path.join(out_dir, "summary.md")
    with open(path, "w", encoding="utf-8") as fp:
        fp.write("\n".join(L) + "\n")
    print("\n" + "\n".join(L))
    return path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out_exp", default="crossover", help="exp dir to write the report under")
    ap.add_argument("--conditions", nargs="+", default=CONDS)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    ap.add_argument("--n_target", type=int, default=20_000)
    args = ap.parse_args()

    out_dir = os.path.join(DENTISTRY, "output", "synth", args.out_exp, "crossover_report")
    os.makedirs(out_dir, exist_ok=True)

    print("=== analyze per-class-N plan (decisive-dim bottleneck per shape) ===")
    rec_by_shape = analyze_plan(DEFAULT_PLAN, args.conditions, args.seeds, args.n_target)
    if not rec_by_shape:
        print("[abort] no trajectories found yet."); return 1
    cross_rows = crossover_stats(rec_by_shape)
    verd = verdict(cross_rows)
    figs = [fig_crossover(cross_rows, os.path.join(out_dir, "crossover.png")),
            fig_phantom(rec_by_shape, os.path.join(out_dir, "phantom.png")),
            fig_parity(rec_by_shape, os.path.join(out_dir, "parity.png")),
            fig_bottleneck_vs_N(args.conditions, args.seeds, args.n_target,
                                os.path.join(out_dir, "bottleneck_vs_N.png"))]
    write_summary(out_dir, rec_by_shape, cross_rows, verd, figs)
    with open(os.path.join(out_dir, "results.json"), "w") as fp:
        json.dump({"records": rec_by_shape, "crossover": cross_rows, "verdict": verd}, fp, indent=2)
    print(f"\n[save] {out_dir}/summary.md + results.json + figures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
