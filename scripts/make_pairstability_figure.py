# scripts/make_pairstability_figure.py
# Round-5 revision-list R7 ("no stability analysis of the pair-frozen
# matching"): plot the per-refresh plan composition ALREADY RECORDED in
# every C1 run's topo_loss_log.json ("refreshes" schema: matched / diagonal
# / recruited / target-unreached counts at each of the ~200 refreshes).
# No new runs. NOTE: the refresh schema exists only in runs from
# 2026-07-09 on (C6/C7 wiring) — the original 3d C1 arms predate it, so
# the panels use post-wiring runs that carry the three regimes:
#   torus C6 (no recruitment): target-unreached chronic at 1 — the
#     mechanism behind the C6 collapse, visualized;
#   eight C1: recruitment claiming the two sub-threshold loops;
#   tom-yum pot C1 (tag kinkin): a stable matched-only plan.
#
#   python scripts\make_pairstability_figure.py

from __future__ import annotations

import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

DENTISTRY = os.environ.get("CGSOUP_ROOT", r"D:\Project\CG-Soup-for-Digital-Dentistry")
TRAIN = os.path.join(DENTISTRY, "output", "synth", "topo3", "_train")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PNG = os.path.join(ROOT, "paper2", "figures", "pairstability.png")

# (tag, panel title, discriminating dim to plot)
PANELS = [("torus_C6_r0.1_s0", "torus, no-recruit (C6): H1", "1"),
          ("eight_C1_r0.1_s0", "eight (C1): H1", "1"),
          ("kinkin_C1_r0.1_s0", "tom-yum pot (C1): H2", "2")]

# Okabe-Ito, matching the paper's grayscale-safe convention. Constant
# series often coincide (e.g. torus C6: matched=1 AND unreached=1), so
# unreached gets x-markers and live-significant a dotted style.
COLORS = {"targets": "#555555", "matched": "#0072B2",
          "recruited": "#D55E00", "diagonal": "#999999",
          "target unreached": "#000000", "live significant": "#009E73"}
STYLES = {"live significant": ":", "targets": "--"}
MARKS = {"target unreached": dict(marker="x", markersize=3.5, markevery=11)}


def series(log_path: str, dim: str):
    """Refresh schema (2026-07-09 wiring): refreshes = list of
    [refresh_idx, step, {dim: {live_sig, target, matched, diag, recruit,
    target_unreached}}, n_gabriel_fail]."""
    with open(log_path, encoding="utf-8") as fh:
        log = json.load(fh)
    if "refreshes" not in log:
        raise SystemExit(f"{log_path}: no refresh schema (pre-2026-07-09 run) "
                         f"— pick a post-wiring tag")
    refreshes = log["refreshes"]
    steps = [r[1] for r in refreshes]
    per = [r[2].get(dim, {}) for r in refreshes]
    out = {"targets": [p.get("target", 0) for p in per],
           "matched": [p.get("matched", 0) for p in per],
           "recruited": [p.get("recruit", 0) for p in per],
           "diagonal": [p.get("diag", 0) for p in per],
           "target unreached": [p.get("target_unreached", 0) for p in per],
           "live significant": [p.get("live_sig", 0) for p in per]}
    gab = sum(r[3] for r in refreshes if len(r) > 3)  # field absent in the
    print(f"  {os.path.basename(os.path.dirname(log_path))}: "  # earliest schema
          f"{len(refreshes)} refreshes, dim H{dim}, gabriel_fail_total={gab}")
    return steps, out


def main():
    fig, axes = plt.subplots(1, 3, figsize=(9.6, 2.6), dpi=200, sharey=False)
    for ax, (tag, title, dim) in zip(axes, PANELS):
        log = os.path.join(TRAIN, tag, "topo_loss_log.json")
        x, s = series(log, dim)
        for name, vals in s.items():
            lw = 0.9 if name == "targets" else 1.1
            ax.plot(x, vals, lw=lw, color=COLORS[name], label=name,
                    ls=STYLES.get(name, "-"), drawstyle="steps-mid",
                    **MARKS.get(name, {}))
        ax.set_title(title, fontsize=9)
        ax.set_xlabel("training step", fontsize=8)
        ax.tick_params(labelsize=7)
        ymax = max(max(v) for v in s.values())
        ax.set_ylim(-0.4, ymax + 0.9)
        ax.grid(alpha=0.25, lw=0.4)
    axes[0].set_ylabel("bars", fontsize=8)
    axes[-1].legend(fontsize=6.5, loc="center right", framealpha=0.9)
    fig.tight_layout()
    os.makedirs(os.path.dirname(PNG), exist_ok=True)
    fig.savefig(PNG, bbox_inches="tight")
    print(f"[out] {PNG}")


if __name__ == "__main__":
    main()
