# scripts/make_kinkin_asset.py
# Ingest the artist-authored tom-yum pot (assets/kinkin.ply, modeled in
# Blender) as the new tomyum-showcase source mesh, replacing the CSG pot for
# the go-forward runs. Unlike tomyum_pot_mesh the input is NOT manifold (raw
# QC: 9 overlapping open shells, 50 boundary edges after weld, 232 non-manifold
# junction edges), so topology cannot be proven by construction. Instead the
# asset is SOLIDIFIED into a thin metal shell and certified by measurement:
#
#   1. parse the binary PLY by hand (mixed quad/12-gon face lists break
#      trimesh's fast path) and fan-triangulate;
#   2. weld exact-duplicate vertices (Blender UV-seam splits);
#   3. offset-solidify: exact unsigned distance field (open3d RaycastingScene)
#      on a padded grid, marching_cubes at iso = eps -> every sheet becomes a
#      wall of thickness 2*eps, exactly the procedural pot's thin-metal regime;
#   4. drop enclosed pocket shells (components strictly inside the main one =
#      internal surfaces of the metal, e.g. the cavities of the two closed
#      slab pieces in the raw model);
#   5. certify, all exact and independent of construction history:
#        a. numpy edge certificate: every directed edge unique, every
#           undirected edge shared by exactly 2 faces (closed, edge-manifold,
#           consistently oriented), no zero-area faces;
#        b. per-component Euler characteristic -> genus; cross-check
#           chi_total = 2k - 2*sum(genus);
#        c. GUDHI exact simplicial homology: b = (k, 2*sum(genus), k);
#        d. trimesh: watertight, winding-consistent, positive volume.
#   6. normalize with the pipeline convention (bbox-centered, max |v| = 1,
#      same as make_synthetic_scene.normalize_mesh) and export;
#   7. density preflight: significant Betti staircase vs M (blind-protocol
#      preview: which cycles clear the 6*r_med floor at which density);
#   8. preview figure (artist mesh + certified shell + cutaway + base).
#
# Run with the dentistry venv (the only one with the full stack):
#   D:\Project\CG-Soup-for-Digital-Dentistry\.venv\Scripts\python.exe `
#       scripts\make_kinkin_asset.py

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


# ── 1. manual PLY parse (Blender binary_little_endian, x y z s t + list) ────

def load_kinkin_ply(path: str):
    buf = open(path, "rb").read()
    head_end = buf.index(b"end_header\n") + len(b"end_header\n")
    header = buf[:head_end].decode("ascii", "replace")
    assert "format binary_little_endian 1.0" in header, header
    nv = int(header.split("element vertex ")[1].split()[0])
    nf = int(header.split("element face ")[1].split()[0])
    n_vprops = header.count("property float")
    vraw = np.frombuffer(buf, dtype="<f4", count=nv * n_vprops,
                         offset=head_end).reshape(nv, n_vprops)
    V = np.ascontiguousarray(vraw[:, :3]).astype(np.float64)
    p = head_end + nv * n_vprops * 4
    tris, sizes = [], []
    for _ in range(nf):
        n = buf[p]; p += 1
        idx = np.frombuffer(buf, dtype="<u4", count=n, offset=p); p += 4 * n
        sizes.append(n)
        for k in range(1, n - 1):                    # fan-triangulate n-gons
            tris.append((idx[0], idx[k], idx[k + 1]))
    assert p == len(buf), f"leftover bytes: {len(buf) - p}"
    F = np.asarray(tris, dtype=np.int64)
    import collections
    hist = dict(sorted(collections.Counter(sizes).items()))
    print(f"[parse] {nv} verts, {nf} faces {hist} -> {len(F)} tris")
    return V, F


def weld(V: np.ndarray, F: np.ndarray):
    """Merge bit-identical vertex positions (Blender UV-seam duplicates)."""
    uq, inv = np.unique(V, axis=0, return_inverse=True)
    F2 = inv[F]
    keep = (F2[:, 0] != F2[:, 1]) & (F2[:, 1] != F2[:, 2]) & (F2[:, 0] != F2[:, 2])
    print(f"[weld ] {len(V)} -> {len(uq)} verts, dropped {int((~keep).sum())} degenerate tris")
    return uq, F2[keep]


# ── 3. offset-solidify: exact unsigned distance + marching cubes ────────────

