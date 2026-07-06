# Phase 3 — Topological Loss: implementation status & results

**Status: implemented end-to-end and validated through the full C-matrix
(stages 3a→3d complete). Headline: the differentiable topological loss gives
topology-specific wins on voids (H2) AND loops (H1) — the class the Phase-2
resampling channel failed — and the two channels stack.** Remaining: C4
(curvature-weighted mask), dental showcase, ShapeNet generality (all deferred
by design; see PHASE3_PLAN.md §9 + Appendix D).

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
| Runner (3c/3d) | `experiments/topo_loss_eval.py` | C0/C1/C2/C2g/C3/C5 × shapes × seeds; per-shape bundle preflight; `--loss_dims` restriction; resumable; quicklook. |
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
| cube (H2, 1200, 3) | .0582±.0047 | **.0074±.0011 (7.9×)** | .1346, **b₂ 1→0** | — | — |
| torus (H1, 700, 5) | .0424±.0031 | **.0180±.0016 (2.4×)** | .0457, **b₁ 2→1** | .0155±.0014 | **.0133±.0004 (3.2×)** |
| two_spheres (H0, 700, 3) | .0065±.0008 | .0007±.0002 (9.3×) | .0008 (**ties C1**) | — | — |
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

### The four findings

1. **The loss channel succeeds where the prior channel failed: H1.** Phase 2's
   concentrated prior manufactured phantom handles; its spread prior never
   beat the random control. The loss cuts torus H1 error 2.4× with zero
   phantom handles in all 5 seeds (#sig H1 = 2 throughout), while the
   repulsion control collapses a loop. Metric pressure on birth/death values
   suits 1-D features better than budget allocation does.
2. **The channels stack.** C5 (loss + Phase-2b's B4 spread prior) is best
   everywhere tested — sphere .0082 (7.6× vs C0, ≈2× vs C1 alone, ≈4.6× below
   B4 alone), torus .0133 — with the best Chamfer too. Allocation (prior) and
   value-tuning (loss) are complementary mechanisms.
3. **H0 is not topological — third channel, same answer.** Component accuracy
   is matched by generic spreading pressure in Phase 2 (B3≈B2), Phase 2b
   (B5≈B4-ish), and now Phase 3 (C2 ties C1). This is now a *finding* about
   the feature class, not a null about any one method.
4. **The curriculum is unnecessary once λ is calibrated** (C3 ≈ C1 on both
   decisive shapes, even marginally tighter). What makes the strength knob
   safe is the gradient-ratio calibration, not scheduling — an evidence-based
   answer to the advisor's blow-up concern (แนวทาง item 2).

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
- Single machine / single scene family: synthetic closed surfaces at
  200×200 renders. ShapeNet generality and real dental data are Phase-3e+
  items (PHASE3_PLAN.md §9).

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

# report:
python experiments\topo_loss_report.py
python scripts\make_phase3_report_docx.py                        # Thai .docx
```
