# scripts/make_pipeline_figure.py
# Paper-2 round-4 figure (advisor Fig-2 + Fig-3 concepts merged): the
# system pipeline as a left-to-right block diagram — standard DiffSoup
# photometric path (gray) + our topological branch (orange) — with the
# recruitment mechanism as a SCHEMATIC persistence-diagram inset (the
# advisor's Fig-3 two-panel concept: optimal matching's zero gradient
# for an absent target vs the greedy recruitment tug). The inset is a
# mechanism illustration, not measured data, and its caption says so.
# All labels use the paper's variables (M=2048, K=10, rho, lambda(t)).
#
#   D:\...\CG-Soup-for-Digital-Dentistry\.venv\Scripts\python.exe `
#       scripts\make_pipeline_figure.py
#
# Output: paper2/figures/pipeline.png

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

_TOPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(_TOPO, "paper2", "figures", "pipeline.png")

GRAY_F, GRAY_E = "#eef0f3", "#8b95a1"
ORAN_F, ORAN_E = "#fdebd9", "#D55E00"
BLUE = "#0072B2"
GREEN = "#009E73"

fig, ax = plt.subplots(figsize=(9.6, 4.0), dpi=200)
ax.set_xlim(0, 96)
ax.set_ylim(0, 40)
ax.axis("off")


def box(x, y, w, h, text, fc, ec, fs=9.5, lw=1.4):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.35,rounding_size=0.9",
                                fc=fc, ec=ec, lw=lw, zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, zorder=3)


def arrow(p, q, color="0.25", lw=1.6, style="-|>", ls="-", rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=13,
                                 color=color, lw=lw, ls=ls, zorder=1,
                                 connectionstyle=f"arc3,rad={rad}"))


# ---- standard photometric path (top, gray) ----
box(1, 30, 12, 7, "input\nviews", GRAY_F, GRAY_E)
box(19, 30, 16, 7, "differentiable\nrasterizer", GRAY_F, GRAY_E)
box(41, 30, 14, 7, "$L_{\\mathrm{photo}}$", GRAY_F, GRAY_E, fs=11)
arrow((13, 33.5), (19, 33.5))
arrow((35, 33.5), (41, 33.5))

# the soup (shared state)
box(17, 16, 17, 7, "triangle soup\n$V, F$ (budget $N$)", "white", "0.2",
    lw=1.8)
arrow((25.5, 23), (25.5, 30))      # soup -> rasterizer
ax.text(26.3, 26.2, "render", fontsize=8, color="0.35")

# ---- topological branch (bottom, orange) ----
box(1, 2, 14, 8, "surface samples\n$X$ ($M{=}2048$,\nfrozen barycentric)",
    ORAN_F, ORAN_E, fs=8.5)
box(20, 2, 13, 8, "alpha complex\n+ persistence\n(GUDHI, exact)",
    ORAN_F, ORAN_E, fs=8.5)
box(38, 2, 13, 8, "live diagram\npaired simplices\n(Gabriel-verified)",
    ORAN_F, ORAN_E, fs=8.5)
box(56, 2, 15, 8, "match + recruit\nvs.\ntarget bundle\n(refresh $K{=}10$)",
    ORAN_F, ORAN_E, fs=8)
box(76, 2, 13, 8, "$\\lambda(t)\\,L_{\\mathrm{topo}}$\n($\\rho$-calibrated)",
    ORAN_F, ORAN_E, fs=9.5)

arrow((20, 16), (9, 10), rad=-0.25)    # soup -> samples
ax.text(10.3, 13.2, "sample", fontsize=8, color="0.35")
arrow((15, 6), (20, 6))
arrow((33, 6), (38, 6))
arrow((51, 6), (56, 6))
arrow((71, 6), (76, 6))

# gradients back to the soup vertices (kept clear of the inset at x>=57)
arrow((76, 7.5), (34, 18.0), color=ORAN_E, lw=2.0, rad=-0.20)
ax.text(45.5, 12.6, "circumradius gradients (pair-frozen backward)",
        fontsize=8.5, color=ORAN_E, ha="center")
arrow((44, 30), (31, 23.4), color="0.35", lw=1.8, rad=0.25)
ax.text(41.5, 26.6, "photometric\ngradients", fontsize=8.5, color="0.35",
        ha="center")

# combined objective
box(76, 30, 19, 7, "$L = L_{\\mathrm{photo}} + \\lambda(t)L_{\\mathrm{topo}}$",
    "white", "0.2", fs=10, lw=1.8)
arrow((55, 33.5), (76, 33.5))
arrow((88, 10), (89.5, 30), color=ORAN_E, lw=1.6, rad=-0.12)

# ---- recruitment inset (schematic; advisor Fig-3 concept) ----
ix, iy, iw, ih = 55, 13.5, 31, 13
ax.add_patch(FancyBboxPatch((ix, iy), iw, ih,
                            boxstyle="round,pad=0.3,rounding_size=0.6",
                            fc="white", ec="0.6", lw=1.0, zorder=4))
ax.text(ix + iw / 2, iy + ih - 1.3,
        "recruitment (schematic): birth/death plane", fontsize=7.5,
        ha="center", zorder=6, color="0.25")
for k, (x0, title) in enumerate([(ix + 2.0, "optimal matching:\nzero gradient"),
                                 (ix + 16.5, "recruitment:\nsparse tug")]):
    w0, h0 = 12, 7
    y0 = iy + 2.6
    ax.plot([x0, x0 + w0], [y0, y0], color="0.5", lw=0.9, zorder=5)
    ax.plot([x0, x0], [y0, y0 + h0], color="0.5", lw=0.9, zorder=5)
    ax.plot([x0, x0 + w0 * 0.9], [y0, y0 + h0 * 0.9], color="0.75", lw=0.8,
            ls="--", zorder=5)                       # diagonal
    tx, ty = x0 + w0 * 0.30, y0 + h0 * 0.76          # absent target bar
    ax.plot([tx], [ty], "*", ms=11, color=GREEN, zorder=6)
    lx, ly = x0 + w0 * 0.72, y0 + h0 * 0.28          # sub-threshold live bar
    ax.plot([lx], [ly], "o", ms=5, color=BLUE, zorder=6)
    ax.text(x0 + w0 / 2, y0 - 1.7, title, fontsize=7, ha="center",
            zorder=6, color="0.25")
    if k == 1:
        ax.add_patch(FancyArrowPatch((lx, ly), (tx + 0.7, ty - 0.5),
                                     arrowstyle="-|>", mutation_scale=11,
                                     color="#D55E00", lw=1.6, ls="--",
                                     zorder=6))

fig.tight_layout()
fig.savefig(OUT)
print("wrote", OUT)
