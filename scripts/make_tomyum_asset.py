# scripts/make_tomyum_asset.py
# Build the Thai hot-pot mesh (topology/meshes.tomyum_pot_mesh), certify its
# topology three independent ways, export it as the pipeline source mesh
# (output/synth/_meshes/tomyum_src.ply in the dentistry repo), print the
# density preflight (which loops are significant at which M — the pot is
# DESIGNED to be M-dependent), and render a preview figure.
#
# Certificates (all must pass or the script exits nonzero):
#   1. manifold3d kernel genus() asserted stepwise inside the builder;
#   2. numpy edge certificate: every directed edge unique + every undirected
#      edge shared by exactly 2 faces (closed, edge-manifold, consistently
#      oriented) and Euler characteristic chi = 2 - 2g;
#   3. GUDHI exact simplicial homology on the triangle mesh: b = (1, 2g, 1);
#   4. trimesh cross-check: watertight, winding-consistent, one body.
#
# Run with the dentistry venv (the only one with the full stack):
#   D:\Project\CG-Soup-for-Digital-Dentistry\.venv\Scripts\python.exe `
#       scripts\make_tomyum_asset.py

from __future__ import annotations

import argparse
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


def edge_certificate(V: np.ndarray, F: np.ndarray, genus: int):
    """Closed + edge-manifold + consistently oriented, and chi == 2-2g."""
    d = F[:, [0, 1, 1, 2, 2, 0]].reshape(-1, 2)
    assert len(np.unique(d, axis=0)) == len(d), \
        "duplicate directed edge -> non-manifold or inconsistent winding"
    s = np.sort(d, axis=1)
    su, cnt = np.unique(s, axis=0, return_counts=True)
    assert (cnt == 2).all(), \
        f"not closed: {(cnt != 2).sum()} edges not shared by exactly 2 faces"
    chi = len(V) - len(su) + len(F)
    assert chi == 2 - 2 * genus, f"chi={chi}, expected {2 - 2 * genus}"
    tri = V[F]
    a2 = np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1)
    assert (a2 > 0).all(), "degenerate (zero-area) faces"
    return chi, len(su)


def exact_betti(F: np.ndarray):
    """Exact simplicial homology of the triangle mesh (GUDHI, Z/2)."""
    import gudhi
    st = gudhi.SimplexTree()
    try:
        st.insert_batch(np.ascontiguousarray(F.T, dtype=np.int64), np.zeros(len(F)))
    except AttributeError:                       # very old gudhi: loop insert
        for f in F:
            st.insert([int(f[0]), int(f[1]), int(f[2])])
    st.compute_persistence(homology_coeff_field=2, persistence_dim_max=True)
    return tuple(st.betti_numbers())


def preflight(V: np.ndarray, F: np.ndarray, Ms, seed: int = 0):
    """Alpha-complex significant reading per sample density (k=6 default)."""
    print("\n[preflight] significant Betti vs sample density "
          "(alpha complex, lifetime > 6*r_med):")
    rows = []
    for M in Ms:
        P = meshes.sample_surface(V, F, int(M), np.random.default_rng(seed))
        res = persistence_from_points(P)
        b = res.betti_numbers()
        thr = res.significance_threshold()
        h1 = res.diagram(1)
        life = np.sort(h1[:, 1] - h1[:, 0])[::-1] if len(h1) else np.zeros(0)
        top = ", ".join(f"{x:.4f}" for x in life[:8])
        print(f"  M={int(M):6d}  r_med={res.median_nn:.5f}  floor={thr:.5f}  "
              f"sig b=({b[0]},{b[1]},{b[2]})   top H1 lifetimes: {top}")
        rows.append((int(M), b, float(thr)))
    return rows


