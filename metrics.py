# topology/metrics.py
# Topology Stability Metric for DiffSoup reconstructions.
#
# Given a sequence of reconstructions across training iterations (a list of
# meshes / point clouds / DiffSoup checkpoints, or a traj_dir of step_*.pt dumps
# like src/diffsoup_train.py writes), track PER ITERATION, against a fixed target
# diagram:
#   * bottleneck distance   (recon diagram -> target diagram), per H0/H1/H2
#   * Wasserstein distance  (recon diagram -> target diagram), per H0/H1/H2
#   * count of SIGNIFICANT features per dimension (lifetime over threshold)
# and return the per-iteration time series.
#
# Distances are computed with GUDHI (bottleneck, built-in) and POT-backed
# Wasserstein (gudhi.wasserstein). Diagrams are already in normalized units
# (fraction of the target bbox diagonal), so these distances are directly
# comparable in magnitude to a Chamfer/Hausdorff percentage.
#
# Essential (infinite) bars — one per connected component in H0 — are CAPPED at
# `inf_value` (default 1.0 = the full normalized diagonal) before distance
# computation, the standard way to make persistence distances finite. A change
# in component count then shows up as a clear, bounded jump in bottleneck_H0.
#
# Phase-1 scope: this MEASURES. It does not feed anything back into training and
# does not call the guidance-oriented persistence_from_target(); the reference
# diagram is supplied by the caller (a PersistenceResult) or computed from raw
# points via the neutral core.

from __future__ import annotations

import csv
import glob
import os
from typing import Iterable, Optional, Sequence, Union

import numpy as np

import gudhi
from gudhi.wasserstein import wasserstein_distance

from .persistence import (
    PersistenceResult,
    persistence_from_points,
    persistence_from_reconstruction,
)


# ── diagram distances (with essential-bar capping) ───────────────────

def _prepare(dg: np.ndarray, inf_value: float, prune_eps: float) -> np.ndarray:
    """Make a diagram ready for GUDHI's distance routines: cap infinite deaths
    at `inf_value`, then drop near-diagonal points whose lifetime <= prune_eps.

    Pruning matters for correctness AND speed: an H0 diagram has one point PER
    sample (~tens of thousands), almost all of them spacing-scale noise sitting
    on the diagonal. Bottleneck/Wasserstein are stable under removing points
    within prune_eps of the diagonal (it changes the distance by at most
    prune_eps), and removing tens of thousands of them turns an intractable
    optimal-transport problem into a trivial one. prune_eps is set from the
    sample spacing (a few x median nearest-neighbour), well below any real
    feature, so no genuine topology is discarded."""
    if dg is None or len(dg) == 0:
        return np.zeros((0, 2))
    out = np.asarray(dg, dtype=float).copy()
    out[~np.isfinite(out[:, 1]), 1] = inf_value
    if prune_eps > 0.0:
        out = out[(out[:, 1] - out[:, 0]) > prune_eps]
    return np.ascontiguousarray(out)


def bottleneck_distance(dg_recon: np.ndarray, dg_target: np.ndarray,
                        inf_value: float = 1.0, prune_eps: float = 0.0) -> float:
    """Bottleneck distance between two single-dimension diagrams."""
    a = _prepare(dg_recon, inf_value, prune_eps)
    b = _prepare(dg_target, inf_value, prune_eps)
    return float(gudhi.bottleneck_distance(a, b))


def wasserstein(dg_recon: np.ndarray, dg_target: np.ndarray,
                order: float = 2.0, inf_value: float = 1.0,
                prune_eps: float = 0.0) -> float:
    """Wasserstein-`order` distance between two single-dimension diagrams
    (POT-backed exact EMD; deterministic)."""
    a = _prepare(dg_recon, inf_value, prune_eps)
    b = _prepare(dg_target, inf_value, prune_eps)
    return float(wasserstein_distance(a, b, order=order, internal_p=2.0))


def _auto_prune_eps(recon: PersistenceResult, target: PersistenceResult,
                    prune_frac: float) -> float:
    """A spacing-scaled diagonal band: prune_frac x the coarser of the two
    samples' median nearest-neighbour spacings (normalized units)."""
    return float(prune_frac * max(recon.median_nn, target.median_nn))


