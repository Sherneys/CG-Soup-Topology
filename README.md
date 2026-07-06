# CG-Soup-Topology

The topology research thread of the CG-Soup / DiffSoup project, checked out as a
standalone repo. It asks one question about differentiable triangle-soup
reconstruction: **can a topological prior fix the topology that photometric
gradients miss — and what shape should that prior have?** The repo contains the
full thread: the measurement harness (Phase 1), the topology-aware resampling
method and its controlled experiments (Phase 2 / 2b), and the paper draft.

**Paper:** *Concentrate or Spread? Shaping Topological Resampling Priors for
Differentiable Triangle-Soup Reconstruction* — prebuilt at `paper/main.pdf`
(rebuild with `latexmk -pdf main.tex` inside `paper/`). Author notes, grounding
log, and open items: `NOTES_FOR_AUTHOR.md`.

## The story in four results

1. **Geometric metrics are topology-blind (Phase 1).** In 3/3 controlled cases,
   candidate reconstructions tuned to *equal Chamfer* but different topology
   (genus / connectivity / enclosed void) are separated ~30–40× by the
   persistence-diagram bottleneck distance — and in 2 of 3 cases Hausdorff95
   *prefers* the topologically wrong candidate. See `figures/summary.md`.
2. **An init-only bias washes out.** A topological bias applied once at
   initialization (condition B1) is erased by the first resampling step —
   topological guidance must be **in-loop**.
3. **Topology-aware in-loop resampling wins — but only for voids (Phase 2).**
   The method: precompute an importance field from the target (persistence pairs
   localized via GUDHI, splatted on the surface), use it to bias where new
   triangles respawn and which are protected from pruning. Budget-neutral, one
   knob `lambda_topo`, and `lambda_topo=0` reduces exactly to the baseline. The
   concentrated field (B2) gives a genuine *topology-specific* win for enclosed
   voids (H2: sphere / cube / cylinder — beats baseline **and** the
   non-topological control at Chamfer parity), is null for components (H0), and
   backfires on loops (H1) at tight budgets by manufacturing phantom handles.
4. **No dimensional crossover — spread, don't concentrate (Phase 2b).** A
   mass-preserving width knob interpolates between the *concentrated* prior (B2)
   and the same mass *spread* over the feature's support (B4). Spread is at
   least as good at every feature dimension and strictly better for voids and
   loops: for voids it cuts bottleneck-to-target **33–53% below baseline** at
   Chamfer parity. But a width-matched non-topological control (B5) recovers
   most of that gain — **the value-add is width, not topological targeting**,
   leaving only a small, shape-dependent topological residual for voids. That
   honest caveat is the paper's thesis.

## Experimental conditions (the vocabulary used everywhere)

| Cond | Importance field | Applied | Isolates |
|------|-----------------|---------|----------|
| B0 | — (baseline DiffSoup resampling) | — | control |
| B1 | topological, concentrated | init only | washout of one-shot bias |
| B2 | topological, concentrated (σ = √death) | in-loop | the Phase-2 method |
| B3 | non-topological (random / curvature) | in-loop | "is *topological* doing anything?" |
| B4 | topological, spread (σ → s·σ, mass-preserving) | in-loop | concentrate vs spread |
| B5 | non-topological, width-matched to B4 | in-loop | "is it just *width*?" |

## Layout