def solidify(V: np.ndarray, F: np.ndarray, pitch: float, eps: float):
    import open3d as o3d
    from skimage import measure

    scene = o3d.t.geometry.RaycastingScene()
    scene.add_triangles(o3d.core.Tensor(V.astype(np.float32)),
                        o3d.core.Tensor(F.astype(np.uint32)))
    pad = eps + 4.0 * pitch
    lo, hi = V.min(axis=0) - pad, V.max(axis=0) + pad
    axes = [np.arange(lo[k], hi[k] + pitch, pitch) for k in range(3)]
    nx, ny, nz = (len(a) for a in axes)
    print(f"[solid] grid {nx}x{ny}x{nz} = {nx*ny*nz/1e6:.1f}M voxels, "
          f"pitch={pitch}, eps={eps} (wall 2*eps = {2*eps})")
    t0 = time.time()
    vol = np.empty((nx, ny, nz), dtype=np.float32)
    X, Y = np.meshgrid(axes[0], axes[1], indexing="ij")
    for k0 in range(0, nz, 16):                       # z-slabs bound the memory
        k1 = min(k0 + 16, nz)
        zs = axes[2][k0:k1]
        pts = np.stack([np.repeat(X[..., None], len(zs), axis=2),
                        np.repeat(Y[..., None], len(zs), axis=2),
                        np.broadcast_to(zs, (nx, ny, len(zs)))],
                       axis=-1).reshape(-1, 3).astype(np.float32)
        d = scene.compute_distance(o3d.core.Tensor(pts)).numpy()
        vol[:, :, k0:k1] = d.reshape(nx, ny, k1 - k0)
    print(f"[solid] distance field {time.time()-t0:.1f}s")

    mv, mf, _, _ = measure.marching_cubes(vol, level=eps,
                                          spacing=(pitch, pitch, pitch))
    mv = mv + lo
    print(f"[solid] marching_cubes: {len(mv)} verts, {len(mf)} tris")
    return np.asarray(mv, dtype=np.float64), np.asarray(mf, dtype=np.int64)


# ── 4. drop enclosed pocket shells ───────────────────────────────────────────

def drop_internal_shells(mv: np.ndarray, mf: np.ndarray):
    import open3d as o3d
    import trimesh
    m = trimesh.Trimesh(mv, mf, process=True)         # weld mc duplicates
    comps = m.split(only_watertight=False)
    comps = sorted(comps, key=lambda c: -float(c.area))
    main = comps[0]
    scene = o3d.t.geometry.RaycastingScene()          # containment via o3d
    scene.add_triangles(
        o3d.core.Tensor(np.asarray(main.vertices, dtype=np.float32)),
        o3d.core.Tensor(np.asarray(main.faces, dtype=np.uint32)))
    kept, dropped = [main], 0
    for c in comps[1:]:
        probe = np.asarray(c.vertices[[0]], dtype=np.float32)
        inside = bool(scene.compute_occupancy(o3d.core.Tensor(probe)).numpy()[0])
        if inside:
            dropped += 1                              # internal metal surface
        else:
            kept.append(c)                            # genuinely separate body
    out = trimesh.util.concatenate(kept) if len(kept) > 1 else main
    trimesh.repair.fix_normals(out, multibody=True)
    print(f"[shell] components: {len(comps)} -> kept {len(kept)}, "
          f"dropped {dropped} enclosed pocket shell(s)")
    return out, len(comps), dropped


# ── 5. certificates (structural; b measured, then triple cross-checked) ─────

def certify(mesh) -> dict:
    import trimesh
    V = np.asarray(mesh.vertices, dtype=np.float64)
    F = np.asarray(mesh.faces, dtype=np.int64)

    # 5a. numpy edge certificate
    d = F[:, [0, 1, 1, 2, 2, 0]].reshape(-1, 2)
    assert len(np.unique(d, axis=0)) == len(d), \
        "duplicate directed edge -> non-manifold or inconsistent winding"
    s = np.sort(d, axis=1)
    su, cnt = np.unique(s, axis=0, return_counts=True)
    assert (cnt == 2).all(), \
        f"not closed: {(cnt != 2).sum()} edges not shared by exactly 2 faces"
    tri = V[F]
    a2 = np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1)
    assert (a2 > 0).all(), "degenerate (zero-area) faces"
    chi = len(V) - len(su) + len(F)

    # 5b. per-component genus
    comps = mesh.split(only_watertight=False)
    genera = []
    for c in sorted(comps, key=lambda c: -float(c.area)):
        cchi = c.euler_number
        assert cchi % 2 == 0, f"component chi {cchi} odd"
        g = (2 - cchi) // 2
        genera.append(g)
        print(f"[cert ] component: V={len(c.vertices)} F={len(c.faces)} "
              f"chi={cchi} genus={g}")
    k, G = len(genera), int(sum(genera))
    assert chi == 2 * k - 2 * G, f"chi={chi} != 2*{k}-2*{G}"
    print(f"[cert ] edge certificate: closed, oriented, edge-manifold; "
          f"chi={chi}=2*{k}-2*{G}  (V={len(V)}, E={len(su)}, F={len(F)})  OK")

    # 5c. GUDHI exact simplicial homology
    import gudhi
    st = gudhi.SimplexTree()
    st.insert_batch(np.ascontiguousarray(F.T, dtype=np.int64), np.zeros(len(F)))
    st.compute_persistence(homology_coeff_field=2, persistence_dim_max=True)
    b = tuple(st.betti_numbers())
    assert b == (k, 2 * G, k), f"gudhi betti {b} != ({k}, {2*G}, {k})"
    print(f"[cert ] gudhi exact mesh homology: b={b}  OK")

    # 5d. trimesh cross-check
    assert mesh.is_watertight and mesh.is_winding_consistent
    assert mesh.volume > 0, "negative volume -> inverted winding"
    print(f"[cert ] trimesh: watertight, winding-consistent, {k} body(ies), "
          f"volume {mesh.volume:.4f} units^3  OK")
    return {"components": k, "genus_per_component": genera, "genus_total": G,
            "chi": int(chi), "betti": list(b), "verts": len(V), "faces": len(F)}


