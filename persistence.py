# topology/persistence.py
# Persistence diagrams (H0/H1/H2) of a 3D shape via an ALPHA COMPLEX (GUDHI).
#
# Why alpha complex: for points sampled on a 2-manifold in R^3 it recovers the
# surface's homology with far fewer simplices than a Vietoris-Rips complex, and
# its filtration value (squared circumradius) is a true length scale — so a
# persistence value is directly comparable to a Chamfer/Hausdorff distance once
# both are normalized by the same bbox diagonal (see src/eval_geometry.py).
#
# This module is MEASUREMENT ONLY (Phase 1). No differentiable persistent
# homology, no guidance, no resampling. It is a leaf module: it depends only on
# numpy / scipy / gudhi (+ optional trimesh, torch for input adapters), never on
# the renderer, so the Phase-2 topology-aware method can import it unchanged.
#
# TWO ENTRY POINTS, kept deliberately distinct (only (b) is used this phase):
#   (a) persistence_from_target(...)          -> future guidance prior  (UNUSED now)
#   (b) persistence_from_reconstruction(...)  -> the metric             (exercised now)
#
# "Significant" features: a persistence interval counts as a real topological
# feature when its lifetime (death - birth) exceeds k x the median
# nearest-neighbour spacing of the sample (both in normalized units). Spacing is
# the natural noise floor of a point sample, so this rule is self-calibrating
# across shapes and densities rather than a hand-set constant. Betti numbers are
# read off as the per-dimension significant counts (the H0 essential class has
# death=inf and always counts).

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional, Union

import numpy as np
from scipy.spatial import cKDTree

import gudhi

# Default significance multiplier (lifetimes above DEFAULT_SIG_K x median spacing
# are "real"). Synthetic shapes have enormous signal-to-noise, so any value in
# ~[4, 10] separates cleanly; calibrated against tests/test_betti.py.
DEFAULT_SIG_K = 6.0

PointsLike = Union[np.ndarray, tuple, list, str, dict, Callable]


# ── result container ─────────────────────────────────────────────────

@dataclass
class PersistenceResult:
    """Per-dimension persistence diagrams in NORMALIZED units (each [birth,death]
    divided by `scale`, the bbox diagonal). H0 carries one essential bar per
    connected component with death=inf."""
    diagrams: dict                      # dim -> (M,2) float [birth, death]
    n_points: int
    scale: float                        # normalizer (bbox diagonal, original units)
    center: np.ndarray                  # sample centroid (bookkeeping / future alignment)
    median_nn: float                    # normalized median nearest-neighbour spacing
    max_dim: int = 2
    meta: dict = field(default_factory=dict)

    def diagram(self, dim: int) -> np.ndarray:
        return self.diagrams.get(dim, np.zeros((0, 2)))

    def significance_threshold(self, k: Optional[float] = None,
                               abs_thr: Optional[float] = None) -> float:
        if abs_thr is not None:
            return float(abs_thr)
        k = DEFAULT_SIG_K if k is None else k
        return float(k * self.median_nn)

    def significant_counts(self, k: Optional[float] = None,
                           abs_thr: Optional[float] = None) -> dict:
        """{dim: number of intervals with lifetime > threshold}."""
        thr = self.significance_threshold(k, abs_thr)
        out = {}
        for d in range(self.max_dim + 1):
            dg = self.diagrams.get(d, np.zeros((0, 2)))
            if len(dg) == 0:
                out[d] = 0
                continue
            life = dg[:, 1] - dg[:, 0]               # inf for essential H0
            out[d] = int(np.sum(life > thr))
        return out

    def betti_numbers(self, k: Optional[float] = None,
                      abs_thr: Optional[float] = None) -> tuple:
        c = self.significant_counts(k, abs_thr)
        return tuple(c.get(d, 0) for d in range(self.max_dim + 1))


# ── alpha-complex persistence ────────────────────────────────────────

def _alpha_diagrams(P: np.ndarray, max_dim: int) -> dict:
    """Raw GUDHI persistence intervals per dimension, in SQUARED-alpha units
    (squared circumradius), original coordinates. Deterministic for fixed P."""
    pts = np.ascontiguousarray(P, dtype=np.float64)
    try:
        ac = gudhi.AlphaComplex(points=pts)
    except TypeError:                                # very old gudhi wants a list
        ac = gudhi.AlphaComplex(points=pts.tolist())
    st = ac.create_simplex_tree()
    st.compute_persistence(persistence_dim_max=False, min_persistence=0.0)
    diags = {}
    for d in range(max_dim + 1):
        arr = np.asarray(st.persistence_intervals_in_dimension(d), dtype=float)
        diags[d] = arr.reshape(-1, 2) if arr.size else np.zeros((0, 2))
    return diags


def _median_nn(P: np.ndarray) -> float:
    if len(P) < 2:
        return 0.0
    d, _ = cKDTree(P).query(P, k=2)
    return float(np.median(d[:, 1]))


