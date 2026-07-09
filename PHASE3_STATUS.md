# Phase 3 — Topological Loss: implementation status & results

**Status: COMPLETE AND FROZEN (git tag `paper2-results-freeze`, 2026-07-09).**
Stages 3a→3d, the 3e generality wave (all verdicts replicate on three external
genus-known meshes, zero per-shape tuning), the C6 recruitment ablation
(load-bearing), the C7 sensor-noise stress (graceful, zero Gabriel failures),
the ramp-window pilot + external C3 (knob-insensitive everywhere), and the
quantified measurement/representation floors. **Headline: the differentiable
topological loss gives topology-specific wins on voids (H2) AND loops (H1) —
the class the Phase-2 resampling channel failed — the two channels stack, the
result survives the family change and sensor noise, and its one essential
ingredient is recruitment.** Everything is written into paper 2 (`paper2/`,
19 pp, both advisor revision rounds answered — see `NOTES_FOR_AUTHOR.md`).
Remaining (deferred by design, out of the paper): C4 curvature-weighted mask
and the dental showcase (Phase-4 items; see PHASE3_PLAN.md §9).

Everything below is grounded in `PHASE3_PLAN.md` Appendices A–D and
`output/synth/topo3/report/results.json` (regenerate:
`experiments/topo_loss_report.py`).

## What was built

| Deliverable | File | Notes |
|---|---|---|
| Differentiable loss core (3a) | `methods/topological_loss.py` | Pair-frozen circumradius backward (closed forms, gradcheck-exact); `live_pairs` forward with index-mapping + Gabriel gates; Hungarian partial matching (exact W₂); **recruitment** for missing target features (pure OT has zero gradient exactly there); plan/eval split; density-matched scale-locked `TargetBundle` + CLI. |
| 3a gate suite | `tests/test_topo_loss.py` | 10/10: gradchecks (incl. detach semantics), gates (mapping exact; Gabriel 22/22 across 6 shapes @M=2048), satisfiability, 4 defect-repair toys (hole 8.8×, spurious handle killed, components 1229×, recruitment probe RECOVERED 450×). Artifacts: `figures/phase3_toy/`. |
| Training integration (3b) | `TopoLossState` (same module) | Frozen α×area barycentric sampling; auto re-pair on `F` tensor identity change + every K=10 steps; λ ramp with **ρ gradient-ratio calibration** (λ_peak = ρ·‖g_photo‖/‖g_topo‖); C2 `control_repulsion` mode (`rep_scale` knob); run log. |
| Hook | `…/CG-Soup-for-Digital-Dentistry/src/diffsoup_train.py` | 8 `--topo_*` flags, lazy import from `TOPO_ROOT`, ONE loss line after `reg_normal`; `topo_loss_log.json` on exit. Flag-off executes zero Phase-3 code. **No renderer/core edits.** |
| Runner (3c/3d) | `experiments/topo_loss_eval.py` | C0/C1/C2/C2g/C3/C5/C6/C7/C7h × shapes × seeds; per-shape bundle preflight; `--loss_dims` restriction; resumable; quicklook. |
| Density bounds | `experiments/density_bound.py` | the measurement floor 6·r_med(M) vs actual bar lifetimes (paper-2 §6 numbers + Appendix B M-sweep). |
| Report | `experiments/topo_loss_report.py` | Auto-discovers runs; cached stability series; per-shape series/tail/nsig plots; Welch σ; verdicts → `report/{results.json,summary.md,*.png}`. |

## Verification gates (full detail: PHASE3_PLAN.md Appendices A–B)

- **3a (hard gate before integration): 10/10.** Alpha vertex ids map 1:1 to
  input indices; **100% of significant-bar simplex values are Gabriel-exact**
  (the pair-frozen backward is fully fed; weighted-Rips fallback unused); the
  loss alone repairs a punctured sphere, a spurious handle, mis-spaced
  components, and (via recruitment) a bridged merge — on raw point clouds.
- **3b cleanliness — criterion had to be REVISED, and the revision is itself
  a finding:** two same-seed FLAG-OFF baselines already diverge in F at the
  first resample on the sphere scene (CUDA V-drift ~2 units flips borderline
  prune/split decisions). Phase 2's "F is deterministic" was torus-smoke-
  specific. Corrected criterion: divergence-EQUIVALENCE vs a baseline-vs-
  baseline control pair — the ρ=0 run passes (same first-divergence step,
  same magnitude; pre-resample steps indistinguishable). Mitigation stays
  seed-averaging.
- **3c calibration:** λ_peak scales linearly with ρ as designed; the response
  is FLAT across ρ ∈ {0.03, 0.1, 0.3} (sphere: 0.0181/0.0172/0.0177) — the
  knob is robust; **ρ=0.1 fixed** for the matrix. Overhead ≈ +45–55 s per
  2,500-step run (refresh 174 ms @M=2048, every 10 steps).

