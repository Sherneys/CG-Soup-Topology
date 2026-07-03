# Phase 2 — Topology-aware Adaptive Resampling: Exploration Report & Plan

**Status: exploration only. Nothing implemented. Awaiting go-ahead.**
Scope guard honored: no differentiable PH, no renderer edits, no reimplementation of
`topology/` or the persistence/metric. Topology enters as a *precomputed sampling bias* only.

---

## 0. Repository map (because `$DIFFSOUP_ROOT` was NOT set)

`$DIFFSOUP_ROOT` is unset in this environment. The pieces live in **three** sibling dirs:

| Path | Role | May I touch it? |
|---|---|---|
| `D:\Project\diffsoup` | **DiffSoup renderer library** — C++/CUDA `_core`, `rasterize.py`, `multires.py`, `remesh.py`, `optimize.py`, `point3d.py`; plus `examples/utils.py` (the resampling *helpers*) | **Renderer/core: NO.** `examples/utils.py` (pure-Python helpers): I will *not edit*, only call/parallel them |
| `D:\Project\CG-Soup-for-Digital-Dentistry` | **The "CG-Soup" repo** = effective `$DIFFSOUP_ROOT`. `src/diffsoup_train.py` (the training loop + resample), `src/eval_geometry.py`, `src/make_synthetic_scene.py`, the **only `.venv` that has gudhi 3.12.0 + POT 0.9.6 + torch-cu128 + diffsoup + trimesh + open3d**, and the synthetic scenes | One small hook seam in `diffsoup_train.py` (see §3) |
| `D:\Project\CG-Soup-Topology` (cwd) | **The `topology/` package** (Phase-1), checked out standalone | Reuse unchanged; add `methods/`, `experiments/` here |

Environment confirmed live: **CUDA RTX 4070 Ti, torch 2.11.0+cu128** → the full sweep can run *here*.
`output/synth/` already contains **`torus`, `sphere`, `fandisk`** scenes (so H1 and H2 targets exist today).

Two import gotchas I verified empirically and will handle in the Phase-2 scripts:
- `import topology` **fails** from this checkout (folder is `CG-Soup-Topology`, not `topology`). `importlib`
  spec-load under the name `topology` **works** (verified: `persistence_from_target` runs, betti=(1,2,1) on a torus).
- All Phase-2 code must run under the **dentistry `.venv`** (the only one with the full stack) and add
  `D:\Project\diffsoup\examples` to `sys.path` (for `import diffsoup` + `from utils import ...`), exactly as
  `diffsoup_train.py:29-30` does.

---

## 1. Where the training loop and adaptive-resampling step live

`src/diffsoup_train.py` → `main()`. The loop is `for i_iter in pbar:` (**lines 390-556**). Geometry is a
**triangle soup**: `V_single` `(3M,3)` verts + `F` `(M,3)` faces (each triangle independent), with per-face
multi-res colour `feat_src` and opacity `alpha_src`. Optimisers: `optimizer_soup` (Adam on feat/alpha),
`optimizer_vert` (`ds.optimize.VectorAdam` on verts), `optimizer_shader` (Adam on the colour MLP).
Photometric loss = `opacity_aux + 0.8·L1 + 0.2·SSIM` (lines 425-447).

**The resample step is one block, every 100 steps, lines 510-535:**

```python
# ── Resample soup ────────────────────────────────────────────
if i_iter % 100 == 0 and i_iter < 9_550:
    with torch.no_grad():
        if F.shape[0] > max_faces:                                  # (A) PRUNE
            alpha_acc = ds.accumulate_to_level(Rmin, Rmax, alpha_src).sigmoid()
            tri_counts = count_visible_triangles(
                (H // 2, W // 2), MVPs, V_single, F,
                level=Rmax, alpha_src=alpha_acc, batch_size=1)
            keep_map = build_keep_map(tri_counts, remove=F.shape[0] - max_faces)
            F = F[keep_map]
            V_single, F = ds.remove_unreferenced_vertices_from_soup(V_single, F)
            feat_src  = ds.expand_by_index(feat_src,  keep_map)
            alpha_src = ds.expand_by_index(alpha_src, keep_map)
        if i_iter < 9_500:                                          # (B) RESPAWN / SPLIT
            alpha_acc = ds.accumulate_to_level(Rmin, Rmax, alpha_src).sigmoid()
            V_single, F, face_map = split_edges_from_training_views(
                (H // 2, W // 2), MVPs, V_single, F, Rmax, alpha_acc,
                tau_ratio=1 / 5, num_views_cap=20)
            feat_src  = ds.expand_by_index(feat_src,  face_map)
            alpha_src = ds.expand_by_index(alpha_src, face_map)
```

