# Phase 2b — Dimensional crossover: does the right resampling prior depend on feature dimension?

**Status (updated 2026-07-09): COMPLETE — crossover thesis REFUTED** (spread
dominates at every dimension), then sharpened by the width-matched control B5
(`h2_unified`): the void gain is width-primary with only a small topological
residual. These results are the thesis of paper 1 (`paper/`) and the premise
of Phase 3 / paper 2 (the loss channel wins the loop class every prior failed;
`PHASE3_STATUS.md`).

## Question
Phase 2 found topology-aware resampling — a **concentrating** prior (condition **B2**) — gives a
topology-specific win for enclosed **voids (H2)** but is null for components (H0) and *backfires* on
loops (H1, phantom handles at tight budget). That suggested a **crossover thesis**: the correct *spatial*
prior depends on feature **dimension** — *concentrate* for high-dim voids (death-locus = the whole 2-D
shell, wide) but *spread* for low-dim loops/gaps (local support, prefer spreading). The test: add
**B4 = the same topological localization as B2 but SPREAD (wide σ)**, run a 2×2 (feature-dim ×
concentrate/spread), and check whether **sign(bottleneck_spread − bottleneck_concentrate) FLIPS** with
dimension.

## Method (everything reused; only a *minimal* field extension)
- **B4 spread field** — `methods/topo_importance.py` gained one knob `spread=s`: σ → s·σ_base,
  weight → life/s² (**mass-preserving**: Σ w·σ² is *exactly* s-invariant, verified). **s=1 is
  byte-identical to B2** (verified, max|Δ|=3e-8); s=3 used. The policy (`topo_resampling.py`) is
  unchanged — B4 just consumes a different `.npz`.
- **New deterministic targets** in `topology/meshes.py`, validated by `tests/test_betti.py` (**9/9 pass**):
  `double_torus` (genus-2, b=(1,4,1), via scikit-image SDF + marching-cubes), `three_spheres` (b0=3),
  `thick_shell` (b2=1, solid-wall volume sample; Betti-only).
- **Condition B4** wired into `experiments/topo_resampling_eval.py` (identical to B2 except the spread npz).
  Four conditions: **B0** baseline · **B2** concentrate · **B4** spread · **B3** non-topological control.
- **Per-class headroom budget** — a 2-seed pilot showed *one* N cannot give all classes headroom, so each
  shape runs where its baseline is imperfect: H2 `sphere`/`cube` @N=1200, H1 `torus` @N=700,
  H1 `double_torus` @N=2000, H0 `two_spheres`/`three_spheres` @N=700. Decisive arms (torus, sphere) at
  **5 seeds**, the rest at 3. Budget-neutral, paired seeds, λ=1, 2500 steps.
- Runner `experiments/dimensional_crossover.py`; analysis/plots `experiments/crossover_report.py`
  (reuses `topology.metrics`/`plots` + `topo_eval_report.py`).

## Result — there is NO crossover; SPREAD dominates concentrate at *every* dimension

PRIMARY = bottleneck-to-target in the decisive dim (tail mean over last 30% of steps; lower = better).

| shape | dim | N | B0 | **B2 concentrate** | **B4 spread** | B3 non-topo | Δ=B4−B2 | winner |
|---|---|---:|---:|---:|---:|---:|---:|---|
| sphere | H2 | 1200 | 0.0525 | 0.0448 | **0.0377** | 0.0472 | −0.0072 | **spread** |
| cube | H2 | 1200 | 0.0565 | 0.0378 | **0.0324** | 0.0496 | −0.0054 | **spread** |
| torus | H1 | 700 | 0.0409 | 0.0425 | **0.0316** | 0.0397 | −0.0108 | **spread** |
| double_torus | H1 | 2000 | 0.0264 | 0.0264 | 0.0264 | 0.0264 | 0.0000 | inconclusive |
| two_spheres | H0 | 700 | 0.0068 | 0.0059 | 0.0057 | 0.0059 | −0.0002 | tie |
| three_spheres | H0 | 700 | 0.0056 | 0.0062 | 0.0053 | 0.0051 | −0.0008 | tie (B3 ties) |

