# experiments/make_crossover_scenes.py
# Generate the NEW synthetic scenes needed by the dimensional-crossover study,
# REUSING the dentistry renderer (src/make_synthetic_scene.py) UNCHANGED via its
# --mesh flag. The analytic meshes are built here from topology/meshes.py (the
# single source of truth that tests/test_betti.py validates), exported to .ply,
# and handed to make_synthetic_scene for COLMAP-scene rendering + gt_mesh.ply.
#
#   double_torus  (genus-2; b0=1,b1=4,b2=1)  -> SDF + marching cubes
#   three_spheres (b0=3)                      -> 3 icospheres concatenated
# (sphere / cube / torus / two_spheres scenes already exist from Phase 1/2;
#  thick_shell is a Betti-only check per the plan, so it gets no render scene.)
#
# Idempotent: skips a scene whose gt_mesh.ply already exists.
#   python experiments/make_crossover_scenes.py [--views 72 --res 256]

from __future__ import annotations

import argparse
import os
import subprocess
import sys

_TOPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _TOPO_ROOT not in sys.path:
    sys.path.insert(0, _TOPO_ROOT)
from methods._paths import load_topology

topology = load_topology()

import numpy as np  # noqa: E402
import trimesh  # noqa: E402

DENTISTRY = os.environ.get("CGSOUP_ROOT", r"D:\Project\CG-Soup-for-Digital-Dentistry")
DIFFSOUP_ROOT = os.environ.get("DIFFSOUP_ROOT", r"D:\Project\diffsoup")
PY = sys.executable                                    # the venv python running this
MK = os.path.join(DENTISTRY, "src", "make_synthetic_scene.py")
SYNTH = os.path.join(DENTISTRY, "output", "synth")
ENV = dict(os.environ, PYTHONUTF8="1", DIFFSOUP_ROOT=DIFFSOUP_ROOT)


def scene_ready(name):
    return os.path.exists(os.path.join(SYNTH, name, "gt_mesh.ply"))


def render_scene(name, mesh_ply, views, res):
    if scene_ready(name):
        print(f"[skip scene] {name} (gt_mesh.ply exists)")
        return
    cmd = [PY, MK, "--mesh", mesh_ply, "--out", os.path.join(SYNTH, name),
           "--views", str(views), "--res", str(res)]
    print("  $", " ".join(cmd))
    if subprocess.run(cmd, env=ENV, cwd=DENTISTRY).returncode != 0:
        raise SystemExit(f"[FAIL] scene render for {name}")


def three_spheres_mesh():
    parts = []
    for cx in (-0.9, 0.0, 0.9):
        s = trimesh.creation.icosphere(subdivisions=4, radius=0.30)
        s.apply_translation([cx, 0.0, 0.0])
        parts.append(s)
    return trimesh.util.concatenate(parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--views", type=int, default=72)
    ap.add_argument("--res", type=int, default=256)
    args = ap.parse_args()
    os.makedirs(SYNTH, exist_ok=True)

    # double_torus (genus-2) — SDF + marching cubes from topology.meshes
    if not scene_ready("double_torus"):
        V, F = topology.meshes.double_torus_mesh()
        ply = os.path.join(SYNTH, "_double_torus_src.ply")
        trimesh.Trimesh(V, F, process=False).export(ply)
        print(f"[mesh] double_torus  {len(V)} verts, {len(F)} faces -> {ply}")
        render_scene("double_torus", ply, args.views, args.res)

    # three_spheres (b0=3)
    if not scene_ready("three_spheres"):
        ply = os.path.join(SYNTH, "_three_spheres_src.ply")
        three_spheres_mesh().export(ply)
        print(f"[mesh] three_spheres -> {ply}")
        render_scene("three_spheres", ply, args.views, args.res)

    print("[done] crossover scenes ready:",
          ", ".join(n for n in ("double_torus", "three_spheres") if scene_ready(n)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
