# Phase 1 — Topology-blindness of Chamfer / Hausdorff

**Measurement-only harness.** No resampling method and no differentiable persistent homology — topology is computed (alpha complex, GUDHI) purely to MEASURE what geometric metrics miss.

- Samples per shape: **40,000** (seeded, reproducible)
- Geometric metrics mirror `src/eval_geometry.py` (normalized by GT bbox diagonal)
- Topology metric: bottleneck distance of each candidate's persistence diagram to the ground-truth diagram, per dimension

## Result table

In every case the two candidates have **equal Chamfer** to GT by construction (A's geometry is bisection-matched to B). `A` is topologically correct, `B` is topologically wrong. The discriminating bottleneck column separates them.

| case | candidate | topo | Chamfer% | Hausd95% | bott→GT (disc) | H0 | H1 | H2 |
|------|-----------|------|---------:|---------:|--------------:|---:|---:|---:|
| i_genus | A: outward blister — genus 0 (correct) | OK  | 0.916 | 0.481 | 0.0000 (H1) | 1 | 0 | 1 |
|  | B: thin handle — genus 1 (WRONG) | BAD | 0.916 | 0.456 | 0.0302 (H1) | 1 | 1 | 1 |
| ii_components | A: two components, scaled (correct) | OK  | 0.628 | 0.536 | 0.0014 (H0) | 2 | 0 | 2 |
|  | B: thin bridge merges them — one component (WRONG) | BAD | 0.628 | 0.357 | 0.0574 (H0) | 1 | 0 | 2 |
| iii_void | A: outward blister — void intact (correct) | OK  | 0.977 | 1.887 | 0.0040 (H2) | 1 | 0 | 1 |
|  | B: punched hole — void destroyed (WRONG) | BAD | 0.977 | 4.375 | 0.1385 (H2) | 1 | 0 | 1 |

## Does each case demonstrate blindness?

A case counts when Chamfer ranks B **equal-or-better** than A, yet the discriminating-dimension bottleneck ranks B clearly worse.

- **i_genus** — disc dim **H1 (loops/handles)**. Chamfer A=0.916%, B=0.916% (Hausdorff95 A=0.481%, B=0.456%); bottleneck→GT B=0.0302 vs A≈0 — the wrong candidate carries a H1 feature the correct one simply does not have. **Blindness demonstrated.**
- **ii_components** — disc dim **H0 (components)**. Chamfer A=0.628%, B=0.628% (Hausdorff95 A=0.536%, B=0.357%); bottleneck→GT **40× larger** for the wrong candidate (A=0.0014, B=0.0574). **Blindness demonstrated.**
- **iii_void** — disc dim **H2 (voids)**. Chamfer A=0.977%, B=0.977% (Hausdorff95 A=1.887%, B=4.375%); bottleneck→GT **35× larger** for the wrong candidate (A=0.0040, B=0.1385). **Blindness demonstrated.**

**Gate: 3/3 cases** show Chamfer-equal-or-inverted while topology separates (requirement: ≥ 1).

### Notes

- Cases (i) and (ii): Hausdorff95 *also* (slightly) prefers the topologically **wrong** candidate B — geometry is not merely tied but inverted.
- Case (iii): a closed shell's enclosed void (H2) only *fully* disappears under a gross hole, because the alpha-complex void fills at the radius scale. With a modest hole the Betti **count** stays 1 for both, but the **bottleneck distance** captures the void's collapsing death-time — the continuous metric is more sensitive than the discrete count. The blister (A) of identical Chamfer leaves the void intact (bottleneck≈0), so Chamfer cannot tell a benign bump from a punctured void.

## Figures

- `pd_i_genus.png` — persistence diagrams (GT / A / B), (i) Genus-0 vs genus-1  (a thin handle)
- `pd_ii_components.png` — persistence diagrams (GT / A / B), (ii) One vs two components  (a spurious bridge)
- `pd_iii_void.png` — persistence diagrams (GT / A / B), (iii) Closed surface vs punctured  (a hole)
- `stability_series.png` — topology stability series: Chamfer drifts smoothly while bottleneck-H1 jumps when a spurious handle becomes significant.