Trajectory dumps (`step_*.pt` = `{step, V, F, alpha, init}`) are written **after** the block
(lines 365-371, 554-556) — exactly what `topology.metrics.load_trajectory` reads. Plumbing is already compatible.

---

## 2. How resampling decides prune / keep / respawn — and what drives respawn LOCATION

Both decision functions are in **`diffsoup/examples/utils.py`** (pure Python, *not* the compiled core).

### (A) PRUNE — driven by image-space **visibility**
`count_visible_triangles` (utils.py:445-482) rasterizes every training view and sums, per face, the number
of pixels where that face is the front/visible surface (`ds.count_triangle_ids`, alpha-weighted, `stochastic=False`):

```python
count += ds.count_triangle_ids(rast, F.shape[0])   # per-face pixel wins, summed over all views
```

`build_keep_map` (utils.py:485-490) then keeps everyone **except the `remove` least-visible faces**:

```python
def build_keep_map(counts, remove):
    sorted_idx = torch.argsort(counts, stable=True)
    keep_idx = sorted_idx[remove:]          # drop the `remove` lowest-visibility faces
    keep_idx, _ = torch.sort(keep_idx)
    return keep_idx
```

→ **Prune signal = cumulative screen visibility.** Rarely-seen triangles die first.

### (B) RESPAWN — driven by **screen-space edge length of *visible* triangles**
`split_edges_from_training_views` (utils.py:493-545): pick ≤20 random views; for each, find the **visible**
faces by rasterizing, mark them `valid_faces`, and bisect their **longest screen-space edge** until no edge
exceeds `tau_ratio = 1/5` of the image height:

```python
face_idx = (rast_i[rast_i[..., -1] > 0][..., -1].int() - 1).unique()  # visible faces this view
valid_faces = torch.zeros(num_original_faces, dtype=torch.int32, device=dev)
valid_faces[face_idx] = 1                                             # ← the per-face eligibility lever
valid_faces = valid_faces[fMap].contiguous()
V, F, fMap_next, _ = ds.split_triangle_soup_clip_until(              # renderer core; we never edit it
    (H, W), perm_MVPs[i], V, F, valid_faces, tau_ratio=tau_ratio)
```

`split_triangle_soup_clip` (remesh.py:73-105) measures edge length **in NDC `(x/w, y/w)`, x scaled by `W/H`
(unit = one image height)** and bisects the longest edge. So:

> **Respawn LOCATION is decided purely by "is a *visible* triangle too big on screen in some view?"**
> It is **NOT** gradient magnitude, **NOT** photometric/image-space error, **NOT** world-space geometry or
> curvature. Children spawn at the **midpoint of the longest screen-space edge** of over-large visible faces.

**This is the gap Phase 2 fills:** the baseline respawn has *no notion of where topology is fragile*
(a thin neck between two components, a loop tube, a void shell). The two per-face levers it exposes are
**`valid_faces` (eligibility, per-face)** and **`tau_ratio` (scale, scalar)** for respawn, and the
**`counts` sort key** for pruning. All three are biasable from outside the renderer.

---

## 3. Cleanest injection point — **no renderer/core edits, one small seam**

**Answer: yes, achievable without editing any diffsoup *internals* (the C++/CUDA `_core` or the Python
renderer modules), and without editing `examples/utils.py`.** The respawn/prune *policy* is assembled in the
CG-Soup training script, and the levers (`valid_faces`, `tau_ratio`, the keep-map sort key) are all reachable
through **public `ds.*` APIs** (`rasterize_multires_triangle_alpha`, `count_triangle_ids`,
`split_triangle_soup_clip_until`, `project_vertices`). My topo functions in `methods/` call those directly.

**Recommended seam (≈15 lines, behavior-preserving):** lift the resample block (§1) into a function in
`diffsoup_train.py`:

```python
def resample_soup(V, F, feat_src, alpha_src, MVPs, H, W, Rmin, Rmax, max_faces, i_iter,
                  policy=None):       # policy=None → the EXACT block above (baseline). bit-identical.
    ...
# in main():  V_single, F, feat_src, alpha_src = resample_soup(..., policy=resample_policy)
```

`main()` gains one optional kwarg `resample_policy=None`. `B0` passes `None` (control, untouched code path);
`B1/B2/B3` pass a `TopoResamplePolicy(importance, lambda_topo, mode)` from `methods/topo_resampling.py`.
**At `lambda_topo == 0` the policy delegates verbatim to `build_keep_map` / `split_edges_from_training_views`,
taking the identical code path *and the identical RNG draws*** (critical: the baseline consumes the torch RNG
via `torch.randperm` inside the split — the topo path must add zero extra draws when `lambda_topo == 0`).

*Minimal diff surface:* `src/diffsoup_train.py` only — extract block → function, thread one kwarg. Zero lines
changed in `D:\Project\diffsoup`. I will show the exact diff for approval before applying it.

