# scripts/make_group_assets.py
# Advisor round-5 follow-up (2026-07-19): "results not diverse — only the
# donut and the tom-yum pot; add two GROUPS and report group means."
# This script ingests a batch of candidate genus-known benchmark meshes for
# the two observable-class groups of the generality wave:
#   loop group (H1, genus >= 1)  — bob's class ("donut-like")
#   void group (H2, genus 0/enclosed chamber) — spot/fandisk/pot's class
#
# Unlike the tom-yum pot (raw artist soup -> solidify), the candidates here
# are supposed to be CLEAN watertight benchmarks (spot/bob/fandisk class):
# no solidification is performed — a mesh that fails the closed-manifold
# certificate is REPORTED AND SKIPPED, never repaired silently, so the wave
# stays "watertight benchmarks, certified" (the pot remains the one
# ingest-and-solidify story).
#
# Per candidate:
#   1. load (trimesh), fan handled by trimesh; weld bit-identical vertices;
#   2. certify — identical machinery to make_kinkin_asset.certify:
#      numpy edge certificate (closed, oriented, edge-manifold),
#      per-component Euler -> genus, GUDHI exact simplicial homology
#      cross-check, trimesh watertight/winding/volume;
#   3. normalize with the pipeline convention (bbox-centered, max|v|=1,
#      = make_synthetic_scene.normalize_mesh) and export
#      <DENTISTRY>/output/synth/_meshes/<key>_src.ply + _cert.json;
#   4. density-staircase preflight (alpha complex, 6*r_med floor) at
#      M in {2048, 4096, 8192, 20000}: per-dim significant counts + top
#      lifetimes -> printed AND stored in the cert json ("staircase"),
#      so the blind-protocol observable/M decision is on the record.
#
# Run (dentistry venv + SAC workaround for gudhi):
#   $env:PYTHONPATH = "D:\Project\CG-Soup-Topology\tools\gudhi311"
#   D:\Project\CG-Soup-for-Digital-Dentistry\.venv\Scripts\python.exe `
#       scripts\make_group_assets.py --src <dir-with-objs> [--only key1 key2]

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from methods._paths import load_topology  # noqa: E402

load_topology()
from topology import meshes  # noqa: E402
from topology.persistence import persistence_from_points  # noqa: E402

DENTISTRY = os.environ.get("CGSOUP_ROOT", r"D:\Project\CG-Soup-for-Digital-Dentistry")


def weld(V: np.ndarray, F: np.ndarray):
    """Merge bit-identical vertex positions (UV/normal-seam duplicates)."""
    uq, inv = np.unique(V, axis=0, return_inverse=True)
    F2 = inv[F]
    keep = (F2[:, 0] != F2[:, 1]) & (F2[:, 1] != F2[:, 2]) & (F2[:, 0] != F2[:, 2])
    if len(uq) != len(V) or (~keep).any():
        print(f"[weld ] {len(V)} -> {len(uq)} verts, "
              f"dropped {int((~keep).sum())} degenerate tris")
    return uq, F2[keep]