```
persistence.py  metrics.py  meshes.py  plots.py     Phase-1 measurement package ("topology"):
                                                    persistence diagrams (alpha complex), stability
                                                    metric, deterministic shapes, plotting
methods/
  _paths.py            import shim (see below) + sibling-repo roots
  topo_importance.py   importance field: persistence localization -> surface splat; spread knob
  topo_resampling.py   TopoResamplePolicy: protected keep-map + budget-neutral densify
  topological_loss.py  Phase 3: differentiable persistence loss (pair-frozen
                       circumradius backward, matched-Wasserstein + recruitment)
experiments/
  topology_blindness.py      Phase-1 demo: 3 controlled cases + table + gate (standalone)
  topo_resampling_eval.py    B0..B5 sweep harness driving diffsoup_train (needs siblings + CUDA)
  topo_eval_report.py        tables + plots: bottleneck-to-target, Betti, Chamfer parity
  dimensional_crossover.py   Phase-2b orchestrator (feature-dim x concentrate/spread)
  crossover_report.py        Phase-2b analysis
  make_crossover_scenes.py   builds the Phase-2b COLMAP scenes
tests/test_betti.py    9/9: Betti recovery on 6 deterministic shapes + determinism checks
tests/test_topo_loss.py  10/10: Phase-3 stage-3a gate (gradchecks, alpha-complex
                       assumption gates, defect-repair toys -> figures/phase3_toy/)
scripts/               builders for the Thai .docx reports (Phase 1 & 2)
paper/                 LaTeX sources, sections/, figures/, refs.bib, prebuilt main.pdf
figures/  docs/        Phase-1 outputs; Thai reports (CG-Soup_Topology_Phase{1,2}_TH.docx)
```

Status documents: `PHASE2_EXPLORATION_AND_PLAN.md` (design + injection-point
exploration), `PHASE2_STATUS.md` (implementation + full-sweep results),
`PHASE2B_CROSSOVER.md` (spread-vs-concentrate experiment), `PHASE3_PLAN.md`
(differentiable topological loss: plan + stage-3a gate results),
`NOTES_FOR_AUTHOR.md` (paper-level narrative and checklist).

## Import quirk (standalone checkout)

The package is written to be imported as `topology`, but this repo's folder is
named `CG-Soup-Topology`, so a plain `import topology` fails here. Use the shim:

```python
from methods._paths import load_topology
load_topology()            # registers this dir under the name "topology"
from topology import meshes, persistence
```

Every script in the repo already goes through it.

## Sibling repos (training sweeps only)

Measurement, tests, the blindness demo, and the paper are self-contained. The
B0–B5 *training* sweeps drive the real DiffSoup optimizer and expect two sibling
checkouts, located via env vars (defaults in parentheses):

- `DIFFSOUP_ROOT` (`D:\Project\diffsoup`) — the differentiable rasterizer
  library. Never modified by this work.
- `CGSOUP_ROOT` (`D:\Project\CG-Soup-for-Digital-Dentistry`) — the training
  repo: `src/diffsoup_train.py` (which carries the non-invasive
  `resample_soup(..., policy=None)` hook and the `--resample_mode /
  --lambda_topo / --importance_npz / --topo_init / --topo_dim` flags),
  `src/make_synthetic_scene.py`, prebuilt `output/synth/*` scenes, and the
  `.venv` the harness invokes (needs gudhi, POT, torch + CUDA, diffsoup,
  trimesh, open3d).

## Run

Standalone (any Python ≥3.11 with `numpy scipy gudhi pot matplotlib scikit-image`):

```powershell
python tests\test_betti.py                                     # 9/9 PASS, fully seeded
$env:PYTHONUTF8=1; python experiments\topology_blindness.py    # Phase-1 demo (~40 s)
python scripts\make_topology_report_docx.py                    # Thai Phase-1 .docx (python-docx)
```

Training sweeps (sibling repos + CUDA GPU; hours):

```powershell
# Phase-2 sweep: shapes x conditions x seeds, resumable
python experiments\topo_resampling_eval.py --shapes sphere cube cylinder `
    --seeds 0 1 2 --conditions B0 B2 B3 --steps 2500 --max_faces 1200
python experiments\topo_eval_report.py                         # tables + figures

# Phase-2b crossover (per-feature-class headroom budgets)
python experiments\dimensional_crossover.py
python experiments\crossover_report.py
```

Reproducibility caveat (documented in `PHASE2_STATUS.md`): resampling
*decisions* are deterministic per seed, but DiffSoup's CUDA rasterizer is not
bit-reproducible run-to-run (atomics), so vertex positions drift slightly —
results are therefore averaged over seeds, and the topology metric samples
soups α×area-weighted to be robust to a few drifting triangles.
