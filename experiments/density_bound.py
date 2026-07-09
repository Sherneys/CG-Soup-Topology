# experiments/density_bound.py
# The measurement floor, quantified (advisor revision item 6 / paper-2
# discussion): a bar is significant iff lifetime > 6 * r_med(M), with r_med
# the sample's median nearest-neighbour spacing (topology.persistence
# DEFAULT_SIG_K = 6). Prints r_med, the floor, and the top H1 lifetimes of
# the GT meshes at the loss density (M=2048) and the eval density (M=20000),
# with margins — the source of the double-torus / torus numbers quoted in
# paper2 §discussion.
#
# Usage: python experiments/density_bound.py [--shapes double_torus torus]
from __future__ import annotations

import argparse
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_TOPO_ROOT = os.path.dirname(_HERE)
for _p in (_HERE, _TOPO_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np

from topo_resampling_eval import scene_dir  # noqa: E402
from methods._paths import load_topology    # noqa: E402

topology = load_topology()


def main() -> int:
    ap = argparse.ArgumentParser(description="significance floor vs density")
    ap.add_argument("--shapes", nargs="+", default=["double_torus", "torus"])
    ap.add_argument("--densities", nargs="+", type=int, default=[2048, 20000])
    ap.add_argument("--dim", type=int, default=1)
    a = ap.parse_args()

    for shape in a.shapes:
        gt = os.path.join(scene_dir(shape), "gt_mesh.ply")
        print(f"== {shape} (H{a.dim}) ==")
        for M in a.densities:
            t = topology.persistence_from_target(gt, n_samples=M, seed=0)
            thr = t.significance_threshold()
            bars = np.asarray(t.diagrams[a.dim]).reshape(-1, 2)
            lifes = sorted((bars[:, 1] - bars[:, 0]).tolist(), reverse=True)[:6]
            n_sig = sum(1 for x in lifes if x > thr)
            print(f"  M={M:6d}  r_med={t.median_nn:.5f}  floor=6*r_med="
                  f"{thr:.5f}  significant: {n_sig}")
            print("           top lifetimes: "
                  + ", ".join(f"{x:.4f} ({x/thr:.2f}x)" for x in lifes[:4]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
