# Open-surface stress probe — PRE-REGISTERED DESIGN (2026-07-17, not yet run)

Round-4 review item (both advisor documents): "at least a synthetic
open-surface stress test (promised) should appear." Paper-2 §7 already
commits to it as the near-term step. This file pre-registers the design
BEFORE any run, following the tom-yum pot's prospective-floor-rule
precedent — the rule is registered, not the outcome.

**STATUS: BLOCKED at execution (2026-07-17).** Windows Smart App Control
(state: On) blocks gudhi's native DLLs in the dentistry venv
(`ImportError: … An Application Control policy has blocked this file`),
which kills bundle building, `density_bound.py`, and training-side
persistence. The same block stopped the double-torus seeds-2–4 rerun.
Unblocking is a USER decision (SAC off is irreversible per Windows) or
an alternative environment (e.g. WSL rebuild). Everything below is
implementable the moment persistence tooling runs again.

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

1. Mesh builder: cap-removal on the analytic sphere mesh (mask faces by
   z-threshold; weld; verify: one shell, 1 boundary loop, expected Euler
   characteristic). Export to `_meshes/bowl_{narrow,wide}_src.ply` with
   a certificate JSON like the pot's.
2. **Renderer check**: `make_synthetic_scene.py --mesh` on an OPEN mesh —
   verify no backface-culling holes in training views (the pot was
   solidified precisely to avoid this; if culling bites, render
   two-sided or thicken minimally and re-certify — record whichever).
3. Staircase + bundle preflight (BLOCKED: gudhi).
4. Runs + report regen + range-based verdicts (BLOCKED: gudhi/GPU path).
5. Paper: §5.2 or §7 upgrade + suppl row; audit extensions.
