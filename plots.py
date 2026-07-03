# topology/plots.py
# Reusable plotting for the topology harness (kept in the module so the Phase-2
# method can reuse it unchanged): persistence diagrams and stability time series.
#
# Matplotlib only. Infinite H0 deaths (essential classes) are drawn on a dashed
# "infinity" line near the top of each axis so they are visible without
# distorting the finite features.

from __future__ import annotations

import os
from typing import Optional, Sequence

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

_DIM_COLOR = {0: "#1f77b4", 1: "#d62728", 2: "#2ca02c"}
_DIM_LABEL = {0: "$H_0$", 1: "$H_1$", 2: "$H_2$"}


def _ensure_dir(path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)


def plot_diagram(ax, result, *, dims: Sequence[int] = (0, 1, 2),
                 title: str = "", top: Optional[float] = None) -> None:
    """Scatter one persistence diagram (birth vs death) onto `ax`."""
    finite = []
    for d in dims:
        dg = result.diagram(d)
        if len(dg):
            finite.append(dg[np.isfinite(dg[:, 1])])
    finite = np.concatenate(finite, axis=0) if finite else np.zeros((0, 2))
    if top is None:
        top = float(np.nanmax(finite[:, 1])) * 1.15 if len(finite) else 1.0
        top = max(top, 1e-3)
    inf_y = top * 0.98

    ax.plot([0, top], [0, top], color="0.7", lw=1, zorder=0)
    ax.axhline(inf_y, ls="--", color="0.5", lw=0.8, zorder=0)
    ax.text(top * 0.02, inf_y, r"$\infty$", va="bottom", ha="left", color="0.4", fontsize=9)

    for d in dims:
        dg = result.diagram(d)
        if not len(dg):
            continue
        b, dth = dg[:, 0], dg[:, 1].copy()
        dth[~np.isfinite(dth)] = inf_y
        ax.scatter(b, dth, s=16, alpha=0.65, color=_DIM_COLOR.get(d, "k"),
                   label=_DIM_LABEL.get(d, f"H{d}"), edgecolors="none", zorder=3)
    ax.set_xlim(0, top); ax.set_ylim(0, top)
    ax.set_xlabel("birth"); ax.set_ylabel("death")
    ax.set_title(title, fontsize=10)
    ax.set_aspect("equal", "box")
    ax.legend(loc="lower right", fontsize=8, framealpha=0.9)


def save_case_diagrams(gt, cand_ok, cand_bad, path: str, *,
                       case_title: str = "", labels=("ground truth",
                       "A — topology OK", "B — topology WRONG")) -> str:
    """Three side-by-side diagrams (GT, correct candidate, wrong candidate) on a
    shared scale, so the wrong candidate's missing/extra features are obvious."""
    _ensure_dir(path)
    tops = []
    for r in (gt, cand_ok, cand_bad):
        for d in (0, 1, 2):
            dg = r.diagram(d)
            if len(dg):
                fin = dg[np.isfinite(dg[:, 1])]
                if len(fin):
                    tops.append(fin[:, 1].max())
    top = (max(tops) * 1.15) if tops else 1.0
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.4))
    for ax, r, lab in zip(axes, (gt, cand_ok, cand_bad), labels):
        plot_diagram(ax, r, title=lab, top=top)
    fig.suptitle(case_title, fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


def save_stability_series(rows: list[dict], path: str, *, disc_dim: int = 1,
                          title: str = "Topology stability vs training step") -> str:
    """Two stacked panels:
      top   — geometry (Chamfer-to-target) vs topology (bottleneck-to-target)
              on twin axes: the geometry curve drifts smoothly while the
              topology curve jumps when a feature appears/disappears.
      bottom— count of significant features per dimension.
    Expects each row to carry: step, chamfer, bottleneck_H{disc_dim},
    nsig_H0/H1/H2.
    """
    _ensure_dir(path)
    step = [r["step"] for r in rows]
    cham = [r.get("chamfer", np.nan) for r in rows]
    bott = [r.get(f"bottleneck_H{disc_dim}", np.nan) for r in rows]

    fig, (ax1, ax3) = plt.subplots(2, 1, figsize=(8, 7), sharex=True,
                                   gridspec_kw={"height_ratios": [2, 1]})
    l1, = ax1.plot(step, cham, "-o", color="#555555", label="Chamfer→target (geometry, %)")
    ax1.set_ylabel("Chamfer→target (%)", color="#555555")
    ax1.tick_params(axis="y", labelcolor="#555555")
    ax2 = ax1.twinx()
    l2, = ax2.plot(step, bott, "-s", color=_DIM_COLOR[disc_dim],
                   label=f"bottleneck→target ({_DIM_LABEL[disc_dim]}, topology)")
    ax2.set_ylabel(f"bottleneck→target ({_DIM_LABEL[disc_dim]})", color=_DIM_COLOR[disc_dim])
    ax2.tick_params(axis="y", labelcolor=_DIM_COLOR[disc_dim])
    ax1.set_title(title, fontsize=11)
    ax1.legend(handles=[l1, l2], loc="upper left", fontsize=9)
    ax1.grid(True, alpha=0.2)

    for d in (0, 1, 2):
        ax3.plot(step, [r.get(f"nsig_H{d}", np.nan) for r in rows], "-o",
                 color=_DIM_COLOR[d], label=f"# sig {_DIM_LABEL[d]}")
    ax3.set_xlabel("training step (synthetic topology-break sequence)")
    ax3.set_ylabel("# significant features")
    ax3.legend(loc="upper left", fontsize=9, ncol=3)
    ax3.grid(True, alpha=0.2)

    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path
