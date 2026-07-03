# topology/ — Topology-aware Adaptive Resampling (Phase 1: measurement + demo)

Self-contained module for the topology research thread, kept separate from the
main CG-Soup / DiffSoup code (`src/`, `data/`, …). **Phase 1 is measurement-only**:
it computes topology (persistent homology via an alpha complex) to *measure* what
geometric metrics (Chamfer / Hausdorff) miss. No resampling method and no
differentiable persistent homology live here yet — those are Phase 2 / 3.

## Layout

```
topology/
  __init__.py          package surface (import topology)
  persistence.py       persistence diagrams H0/H1/H2 (GUDHI alpha complex); 2 entry points
  metrics.py           Topology Stability Metric (bottleneck/Wasserstein + significant-feature counts)
  meshes.py            deterministic synthetic shapes + seeded samplers (incl. soup/mesh adapters)
  plots.py             persistence-diagram + stability-series plotting
  experiments/
    topology_blindness.py   the demo: 3 controlled cases + table + gate
  tests/
    test_betti.py           Betti recovery (sphere/torus/2-spheres) + determinism
  scripts/
    make_topology_report_docx.py   build the Thai .docx summary
  figures/             generated: pd_*.png, stability_series.png/csv, summary.md, blindness_results.json
  docs/                generated: CG-Soup_Topology_Phase1_TH.docx
```

## Install

```powershell
uv pip install gudhi pot        # both ship Apple-Silicon (macOS arm64) wheels — no compiler needed
```

## Run (deterministic — every sample is seeded)

```powershell
# from the repo root:
.venv\Scripts\python.exe topology\tests\test_betti.py                  # 6/6 PASS
$env:PYTHONUTF8=1 ; .venv\Scripts\python.exe topology\experiments\topology_blindness.py   # table + figures (~40s)
.venv\Scripts\python.exe topology\scripts\make_topology_report_docx.py # Thai .docx into topology/docs/
```

The scripts add the repo root to `sys.path`, so `import topology` resolves wherever
you run them from.

## Result (Phase 1)

Betti recovery passes 6/6. The blindness demo passes **3/3 cases**: A (topology-correct)
and B (topology-wrong) are tuned to **equal Chamfer**, yet the bottleneck distance of
the persistence diagram to ground truth separates them by ~30–40× in the relevant
dimension — and in 2 of 3 cases Hausdorff95 even *prefers* the wrong candidate. See
`figures/summary.md` (English) or `docs/CG-Soup_Topology_Phase1_TH.docx` (Thai).

## Reuse / forward-compat (Phase 2)

- `persistence.persistence_from_target(...)` is defined and API-frozen but **unused** by
  Phase-1 code — it is the topological prior a Phase-2 resampler will match against.
- `metrics.load_trajectory(traj_dir)` ingests the `step_*.pt` dumps that
  `src/diffsoup_train.py --traj_dir` writes, so the stability metric plugs straight onto a
  real DiffSoup run.
- `meshes.soup_cloud(ckpt, …)` samples a DiffSoup checkpoint the same way
  `src/eval_geometry.py` does (alpha × area), so topology and geometry metrics are
  numerically consistent.