## RESULTS — the C-matrix (2,500 steps, ρ=0.1, ramp 0.2:0.5, Chamfer parity)

Tail-mean bottleneck-to-target in the discriminating dimension (mean ± sd
over seeds; ×N = reduction vs C0):

| shape (dim, N, seeds) | C0 | C1 topo loss | C2 control | C3 no-ramp | C5 loss+B4 |
|---|---|---|---|---|---|
| sphere (H2, 1200, 5) | .0623±.0063 | **.0156±.0013 (4.0×)** | .1372 (2.2× worse); gentle C2g .0972±.0169 (still worse than C0) | .0151±.0004 | **.0082±.0007 (7.6×)** |
| cube (H2, 1200, 3) | .0582±.0046 | **.0074±.0011 (7.9×)** | .1346, **b₂ 1→0** | — | — |
| torus (H1, 700, 5) | .0424±.0031 | **.0180±.0016 (2.3×)** | .0457, **b₁ 2→1** | .0155±.0015 | **.0133±.0004 (3.2×)** |
| two_spheres (H0, 700, 3) | .0065±.0008 | .0007±.0002 (9.5×) | .0008 (**ties C1**) | — | — |
| double_torus (H1, 2000, 2) | .0264±.0000 | .0264±.0000 | .0264±.0000 | — | — |

