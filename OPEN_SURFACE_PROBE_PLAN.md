# Open-surface stress probe — PRE-REGISTERED DESIGN (2026-07-17, not yet run)

Round-4 review item (both advisor documents): "at least a synthetic
open-surface stress test (promised) should appear." Paper-2 §7 already
commits to it as the near-term step. This file pre-registers the design
BEFORE any run, following the tom-yum pot's prospective-floor-rule
precedent — the rule is registered, not the outcome.

**STATUS UPDATE (2026-07-17, later): UNBLOCKED + assets built.** The
Smart App Control block (which stopped gudhi 3.12.0's DLLs) does NOT
apply to the gudhi **3.11.0** wheel — per-binary verdicts. A stable
copy lives at `tools\gudhi311` (gitignored, like tectonic), used via
`PYTHONPATH`. **Numerical equivalence verified before any use**:
`density_bound.py` under 3.11.0 reproduces every recorded 3.12.0
number exactly (floors .05394/.06233 @2048, tube lifetimes
.0460/.0449 = 0.85/0.83×, torus 2nd loop .0832 = 1.33×, r_med
.00899→.00284 = 3.16 ratio, eval floor .01707).

**Steps 1–3 EXECUTED (`scripts/make_bowl_assets.py`):** both bowls
built and certified (disk topology: 1 boundary loop, edge-manifold,
consistently oriented, χ=1; measured openings 0.140R / 0.499R; certs in
`_meshes/bowl_{narrow,wide}_src_cert.json`). **Pre-registered staircase
result — the certified reading overrides the plan's expectation:**

| M | bowl_narrow sig(H0,H1,H2) | top H2 | bowl_wide sig | top H2 | top H1 (both) |
|---|---|---|---|---|---|
| 2048 | (0,0,1) | 3.79× | (0,0,1) | 2.34× | 0.42–0.47× |
| 4096 | (0,0,1) | 5.50× | (0,0,1) | 3.50× | 0.51–0.57× |
| 8192 | (0,0,1) | 7.82× | (0,0,1) | 4.94× | 0.45–0.46× |

The plan EXPECTED bowl_wide to lose its H2 bar to the rim's H1; the
measurement says otherwise — even a 0.5R mouth caps at these densities,
the interior reads as an enclosed chamber for both bowls, and the
designed rim's H1 never clears the floor. Per the registered rule:
**observable = H2 for both, bundle density M=2048** (first-clearing),
budget N=1200 (H2 class), `--loss_dims 2` (rim H1 sub-floor ⇒ restrict,
the torus precedent). The expectation-vs-measurement delta is itself a
reportable finding about open-surface alpha readings.

Shape wiring done: `SHAPE_DIM` (topo_resampling_eval.py) and the
report's target-count table (topo_loss_report.py) carry both bowls.

## Shapes (analytic, built from the existing sphere generator)

1. **bowl_narrow** — the analytic sphere with a small polar cap removed
   (opening radius ≈ 0.15 R). Expected cloud reading (to be verified by
   the staircase, not assumed): the narrow mouth caps at small alpha, so
   the interior still reads as an enclosed chamber — an H2 void, the
   pot's mechanism on an open surface. Probes: does the loss's H2 repair
   survive a genuinely open shell?
2. **bowl_wide** — cap removed at ≈ 0.5 R. Expected reading: no H2 bar;
   the rim's H1 loop becomes the dominant feature. Probes: boundary-born
   H1 as the *target* observable.

## Pre-registered rules (decided now, before any measurement)

- **Bundle rule**: identical to the pot — run the density staircase
  (`density_bound.py` logic) on the certified open mesh; build the
  target bundle at the first density where the discriminating feature
  clears the 6·r_med floor; density-matched contract via
  `--topo_loss_pts`.
- **Boundary-born-bar policy**: rim-born bars of the *designed* opening
  are REAL features of the open target and are retained in the bundle.
  (The §7 "bar-filtering" plan concerns scan-noise boundaries, not a
  designed rim — state this distinction in the paper when reporting.)
- **Observable**: whatever the staircase certifies (H2 for bowl_narrow,
  H1 for bowl_wide is the expectation — but the certified reading wins;
  if the narrow bowl reads no H2 at any working M, that IS the result).
- **Conditions**: C0/C1/C2 × seeds {0,1,2}; ρ=0.1, ramp 0.2:0.5, 2,500
  steps; budget by class (H2 → N=1200, H1 → N=700); verdict rule
  unchanged (C1 < C0 and < C2 at Chamfer parity; n=3 ⇒ per-seed ranges,
  no Welch σ).
- **All outcomes reportable**: win (loss repairs open-surface topology),
  null (open boundary breaks the channel — the honest scope statement
  sharpens), or harm (rim features destabilize matching — a real
  finding about boundary contamination).

## Implementation checklist (in order)

1. ~~Mesh builder + certificates~~ **DONE** (`scripts/make_bowl_assets.py`).
2. **Renderer check** (NEXT, after the GPU frees from the double-torus
   runs): `make_synthetic_scene.py --shape bowl_narrow --mesh
   output\synth\_meshes\bowl_narrow_src.ply --out output\synth\bowl_narrow
   --views 48 --res 200` (and bowl_wide) — verify no backface-culling
   holes in training views (the pot was solidified precisely to avoid
   this; if culling bites, render two-sided or thicken minimally and
   re-certify — record whichever).
3. ~~Staircase~~ **DONE** (table above); bundle builds automatically at
   run launch (`ensure_bundle`, M=2048 default).
4. ~~Runs + report + verdicts~~ **EXECUTED 2026-07-17/18 — BOTH PASS.**
   - bowl_narrow: C0 .0588±.0035 → C1 **.0138±.0013 (4.2×)** at 0.89×
     baseline Chamfer, per-seed ranges disjoint; C2 pins the void at
     .1249 (2.1× worse than baseline, sd 0) at 3.5× worse Chamfer.
   - bowl_wide: C0 .0560±.0098 → C1 **.0137±.0003 (4.1×)** at 0.87×
     Chamfer, ranges disjoint; C2 .0770 and **erases the void in 2/3
     seeds** (β₂ 1→0) at 3.1× worse Chamfer.
   - #sig H2 = 1 in every C0/C1 seed; effects inside the study's
     2.1–10.4× span. (src: topo3/report/results.json, 2026-07-18.)
5. ~~Paper~~ **DONE**: main §7's promise converted to the result
   ("Synthetic, single-machine" item; scope wording updated in the
   abstract); full account = **suppl §F** (appendix_probe.tex, Tables
   S9 staircase + S10 C-matrix w/ per-seed rows); audit extended
   (means/sds/reductions/parity/disjointness/per-seed triplets) — all
   green; body still ends exactly p8.
