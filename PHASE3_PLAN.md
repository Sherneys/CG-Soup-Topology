# Phase 3 — Topological Loss (Differentiable Persistence): Plan

**Goal: put topology INSIDE the training objective.** Phase 2 steered *where the
triangle budget goes* (resampling prior); Phase 3 adds a differentiable
persistence term to the loss so gradients *move vertices directly* toward the
target's topology: `L = photometric + λ(t) · L_topo(V)`.

Status: **PLAN — not implemented.** Design grounded in the current code
(file:line refs verified 2026-07-06). Follows the advisor's แนวทาง (2026-07-06);
§0 maps each of its five points to what this plan adopts, adapts, or defers.

---

## 0. Provenance — the advisor's five points → this plan

| # | Advisor's point | Disposition here |
|---|---|---|
| 1 | Differentiable persistence loss, `L = chamfer + 0.1·topo` | **Adopted, corrected**: DiffSoup's training loss is *photometric* (`aux + 0.8·L1 + 0.2·SSIM`, `diffsoup_train.py:529`), not Chamfer. The term is `+ λ(t)·L_topo` on that objective (§3). The `0.1` becomes the calibrated ratio ρ (§3.6). |
| 2 | Curriculum on λ (avoid gradient blow-up) | **Adopted** as the default schedule (§3.6) and tested as an explicit ablation arm C3 (§6). (Rationale adjusted: the 30–40× figure is a metric separation ratio, not a gradient scale — but Phase 2's own λ=1 phantom-handle backfire independently motivates a ramp.) |
| 3 | Curvature as a *weight* in the loss, not as init | **Adopted** as extension arm C4 — `build_curvature_field` (the Phase-2 B3 control) is reused verbatim as a spatial weight (§6). Consistent with F1 (init interventions wash out). |
| 4 | Dentistry tailoring (H1-primary, mouth-edge sensitivity, vs diffusion/SDF, internship data) | **Descoped from the validation phase** (discussed & agreed 2026-07-06): no ground-truth topology on real scans, open-surface H1 is boundary-contaminated, cross-representation baselines are a different paper. What survives: per-dim weighting is a flag (`--topo_loss_dims`), spatial weighting is C4, and a *qualitative* dental demo is a post-validation showcase (§9). |
| 5 | Publish; extend to ShapeNet; "Topology-Correcting Differentiable Rendering via PH" | **Adopted as sequencing**: finish the Phase-2 paper as-is (advisor judges it publishable); Phase 3 targets the follow-up paper. ShapeNet generalization = stage 3e stretch (§7). |

## 1. What already exists that Phase 3 reuses

| Piece | Where | Reused as |
|---|---|---|
| Target diagrams (API-frozen since Phase 1) | `persistence.persistence_from_target` | the loss's constant target |
| Pair localization: `persistence_pairs()` + `get_point()` + `sqrt(filtration)` | `methods/topo_importance.py:100-115` | exactly the forward bookkeeping the custom backward needs (§3.2) |
| Significance threshold (self-calibrating) | `persistence.py:63-90` | noise-bar filtering before matching (§3.4) |
| Wasserstein / bottleneck + prep (inf-handling, prune) | `metrics.py:49-113` | evaluation; the *matching* inside the loss (§3.4) |
| α×area surface sampling (eval-consistent) | `meshes.soup_cloud` / `eval_geometry.py` recipe | the differentiable sampler mirrors it (§3.3) |
| Headroom-characterized scenes & budgets | Phase 2/2b sweeps | experiment matrix reuses them; C0 ≡ B0 runs already on disk (§6) |
| Verdict discipline (beat baseline AND a non-topological control at Chamfer parity) | `topo_eval_report.verdict` | verdict rule for the loss channel (§6) |
| Hook style: lazy import, flag-gated, baseline untouched | Phase-2 `resample_soup(..., policy=None)` seam | the loss hook follows the same contract (§4) |

Carried cautions from Phase 2: never call `flag_persistence_generators` on an
alpha complex (segfault); CUDA training is not bit-reproducible (seed-average;
cleanliness is judged on the F-trajectory); PD build ≈1.5 s @20k pts ⇒ the
in-loop cloud must be small (M≈2k) and re-computation infrequent (§3.5).

## 2. Loss channel vs resampling channel — why Phase 2b does not foreclose this

Phase 2b's verdict ("the gain is carried by *width*, not topological placement")
is a statement about the **budget-allocation channel**: the prior only chooses
*where triangles respawn / which survive*; random wide blobs allocate budget
almost as well as topologically-placed ones. The loss channel is mechanically
different: it applies **metric pressure on birth/death values themselves** —
matched pairs are pulled toward the target's coordinates in diagram space,
spurious bars are pushed to the diagonal. Notably, Phase 2b's genuine win was
precisely in diagram *accuracy* (bottleneck), not Betti counts — the quantity
the loss acts on directly.

Honest structural hypothesis (stated up front so the result can't be
retro-fitted): each significant pair back-props through ≤ ~8 sampled points
(birth + death simplex vertices) ⇒ the loss delivers **precise but sparse**
tugs, where the resampling prior delivered **broad but indirect** allocation.
Possible outcomes, all informative: (a) loss beats controls where resampling
couldn't (H1 loops — double_torus was resampling-inconclusive); (b) loss is
redundant with B4; (c) loss + B4 stack (C5 tests this). If the sparse-tug
mechanism underwhelms, that is the Phase-3 negative result and it completes the
"which channel carries topology" story across both channels.

## 3. The loss — design

### 3.1 Definition

Per evaluated dimension d (default: the shape's discriminating dim; flag for
sets):

```
L_topo = Σ_matched (m)      [ (b_m − b*_m)² + (d_m − d*_m)² ]        # pull to target
       + Σ_unmatched live   [ ((d_u − b_u)/2)²  ]                    # push spurious to diagonal
       (unmatched TARGET bars: no gradient path — logged for monitoring only)
```

Matching = per-dim optimal partial matching between the live significant
diagram and the target diagram (`gudhi.wasserstein` with `matching=True`, or
Hungarian — both trivial at ≤ tens of significant bars after filtering).
Target values `(b*, d*)` are constants.

### 3.2 Differentiable birth/death — pair-frozen circumradius backward

For an alpha complex, a simplex's filtration value is (generically) the squared
circumradius of its defining vertices; our diagrams store `sqrt(filtration)/scale`
(`persistence.py:137,141`). Forward pass (non-differentiable, GUDHI): build the
alpha complex on the live cloud, run `persistence_pairs()`, keep significant
pairs, record each pair's **birth-simplex and death-simplex vertex indices**
(`topo_importance.py:100-115` machinery). Backward path (PyTorch): recompute
each recorded simplex's circumradius **in torch from the live point positions**
(closed form for edge/triangle/tetra) ⇒ `sqrt/scale` ⇒ the loss above ⇒
autograd flows points→vertices. The combinatorial pairing is treated as locally
constant (standard in the differentiable-PH literature); it is refreshed on a
schedule (§3.5).

Two verified-at-runtime assumptions, each with a gate in the 3a tests (§5):

- **Index mapping**: alpha-complex vertex ids must map 1:1 to input-cloud
  indices (`assert allclose(P[v], ac.get_point(v))` for every used vertex;
  fallback: KD-tree snap).
- **Non-Gabriel simplices**: a simplex's alpha value can be *inherited* rather
  than its own circumradius; then the torch-recomputed value ≠ the diagram
  value. Gate: compare recomputed vs `st.filtration` on all significant pairs
  across our 6 shapes; pairs off by > tol are dropped from the gradient (kept
  in monitoring). Fallback if this bites hard: weighted-Rips on the subsample
  (O(M²) but fine at M≈2k) — slower, but every filtration value is a pairwise
  distance, exactly differentiable.

### 3.3 Differentiable sampling of the soup

`X_j = Σ_i w_ij · V[F[f_j], i]` — face ids `f_j` drawn `sigmoid(alpha)×area`-
weighted (mirroring eval; probabilities detached) and barycentric weights
`w_ij` fixed per pairing refresh. Gradients reach `V_single` (the vertex tensor
optimized by VectorAdam, `diffsoup_train.py:370,422`) through the barycentric
combination. M = 2,048 default.

### 3.4 Noise control

Only bars with lifetime above the self-calibrating significance threshold
(`persistence.py:63`) enter matching; sub-threshold live bars contribute a
*capped* diagonal-push term (they are where spurious features are born —
killing them early is the point) with a floor to avoid chasing sampling noise.
Exact cap: decided during 3a toy runs.

### 3.5 Refresh schedule (pairing staleness vs cost)

Re-sample points + rebuild complex + re-pair every **K=10 steps** and
immediately **after every resample** (resampling detaches/re-creates `V_single`
and rewrites `F`, `diffsoup_train.py:411-413` — all recorded indices go stale;
K=10 divides the 100-step resample period). Between refreshes the *same* frozen
pairs are re-evaluated in torch each step (a few dozen circumradii —
microseconds), so the pull is continuous, not impulsive. Cost: ~250 refreshes ×
~0.1–0.3 s (M=2k alpha + pairing) ≈ **+30–80 s per run** — negligible against a
2,500-step training run.

### 3.6 λ curriculum + auto-calibration

`λ(t) = λ_peak · ramp(t; s₀, s₁)`, linear from step-fraction s₀=0.2 to s₁=0.5,
0 before (geometry settles first — advisor point 2). λ_peak is set by
**gradient-ratio calibration**: at s₀, scale so `‖∇V L_topo‖ ≈ ρ · ‖∇V L_photo‖`
with **ρ=0.1 default** (the advisor's 0.1, made dimensionless). ρ is the single
strength knob reported in experiments; ρ=0 ⇒ term never evaluated ⇒ baseline.

## 4. Integration — one flag-gated term, Phase-2 hook discipline

Injection point: after the `reg_normal` term (`diffsoup_train.py:534` — the
existing precedent for a flag-gated extra loss term), before `backward()`:

```python
if topo_loss_state is not None:                       # built iff --topo_loss_npz given
    loss = loss + topo_loss_state.term(V_single, F, step)
```

- New flags (all inert unless `--topo_loss_npz` set): `--topo_loss_npz`
  (target-diagram bundle), `--topo_rho` (0.1), `--topo_loss_every` (10),
  `--topo_loss_pts` (2048), `--topo_loss_dims` (default: shape's disc dim),
  `--topo_ramp` ("0.2:0.5"), `--topo_loss_mode` (`matched` | `control_repulsion`).
- Lazy import from `TOPO_ROOT` exactly like the Phase-2 policy import — flag
  off ⇒ zero Phase-3 code executes ⇒ baseline byte-identical.
- **Cleanliness contract** (REVISED in 3b — see Appendix B): flag-off and ρ=0
  runs must be **divergence-equivalent** to a baseline-vs-baseline control
  pair (same first-divergence step, same magnitude). The Phase-2 criterion
  (bit-identical F-trajectory) turned out to be torus-smoke-specific: on the
  sphere scene two same-seed FLAG-OFF baselines already flip borderline
  prune/split decisions at the first resample (CUDA V-drift ~2 units;
  bit-identical V was already known impossible, `PHASE2_STATUS.md`).
- Target bundle builder: `python -m methods.topological_loss --shape sphere
  --out fields/sphere_diag.npz` — stores per-dim target diagrams, `scale`,
  significance threshold, and config. **Density-matched**: the target diagram
  is computed at the SAME M=2,048 (averaged over a few sample seeds), not at
  the 20k eval density — alpha birth/death values shift with point spacing, and
  live-vs-target must not carry a density bias. **Scale-locked**: the live
  computation reuses the bundle's `scale` (never auto-rescale per step).

## 5. Stage 3a — de-risk gate BEFORE touching the training repo

Pure point-cloud optimization, no DiffSoup, no CUDA (this repo only):

1. **Gradcheck**: autograd vs finite differences for edge/triangle/tetra
   circumradius and for the full matched loss on ~30-point clouds. Exact
   closed forms ⇒ tight tolerances.
2. **Mapping + Gabriel gates** (§3.2) across the 6 deterministic shapes.
3. **Toy recovery**: Adam directly on point positions, L_topo alone —
   (a) punctured-sphere cloud → target (1,0,1): the H2 bar must be born and
   its death pulled to target; (b) torus with a pinched handle → (1,2,1);
   (c) two bridged spheres → (2,0,2). Success: bottleneck-to-target in the
   disc dim drops ≥5× and significant Betti hits target, with monitoring for
   pairing oscillation (§8).

**Hard gate: no integration work (§4) until 3a passes.** 3a artifacts land in
`figures/phase3_toy/` + a short section appended to this file.

## 6. Experiment matrix (after 3a + integration smoke)

Conditions (names chosen to not collide with Phase-2 B-arms):

| Cond | Objective | Isolates |
|---|---|---|
| C0 | photometric only (= B0; **reuse Phase-2 trajectories on disk** where shape/N/steps/seed match) | baseline |
| C1 | + matched topo loss (ρ=0.1, ramp 0.2:0.5) | the method |
| C2 | + gradient-norm-matched short-range **repulsion** on the same sampled points (same channel, same ρ, zero topology) | "is it just extra vertex regularization?" — the B3/B5 lesson applied to the loss channel |
| C3 | C1 with constant λ (no ramp) | advisor's curriculum claim |
| C4 | C1 with curvature-weighted spatial mask (reuses `build_curvature_field`) | advisor point 3 (extension; decisive shapes only) |
| C5 | C1 + B4 spread resampling prior (Phase-2 best) | do the two channels stack? (sphere + torus only) |

Shapes at their Phase-2b headroom budgets, 2,500 steps: sphere@N=1200 (H2,
decisive, 5 seeds), cube@1200 (H2 replicate, 3), torus@700 (H1 — the channel's
hardest test: does metric pressure avoid the phantom-handle failure that
concentration caused?, 5), two_spheres@700 (H0, 3), double_torus@2000 (stretch,
2 seeds — resampling was inconclusive here; a loss win would be the headline).

Metrics & verdict: identical to Phase 2 (`topo_eval_report`; tail-mean
bottleneck-to-target in disc dim, significant-Betti trajectory, Chamfer/
Hausdorff parity). **Verdict rule: C1 < C0 AND C1 < C2 at Chamfer parity**
(seed-averaged, ≥2σ) — a win over baseline that a dumb norm-matched regularizer
matches is NOT a topological win. Runner: `experiments/topo_loss_eval.py`
(thin variant of `topo_resampling_eval.py`; same resumability, same env/venv
invocation, same trajectory format so the report needs only new
condition labels/colors).

## 7. Deliverables & stages

| Stage | Deliverable | Gate to next |
|---|---|---|
| 3a | `methods/topological_loss.py` (circumradius autograd, matched loss, bundle builder CLI) + `tests/test_topo_loss.py` (gradcheck, gates, toy recovery) | all 3a tests pass |
| 3b | hook in `diffsoup_train.py` (flags above) + cleanliness check (F-trajectory identity, flag off & ρ=0) | cleanliness PASS |
| 3c | smoke: sphere seed 0, C0/C1, 500 steps — loss decreases, no NaN, overhead within §3.5 budget | smoke sane |
| 3d | full matrix (§6) + `experiments/topo_loss_eval.py` + report extension | — |
| 3e | writeup: PHASE3_STATUS.md + Thai .docx; stretch: ShapeNet subset (genus-known meshes) for the paper-2 generality section | — |

## 8. Risks / honest failure modes

- **Pairing oscillation**: matching flips between refreshes → loss jitter.
  Monitor matched-pair identity churn; damp with EMA on λ or longer K if seen.
- **Sparse-gradient underwhelm** (§2): few vertices touched per feature. If C1
  ≈ C0, that's the reportable negative for this channel — the 3a toy isolates
  whether the *gradient* works, so a training null is attributable to the
  channel, not the implementation.
- **Non-Gabriel drop-rate too high** (§3.2 gate): switch to weighted-Rips
  fallback; accept the O(M²) cost or lower M.
- **Density mismatch bias**: prevented by density-matched, scale-locked target
  bundles (§4) — treat any residual as a 3c smoke check item.
- **Resample interaction**: refresh-after-resample (§3.5) prevents stale-index
  crashes; still verify no step-100 loss spikes in smoke.
- **CUDA nondeterminism** (inherited): seed-average; never claim bit-identity.

## 9. Explicitly out of scope (deferred, with reasons agreed 2026-07-06)

- **Real dental/face data** — no ground-truth target diagram; open-surface H1 is
  scan-boundary-contaminated; internship-data publication clearance unverified.
  Revisit as a single qualitative showcase figure AFTER §6 lands.
- **Diffusion/SDF baseline comparisons** — cross-representation benchmark ≠
  this paper's ablation structure.
- **Mouth-edge-specific Wasserstein tuning** — subsumed by C4's spatial
  weighting mechanism if ever needed.

## 10. Open decisions (defaults proceed unless overridden)

1. **Between-refresh behavior**: frozen-pair continuous term (default) vs
   impulse-only-at-refresh (ablation if time permits).
2. **C2 control**: short-range repulsion on sampled points (default) vs
   Laplacian smoothing on V — repulsion shares C1's exact channel, so it is the
   stricter control.
3. **C5 scope**: sphere + torus only (default) vs full shape set.
4. **double_torus**: keep as 2-seed stretch (default) or drop.
5. **ρ default 0.1** with a mini-sweep {0.03, 0.1, 0.3} on sphere seed 0 during
   3c before committing the matrix.

---

## Appendix A — Stage 3a results (2026-07-06): **GATE PASSED, 10/10**

Deliverables landed: `methods/topological_loss.py` (circumradius autograd ·
`live_pairs` forward · Hungarian partial matching · recruitment · plan/eval
split · density-matched bundle builder CLI) and `tests/test_topo_loss.py`.
Suite: 3 gradcheck tests, mapping + Gabriel gates, loss-satisfiability, toys
T1–T3 (hard-gated) + T4 (probe). All numbers below from the suite run
(deterministic, CPU float64, dentistry venv).

### Gates (§3.2 assumptions)

- **Index mapping**: `get_point(v) == P[v]` exactly on all 6 registry shapes
  at M=2048 — no vertex-map fallback needed.
- **Gabriel**: **22/22 (100%)** of significant-bar simplex values recompute
  exactly (rtol 1e-6) across the 6 shapes ⇒ the pair-frozen backward is fully
  fed; the weighted-Rips fallback stays unused. The detach path is still
  wired and unit-tested (value kept, gradient blocked) in case denser/noisier
  clouds hit inherited filtration values.
- **Satisfiability**: loss ≡ 0 (< 1e-12) on the bundle's own cloud; 9.5e-3 on
  the punctured defect.
- **Cost**: plan refresh 174 ms @M=2048 (93 ms @M=1200) ⇒ §3.5's per-run
  overhead estimate (~44 s at refresh-every-10 over 2,500 steps) confirmed.

### Toys (Adam on raw positions, L_topo alone, refresh every iter)

| Toy | Mechanism gated | bottleneck (disc dim) | Betti | Verdict |
|---|---|---|---|---|
| T1 punctured sphere → sphere | matched BIRTH pull (close the hole) | H2 0.0973 → 0.0111 (**8.8×**) | (1,0,1) ✓ | PASS |
| T2 handle sphere → sphere | DIAGONAL push (kill spurious handle) | H1 0.0442 → **0** (bar killed) | (1,1,1)→(1,0,1) ✓ | PASS |
| T3 far two-spheres → gap 0.7 | matched DEATH pull (H0) | H0 0.0637 → 0.0001 (**1229×**) | (2,0,2) ✓ | PASS |
| T4 bridged spheres → two-spheres | RECRUITMENT (no significant live bar exists) | H0 0.0557 → 0.0001 (**450×**) | (1,0,2)→(2,0,2) ✓ | RECOVERED (probe) |

Artifacts: `figures/phase3_toy/t{1..4}.{png,json}`.

### Mechanism observations (carry into §2's hypothesis and the paper-2 draft)

1. **Sparse tugs repair via iteration.** Each refresh moves ≤ ~8 points, but
   per-iter re-pairing walks the surgery around the defect (T1's ~35-point
   hole rim closes in ~100 iters; T3 rings down like a damped oscillator under
   Adam momentum).
2. **Collateral roughening.** Every toy leaves a fuzz of abandoned tugs around
   the repaired cloud — diagram satisfaction is not clean geometry. In
   training, the photometric term is exactly the counterweight; watch the
   fuzz-vs-photo balance in 3c (this is what ρ calibrates).
3. **Recruitment is location-blind but landscape-guided (T4's surprise).** The
   predicted wrong-place-cut pathology did NOT materialize: tearing a 2-manifold
   shell cannot grow a component bar past the local detour scale (death
   saturates → tug abandoned → fuzz), while cutting the 1-D bridge raises the
   recruited bar's death monotonically toward the target ⇒ the runaway
   concentrates on the bridge — the only profitable direction. Caveat kept: a
   target death larger than any achievable detour could still tear shells.
4. **Density-vs-threshold calibration matters.** At M=2048 the default
   sig_k=6 swallows the defect bars (probe 2026-07-06); toys run at sig_k=4.
   Coarser M ⇒ coarser measurable topology (e.g., the torus tube loop is
   sub-threshold at M=2048/k=6). The bundle CLI prints bars + threshold at
   build time so per-shape M/sig_k misconfiguration is visible; re-check per
   shape when building 3b/3d bundles (H2-class bars are comfortable even at
   k=6; H1 at tight M is the fragile one).
5. **Plan §5 deviations (documented):** toy (b) pinched-torus was replaced by
   the handle-sphere (same H1 family, sampler already existed, mirrors the
   Phase-2 phantom-handle failure mode); toy (c) split into T3 (matched-pull)
   + T4 (recruitment probe). The recruitment term itself is a deliberate
   deviation from pure Wasserstein matching — optimal matching returns ZERO
   gradient exactly in the missing-feature case (T4's initial state: the
   bridge merges components below the noise floor, no significant live H0 bar
   exists) — §3.1's term list is amended accordingly.

**Gate to 3b: OPEN.** Next: the `diffsoup_train.py` hook (§4) + cleanliness
check.

---

## Appendix B — Stage 3b results (2026-07-06): **hook landed, gate PASSED**

Deliverables: `TopoLossState` (this repo, `methods/topological_loss.py`) —
frozen α×area barycentric sampling, auto re-pair on `F` tensor identity change
+ every K steps, λ ramp with ρ gradient-ratio calibration, C2
`control_repulsion` mode, run log writer — and the `diffsoup_train.py` hook
(dentistry repo): 7 `--topo_*` flags, lazy import, a one-line loss addition
after the `reg_normal` block, `topo_loss_log.json` on exit. Flag-off executes
zero Phase-3 code; ρ=0 short-circuits before any sampling.

### Cleanliness (sphere scene, 500 steps, N=2500, seed 0, downscale 1)

The original criterion FAILED — and the failure was **informative, not ours**:

| pair | first F divergence | face-count Δ at checkpoints |
|---|---|---|
| flag-off **A vs A′** (two identical baselines) | step 100 (F content; counts equal) | 0–1 |
| A/A′ vs **ρ=0** | step 100 | 1–6 |

Two same-seed FLAG-OFF baselines already diverge in F at the first resample:
the documented CUDA V-drift (~2 units, `PHASE2_STATUS.md`) flips borderline
prune/split decisions on this scene. Phase 2's "F is deterministic" held on
its torus smoke but is NOT a general property. Pre-resample steps (1–99) are
indistinguishable across all three runs (identical F, V-drift onset 0.0195 vs
0.0197). Verdict under the corrected criterion (divergence-equivalence):
**PASS** — the ρ=0 run's divergence starts at the same step with baseline-like
magnitude; post-divergence trajectories are chaos amplification in all pairs
alike. `phase2-task` memory and §4 updated; seed-averaging (already the
Phase-2 methodology) remains the mitigation.

### C1 engagement smoke (ρ=0.1, ramp 0.2:0.5, same scene/settings)

- Calibration fired once at step 101: **λ_peak = 0.405** (=ρ·‖g_photo‖/‖g_topo‖).
- λ ramps exactly per schedule (0.0027 @101 → 0.405 @250, flat after).
- Live diagram: 1 matched H2 term throughout, raw cost ~7–9e-4, no spurious
  bars, no recruitment, no NaN. At N=2500 the sphere has no topological
  headroom (baseline already recovers the void — the Phase-2 "too easy"
  regime), so a flat-small raw is the CORRECT behavior; effect measurement
  belongs to 3d at headroom budgets (N=1200).
- Quality preserved: PSNR 30.10 / SSIM 0.949 vs baseline 29.96 / 0.947.
- Overhead: ~+9 s over 400 active steps at this scale (32 vs 72 it/s on the
  tiny smoke) ⇒ ~+45–55 s for a real 2,500-step run — within the §3.5 budget.

**Gate to 3c/3d: OPEN.** Next: ρ mini-sweep {0.03, 0.1, 0.3} on sphere seed 0
(§10.5), then the C-matrix at headroom budgets (§6) via
`experiments/topo_loss_eval.py`.