**Verdicts** (report's Welch σ; C1 < C0 AND C1 < every control at Chamfer
parity): **sphere H2 PASS (16.2σ; also beats gentle C2g) · cube H2 PASS
(18.5σ) · torus H1 PASS (15.6σ) · two_spheres H0 PASS by the rule (12.6σ) but
NOT topology-specific** (C1 ties the generic control on the diagram metric;
the topological increment shows only in Chamfer, 0.54 vs 1.94) ·
**double_torus SATURATED** — bottleneck pinned at .0264 (sd 0) in every arm
AND Wasserstein equally pinned (.0527–.0528): the two unrecoverable tube
loops set a metric floor; the constraint is DiffSoup's expressiveness (2/4
loops at any feasible budget, replicating Phase 2b), not the guidance
channel. The loss neither helps nor harms there (#sig H1 = 2 everywhere;
Chamfer 0.96 vs C0's 0.98).

### The six findings

1. **The loss channel succeeds where the prior channel failed: H1.** Phase 2's
   concentrated prior manufactured phantom handles; its spread prior never
   beat the random control. The loss cuts torus H1 error 2.3× with zero
   phantom handles in all 5 seeds (#sig H1 = 2 throughout), while the
   repulsion control collapses a loop. Metric pressure on birth/death values
   suits 1-D features better than budget allocation does.
2. **The channels stack.** C5 (loss + Phase-2b's B4 spread prior) is best
   everywhere tested — sphere .0082 (7.6× vs C0, ≈2× vs C1 alone, ≈4.6× below
   B4 alone), torus .0133 — with the best sphere Chamfer too; on the torus its
   Chamfer (.502) trails only C3 (.495). Allocation (prior) and
   value-tuning (loss) are complementary mechanisms.
3. **H0 is not topological — third channel, same answer.** Component accuracy
   is matched by generic spreading pressure in Phase 2 (B3≈B2), Phase 2b
   (B5≈B4-ish), and now Phase 3 (C2 ties C1). This is now a *finding* about
   the feature class, not a null about any one method.
4. **The curriculum is unnecessary once λ is calibrated** (C3 ≈ C1 on both
   decisive shapes, even marginally tighter). What makes the strength knob
   safe is the gradient-ratio calibration, not scheduling — an evidence-based
   answer to the advisor's blow-up concern (แนวทาง item 2).
5. **Recruitment is load-bearing for loops (C6 ablation, 2026-07-09).**
   Removing the recruitment term (pure matching+diagonal, all else identical)
   collapses the torus win entirely: C6 .0411±.0038 — statistically baseline
   (0.6σ from C0; 12.4σ worse than C1) at baseline Chamfer, loops still
   present (#sig 2 every seed). The new per-refresh logs
   (`topo_loss_log.json → "refreshes"`) show why: at M=2048 one torus loop is
   significant at EVERY refresh, the other chronically sub-threshold — all 5
   seeds, all 200 refreshes, profile (live_sig=1, matched=1, unreached=1) —
   so recruitment is the ONLY gradient path to the second loop, at every
   refresh. Not a cold-start device; on the loop class it IS the mechanism.
   On the sphere recruitment never fires (0/200, void always matched) ⇒
   sphere-C6 is loss-identical to C1; its tail (.0166 vs .0156, 1.5σ)
   measures pure run-to-run CUDA noise — a free replication control.
6. **Graceful under sensor noise (C7/C7h, 2026-07-09 — advisor item 4).**
   Gaussian noise on the cloud the PLAN sees, every refresh (σ = 0.5%/1% of
   the diagonal ≈ 0.5/1.0 median spacings at M=2048; pulls apply to true
   positions): torus .0210±.0018 / .0259±.0022 (2.0×/1.6× below C0; C1 is
   2.3×), sphere .0235±.0009 / .0328±.0013 (2.7×/1.9×; C1 is 4.0×) — at
   equal-or-better Chamfer, correct #sig in every run. **Zero Gabriel
   failures in all 2,400 noisy refreshes** (the detachment fallback never
   fired); recruitment absorbed the noise (torus second loop sub-threshold
   at every σ=1% refresh, unreached=0 throughout). λ_peak calibration
   spreads ≈3× across seeds under noise, tails stay tight (flat-ρ
   robustness extends to noisy calibration).

### Round-2 additions (advisor review, 2026-07-09): knob insensitivity + quantified floors

- **Ramp window is immaterial** (real pilot, sphere ×3 seeds): windows
  10–40% → .0154±.0017 and 30–60% → .0179±.0019 vs the default 20–50%'s
  .0156±.0013 — within seed noise (`ramp_1040/`, `ramp_3060/` +
  quicklook.json). Combined with C3 ≈ C1, the schedule carries nothing once
  ρ is calibrated.
- **Curriculum-free generalizes off the analytic family**: bob C3 =
  .0171±.0026 vs C1's .0208±.0008 (3 seeds, in topo3/report).
- **The measurement floor is a law, not a folk rule**: significant ⟺
  lifetime > 6·r_med(M), with r_med ∝ M^(−1/2) (measured ratio 3.16 vs
  theoretical 3.13). M-sweep (512/1024/2048/4096): torus's 2nd loop appears
  at 2048, its void at 4096; the double torus's 4 loops all clear the floor
  at 4096 — confirming the M≈3×10³ bound. The binding double-torus
  constraint is representation (budget N), not measurement.
  (`experiments/density_bound.py`; paper-2 Appendix B table.)
- **The control's failure mechanism, visualized**: persistence-diagram
  trajectories (paper-2 Appendix B figure) show C0's void drifting off
  target, C1's returning once the ramp activates (final gap ≈ its tail),
  and C2's void *pinned and dragged* over an accumulating carpet of phantom
  bars — the repulsion-equilibrium signature.
- **Honest cost numbers** (replacing optimistic estimates): the loss adds a
  fixed ≈46 s per 2,500-step run vs 33–41 s photometric baselines (more
  than 2× on these tiny scenes; scales with M, not scene complexity).
  Nondeterminism: tail CVs 7–10% for baseline and loss arms alike; the
  loss-identical sphere C6/C1 pair lands 6% apart (pure run-to-run noise).

## 3e generality wave (2026-07-09): external genus-known meshes — 3/3 PASS

The plan's stretch item said "ShapeNet subset (genus-known meshes)".
Substitution, for cause: ShapeNet needs a licensed account and its meshes are
routinely non-watertight/non-manifold — no trustworthy ground-truth topology,
which is the one property the generality claim needs. Used instead (the
parenthetical's actual requirement): **spot** (genus 0, organic, CC0 Crane
repository), **bob** (genus 1, organic, CC0), **fandisk** (genus 0, CAD,
A-series scene reused). Both downloads seam-merged (`merge_vertices`) and
verified watertight with the expected genus before export to
`output/synth/_meshes/*_src.ply`; scenes built with the unchanged renderer
(48 views, 200 px); bundles preflighted at M=2048 (spot/fandisk: exactly 1
significant H2 bar; bob: its 2 loop bars AND a significant H2 void bar —
fat tube, so bob runs the FULL unrestricted bundle, unlike the thin torus).
Class budgets carried over blind (H2→1200, H1→700); a seed-0 C0 pilot landed
every baseline inside the analytic shapes' imperfection band (.043–.054).

Protocol: C0/C1/C2 × seeds {0,1,2}, ρ=0.1, ramp 0.2:0.5, 2,500 steps —
27 runs, zero failures. Same verdict rule, same report.

| shape (dim, N) | C0 | C1 topo loss | C2 control | verdict |
|---|---|---|---|---|
| spot (H2, 1200) | .0521±.0081 | **.0237±.0000 (2.2×)** | .0652, **b₂ 1→0** | PASS (6.1σ) |
| bob (H1, 700) | .0426±.0012 | **.0208±.0008 (2.1×)** | .0437, **b₁ 2→1** | PASS (26.1σ) |
| fandisk (H2, 1200) | .0538±.0022 | **.0052±.0008 (10.4×)** | .0571, **b₂ 1→0** | PASS (35.7σ) |

C1's Chamfer is *better* than C0 on all three (parity trivially OK). The
control's failure modes replicate exactly: void erased on both H2 shapes,
loop collapsed on the genus-1 shape, all seeds. **The H1 claim survives the
family change** (bob: #sig H1 = 2 in every seed — zero phantom handles,
replicating torus); **fandisk's 10.4× is the largest effect in the study**.

Caveats, honestly: spot's *baseline* manufactures a phantom void in 2/3
seeds (final #sig H2 = 2,1,2); C1 clears it in two seeds but retains one
spurious bar in the third (1,2,1) — value repair is reliable, count repair
on sub-budget organic detail (legs/horns at N=1200) is an improvement, not a
guarantee. Spot's C1 tail is pinned across seeds (sd 0 at .0237) — a
geometric floor of the double-torus kind, far milder in degree.

### Honest caveats

- **The loss can only enforce topology measurable at its sampling density**:
  the target bundle is density-matched at M=2048; torus's own H2 void bar and
  double_torus's two tube loops are sub-threshold there (runs restrict to H1
  via `--topo_loss_dims 1`; double_torus targets its 2 measurable big loops —
  consistent with Phase 2b, where DiffSoup could only express 2/4 loops at
  any feasible budget anyway). The bundle CLI prints bars + threshold at
  build time, so miscalibration is visible.
- **Control strength is now bounded from both sides**: the aggressive C2
  (2× median spacing) destroys topology; the gentle C2g (1×) still sits 1.6×
  WORSE than baseline on sphere (.0972 vs .0623) — no repulsion strength
  reproduces any of C1's gain, so the verdicts do not hinge on control
  tuning.
- CUDA non-reproducibility (3b): all claims are seed-averaged; no bit-level
  statements.
- Single machine, synthetic closed-surface renders (200–256 px, 24–72
  views). The 3e wave (above) extends the analytic family with three
  external genus-known meshes — still short of a public shape-set benchmark;
  real dental data remains deferred (PHASE3_PLAN.md §9).

## How to reproduce

```powershell
# gates (topology repo, dentistry venv):
python tests\test_topo_loss.py                                  # 10/10

# matrix (needs sibling repos + CUDA):
python experiments\topo_loss_eval.py --shapes sphere --seeds 0 1 2 3 4 `
    --conditions C0 C1 C2 C3 C5 --rhos 0.1 --steps 2500 --max_faces 1200
python experiments\topo_loss_eval.py --shapes torus --seeds 0 1 2 3 4 `
    --conditions C0 C1 C2 C3 C5 --rhos 0.1 --steps 2500 --max_faces 700 --loss_dims 1
# … cube/two_spheres/double_torus per PHASE3_PLAN.md Appendix C/D …

# ramp-window pilot (round 2; separate exp roots so tags don't collide):
python experiments\topo_loss_eval.py --shapes sphere --seeds 0 1 2 --conditions C1 `
    --rhos 0.1 --ramp 0.1:0.4 --steps 2500 --max_faces 1200 --exp_name ramp_1040
python experiments\topo_loss_eval.py --shapes sphere --seeds 0 1 2 --conditions C1 `
    --rhos 0.1 --ramp 0.3:0.6 --steps 2500 --max_faces 1200 --exp_name ramp_3060

# density / measurement-floor numbers (CPU only):
python experiments\density_bound.py

# C7/C7h sensor-noise stress (decisive shapes only):
python experiments\topo_loss_eval.py --shapes torus --seeds 0 1 2 `
    --conditions C7 C7h --rhos 0.1 --steps 2500 --max_faces 700 --loss_dims 1
python experiments\topo_loss_eval.py --shapes sphere --seeds 0 1 2 `
    --conditions C7 C7h --rhos 0.1 --steps 2500 --max_faces 1200

# C6 recruitment ablation (decisive shapes only):
python experiments\topo_loss_eval.py --shapes torus --seeds 0 1 2 3 4 `
    --conditions C6 --rhos 0.1 --steps 2500 --max_faces 700 --loss_dims 1
python experiments\topo_loss_eval.py --shapes sphere --seeds 0 1 2 3 4 `
    --conditions C6 --rhos 0.1 --steps 2500 --max_faces 1200

# 3e generality (scenes prebuilt under output/synth/{spot,bob,fandisk};
# sources in output/synth/_meshes/; bundles in topo3/fields/; resumable):
python experiments\topo_loss_eval.py --shapes spot fandisk --seeds 0 1 2 `
    --conditions C0 C1 C2 --rhos 0.1 --steps 2500 --max_faces 1200
python experiments\topo_loss_eval.py --shapes bob --seeds 0 1 2 `
    --conditions C0 C1 C2 --rhos 0.1 --steps 2500 --max_faces 700

# report:
python experiments\topo_loss_report.py
python scripts\make_phase3_report_docx.py                        # Thai .docx
```
