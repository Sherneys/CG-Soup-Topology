# experiments/topo_resampling_eval.py
# Phase-2 deliverable 3: the controlled comparison harness.
#
# Drives DiffSoup training under four resampling CONDITIONS that are IDENTICAL in
# everything (seed, target scene, triangle budget N=max_faces, optimizer, steps,
# downscale, batch) EXCEPT the resampling importance:
#
#   B0  baseline DiffSoup resampling (unchanged)                 # control
#   B1  topology importance applied ONCE at init (--topo_init)   # tests F1 washout
#   B2  topology-aware resampling EVERY step (in-loop)           # the proposed method
#   B3  a NON-topological importance in-loop (random / curvature)# isolates "topological"
#
# Targets are synthetic shapes with KNOWN topology and a discriminating dimension:
#   torus       -> H1 (a loop/handle)        b=(1,2,1)
#   two_spheres -> H0 (two components)        b=(2,0,2)
#   sphere      -> H2 (an enclosed void)      b=(1,0,1)
#
# Per shape the importance fields (topo / curvature / random) are precomputed ONCE
# (methods/topo_importance) and reused across conditions & seeds. Each run dumps a
# trajectory (diffsoup_train --traj_dir) in the step_*.pt layout that
# topology.metrics.load_trajectory reads. Resumable (skips finished runs).
#
# Run (smoke):  python experiments/topo_resampling_eval.py --shapes torus \
#                   --seeds 0 --conditions B0 B2 --steps 600 --max_faces 2500
# Run (full):   python experiments/topo_resampling_eval.py --shapes torus two_spheres sphere \
#                   --seeds 0 1 2 --steps 4000 --max_faces 2500

from __future__ import annotations

import argparse
import os
import subprocess
import sys

# bootstrap: TOPO_ROOT on path for `import methods.*`
_TOPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _TOPO_ROOT not in sys.path:
    sys.path.insert(0, _TOPO_ROOT)

DENTISTRY = os.environ.get("CGSOUP_ROOT", r"D:\Project\CG-Soup-for-Digital-Dentistry")
DIFFSOUP_ROOT = os.environ.get("DIFFSOUP_ROOT", r"D:\Project\diffsoup")
PY = os.path.join(DENTISTRY, ".venv", "Scripts", "python.exe")
TRAIN = os.path.join(DENTISTRY, "src", "diffsoup_train.py")
EXP_ROOT = os.path.join(DENTISTRY, "output", "synth", "topo2")

# shape -> discriminating homology dimension (also drives --topo_dim)
# cube/cylinder = extra H2 (void) targets; double_torus/three_spheres/thick_shell
# = dimensional-crossover targets (multi-loop H1 / more H0 components / thick void).
SHAPE_DIM = {"torus": 1, "two_spheres": 0, "sphere": 2, "cube": 2, "cylinder": 2,
             "double_torus": 1, "three_spheres": 0, "thick_shell": 2,
             # Phase-3e generality meshes (external, genus-known, watertight):
             # spot (genus 0) / bob (genus 1) from the Crane model repository
             # (CC0); fandisk (genus 0 CAD) reuses the A-series scene.
             "spot": 2, "bob": 1, "fandisk": 2,
             # Thai signature mesh (topology/meshes.tomyum_pot_mesh): tom-yum
             # hot pot, genus 9 BY CONSTRUCTION (chimney + 2 handles + 6
             # vents); its cloud reads the metal SOLID, and at M=2048 exactly
             # the chimney H1 cycle is significant (seed-robust preflight).
             "tomyum": 1,
             # kinkin: the artist-authored (Blender) tom-yum pot, solidified to
             # a certified thin shell (scripts/make_kinkin_asset.py; 1 body,
             # genus 3, exact b=(1,6,1)). All its loops are sub-floor at every
             # working M; the discriminating feature is the CHIMNEY-WELL VOID
             # (the narrow mouth caps early, so the flue interior reads as a
             # hidden chamber): sig (1,0,1) from M=8192, margin 1.20-1.23x over
             # seeds 0-4, localized on the pot axis. H2 class => N=1200,
             # bundle_n 8192 (floor rule).
             "kinkin": 2}