def certify(mesh) -> dict:
    """Identical certificate chain to make_kinkin_asset.certify."""
    V = np.asarray(mesh.vertices, dtype=np.float64)
    F = np.asarray(mesh.faces, dtype=np.int64)

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

    comps = mesh.split(only_watertight=False)
    genera = []
    for c in sorted(comps, key=lambda c: -float(c.area)):
        cchi = c.euler_number
        assert cchi % 2 == 0, f"component chi {cchi} odd"
        genera.append((2 - cchi) // 2)
    k, G = len(genera), int(sum(genera))
    assert chi == 2 * k - 2 * G, f"chi={chi} != 2*{k}-2*{G}"
    print(f"[cert ] closed, oriented, edge-manifold; chi={chi}; "
          f"components={k}, genus={genera}")

    import gudhi
    st = gudhi.SimplexTree()
    st.insert_batch(np.ascontiguousarray(F.T, dtype=np.int64), np.zeros(len(F)))
    st.compute_persistence(homology_coeff_field=2, persistence_dim_max=True)
    b = tuple(st.betti_numbers())
    assert b == (k, 2 * G, k), f"gudhi betti {b} != ({k}, {2*G}, {k})"
    print(f"[cert ] gudhi exact mesh homology: b={b}  OK")

    assert mesh.is_watertight and mesh.is_winding_consistent
    assert mesh.volume > 0, "negative volume -> inverted winding"
    return {"components": k, "genus_per_component": genera, "genus_total": G,
            "chi": int(chi), "betti": list(b), "verts": len(V), "faces": len(F)}


def staircase(V: np.ndarray, F: np.ndarray, Ms, seed: int = 0):
    """Per-dim significant counts + floors + top lifetimes across densities."""
    rows = []
    print("[stair] M      r_med    floor    sig b        top H1            top H2")
    for M in Ms:
        P = meshes.sample_surface(V, F, int(M), np.random.default_rng(seed))
        res = persistence_from_points(P)
        b = res.betti_numbers()
        thr = res.significance_threshold()
        tops = {}
        for dim in (1, 2):
            dg = res.diagram(dim)
            life = np.sort(dg[:, 1] - dg[:, 0])[::-1] if len(dg) else np.zeros(0)
            tops[dim] = [float(x) for x in life[:4]]
        t1 = ", ".join(f"{x:.4f}" for x in tops[1]) or "-"
        t2 = ", ".join(f"{x:.4f}" for x in tops[2]) or "-"
        print(f"[stair] {int(M):6d} {res.median_nn:.5f} {thr:.5f} "
              f"({b[0]},{b[1]},{b[2]})   {t1}   {t2}")
        rows.append({"M": int(M), "r_med": float(res.median_nn),
                     "floor": float(thr), "sig_b": list(b),
                     "top_H1": tops[1], "top_H2": tops[2]})
    return rows


def process(path: str, key: str, Ms, out_dir: str) -> dict:
    import trimesh
    print(f"\n=== {key}  ({os.path.basename(path)}) ===")
    m = trimesh.load(path, force="mesh", process=False)
    V = np.asarray(m.vertices, dtype=np.float64)
    F = np.asarray(m.faces, dtype=np.int64)
    print(f"[load ] {len(V)} verts, {len(F)} tris")
    V, F = weld(V, F)
    mesh = trimesh.Trimesh(V, F, process=False)

    try:
        cert = certify(mesh)
    except AssertionError as e:
        print(f"[SKIP ] certificate FAILED: {e}")
        return {"key": key, "src": os.path.basename(path), "status": "failed",
                "reason": str(e)}

    # pipeline-convention normalization (same as make_synthetic_scene)
    V = np.asarray(mesh.vertices, dtype=np.float64)
    F = np.asarray(mesh.faces, dtype=np.int64)
    V = V - 0.5 * (V.min(axis=0) + V.max(axis=0))
    V /= np.linalg.norm(V, axis=1).max()

    out_ply = os.path.join(out_dir, f"{key}_src.ply")
    os.makedirs(out_dir, exist_ok=True)
    trimesh.Trimesh(V, F, process=False).export(out_ply)
    print(f"[out  ] {out_ply}")

    rows = staircase(V, F, Ms)
    meta = dict(cert, key=key, src=os.path.basename(path), status="certified",
                staircase=rows)
    cert_path = os.path.join(out_dir, f"{key}_src_cert.json")
    with open(cert_path, "w") as fh:
        json.dump(meta, fh, indent=2)
    print(f"[out  ] {cert_path}")
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="dir with candidate .obj/.off/.ply")
    ap.add_argument("--only", nargs="*", default=None,
                    help="restrict to these keys (basename sans ext, sanitized)")
    ap.add_argument("--Ms", type=int, nargs="+", default=[2048, 4096, 8192, 20000])
    ap.add_argument("--out", default=os.path.join(
        DENTISTRY, "output", "synth", "_meshes"))
    ap.add_argument("--summary", default=os.path.join(
        ROOT, "output", "group_assets_summary.json"))
    args = ap.parse_args()

    paths = sorted(sum((glob.glob(os.path.join(args.src, pat))
                        for pat in ("*.obj", "*.off", "*.ply")), []))
    results = []
    for p in paths:
        key = os.path.splitext(os.path.basename(p))[0].replace("-", "").replace("_", "").lower()
        if args.only and key not in args.only:
            continue
        try:
            results.append(process(p, key, args.Ms, args.out))
        except Exception as e:  # honest failure, never silent repair
            print(f"[SKIP ] {key}: unexpected failure: {e}")
            results.append({"key": key, "src": os.path.basename(p),
                            "status": "error", "reason": str(e)})

    os.makedirs(os.path.dirname(args.summary), exist_ok=True)
    with open(args.summary, "w") as fh:
        json.dump(results, fh, indent=2)
    print(f"\n[out  ] {args.summary}")
    print("\n=== SUMMARY ===")
    for r in results:
        if r["status"] == "certified":
            b = r["betti"]
            sig = {row["M"]: tuple(row["sig_b"]) for row in r["staircase"]}
            print(f"  {r['key']:14s} genus={r['genus_total']} b=({b[0]},{b[1]},{b[2]}) "
                  f"verts={r['verts']:7d}  sig@2048={sig.get(2048)}  "
                  f"sig@8192={sig.get(8192)}")
        else:
            print(f"  {r['key']:14s} {r['status'].upper()}: {r.get('reason', '')[:70]}")


if __name__ == "__main__":
    main()