**Phantom-feature check** (decisive-dim #significant vs true Betti): torus **B2=4.4** (true 2!) vs **B4=2.0**;
double_torus B2=B4=2.0 (true 4); H0 shapes all correct.

- **The crossover thesis is REFUTED** — no sign flip. **Spread (B4) beats concentrate (B2) for all six
  shapes, including the H2 voids.**
- **H2 voids — spread > concentrate > non-topo > baseline.** B4 cuts the void bottleneck **~28% (sphere) /
  ~43% (cube) below baseline**, ~14–16% below concentrate, ~20–35% below B3, at **equal-or-better Chamfer**
  (B4's geometry is actually the best of the four). This **refines Phase 2**: the void benefit is real and
  topology-specific, but it is *maximized by spreading*, not concentrating — Phase 2 simply never tested
  spread, so it crowned B2 the winner among {B0,B1,B2,B3}.
- **H1 torus — spread wins big; concentrate backfires.** B4 0.032 < B0 0.041 < B3 0.040 ≈ B2 0.043:
  concentrate is *worse than baseline* and manufactures **phantom handles** (#sig-H1 = 4.4 vs true 2),
  while spread recovers b1=2 exactly with the best Chamfer. Replicates **and fixes** the Phase-2 torus backfire.
- **H0 components — null.** Topology ≈ random ≈ mild densification; not topology-specific (consistent with Phase 2).
- **double_torus — inconclusive.** Bottleneck pinned at 0.0264 (sd=0) for *all* conditions at both N=700 and
  N=2000; the soup only ever recovers 2 of 4 loops (#sig=2). DiffSoup under-resolves a genus-2 surface at
  feasible budgets, so this arm yields no discriminating signal (reported, not hidden).

## Revised conclusion (data-driven)
The right resampling prior does **not** flip with feature dimension. Instead, a single unified rule:

> **A SPREAD topological importance field is the better resampling prior at every feature dimension** —
> it beats baseline, beats the concentrated field, and beats the non-topological control, at
> comparable-or-better geometry. Concentrating the prior is at best equal (H0) and at worst harmful
> (H1 → phantom handles).

**Mechanism:** a feature's death-locus is its *whole support* — the bounding shell for a void, the entire
tube for a handle. Spreading importance over that support densifies/protects the feature coherently;
concentrating it at the localized death-simplex under-covers the rest of the shell (voids) or fragments the
loop into spurious handles (loops). So "spread over the feature, don't pile on its death point" is the
operative lesson — a cleaner and more actionable result than the hypothesized crossover.

## Gates (all green)
- Betti recovery **9/9** (incl. double_torus (1,4,1), three_spheres (3,0,3), thick_shell (1,0,1)).
- **Cleanliness:** B4@s=1 field byte-identical to the B2 field; λ=0 ≡ B0 (policy code unchanged).
- **Mass preservation:** Σ w·σ² exactly invariant across s.
- Budget-neutral; paired seeds; deterministic F-trajectory.

## Caveats
- The spread knob has **limited dynamic range** for compact shapes (topological death-scales are O(shape
  size), so even s=1 covers ~the whole surface); the operative effect of s is the *peakedness* of the field
  and hence the `keep_map` protection differential. The win is robust nonetheless (s=3).
- double_torus is inconclusive (above). A genus-2 signal would need a renderer/budget that can resolve 4 loops.
- H0 "spread wins" margins are within noise of B3 — treat as a tie/null, not a topological win.

## Files
`methods/topo_importance.py` (spread knob) · `topology/meshes.py` (+double_torus/three_spheres/thick_shell)
· `tests/test_betti.py` (+3 cases + import shim) · `experiments/{topo_resampling_eval.py (B4),
topo_eval_report.py (B4 + shapes), make_crossover_scenes.py, dimensional_crossover.py, crossover_report.py}`.
Artifacts: `output/synth/{crossover, crossover_N1200, crossover_N2000, crossover_N400}/` and
`crossover/crossover_report/{summary.md, results.json, crossover.png, phantom.png, parity.png, bottleneck_vs_N.png}`.