ENV = dict(os.environ, PYTHONUTF8="1", DIFFSOUP_ROOT=DIFFSOUP_ROOT, TOPO_ROOT=_TOPO_ROOT)


def _run(cmd):
    print("  $", " ".join(str(c) for c in cmd))
    return subprocess.run(cmd, env=ENV, cwd=DENTISTRY).returncode == 0


def scene_dir(shape):
    return os.path.join(DENTISTRY, "output", "synth", shape)


def fields_dir():
    return os.path.join(EXP_ROOT, "fields")


def field_path(shape, kind):
    return os.path.join(fields_dir(), f"{shape}_{kind}.npz")


def spread_kind(spread):
    """Field-kind tag for the SPREAD (B4) topo field, encoding s so different
    spread scales don't collide on disk (e.g. 'topo_spread3')."""
    return f"topo_spread{spread:g}"


def b5_kind(spread):
    """Field-kind tag for the width-matched NON-topological control (B5): random
    blobs widened to B4's spread sigma (e.g. 'random_spread3')."""
    return f"random_spread{spread:g}"


# ── precompute importance fields (once per shape) ────────────────────────

def ensure_fields(shape, conditions, b3_mode, spread=3.0, rebuild=False):
    """Build ONLY the importance fields the requested conditions need (in-process,
    needs gudhi). B1/B2 -> concentrated topo field; B4 -> spread topo field
    (spread=s, mass-preserving); B3 -> non-topological control field."""
    from methods import topo_importance as ti

    os.makedirs(fields_dir(), exist_ok=True)
    gt = os.path.join(scene_dir(shape), "gt_mesh.ply")
    if not os.path.exists(gt):
        raise FileNotFoundError(
            f"missing target mesh: {gt} "
            f"(run make_synthetic_scene / experiments/make_crossover_scenes for {shape})")

    if any(c in ("B1", "B2") for c in conditions):
        p = field_path(shape, "topo")
        if rebuild or not os.path.exists(p):
            print(f"[field] {shape} topo (concentrated, s=1) …")
            ti.build_importance_field(gt, n_persist=20_000, n_field=60_000, seed=0).save(p)

    if any(c in ("B4", "B5") for c in conditions):
        p = field_path(shape, spread_kind(spread))
        if rebuild or not os.path.exists(p):
            print(f"[field] {shape} topo SPREAD s={spread:g} (mass-preserving) …")
            ti.build_importance_field(gt, n_persist=20_000, n_field=60_000, seed=0,
                                      spread=spread).save(p)

    if "B5" in conditions:                       # width-matched non-topological control
        p = field_path(shape, b5_kind(spread))
        if rebuild or not os.path.exists(p):
            sf = ti.ImportanceField.load(field_path(shape, spread_kind(spread)))
            feats = [f for f in sf.meta.get("features", []) if f["dim"] == SHAPE_DIM[shape]] \
                    or sf.meta.get("features", [])
            sigma_abs = max((f["sigma"] for f in feats), default=None)
            print(f"[field] {shape} random SPREAD (width-matched to B4, sigma={sigma_abs}) …")
            ti.build_random_field(gt, n_field=60_000, seed=0, sigma_abs=sigma_abs).save(p)

    if "B3" in conditions:
        p = field_path(shape, b3_mode)
        if rebuild or not os.path.exists(p):
            print(f"[field] {shape} {b3_mode} …")
            if b3_mode == "curvature":
                ti.build_curvature_field(gt, n_field=60_000, seed=0).save(p)
            else:
                ti.build_random_field(gt, n_field=60_000, seed=0).save(p)


# ── condition -> diffsoup_train flags ────────────────────────────────────

