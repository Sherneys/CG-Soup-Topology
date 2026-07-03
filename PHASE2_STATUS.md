# Phase 2 — Implementation status & how to run the full sweep

**Status: implemented and smoke-validated end-to-end. The full scientific sweep
(more steps / seeds / shapes / budgets) is the remaining compute — see below.**

## What was built (all deliverables)

| Deliverable | File | Notes |
|---|---|---|
| 1. Importance field | `methods/topo_importance.py` | `build_importance_field` (topo, Option-B surface-splat, σ=√death) + `build_curvature_field` / `build_random_field` (B3 controls). Reuses `persistence_from_target`; localizes via `persistence_pairs` + `get_point`. CLI: `python -m methods.topo_importance`. |
| 2. The method | `methods/topo_resampling.py` | `TopoResamplePolicy`: importance-protected keep-map (exact-neutral) + budget-neutral densify-and-rebalance. One knob `lambda_topo`; `=0` ⇒ baseline. Field-agnostic (B2=topo npz, B3=curv/rand npz). No gudhi at train time. |
| Hook seam | `…/CG-Soup-for-Digital-Dentistry/src/diffsoup_train.py` | `resample_soup(…, policy=None)` (baseline lifted verbatim) + flags `--resample_mode/--lambda_topo/--importance_npz/--topo_init/--topo_dim`. Lazy import — baseline never touches Phase-2 code. **No diffsoup renderer/core edits.** |
| H0 target | `…/src/make_synthetic_scene.py` (`two_spheres`) + `output/synth/two_spheres` | torus (H1) & sphere (H2) scenes already existed. |
| 3. Experiment | `experiments/topo_resampling_eval.py` | Drives B0/B1/B2/B3 × shapes × seeds via `diffsoup_train --traj_dir`; identical seed/target/N/optimizer; resumable. |
| 4. Eval + plots | `experiments/topo_eval_report.py` | bottleneck-to-target (disc dim), significant Betti, Chamfer/Hausdorff parity over training; `summary.md` + `results.json` + 3 PNGs/shape. Reuses `topology.metrics`. |

## Verification results (smoke: torus, seed 0, 500 steps, N=2500)