*Zero-edit alternative (offered, not recommended):* monkeypatch `diffsoup_train.build_keep_map` /
`...split_edges_from_training_views` from the runner. Works, but the keep-map patch can't see `V,F` to compute
per-face importance (the call passes only `counts`), so it needs a side-channel stash — uglier than the seam.

---

## 4. How the budget N is held fixed → budget-neutral by construction

**Budget = `max_faces`** (CLI `--max_faces`, default 15 000). The **prune** enforces it: it fires only when
`F > max_faces` and removes **exactly `F − max_faces`** faces (`build_keep_map(counts, remove=F-max_faces)`),
capping the soup at `max_faces`. Split overshoots; the next prune trims back. The soup **saturates at
`max_faces`** and the count is a shallow sawtooth `[max_faces, max_faces+Δ]`.

**My method stays budget-neutral because it only *reallocates*, never grows, the budget:**
- **Prune lever (exactly neutral):** topo keep-map sorts by `counts + λ·protect·importance(face)` but still
  removes **exactly `remove`** faces → same N, different survivors. (`λ=0` ⇒ returns the baseline call ⇒ bit-exact.)
- **Respawn lever (neutral via the shared cap):** important regions are split to a finer screen scale by an
  extra graduated-`tau` pass (smaller `tau` where `importance` is high, baseline `tau` everywhere — using only
  `valid_faces` masks + scalar `tau`, no per-face-tau renderer change). This adds faces *pre-prune*; the shared
  `max_faces` cap trims them back. Post-prune **N = `max_faces` for every condition.**

Two budget definitions to choose between (see decision A):
- **(Recommended) cap-N:** keep B0 literally unchanged; rely on `max_faces` saturation. N(t) is identical at the
  steady state (`max_faces`); I log per-step face counts and report the (tiny) post-split overshoot to prove parity.
- **(Strict) exact-N:** add a uniform "trim-to-`max_faces` after split" to **all** conditions (incl. a `B0′`) so
  N(t) is *identical at every logged step*. Costs B0′ an infinitesimal deviation from stock baseline.

---

## 5. GUDHI 3.12.0 — representative cycles / generators for the alpha complex?

**Empirically tested against the installed GUDHI 3.12.0 (not from memory):**

- **Representative *cycles* for an alpha complex: NOT available.** `SimplexTree.flag_persistence_generators`
  and `lower_star_persistence_generators` exist but are for **flag/Rips** and **lower-star** filtrations; called
  on an alpha complex they **hard-crash** (segfault — that was a real exit in my probe). So there is no
  per-feature full-cycle chain for alpha.
- **But localization IS available and robust** via **`SimplexTree.persistence_pairs()`** → returns, per
  interval, the **birth simplex and death simplex as vertex-index lists**, and **`AlphaComplex.get_point(v)`**
  maps each vertex to its exact 3D coordinate (verified: input order preserved, `match=True`). This localizes
  every significant feature to a concrete 3D site:

| dim | what dies it | where it localizes (verified on synthetic shapes) |
|---|---|---|
| H1 (loop/handle) | birth = **edge**, death = **triangle** that fills the loop | torus → exactly **2** dominant loops (life 0.63, 0.33) ≫ noise (~0.04); triangles sit on the loop |
| H2 (void) | death = **tetrahedron** filling the void | sphere → **1** void (life 0.46); tetra centroid lies *on the shell* (|c|=R), i.e. **coarse** for H2 |
| H0 (component) | death = **edge** that merges two components | two-spheres → the long finite H0 bar (life 0.70) localizes its edge to **the exact gap midpoint `[0,−0.017,−0.005]`** |

- **Cost:** building the 20 k-point alpha complex = **1.5 s**; reading `persistence_pairs` = **0.02 s**.
  One-time, offline (the field is precomputed from the *fixed* target). **Deterministic** (identical across runs).
- **Conclusion:** `persistence_pairs` + `get_point` is the **primary** localizer — no fallback needed. (A
  deterministic geometric fallback exists if ever required: for synthetic targets the loci are analytically
  known, and generally one can threshold target points by the feature's birth/death filtration scale, or reuse
  `curvature_density.py`. This is also what **B3** uses as its *non-topological* importance.)

### Importance-field construction — two concrete options (deliverable 1)

Both build on `persistence_from_target(...)`, keep only features with normalized lifetime above
`significance_threshold` (`k·median_nn`, the module's self-calibrating rule), and weight each kept feature by
its (normalized) persistence `w_f`. Each feature gets a 3D **center** `c_f` (mean of its birth∪death simplex
points) and a **scale** `σ_f = √death_f` — the feature's own geometric radius (verified: 0.5 = sphere radius,
0.64 = torus-loop radius). The mapping **3D point → scalar weight** is then:

- **Option A — feature-site Gaussian mixture (simplest):**
  `imp(x) = Σ_f w_f · exp(−‖x − c_f‖² / 2σ_f²)`, normalized to [0,1]. A handful of kernels; serializes to a
  tiny `.npz` of `(c_f, σ_f, w_f, dim)`. Cheap, fully deterministic. May under-cover very extended loops.
- **Option B — persistence-weighted splat onto the target surface (recommended):** evaluate the same mixture
  at the **dense target surface samples**, build a `cKDTree`; a query point takes the importance of its nearest
  target sample (or a kernel average). Because `σ_f = √death_f` already spans the feature and the surface
  samples trace it, this **robustly covers the full loop tube / void shell / merge neck** and ties importance to
  the surface the soup must reproduce. Slightly more code; still deterministic and offline.

Per-dimension fields (`imp_H0/H1/H2`) are kept separately so the evaluation can attribute any gain to a
specific homology dimension; the resampler uses their max (or a weighted sum). Query is vectorized over all
face centroids each resample (GPU-friendly).

---

## 6. Proposed implementation plan (after approval)

**Layout** (all under `D:\Project\CG-Soup-Topology`, run with the dentistry `.venv` + diffsoup on path):

1. **`methods/topo_importance.py`** — `build_importance_field(target_mesh, dims, k, option=A|B) → ImportanceField`
   with `field.query(points)→[0,1]` and `field.save/load(npz)`. Built on `persistence_from_target` +
   `persistence_pairs` + `get_point`. Isolated, reusable, documented mapping (§5).
2. **`methods/topo_resampling.py`** — `TopoResamplePolicy(importance, lambda_topo, mode)` implementing the two
   levers (§3–4): importance-protected keep-map + graduated-`tau` respawn. `lambda_topo=0` ⇒ exact baseline.
   `mode ∈ {topo, curvature, random}` so the same machine drives **B3**.
3. **One seam in `src/diffsoup_train.py`** (§3) + flags `--resample_mode`, `--lambda_topo`, `--importance_npz`.
4. **`experiments/topo_resampling_eval.py`** — generalizes `run_a3_traj.py`: drive
   {B0,B1,B2,B3} × {torus(H1), two-spheres(H0), sphere(H2)} × seeds, each `diffsoup_train --traj_dir`, identical
   seed/target/`max_faces`/optimizer/hparams; the **only** difference is the resample policy. (Two-spheres scene
   built once via `make_synthetic_scene` with a custom two-sphere mesh; torus/sphere already exist.)
5. **`experiments/topo_eval_report.py`** — reuse `topology.metrics.topology_stability_series` (vs each target's
   `persistence_from_target` diagram) + `topology.plots`: bottleneck-to-target per relevant dim over training
   (primary), significant Betti over training, Chamfer/Hausdorff parity (`eval_geometry` convention), and a
   markdown summary table.

**Verification protocol (honest; a null result is a valid result):**
- **Cleanliness:** unit test on a tiny CPU soup — at `λ=0` the topo keep-map *and* split masks equal baseline
  element-for-element; and a short `λ=0` GPU run matches B0's face-count trajectory + keep/split decisions.
  (Note: true bit-for-bit *pixels* may be limited by CUDA atomics; I'll assert identical *decisions/RNG/N(t)*,
  which is the meaningful cleanliness claim, and say so plainly.)
- **F1 replication:** B1 (topology once at init) should drift toward B0 by the first resample (~step 100), per
  the A3 finding ("resampling washes out the init concentration in ~100 steps"). Report whether it holds in-loop.
- **Main question:** does **B2** reach **lower & more stable bottleneck-to-target** than **both B0 and B1**, at
  **Chamfer within a stated tolerance of B0**? Does **B3** stay at B0-level topology (showing the gain is
  *topological*, not just "any biased resampling")? Print the table; report even if B2 does **not** win.

**What runs where:** GPU is present, so I can run the whole sweep here. First milestone is a **cheap smoke test**
(torus, B0 vs B2, 1 seed, reduced steps) to prove the seam + cleanliness before the full matrix.

---

## 7. Open decisions for you (then I implement)

A. **Budget definition** — cap-N (B0 untouched, parity at saturation) *[recommended]* vs strict exact-N (uniform
   post-split trim on all incl. B0′).
B. **Importance field** — Option B surface-splat *[recommended]* vs Option A site-Gaussian.
C. **Injection style** — hook-seam refactor of `diffsoup_train.py` *[recommended]* vs zero-edit monkeypatch.
D. **First run** — cheap torus smoke test first *[recommended]* vs straight to the full B0–B3 × 3-shape × multi-seed matrix.