def condition_flags(cond, shape, lam, b3_mode, dim_override=None, spread=3.0):
    dim = SHAPE_DIM[shape] if dim_override is None else dim_override
    topo_npz = field_path(shape, "topo")
    spread_npz = field_path(shape, spread_kind(spread))
    b3_npz = field_path(shape, b3_mode)
    if cond == "B0":
        return ["--resample_mode", "baseline"]
    if cond == "B1":
        return ["--resample_mode", "topo", "--importance_npz", topo_npz,
                "--lambda_topo", str(lam), "--topo_dim", str(dim), "--topo_init"]
    if cond == "B2":                                    # topology-localized, CONCENTRATED
        return ["--resample_mode", "topo", "--importance_npz", topo_npz,
                "--lambda_topo", str(lam), "--topo_dim", str(dim)]
    if cond == "B4":                                    # topology-localized, SPREAD (==B2 but spread field)
        return ["--resample_mode", "topo", "--importance_npz", spread_npz,
                "--lambda_topo", str(lam), "--topo_dim", str(dim)]
    if cond == "B5":                                    # NON-topological control width-matched to B4 (random @ B4 sigma)
        return ["--resample_mode", "random", "--importance_npz", field_path(shape, b5_kind(spread)),
                "--lambda_topo", str(lam)]
    if cond == "B3":                                    # non-topological control
        return ["--resample_mode", b3_mode, "--importance_npz", b3_npz,
                "--lambda_topo", str(lam)]
    raise ValueError(cond)


def traj_schedule(steps):
    base = [0, 50, 100, 150, 200, 300, 400, 600, 800, 1200, 1600, 2000, 3000,
            4000, 6000, 8000, 10000]
    keep = [s for s in base if s <= steps]
    if steps not in keep:
        keep.append(steps)
    return ",".join(str(s) for s in keep)


# ── main sweep ───────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--shapes", nargs="+", default=["torus", "two_spheres", "sphere"])
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    ap.add_argument("--conditions", nargs="+", default=["B0", "B1", "B2", "B3"])
    ap.add_argument("--lambda_topo", type=float, default=1.0)
    ap.add_argument("--b3_mode", choices=["random", "curvature"], default="random")
    ap.add_argument("--steps", type=int, default=4000)
    ap.add_argument("--downscale", type=int, default=1)
    ap.add_argument("--max_faces", type=int, default=2500)
    ap.add_argument("--batch_size", type=int, default=4)
    ap.add_argument("--init", default="random", choices=["random", "curvature"])
    ap.add_argument("--rebuild_fields", action="store_true")
    ap.add_argument("--exp_name", default="topo2", help="output subdir under output/synth/")
    ap.add_argument("--topo_dim", type=int, default=-999,
                    help="override discriminating dim for the topo field (-1 = combined; -999 = per-shape default)")
    ap.add_argument("--spread", type=float, default=3.0,
                    help="B4 spread scale s (mass-preserving kernel widen factor; B4 = topo-localized but SPREAD)")
    args = ap.parse_args()
    dim_override = None if args.topo_dim == -999 else args.topo_dim

    global EXP_ROOT
    EXP_ROOT = os.path.join(DENTISTRY, "output", "synth", args.exp_name)
    os.makedirs(EXP_ROOT, exist_ok=True)
    sched = traj_schedule(args.steps)

    for shape in args.shapes:
        # fields needed only if a non-baseline condition is requested
        if any(c != "B0" for c in args.conditions):
            ensure_fields(shape, args.conditions, args.b3_mode,
                          spread=args.spread, rebuild=args.rebuild_fields)
        scene = scene_dir(shape)
        for cond in args.conditions:
            for s in args.seeds:
                tag = f"{shape}_{cond}_s{s}"
                traj = os.path.join(EXP_ROOT, tag)
                done = os.path.join(traj, f"step_{args.steps:05d}.pt")
                if os.path.exists(done):
                    print(f"[skip] {tag}")
                    continue
                cmd = [PY, TRAIN, "--scene_root", scene,
                       "--downscale", str(args.downscale), "--max_faces", str(args.max_faces),
                       "--steps", str(args.steps), "--batch_size", str(args.batch_size),
                       "--seed", str(s), "--init", args.init,
                       "--out_dir", os.path.join(EXP_ROOT, "_train", tag),
                       "--traj_dir", traj, "--traj_schedule", sched]
                if args.init == "curvature":
                    cmd += ["--init_npz", os.path.join(scene, "curv_init.npz")]
                cmd += condition_flags(cond, shape, args.lambda_topo, args.b3_mode,
                                       dim_override, spread=args.spread)
                print(f"[run ] {tag}")
                if not _run(cmd):
                    print(f"[FAIL] {tag} — stopping")
                    return 1
    print("\n[done] all runs complete. Next: experiments/topo_eval_report.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