def persistence_from_points(P: np.ndarray, *, scale: Optional[float] = None,
                            center=None, max_dim: int = 2,
                            meta: Optional[dict] = None) -> PersistenceResult:
    """Core: persistence diagram of a raw (N,3) point cloud. `scale`/`center`
    let a reconstruction be normalized by the TARGET's bbox diagonal/centroid so
    the two diagrams live in one metric space (mirrors eval_geometry, which
    normalizes both clouds by the reference diagonal)."""
    P = np.ascontiguousarray(np.asarray(P, dtype=np.float64))
    if P.ndim != 2 or P.shape[1] != 3:
        raise ValueError(f"expected (N,3) points, got {P.shape}")
    center = P.mean(axis=0) if center is None else np.asarray(center, dtype=float)
    if scale is None:
        scale = float(np.linalg.norm(P.max(axis=0) - P.min(axis=0)))
    scale = max(float(scale), 1e-12)

    raw = _alpha_diagrams(P, max_dim)
    diags = {}
    for d, arr in raw.items():
        if len(arr) == 0:
            diags[d] = np.zeros((0, 2))
            continue
        birth = np.sqrt(np.clip(arr[:, 0], 0.0, None)) / scale
        death = arr[:, 1].astype(float)
        fin = np.isfinite(death)
        out = np.empty_like(death)
        out[fin] = np.sqrt(np.clip(death[fin], 0.0, None)) / scale
        out[~fin] = np.inf
        diags[d] = np.stack([birth, out], axis=1)

    return PersistenceResult(
        diagrams=diags, n_points=len(P), scale=scale, center=center,
        median_nn=_median_nn(P) / scale, max_dim=max_dim, meta=meta or {},
    )


# ── input adapters ───────────────────────────────────────────────────
#   Accept whatever a "shape" might be in this project: a point cloud, a
#   (V,F) mesh, a mesh file, a DiffSoup checkpoint / trajectory dump, or a
#   thunk(n, rng) -> points. All sampling is seeded -> reproducible.

def _to_points(obj: PointsLike, n_samples: int, seed: int,
               sampler: Optional[Callable] = None) -> np.ndarray:
    from . import meshes                              # local: avoid import cycle
    rng = np.random.default_rng(seed)

    if sampler is not None:
        return np.asarray(sampler(obj, n_samples, rng), dtype=float)

    if isinstance(obj, np.ndarray):
        return np.asarray(obj, dtype=float)

    if callable(obj):                                 # thunk(n, rng) -> (N,3)
        return np.asarray(obj(n_samples, rng), dtype=float)

    if isinstance(obj, (tuple, list)) and len(obj) == 2:   # (V, F)
        V, F = obj
        return meshes.sample_surface(np.asarray(V), np.asarray(F), n_samples, rng)

    if isinstance(obj, dict):                         # checkpoint / trajectory
        return meshes.soup_cloud(obj, n_samples, rng)

    if isinstance(obj, str):
        if obj.endswith(".pt"):
            import torch                              # lazy: only the soup path needs it
            ckpt = torch.load(obj, map_location="cpu", weights_only=False)
            return meshes.soup_cloud(ckpt, n_samples, rng)
        import trimesh                                # lazy: only mesh files need it
        m = trimesh.load(obj, process=False, force="mesh")
        return meshes.sample_surface(np.asarray(m.vertices), np.asarray(m.faces), n_samples, rng)

    raise TypeError(f"cannot turn {type(obj)} into a point cloud")


# ── (a) target entry point — structured now, UNUSED this phase ───────

def persistence_from_target(target: PointsLike, *, n_samples: int = 20_000,
                            seed: int = 0, scale: Optional[float] = None,
                            center=None, max_dim: int = 2,
                            sampler: Optional[Callable] = None) -> PersistenceResult:
    """(a) Persistence diagram of the TARGET / ground-truth shape.

    Purpose: the topological prior a Phase-2 topology-aware resampler would match
    its reconstruction against. Defined and tested now so the API is frozen, but
    NOT used by any Phase-1 metric — Phase 1 only MEASURES reconstructions.

    Kept separate from persistence_from_reconstruction so the two can diverge in
    Phase 2 (the target path will additionally distil a guidance signature; the
    reconstruction path must stay a pure, side-effect-free measurement).
    """
    P = _to_points(target, n_samples, seed, sampler)
    res = persistence_from_points(P, scale=scale, center=center, max_dim=max_dim,
                                  meta={"role": "target", "seed": seed})
    return res


# ── (b) reconstruction entry point — the Phase-1 metric ──────────────

def persistence_from_reconstruction(recon: PointsLike, *, n_samples: int = 20_000,
                                    seed: int = 0, scale: Optional[float] = None,
                                    center=None, max_dim: int = 2,
                                    sampler: Optional[Callable] = None) -> PersistenceResult:
    """(b) Persistence diagram of a RECONSTRUCTION — a candidate mesh, a point
    cloud, or a trained DiffSoup checkpoint/trajectory dump.

    This is the path exercised in Phase 1 by experiments/topology_blindness.py
    and topology/metrics.py. Pass the target's `scale`/`center` to place this
    diagram in the target's normalized metric space before measuring distance.
    """
    P = _to_points(recon, n_samples, seed, sampler)
    res = persistence_from_points(P, scale=scale, center=center, max_dim=max_dim,
                                  meta={"role": "reconstruction", "seed": seed})
    return res