# ── 7. density preflight (identical convention to make_tomyum_asset) ────────

def preflight(V: np.ndarray, F: np.ndarray, Ms, seed: int = 0):
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


# ── 8. preview figure ────────────────────────────────────────────────────────

def display_copy(V: np.ndarray, F: np.ndarray, target: int = 120_000):
    """Visual-only decimation so matplotlib stays tractable; the certified
    asset itself is never decimated."""
    if len(F) <= target:
        return V, F
    import open3d as o3d
    m = o3d.geometry.TriangleMesh(
        o3d.utility.Vector3dVector(V), o3d.utility.Vector3iVector(F))
    m = m.simplify_quadric_decimation(target_number_of_triangles=target)
    return np.asarray(m.vertices), np.asarray(m.triangles)


def render_preview(Vraw, Fraw, V, F, path: str):
    V, F = display_copy(V, F)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    def panel(ax, Vp, Fp, keep, elev, azim, title):
        tri = Vp[Fp[keep]]
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
        lo, hi = Vp.min(axis=0), Vp.max(axis=0)
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
    panel(fig.add_subplot(2, 2, 1, projection="3d"),
          Vraw, Fraw, np.ones(len(Fraw), dtype=bool), 18, -60,
          "kinkin.ply - the artist mesh as modeled (Blender)")
    allf = np.ones(len(F), dtype=bool)
    panel(fig.add_subplot(2, 2, 2, projection="3d"), V, F, allf, 18, -60,
          "certified thin-shell solid (2*eps metal walls)")
    panel(fig.add_subplot(2, 2, 3, projection="3d"), V, F, cen[:, 1] < 0.0,
          6, 90, "cutaway: moat / chimney / pedestal")
    panel(fig.add_subplot(2, 2, 4, projection="3d"), V, F, allf, -14, 30,
          "base: pedestal vents")
    fig.tight_layout()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", default=os.path.join(ROOT, "assets", "kinkin.ply"))
    ap.add_argument("--pitch", type=float, default=0.02,
                    help="voxel pitch in raw-model units (bbox ~3.6x4.2x2.4)")
    ap.add_argument("--eps", type=float, default=0.045,
                    help="offset radius; wall thickness = 2*eps")
    ap.add_argument("--out", default=os.path.join(
        DENTISTRY, "output", "synth", "_meshes", "kinkin_src.ply"))
    ap.add_argument("--png", default=os.path.join(ROOT, "figures", "kinkin_pot.png"))
    ap.add_argument("--Ms", type=int, nargs="+", default=[2048, 8192, 20000, 50000])
    ap.add_argument("--no-png", action="store_true")
    args = ap.parse_args()

    Vr, Fr = load_kinkin_ply(args.src)
    Vw, Fw = weld(Vr, Fr)
    ext = Vw.max(axis=0) - Vw.min(axis=0)
    print(f"[weld ] extents {ext[0]:.3f} x {ext[1]:.3f} x {ext[2]:.3f} units")

    mv, mf = solidify(Vw, Fw, pitch=args.pitch, eps=args.eps)
    mesh, n_mc_comps, n_dropped = drop_internal_shells(mv, mf)
    cert = certify(mesh)
    cert.update(mc_components=n_mc_comps, dropped_internal_shells=n_dropped,
                src_raw={"verts": len(Vr), "tris_after_fan": len(Fr),
                         "welded_verts": len(Vw)})

    # determinism: a second solidify from the same inputs must certify equal
    mv2, mf2 = solidify(Vw, Fw, pitch=args.pitch, eps=args.eps)
    assert np.array_equal(mv, mv2) and np.array_equal(mf, mf2), \
        "second solidify differs -> determinism contract broken"
    print("[build] determinism: second distance-field/mc pass bit-identical  OK")

    # pipeline-convention normalization (same transform the scene builder uses)
    V = np.asarray(mesh.vertices, dtype=np.float64)
    F = np.asarray(mesh.faces, dtype=np.int64)
    V = V - 0.5 * (V.min(axis=0) + V.max(axis=0))
    V /= np.linalg.norm(V, axis=1).max()

    import trimesh
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    trimesh.Trimesh(V, F, process=False).export(args.out)
    print(f"[out  ] {args.out}")
    import json
    meta = dict(cert, src=os.path.basename(args.src),
                pitch=args.pitch, eps=args.eps)
    with open(os.path.splitext(args.out)[0] + "_cert.json", "w") as fh:
        json.dump(meta, fh, indent=2)
    print(f"[out  ] {os.path.splitext(args.out)[0] + '_cert.json'}")

    preflight(V, F, args.Ms)

    if not args.no_png:
        t1 = time.time()
        render_preview(Vw, Fw, V, F, args.png)
        print(f"[out  ] {args.png}  ({time.time()-t1:.1f}s)")

    print("\nALL CHECKS PASSED")


if __name__ == "__main__":
    main()
