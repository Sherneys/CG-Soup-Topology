# scripts/floor_sensitivity.py
# Round-5 revision-list R6 ("the 6*r_med floor looks arbitrary"):
# re-analysis only, no training. For every shape in the study, sample its
# scene GT at the shape's PROTOCOL bundle density (seed 0 — the
# ensure_bundle convention), recompute all H1/H2 lifetimes, and report for
# each documented bundle decision (feature IN the bundle vs EXCLUDED as
# sub-floor) the multiplier window over which that decision is unchanged:
#   a feature with margin m = lifetime / (6 r_med) stays IN  while k < 6m
#   an excluded feature with margin m           stays OUT while k > 6m
# The study's every decision is invariant over the intersection window,
# printed last. Also times the persistence step (the refresh's dominant
# cost) at M in {2048, 4096, 8192, 20000} on the torus cloud.
#
#   $env:PYTHONPATH = "D:\Project\CG-Soup-Topology\tools\gudhi311"
#   python scripts\floor_sensitivity.py

from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from methods._paths import load_topology  # noqa: E402

load_topology()
from topology import meshes  # noqa: E402
from topology.persistence import persistence_from_points  # noqa: E402

DENTISTRY = os.environ.get("CGSOUP_ROOT", r"D:\Project\CG-Soup-for-Digital-Dentistry")
OUT = os.path.join(ROOT, "output", "floor_sensitivity.json")

# shape -> (bundle M, decisions). Decision = (dim, rank[0-based, by
# lifetime], "in"/"out", label). Encodes the documented protocol:
# tab:main/tab:gen bundles + the printed exclusions (torus void, double
# torus loops 3-4 + void, rocker-arm loop 2 + void, kinkin loops, bowl rims).
PROTOCOL = {
    "sphere":       (2048, [(2, 0, "in", "void")]),
    "cube":         (2048, [(2, 0, "in", "void")]),
    "torus":        (2048, [(1, 0, "in", "loop 1"), (1, 1, "in", "loop 2"),
                            (2, 0, "out", "void")]),
    "two_spheres":  (2048, [(2, 0, "in", "void A"), (2, 1, "in", "void B")]),
    "double_torus": (2048, [(1, 0, "in", "loop 1"), (1, 1, "in", "loop 2"),
                            (1, 2, "out", "tube loop 3"),
                            (1, 3, "out", "tube loop 4")]),
    "spot":         (2048, [(2, 0, "in", "void")]),
    "bob":          (2048, [(1, 0, "in", "loop 1"), (1, 1, "in", "loop 2"),
                            (2, 0, "in", "void")]),
    "fandisk":      (2048, [(2, 0, "in", "void")]),
    "kinkin":       (8192, [(2, 0, "in", "flue void"),
                            (1, 0, "out", "top H1 (all sub-floor)")]),
    "rockerarm":    (2048, [(1, 0, "in", "shaft loop"),
                            (1, 1, "out", "loop 2"), (2, 0, "out", "void")]),
    "eight":        (8192, [(1, 0, "in", "loop 1"), (1, 1, "in", "loop 2"),
                            (1, 2, "in", "loop 3"), (1, 3, "in", "loop 4"),
                            (2, 0, "in", "void")]),
    "armadillo":    (2048, [(2, 0, "in", "void")]),
    "horse":        (2048, [(2, 0, "in", "void")]),
    "bowl_narrow":  (2048, [(2, 0, "in", "chamber"), (1, 0, "out", "rim H1")]),
    "bowl_wide":    (2048, [(2, 0, "in", "chamber"), (1, 0, "out", "rim H1")]),
}


def gt_cloud(shape: str, M: int):
    import trimesh
    p = os.path.join(DENTISTRY, "output", "synth", shape, "gt_mesh.ply")
    m = trimesh.load(p, force="mesh", process=False)
    V = np.asarray(m.vertices, dtype=np.float64)
    F = np.asarray(m.faces, dtype=np.int64)
    return meshes.sample_surface(V, F, int(M), np.random.default_rng(0))


def main():
    rows = {}
    k_lo_bound, k_hi_bound = 0.0, float("inf")
    binder_lo, binder_hi = None, None
    for shape, (M, decisions) in PROTOCOL.items():
        P = gt_cloud(shape, M)
        res = persistence_from_points(P)
        thr = res.significance_threshold()          # = 6 * r_med
        out = []
        for dim, rank, status, label in decisions:
            dg = res.diagram(dim)
            life = np.sort(dg[:, 1] - dg[:, 0])[::-1] if len(dg) else np.zeros(0)
            if rank >= len(life):
                out.append({"dim": dim, "rank": rank, "label": label,
                            "status": status, "margin": 0.0, "flip_k": 0.0})
                continue
            m = float(life[rank] / thr)              # margin at k=6
            flip_k = 6.0 * m                          # decision flips at this k
            out.append({"dim": dim, "rank": rank, "label": label,
                        "status": status, "lifetime": float(life[rank]),
                        "margin_at_6": m, "flip_k": flip_k})
            if status == "in" and flip_k < k_hi_bound:
                k_hi_bound, binder_hi = flip_k, f"{shape} {label}"
            if status == "out" and flip_k > k_lo_bound:
                k_lo_bound, binder_lo = flip_k, f"{shape} {label}"
            print(f"  {shape:13s} H{dim} {label:22s} {status.upper():3s} "
                  f"margin {m:5.2f}x  -> decision holds "
                  f"{'while k < ' if status == 'in' else 'while k > '}{flip_k:.2f}")
        rows[shape] = {"M": M, "r_med": float(res.median_nn),
                       "floor_at_6": float(thr), "decisions": out}

    print(f"\nGLOBAL WINDOW: every documented bundle decision is unchanged "
          f"for k in ({k_lo_bound:.2f}, {k_hi_bound:.2f})")
    print(f"  lower bound set by: {binder_lo} (an excluded feature would enter)")
    print(f"  upper bound set by: {binder_hi} (an included feature would leave)")

    print("\npersistence-step timing on the torus cloud (dominant refresh cost):")
    timing = {}
    for M in (2048, 4096, 8192, 20000):
        P = gt_cloud("torus", M)
        t0 = time.perf_counter()
        persistence_from_points(P)
        dt = time.perf_counter() - t0
        t0 = time.perf_counter()
        persistence_from_points(P)                   # second call = warm
        dt2 = time.perf_counter() - t0
        timing[M] = {"cold_s": dt, "warm_s": dt2}
        print(f"  M={M:6d}  {dt2*1000:8.1f} ms (warm; cold {dt*1000:.1f})")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump({"shapes": rows,
                   "global_window": [k_lo_bound, k_hi_bound],
                   "window_binders": {"lower": binder_lo, "upper": binder_hi},
                   "timing_torus": timing}, fh, indent=2)
    print(f"[out] {OUT}")


if __name__ == "__main__":
    main()