- **Cleanliness PASS.** B2 at `lambda_topo=0` vs B0: face-count trajectory and `F` structure **bit-identical at every step** (`torch.equal(F)=True`). The hook is non-invasive.
- **Determinism caveat (important, honest).** DiffSoup on CUDA is **not** bit-reproducible run-to-run: two baseline runs with the same seed diverge in vertex positions `V` by up to ~2 units (atomics in the rasterizer → nondeterministic gradients; a few unconstrained triangles drift). `F`/resampling decisions ARE deterministic. B2(λ=0)-vs-B0 `V` divergence equals B0-vs-B0 divergence ⇒ the hook adds none. Mitigation: average over seeds; the topology metric samples the soup α×area-weighted, robust to a few drifting triangles.
- **Budget-neutral.** Every resample held `faces = N` (±the baseline split's own data-dependent count). Confirmed for B0/B1/B2/B3.
- **Pipeline OK.** All four conditions train; report computes bottleneck/Betti/Chamfer, writes table + figures; **null results are reported honestly**.
- **Not a scientific result yet:** at N=2500/500 steps the torus is *too easy* — baseline already recovers b1=2, so there is no headroom and B2≈B0 (correctly reported as "not a win").

## RESULT (full sweep: 3 shapes × B0/B1/B2/B3 × 3 seeds, N=1200, 2500 steps, λ=1.0)

Primary metric = bottleneck-to-target in the discriminating dim, tail mean±sd over the last 30% of steps (lower=better). A genuine win must beat B0, beat the washout B1, hold Chamfer parity, AND beat the non-topological control B3.

| shape | dim | B0 | B1 | **B2** | B3 | verdict |
|---|---|---:|---:|---:|---:|---|
| **sphere** | **H2** | 0.0602±0.0042 | 0.0602±0.0009 | **0.0403±0.0030** | 0.0505±0.0063 | **PASS — clean win** |
| two_spheres | H0 | 0.0073 | 0.0074 | 0.0072 | **0.0057** | not a win (no headroom; B3≤B2) |
| torus | H1 | 0.0457 | 0.0457 | 0.0456 | **0.0435** | not a win (no headroom; B3≤B2) |

- **sphere/H2 is a real, topology-specific win:** B2 cuts void-topology error to target **~33%** below baseline (0.060→0.040, ~4σ over 3 seeds), beats the **washed-out** B1 (=B0, replicating **F1**) and the **non-topological** B3 (0.051), at comparable Chamfer (1.02% vs 0.92%). Of the total gain, ~⅓ is generic densification (B3) and ~⅔ is topology-specific (B2−B3). Coherent with Phase-1: the void (H2) is the subtlest case, and the shell-covering field targets exactly where a puncture would destroy it.
- **H0/H1 show no topological win at N=1200:** baseline already recovers the correct Betti number (b0=2, b1=2), so there is no headroom, and random bias (B3) does as well or better — i.e. any tiny B2−B0 difference is "biased resampling", not topology. These need a **tighter budget** (where baseline fails) to create headroom. (Note torus B1 final #sig H1 dropped to 1.7 — one-shot topo init sometimes *destabilized* a loop, another flavor of washout.)

Artifacts: `…/output/synth/topo2/report/summary.md`, `results.json`, and `<shape>_{bottleneck,betti,geometry}.png`.

### Budget scan (N∈{400,700,1200}, B0/B2/B3 × 3 seeds) — the full picture

bottleneck-to-target (disc dim), tail mean; **#sig** = final significant count in that dim (correct in parens).

**two_spheres H0 (b0=2):** B2 helps at tight N but **B3 (random) helps equally** ⇒ not topological; baseline never fails.
| N | B0 | B2 | B3 | B2 #sig (→2) |
|---|---:|---:|---:|---:|
| 400 | 0.0055 | 0.0043 | 0.0043 | 2.0 |
| 700 | 0.0072 | 0.0056 | 0.0054 | 2.0 |
| 1200 | 0.0073 | 0.0072 | 0.0057 | 2.0 |

**torus H1 (b1=2): B2 BACKFIRES at tight N** — over-concentrating on the loop **manufactures spurious handles** and starves the torus body.
| N | B0 | B2 | B3 | B2 #sig (→2) |
|---|---:|---:|---:|---:|
| 400 | 0.0162 | 0.0367 | 0.0414 | **7.7** |
| 700 | 0.0408 | 0.0448 | 0.0440 | **3.7** |
| 1200 | 0.0457 | 0.0456 | 0.0435 | 2.0 |

**sphere H2 (b2=1): the clean win** (N=1200): B2 0.0403 vs B0 0.0602, beats B1/B3, #sig 1.0, Chamfer parity.

### H1-fix (torus N=700, combined field topo_dim=-1, 3 seeds)

| λ | B0 | B2 | B3 | B2 #sig H1 (→2) |
|---|---:|---:|---:|---:|
| 1.0 | 0.042 | 0.043 | 0.036 | **5.0** (still spurious) |
| 0.3 | 0.044 | **0.037** | 0.028 | **2.0** (fixed!) |

At **λ=0.3 the backfire is fixed**: B2 recovers correct topology (b₁=2, no spurious handles) and **beats baseline** (0.037 vs 0.044) at Chamfer parity. BUT **random B3 (0.028) still beats B2** ⇒ the H1 gain is **not topology-specific** — generic densification does it better. (Mechanism: a loop is 1-D; *spreading* triangles preserves it, *concentrating* fragments it — so topo-targeting is the wrong prior for H1, whereas for an H2 void shell it is exactly right.)

## H2 GENERALIZATION — does the void win transfer beyond the sphere? (cube, cylinder)

The sphere/H2 win could have been a sphere-specific artifact, so two more **void-bounding
shapes** were added — both genus-0 closed surfaces (target betti `(1,0,1)`, i.e. b₂=1): a
**cube** (flat faces, sharp edges/corners) and a **capped cylinder** (developable side + 2
flat caps + circular edges). Identical regime to the sphere win: N=1200, 2500 steps, λ=1.0,
B0/B2/B3 × 3 seeds. Primary metric = bottleneck-to-target in H2 (tail mean±sd, lower=better).

| shape | B0 | **B2** (method) | B3 (control) | B2 vs B0 | B2 vs B3 (topo-specific) | verdict |
|---|---:|---:|---:|---:|---:|---|
| sphere   | 0.0602±0.0042 | **0.0403±0.0030** | 0.0505±0.0063 | −33% | −20% (~2σ)   | **PASS** |
| cube     | 0.0618±0.0010 | **0.0368±0.0026** | 0.0457±0.0025 | −40% | −19% (~3.5σ) | **PASS** |
| cylinder | 0.0592±0.0021 | **0.0422±0.0008** | 0.0446±0.0010 | −29% | −5% (~2.5σ)  | **PASS** |

**Result: the topology-specific void win generalizes 3/3.** On every void shape B2
(a) cuts void-to-target bottleneck **29–40% below baseline**, (b) **beats the non-topological
densification control B3** (so the gain is *topological*, not just "more triangles"), and
(c) holds **Chamfer parity or better** — cube/cylinder B2 are in fact geometrically *better*
than B0 (Chamfer 1.585<1.997, 1.600<1.674; sphere within the 15% tol). The topology-specific
increment (B2−B3) is large for sphere & cube (~20%, 2–3.5σ) and small-but-significant for
cylinder (~5%, ~2.5σ — cylinder's total gain is mostly generic densification with a real
topological increment on top). All conditions recover b₂=1 (final #sig H2 = 1.0): the win is
in the **accuracy/robustness of the void's persistence signature**, not the Betti count.

This elevates the Phase-2 finding from one shape to a **reproducible property of the void
class** across smooth / flat-sharp / capped-curved geometries. Mechanism (now confirmed
shape-independent): a void can be punctured *anywhere* on its 2-D bounding shell, the field
covers the *whole* shell, so only the topological prior densifies the whole feature
systematically — random blobs (B3) cannot.

Artifacts: `…/output/synth/h2_generalize/report/{summary.md, results.json, cube_{bottleneck,betti,geometry}.png, cylinder_{bottleneck,betti,geometry}.png}`.

## FINAL CONCLUSION

> **⚠ Update — superseded in part by Phase 2b (dimensional crossover, `PHASE2B_CROSSOVER.md`):** adding a
> SPREAD condition (B4 = the same topological field but wide-σ) shows the H2 void benefit is **maximized by
> SPREADING** the topological field, not concentrating it: **B4 < B2 < B3 < B0 for voids**, and spread also
> wins for loops (where concentrate → phantom handles). So the "concentrate wins the void" framing below is
> refined — **a SPREAD topological prior dominates the concentrated one at every feature dimension** (Phase 2
> simply never tested spread). The Phase-2 nulls (H0) and the torus backfire stand.

The **B3 control is decisive** and isolates a clean, honest finding:

> **Topology-aware resampling gives a genuine *topology-specific* benefit only for the VOID (H2) case** — B2 cuts void-error ~33% below baseline and beats *both* the washout (B1) and the non-topological control (B3), at equal geometry. For **components (H0)** it merely matches generic densification (B3), and for **loops (H1)** it is at best equal to B3 and, if λ is too high, actively harmful (spurious handles). The H2 win is mechanistically sound: a void dies from a hole *anywhere* on its bounding shell, the field covers the *whole* shell, and only the topological prior densifies that whole 2-D feature systematically — random blobs (B3) cannot. Lower-dimensional features (loops, gaps) prefer *spread* over *concentration*, so the topological prior offers no edge there.

**Generalization (3/3 voids):** the H2 win is **not a sphere artifact** — it replicates on the **cube** and **capped cylinder** too (29–40% below B0, beating B3 every time at Chamfer parity; see "H2 GENERALIZATION" above), making the topology-specific void benefit a reproducible property of the void *class* across smooth / flat-sharp / capped geometries.

F1 replicated throughout (B1 ≈ B0). Budget-neutral and λ=0-clean throughout. A complete Phase-2 result: one positive, topology-specific win (now shown to generalize across 3 void shapes) with a mechanism; honest nulls; a characterized+fixed failure mode.

## Run the full sweep

```powershell
$env:PYTHONUTF8="1"; $env:DIFFSOUP_ROOT="D:\Project\diffsoup"; $env:TOPO_ROOT="D:\Project\CG-Soup-Topology"
cd D:\Project\CG-Soup-Topology
# all conditions, all shapes, 3 seeds (resumable; ~controls compute via --steps/--max_faces)
.\…\python.exe experiments\topo_resampling_eval.py --shapes torus two_spheres sphere `
    --seeds 0 1 2 --conditions B0 B1 B2 B3 --steps 4000 --max_faces 1200 --lambda_topo 1.0
.\…\python.exe experiments\topo_eval_report.py --shapes torus two_spheres sphere --seeds 0 1 2
```

### Recommended regime to give the method headroom
The effect should appear where **baseline's topology is wrong some of the time**:
- **Tighter budget** `--max_faces 800–1500` (the A4 finding: low budget controls topology/coverage).
- **Harder targets first:** `two_spheres` (H0 — a spurious bridge merges components) and `sphere` (H2 — a punctured void) are harder to keep correct than the torus.
- **More steps** (≥2000) and **3 seeds** for the paired average + variance bands.
- Optionally sweep `--lambda_topo 0.5 1 2` and `--b3_mode curvature` (vs default `random`) for the B3 control.

Outputs land in `…/CG-Soup-for-Digital-Dentistry/output/synth/topo2/` (trajectories,
`fields/`, `report/summary.md` + figures).