def diagram_distances(recon: PersistenceResult, target: PersistenceResult, *,
                      dims: Sequence[int] = (0, 1, 2), order: float = 2.0,
                      inf_value: float = 1.0, prune_eps: Optional[float] = None,
                      prune_frac: float = 2.0) -> dict:
    """All per-dimension bottleneck + Wasserstein distances recon -> target.
    Near-diagonal noise is pruned (prune_eps; auto = prune_frac x median spacing)
    so H0's tens-of-thousands of noise bars don't dominate cost or distance."""
    if prune_eps is None:
        prune_eps = _auto_prune_eps(recon, target, prune_frac)
    out = {"prune_eps": prune_eps}
    for d in dims:
        out[f"bottleneck_H{d}"] = bottleneck_distance(recon.diagram(d), target.diagram(d),
                                                      inf_value, prune_eps)
        out[f"wasserstein_H{d}"] = wasserstein(recon.diagram(d), target.diagram(d),
                                               order, inf_value, prune_eps)
    return out


# ── target normalization helper ──────────────────────────────────────

def _as_target(target: Union[PersistenceResult, np.ndarray], max_dim: int) -> PersistenceResult:
    if isinstance(target, PersistenceResult):
        return target
    # raw points -> neutral core (NOT the guidance persistence_from_target path)
    return persistence_from_points(np.asarray(target), max_dim=max_dim)


# ── the stability time series ────────────────────────────────────────

def topology_stability_series(
    reconstructions: Iterable,
    target: Union[PersistenceResult, np.ndarray],
    *,
    steps: Optional[Sequence[int]] = None,
    n_samples: int = 20_000,
    seed: int = 0,
    k: Optional[float] = None,
    abs_thr: Optional[float] = None,
    dims: Sequence[int] = (0, 1, 2),
    order: float = 2.0,
    inf_value: float = 1.0,
) -> list[dict]:
    """Per-iteration topology stability series.

    reconstructions : ordered iterable of recon objects (mesh / (V,F) / points /
                      checkpoint dict / .pt path) — anything
                      persistence_from_reconstruction accepts.
    target          : a PersistenceResult (preferred) or a raw (N,3) GT cloud.
    Each recon is normalized into the TARGET's metric space (shared scale/center)
    before distances are taken.

    Returns a list of row dicts, one per iteration:
      {step, bottleneck_H0/1/2, wasserstein_H0/1/2, nsig_H0/1/2}
    """
    tgt = _as_target(target, max_dim=max(dims))
    recon_list = list(reconstructions)
    if steps is None:
        steps = list(range(len(recon_list)))

    rows = []
    for step, recon in zip(steps, recon_list):
        res = persistence_from_reconstruction(
            recon, n_samples=n_samples, seed=seed,
            scale=tgt.scale, center=tgt.center, max_dim=max(dims),
        )
        counts = res.significant_counts(k=k, abs_thr=abs_thr)
        row = {"step": int(step)}
        dist = diagram_distances(res, tgt, dims=dims, order=order, inf_value=inf_value)
        row.update({key: round(val, 6) for key, val in dist.items()
                    if key.startswith(("bottleneck_", "wasserstein_"))})
        for d in dims:
            row[f"nsig_H{d}"] = int(counts.get(d, 0))
        rows.append(row)
    return rows


# ── trajectory ingestion (forward-compat with diffsoup_train --traj_dir) ──

def load_trajectory(traj_dir: str) -> tuple[list[int], list[dict]]:
    """Read step_*.pt dumps written by src/diffsoup_train.py (--traj_dir) and
    return (steps, checkpoint_dicts) sorted by step. Each dict carries V, F,
    alpha — consumable directly by persistence_from_reconstruction."""
    import torch                                     # lazy: only this path needs torch
    paths = sorted(glob.glob(os.path.join(traj_dir, "step_*.pt")))
    steps, recons = [], []
    for p in paths:
        d = torch.load(p, map_location="cpu", weights_only=False)
        steps.append(int(d.get("step", len(steps))))
        recons.append(d)
    order = np.argsort(steps)
    steps = [steps[i] for i in order]
    recons = [recons[i] for i in order]
    return steps, recons


# ── CSV writer ───────────────────────────────────────────────────────

def write_series_csv(rows: list[dict], path: str) -> str:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    if not rows:
        return path
    cols = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    return path