def render_preview(V: np.ndarray, F: np.ndarray, path: str):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    def panel(ax, keep, elev, azim, title):
        tri = V[F[keep]]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        L1 = np.array([0.5, 0.7, 0.5]); L1 /= np.linalg.norm(L1)
        L2 = np.array([-0.6, -0.2, -0.3]); L2 /= np.linalg.norm(L2)
        shade = (0.28 + 0.62 * np.clip(n @ L1, 0, None)
                 + 0.22 * np.clip(n @ L2, 0, None)).clip(0, 1)
        albedo = np.array([0.85, 0.80, 0.70])
        col = shade[:, None] * albedo
        pc = Poly3DCollection(tri, facecolors=np.c_[col, np.ones(len(col))],
                              edgecolor="none", zsort="average")
        ax.add_collection3d(pc)
        lo, hi = V.min(axis=0), V.max(axis=0)
        c, r = 0.5 * (lo + hi), 0.55 * (hi - lo).max()
        ax.set_xlim(c[0] - r, c[0] + r)
        ax.set_ylim(c[1] - r, c[1] + r)
        ax.set_zlim(c[2] - r, c[2] + r)
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(elev=elev, azim=azim)
        ax.set_axis_off()
        ax.set_title(title, fontsize=9)

    cen = V[F].mean(axis=1)
    fig = plt.figure(figsize=(11, 10), dpi=130)
    all_f = np.ones(len(F), dtype=bool)
    panel(fig.add_subplot(2, 2, 1, projection="3d"), all_f, 18, -60,
          "tom-yum hot pot - genus 9 (1 chimney + 2 handles + 6 vents)")
    panel(fig.add_subplot(2, 2, 2, projection="3d"), all_f, 72, -90,
          "top: soup moat around the chimney")
    panel(fig.add_subplot(2, 2, 3, projection="3d"), cen[:, 1] < 0.0, 6, 90,
          "cutaway: moat / floor / charcoal chamber / flue")
    panel(fig.add_subplot(2, 2, 4, projection="3d"), all_f, -14, 30,
          "base: pedestal air vents")
    fig.tight_layout()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--handles", type=int, default=2)
    ap.add_argument("--vents", type=int, default=6)
    ap.add_argument("--segments", type=int, default=192)
    ap.add_argument("--out", default=os.path.join(
        DENTISTRY, "output", "synth", "_meshes", "tomyum_src.ply"))
    ap.add_argument("--png", default=os.path.join(ROOT, "figures", "tomyum_pot.png"))
    ap.add_argument("--Ms", type=int, nargs="+", default=[2048, 8192, 20000])
    ap.add_argument("--no-png", action="store_true")
    args = ap.parse_args()

    genus = 1 + args.handles + args.vents
    t0 = time.time()
    Vmm, F = meshes.tomyum_pot_mesh(handles=args.handles, vents=args.vents,
                                    segments=args.segments, normalize=False)
    print(f"[build] {len(Vmm)} verts, {len(F)} faces, genus {genus} "
          f"(kernel-asserted), {time.time() - t0:.1f}s")

    # determinism: an identical second build must be bit-identical
    V2, F2 = meshes.tomyum_pot_mesh(handles=args.handles, vents=args.vents,
                                    segments=args.segments, normalize=False)
    assert np.array_equal(Vmm, V2) and np.array_equal(F, F2), \
        "second build differs -> determinism contract broken"
    print("[build] determinism: second build bit-identical  OK")

    # physical sanity (mm units)
    ext = Vmm.max(axis=0) - Vmm.min(axis=0)
    chi, n_edges = edge_certificate(Vmm, F, genus)
    print(f"[cert ] edge certificate: closed, oriented, edge-manifold; "
          f"chi={chi}=2-2*{genus}  (V={len(Vmm)}, E={n_edges}, F={len(F)})  OK")
    b = exact_betti(F)
    assert b == (1, 2 * genus, 1), f"gudhi betti {b} != (1, {2 * genus}, 1)"
    print(f"[cert ] gudhi exact mesh homology: b={b}  OK")

    import trimesh
    tm = trimesh.Trimesh(Vmm, F, process=False)
    assert tm.is_watertight and tm.is_winding_consistent and tm.body_count == 1
    print(f"[cert ] trimesh: watertight, winding-consistent, 1 body; "
          f"metal volume {tm.volume / 1e6:.3f} L "
          f"(~{tm.volume / 1e3 * 2.7 / 1e3:.2f} kg in aluminium), "
          f"extents {ext[0]:.0f} x {ext[1]:.0f} x {ext[2]:.0f} mm  OK")

    # pipeline-convention normalization (same transform the scene builder uses;
    # positive uniform scale+shift preserves the canonical ordering)
    V = Vmm - 0.5 * (Vmm.min(axis=0) + Vmm.max(axis=0))
    V /= np.linalg.norm(V, axis=1).max()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    trimesh.Trimesh(V, F, process=False).export(args.out)
    print(f"[out  ] {args.out}")

    preflight(V, F, args.Ms)

    if not args.no_png:
        t1 = time.time()
        render_preview(V, F, args.png)
        print(f"[out  ] {args.png}  ({time.time() - t1:.1f}s)")

    print("\nALL CHECKS PASSED")


if __name__ == "__main__":
    main()
