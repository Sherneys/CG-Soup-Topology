# scripts/make_bowl_assets.py
# Open-surface probe assets (OPEN_SURFACE_PROBE_PLAN.md, pre-registered
# 2026-07-17): two open bowls cut from the analytic sphere's GT mesh —
#   bowl_narrow: polar cap removed at opening radius ~0.15 R
#   bowl_wide:   polar cap removed at opening radius ~0.50 R
# Steps here: (1) build + certify-by-measurement with a NUMPY certificate
# (open-surface variant of the kinkin certificate: manifold-with-boundary,
# ONE boundary loop, consistent orientation, Euler characteristic 1);
# (2) export _meshes/bowl_{narrow,wide}_src.ply + cert JSONs;
# (3) run the pre-registered density staircase (M in {2048,4096,8192})
# and PRINT the significant-bar signature per dimension — the floor rule
# (first density where the discriminating feature clears 6*r_med) picks
# the observable and bundle density; this script records, it does not
# decide.
# gudhi: use the SAC-passing 3.11.0 copy (numerically verified identical
# to the recorded 3.12.0 numbers, 2026-07-17):
#   $env:PYTHONPATH = "D:\Project\CG-Soup-Topology\tools\gudhi311"
#   D:\...\CG-Soup-for-Digital-Dentistry\.venv\Scripts\python.exe `
#       scripts\make_bowl_assets.py

from __future__ import annotations

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_TOPO_ROOT = os.path.dirname(_HERE)
for _p in (os.path.join(_TOPO_ROOT, "experiments"), _TOPO_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np
import trimesh

from methods._paths import load_topology  # noqa: E402

DENTISTRY = os.environ.get("CGSOUP_ROOT",
                           r"D:\Project\CG-Soup-for-Digital-Dentistry")
SPHERE_GT = os.path.join(DENTISTRY, "output", "synth", "sphere", "gt_mesh.ply")
MESH_DIR = os.path.join(DENTISTRY, "output", "synth", "_meshes")

BOWLS = {"bowl_narrow": 0.15, "bowl_wide": 0.50}   # opening radius / R
STAIRCASE_M = [2048, 4096, 8192]


def edge_census(F: np.ndarray):
    """Directed-edge census: returns (E_undirected, boundary_edges,
    max_faces_per_edge, orientation_ok)."""
    e_dir = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
    key = e_dir.min(1).astype(np.int64) * (F.max() + 1) + e_dir.max(1)
    uniq, counts = np.unique(key, return_counts=True)
    # orientation: an interior undirected edge must appear once per
    # direction — count directed duplicates
    dkey = e_dir[:, 0].astype(np.int64) * (F.max() + 1) + e_dir[:, 1]
    _, dcounts = np.unique(dkey, return_counts=True)
    orientation_ok = bool((dcounts == 1).all())
    return len(uniq), int((counts == 1).sum()), int(counts.max()), orientation_ok


def boundary_loops(F: np.ndarray) -> int:
    """Count closed loops formed by boundary edges."""
    e_dir = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
    key = e_dir.min(1).astype(np.int64) * (F.max() + 1) + e_dir.max(1)
    uniq, inv, counts = np.unique(key, return_inverse=True,
                                  return_counts=True)
    bmask = (counts == 1)[inv]
    be = e_dir[bmask]
    nxt = {int(a): int(b) for a, b in be}
    loops, seen = 0, set()
    for start in list(nxt):
        if start in seen:
            continue
        loops += 1
        v = start
        while v in nxt and v not in seen:
            seen.add(v)
            v = nxt[v]
    return loops


def build_bowl(mesh: trimesh.Trimesh, open_ratio: float):
    V, F = mesh.vertices.copy(), mesh.faces.copy()
    center = V.mean(0)
    R = float(np.linalg.norm(V - center, axis=1).mean())
    z_cut = center[2] + R * np.cos(np.arcsin(open_ratio))
    keep = V[F].mean(axis=1)[:, 2] < z_cut
    Fk = F[keep]
    used = np.unique(Fk)
    remap = -np.ones(len(V), dtype=np.int64)
    remap[used] = np.arange(len(used))
    return trimesh.Trimesh(vertices=V[used], faces=remap[Fk],
                           process=False), R, center


def main() -> int:
    topology = load_topology()
    os.makedirs(MESH_DIR, exist_ok=True)
    src = trimesh.load(SPHERE_GT, process=False)
    print(f"sphere GT: {len(src.vertices)}v/{len(src.faces)}t")

    for name, ratio in BOWLS.items():
        bowl, R, center = build_bowl(src, ratio)
        V, F = np.asarray(bowl.vertices), np.asarray(bowl.faces)
        E, n_bedges, max_per_edge, orient_ok = edge_census(F)
        loops = boundary_loops(F)
        chi = len(V) - E + len(F)
        bverts_key = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
        # measured opening radius: radial distance of boundary vertices
        ekey = bverts_key.min(1).astype(np.int64) * (F.max() + 1) + bverts_key.max(1)
        uq, inv, cts = np.unique(ekey, return_inverse=True, return_counts=True)
        bvs = np.unique(bverts_key[(cts == 1)[inv]])
        r_open = float(np.linalg.norm((V[bvs] - center)[:, :2], axis=1).mean())

        cert = {
            "source": SPHERE_GT,
            "open_ratio_target": ratio,
            "open_radius_measured_over_R": r_open / R,
            "verts": int(len(V)), "faces": int(len(F)), "edges": int(E),
            "boundary_edges": n_bedges, "boundary_loops": loops,
            "edge_manifold": bool(max_per_edge <= 2),
            "orientation_consistent": orient_ok,
            "euler_characteristic": int(chi),
        }
        ok = (loops == 1 and chi == 1 and cert["edge_manifold"]
              and orient_ok)
        cert["certificate"] = "PASS (disk topology, one designed rim)" if ok \
            else "FAIL"
        out_ply = os.path.join(MESH_DIR, f"{name}_src.ply")
        bowl.export(out_ply)
        with open(os.path.join(MESH_DIR, f"{name}_src_cert.json"), "w") as f:
            json.dump(cert, f, indent=1)
        print(f"\n== {name}: {cert['certificate']} ==")
        for k, v in cert.items():
            if k not in ("source", "certificate"):
                print(f"   {k}: {v}")
        assert ok, f"{name} failed certification"

        # pre-registered staircase (records; the floor rule decides)
        print(f"   staircase ({name}):")
        for M in STAIRCASE_M:
            t = topology.persistence_from_target(out_ply, n_samples=M, seed=0)
            thr = t.significance_threshold()
            sig = []
            for d in (0, 1, 2):
                bars = np.asarray(t.diagrams[d]).reshape(-1, 2)
                fin = bars[np.isfinite(bars[:, 1])]
                lifes = fin[:, 1] - fin[:, 0]
                sig.append(int((lifes > thr).sum()))
            top1 = {}
            for d in (1, 2):
                bars = np.asarray(t.diagrams[d]).reshape(-1, 2)
                fin = bars[np.isfinite(bars[:, 1])]
                lifes = sorted((fin[:, 1] - fin[:, 0]).tolist(), reverse=True)
                top1[d] = (lifes[0] / thr) if lifes else 0.0
            print(f"     M={M:5d} floor={thr:.5f} sig(H0,H1,H2)={tuple(sig)}"
                  f"  top H1={top1[1]:.2f}x floor, top H2={top1[2]:.2f}x")
    print("\nnext (after GPU free): scenes via make_synthetic_scene.py "
          "--shape <name> --mesh <ply> --out output/synth/<name> "
          "--views 48 --res 200")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
