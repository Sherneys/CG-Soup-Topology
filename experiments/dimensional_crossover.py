# experiments/dimensional_crossover.py
# Phase-2 follow-up: the DIMENSIONAL-CROSSOVER experiment.
#
# Thesis: the correct SPATIAL resampling prior depends on the DIMENSION of the
# topological feature. A CONCENTRATING prior (B2) should help enclosed voids (H2,
# whose death-locus is the whole 2-D shell) but a SPREADING prior (B4) should be
# preferred for low-dim features (1-D loops H1, 0-D gaps H0), which a concentrating
# prior over-tessellates into phantom features.
#
# 2x2 crossover (feature dimension x concentrate/spread), budget-neutral, paired
# seeds. CRUCIAL: each feature class is run at its OWN HEADROOM budget N (the pilot
# showed a single N can't give all classes headroom — H2 needs a looser N where the
# void is still imperfect, H1 a tight N where loops are fragile, the genus-2 shape a
# larger N to afford 4 loops at all). Conditions:
#   B0 baseline | B2 topo-CONCENTRATE (s=1) | B4 topo-SPREAD (s>1) | B3 non-topo.
# B2 and B4 are IDENTICAL except the field's spread scale s (mass-preserving), so
# B4-vs-B2 isolates concentrate-vs-spread at the SAME (correct) feature locations.
#
# Orchestrates experiments/topo_resampling_eval.py (the B0..B4 harness) per group.
# Resumable (the eval driver skips finished runs; reuses the 2-seed pilot). Data is
# grouped into per-budget exp dirs that experiments/crossover_report.py reads.
#
#   python experiments/dimensional_crossover.py            # the lean per-class plan
#   python experiments/dimensional_crossover.py --dry_run  # print the plan only

from __future__ import annotations

import argparse
import os
import subprocess
import sys

_TOPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
EVAL = os.path.join(_TOPO_ROOT, "experiments", "topo_resampling_eval.py")
ENV = dict(os.environ, PYTHONUTF8="1",
           DIFFSOUP_ROOT=os.environ.get("DIFFSOUP_ROOT", r"D:\Project\diffsoup"),
           TOPO_ROOT=_TOPO_ROOT)

# (shape, N, seeds, exp_name) — each shape at its HEADROOM budget. Decisive arms
# (torus H1, sphere H2) at 5 seeds; the rest at 3. exp_name groups runs by budget.
# Ordered to surface the sign flip first: sphere(H2) then torus(H1).
PLAN = [
    ("sphere",        1200, [0, 1, 2, 3, 4], "crossover_N1200"),  # H2 headline (Phase-2 void regime)
    ("torus",          700, [0, 1, 2, 3, 4], "crossover"),        # H1 headline (loop-fragile regime)
    ("double_torus",  2000, [0, 1, 2],       "crossover_N2000"),  # H1 genus-2 (needs N for 4 loops)
    ("cube",          1200, [0, 1, 2],       "crossover_N1200"),  # H2 generalization
    ("two_spheres",    700, [0, 1, 2],       "crossover"),        # H0
    ("three_spheres",  700, [0, 1, 2],       "crossover"),        # H0 generalization
]
# H1 bottleneck-vs-N sweep (torus is cheap; N=700 already in PLAN under "crossover").
NSWEEP = [
    ("torus",  400, [0, 1, 2], "crossover_N400"),
    ("torus", 1200, [0, 1, 2], "crossover_N1200"),
]


def run(shape, N, seeds, exp_name, conditions, spread, steps, lam, dry):
    cmd = [PY, EVAL, "--shapes", shape, "--seeds", *map(str, seeds),
           "--conditions", *conditions, "--max_faces", str(N), "--steps", str(steps),
           "--lambda_topo", str(lam), "--spread", str(spread), "--exp_name", exp_name]
    print(f"\n>>> [{exp_name}] {shape} N={N} seeds={seeds}\n    " + " ".join(cmd), flush=True)
    if dry:
        return
    if subprocess.run(cmd, env=ENV, cwd=_TOPO_ROOT).returncode != 0:
        raise SystemExit(f"[FAIL] {exp_name}: {shape} N={N}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--conditions", nargs="+", default=["B0", "B2", "B4", "B3"])
    ap.add_argument("--spread", type=float, default=3.0)
    ap.add_argument("--steps", type=int, default=2500)
    ap.add_argument("--lambda_topo", type=float, default=1.0)
    ap.add_argument("--skip_nsweep", action="store_true")
    ap.add_argument("--dry_run", action="store_true")
    args = ap.parse_args()

    plan = list(PLAN) + ([] if args.skip_nsweep else list(NSWEEP))
    print(f"[crossover] per-class-N plan ({len(plan)} groups), conditions={args.conditions}, "
          f"spread={args.spread}, steps={args.steps}", flush=True)
    for shape, N, seeds, exp in plan:
        run(shape, N, seeds, exp, args.conditions, args.spread, args.steps,
            args.lambda_topo, args.dry_run)

    print("\n[done] dimensional-crossover runs complete. Next: experiments/crossover_report.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
