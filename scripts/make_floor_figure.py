# scripts/make_floor_figure.py
# Paper-2 round-4 figure (advisor Fig-5 concept, right panel): the
# measurement floor vs sampling density. Every plotted value is a
# RECORDED measurement from the 2026-07-09 density sweep (the same
# numbers behind suppl Table S3 and main §6) — this script only plots;
# it computes nothing new. (gudhi is unavailable under Smart App
# Control as of 2026-07-17, so regeneration via density_bound.py is
# blocked; values below are transcribed with their sources.)
#
#   D:\...\CG-Soup-for-Digital-Dentistry\.venv\Scripts\python.exe `
#       scripts\make_floor_figure.py
#
# Output: paper2/figures/floor.png

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

_TOPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(_TOPO, "paper2", "figures", "floor.png")

# Measured floors 6*r_med(M), density sweep 2026-07-09, seed 0.
# src: paper2/sections/appendix_diagnostics.tex Table S3 source comment
#      ("floors .1261/.0895/.0644/.0458 sphere; .1228/.0843/.0623/.0437
#        torus; .1107/.0739/.0539/.0382 double_torus")
MS = np.array([512, 1024, 2048, 4096])
FLOORS = {
    "sphere":       [0.1261, 0.0895, 0.0644, 0.0458],
    "torus":        [0.1228, 0.0843, 0.0623, 0.0437],
    "double torus": [0.1107, 0.0739, 0.0539, 0.0382],
}
# Eval-density anchor (M=20000): torus-scene floor .0171
# src: main §6 ("at the evaluation density (M=20000, floor .0171)")
M_EVAL, FLOOR_EVAL = 20000, 0.0171

# Feature lifetimes on the clean GT surfaces (constant in M):
# src: main §6 — double torus's tube loops "live at lifetime .045–.046";
#      torus's second loop "clears the clean floor by only 1.33x" at
#      M=2048 => lifetime = 1.33 * .0623 = .0829 (derived from the two
#      recorded quantities, marked as such in the caption).
TUBE_LO, TUBE_HI = 0.045, 0.046
TORUS_2ND = 1.33 * 0.0623

# Okabe-Ito colour-blind-safe
COLS = {"sphere": "#0072B2", "torus": "#009E73", "double torus": "#D55E00"}

fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=200)

# the M^-1/2 law through the torus M=2048 point, up to the eval density
mm = np.geomspace(400, 26000, 200)
law = FLOORS["torus"][2] * np.sqrt(2048.0 / mm)
ax.plot(mm, law, ls=":", color="0.45", lw=1.4,
        label=r"$\propto M^{-1/2}$ law")

for shape, fl in FLOORS.items():
    ax.plot(MS, fl, "o-", ms=5, lw=1.6, color=COLS[shape],
            label=f"floor, {shape}")
ax.plot([M_EVAL], [FLOOR_EVAL], "s", ms=6, color=COLS["torus"])
ax.annotate("eval density\n(M=20000, floor .0171)", (M_EVAL, FLOOR_EVAL),
            textcoords="offset points", xytext=(-8, 12), ha="right",
            fontsize=8)

# constant feature lifetimes vs the falling floor
ax.axhspan(TUBE_LO, TUBE_HI, color=COLS["double torus"], alpha=0.18, lw=0)
ax.text(430, 0.0455, "double-torus tube loops (.045–.046):\n"
        "below the floor at M=2048, clear it by M=4096", fontsize=8,
        color=COLS["double torus"], va="center")
ax.plot([2048], [TORUS_2ND], "D", ms=6, color=COLS["torus"])
ax.annotate("torus 2nd loop:\nclears by only 1.33× at M=2048",
            (2048, TORUS_2ND), textcoords="offset points", xytext=(10, 6),
            fontsize=8, color=COLS["torus"])

ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xticks([512, 1024, 2048, 4096, 8192, 20000])
ax.set_xticklabels(["512", "1024", "2048", "4096", "8192", "20000"])
ax.set_xlabel("sampling density $M$")
ax.set_ylabel(r"significance floor $6\,r_{\mathrm{med}}(M)$ / bar lifetime")
ax.grid(True, which="both", alpha=0.25, lw=0.5)
ax.legend(fontsize=8, loc="upper right")
fig.tight_layout()
fig.savefig(OUT)
print("wrote", OUT)
