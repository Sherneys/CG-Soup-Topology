# methods/topo_resampling.py
# Phase-2 deliverable 2: a BUDGET-NEUTRAL, topology-aware resampling policy that
# biases DiffSoup's EXISTING prune/respawn with a PRECOMPUTED importance field.
#
# Train-time module: needs only torch + diffsoup (NO gudhi / topology). It reads a
# field .npz produced offline by methods/topo_importance.py and exposes a policy
# object that src/diffsoup_train.py's `resample_soup` seam calls.
#
# TWO LEVERS, one knob `lambda_topo` (lambda_topo = 0 -> EXACT baseline):
#
#   (a) PRUNE PROTECTION — `keep_map`. The baseline keeps everyone but the `remove`
#       least-visible faces. We sort by  visibility + lambda*scale*importance  so
#       important faces are protected, but still remove EXACTLY `remove` faces
#       (argsort drops `remove`) -> budget-neutral by construction.
#
#   (b) RESPAWN REALLOCATION — `densify_and_rebalance`. AFTER the unchanged baseline
#       split (identical across all conditions, same RNG), we (1) add up to `cap`
#       extra triangles by finely subdividing the TOP-importance visible faces, then
#       (2) remove exactly `cap` faces with the protective keep-map. Net face count
#       is UNCHANGED -> exact budget neutrality at every logged step; the effect is a
#       pure trade of low-importance triangles for high-importance subdivisions.
#
# `cap = lambda * split_cap_frac * M`, so lambda is one coherent strength knob:
# 0 = baseline, larger = more reallocation + stronger protection. Eligibility uses a
# RELATIVE (top-fraction) importance threshold, so a field with a high floor (e.g. a
# torus, where most of the surface is topological) still discriminates.
#
# B2 (topology) vs B3 (non-topological control) differ ONLY by which field .npz is
# loaded — the policy is field-agnostic.

from __future__ import annotations

import os
from typing import Optional

import numpy as np
import torch
from scipy.spatial import cKDTree

from . import _paths

_paths.add_diffsoup_path()
import diffsoup as ds              # noqa: E402
from utils import project_vertices  # noqa: E402  (diffsoup examples helper)


# ── lightweight field reader (no gudhi/topology at train time) ───────────

class _Field:
    """Reads the importance .npz written by topo_importance.ImportanceField.save."""

    def __init__(self, path: str):
        z = np.load(path, allow_pickle=False)
        self.points = np.ascontiguousarray(z["points"].astype(np.float64))
        self.importance = z["importance"].astype(np.float64)
        self.by_dim = {int(k.split("_")[-1]): z[k].astype(np.float64)
                       for k in z.files if k.startswith("by_dim_")}
        self._tree = cKDTree(self.points) if len(self.points) else None

    def query(self, X: np.ndarray, dim: Optional[int] = None) -> np.ndarray:
        if self._tree is None:
            return np.zeros(len(X))
        _, idx = self._tree.query(np.ascontiguousarray(X, dtype=np.float64))
        src = self.importance if dim is None else self.by_dim.get(dim, self.importance)
        return src[idx]


# ── the policy ───────────────────────────────────────────────────────────

class TopoResamplePolicy:
    def __init__(self, field_npz: str, lambda_topo: float = 1.0, *,
                 query_dim: Optional[int] = None, protect: bool = True,
                 respawn: bool = True, top_frac: float = 0.34,
                 split_cap_frac: float = 0.5, fine_tau_mult: float = 0.5,
                 protect_quantile: float = 0.9):
        self.field = _Field(field_npz)
        self.lambda_topo = float(lambda_topo)
        self.query_dim = query_dim
        self.protect = protect
        self.respawn = respawn
        self.top_frac = float(top_frac)
        self.split_cap_frac = float(split_cap_frac)
        self.fine_tau_mult = float(fine_tau_mult)
        self.protect_quantile = float(protect_quantile)

    # -- per-face importance in [0,1] on the CURRENT soup --
    def importance_per_face(self, V: torch.Tensor, F: torch.Tensor) -> torch.Tensor:
        cen = V[F.long()].mean(dim=1).detach().cpu().numpy()
        imp = self.field.query(cen, dim=self.query_dim)
        return torch.from_numpy(imp).to(device=V.device, dtype=torch.float32)

    # ── lever (a): importance-protected, exactly-budget-neutral keep-map ──
    def keep_map(self, counts: torch.Tensor, remove: int,
                 V: torch.Tensor, F: torch.Tensor, build_keep_map) -> torch.Tensor:
        if self.lambda_topo == 0.0 or remove <= 0 or not self.protect:
            return build_keep_map(counts, remove)        # exact baseline path
        imp = self.importance_per_face(V, F)
        counts_f = counts.to(torch.float32)
        scale = torch.quantile(counts_f, self.protect_quantile).clamp(min=1.0)
        score = counts_f + self.lambda_topo * scale * imp
        order = torch.argsort(score, stable=True)
        keep = order[remove:]
        keep, _ = torch.sort(keep)
        return keep

    # ── lever (b): add `cap` important subdivisions, then trim `cap` -> net 0 ──
    def densify_and_rebalance(self, resolution, MVPs, V, F, feat_src, alpha_src,
                              Rmin, Rmax, base_tau, num_views_cap,
                              count_visible_triangles, build_keep_map):
        if self.lambda_topo == 0.0 or not self.respawn:
            return V, F, feat_src, alpha_src
        M0 = F.shape[0]
        cap = int(self.lambda_topo * self.split_cap_frac * M0)
        if cap <= 0:
            return V, F, feat_src, alpha_src

        alpha_acc = ds.accumulate_to_level(Rmin, Rmax, alpha_src).sigmoid()
        V, F, dmap = self._densify(resolution, MVPs, V, F, Rmax, alpha_acc,
                                   num_views_cap, base_tau, cap)
        feat_src = ds.expand_by_index(feat_src, dmap)
        alpha_src = ds.expand_by_index(alpha_src, dmap)

        added = F.shape[0] - M0
        if added > 0:                                    # trim exactly `added` -> net 0
            H, W = resolution
            alpha_acc = ds.accumulate_to_level(Rmin, Rmax, alpha_src).sigmoid()
            counts = count_visible_triangles((H, W), MVPs, V, F, level=Rmax,
                                             alpha_src=alpha_acc, batch_size=1)
            keep = self.keep_map(counts, added, V, F, build_keep_map)
            F = F[keep]
            V, F = ds.remove_unreferenced_vertices_from_soup(V, F)
            feat_src = ds.expand_by_index(feat_src, keep)
            alpha_src = ds.expand_by_index(alpha_src, keep)
        return V, F, feat_src, alpha_src

    # finely subdivide the TOP-importance visible faces, bounded by `cap`
    def _densify(self, resolution, MVPs, V, F, Rmax, alpha_acc, num_views_cap,
                 base_tau, cap):
        H, W = resolution
        dev = V.device
        M0 = F.shape[0]
        num_views = MVPs.shape[0]
        perm = torch.randperm(num_views, device=dev)[: min(num_views, num_views_cap)]
        perm_MVPs = MVPs[perm]

        V_clip = project_vertices(V, perm_MVPs)
        rast = ds.rasterize_multires_triangle_alpha(
            (H, W), V_clip, F, Rmax, alpha_acc, stochastic=False)

        imp0 = self.importance_per_face(V, F)            # on the fixed F0
        thr = torch.quantile(imp0, 1.0 - self.top_frac)
        important0 = (imp0 >= thr).to(torch.int32)       # top-importance faces, F0 frame
        fine_tau = base_tau * self.fine_tau_mult

        fMap = torch.arange(M0, device=dev, dtype=torch.long)
        for i in range(perm_MVPs.shape[0]):
            if F.shape[0] - M0 >= cap:
                break
            rast_i = rast[i]
            face_idx = (rast_i[rast_i[..., -1] > 0][..., -1].int() - 1)
            vis0 = torch.zeros(M0, dtype=torch.int32, device=dev)
            if face_idx.numel():
                vis0[face_idx.unique().clamp(min=0)] = 1
            valid0 = vis0 * important0                    # visible AND important (F0)
            valid = valid0[fMap].contiguous()            # -> current F
            if int(valid.sum()) == 0:
                continue
            remaining = cap - (F.shape[0] - M0)
            V, F, fMap_next, _ = ds.split_triangle_soup_clip_until(
                (H, W), perm_MVPs[i], V, F, valid, tau_ratio=fine_tau,
                hard_cap=int(remaining))
            fMap = fMap[fMap_next]
        return V, F, fMap


def make_policy(resample_mode: str, importance_npz: Optional[str],
                lambda_topo: float, **kw) -> Optional["TopoResamplePolicy"]:
    """Factory used by diffsoup_train. resample_mode='baseline' -> None.
    'topo'/'curvature'/'random' all use the same policy on the corresponding field
    .npz (the field encodes which signal it came from)."""
    if resample_mode == "baseline" or not importance_npz:
        return None
    if not os.path.exists(importance_npz):
        raise FileNotFoundError(f"importance field not found: {importance_npz}")
    return TopoResamplePolicy(importance_npz, lambda_topo=lambda_topo, **kw)
