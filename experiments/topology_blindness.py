# experiments/topology_blindness.py
# Phase-1 core demonstration: Chamfer / Hausdorff are TOPOLOGY-BLIND.
#
# For each of three controlled cases we build a ground-truth shape GT and two
# candidate reconstructions:
#     A  — topology CORRECT  (same homology as GT)
#     B  — topology WRONG    (a handle / a merge / a punched void)
# tuned (by bisection on a single geometric parameter) so that A and B have
# essentially EQUAL Chamfer distance to GT. We then show that a topology metric
# (bottleneck distance of each candidate's persistence diagram to GT) cleanly
# SEPARATES A from B in the dimension the defect lives in — separation that no
# geometric metric provides.
#
#   (i)   genus-0 vs genus-1 : a thin handle      -> H1  (b1: 0 -> 1)
#   (ii)  one vs two pieces  : a spurious bridge   -> H0  (b0: 2 -> 1)
#   (iii) closed vs punctured: a hole in the shell -> H2  (void death collapses)
#
# Output table columns (printed + saved):
#   case, candidate, topology-ok?, Chamfer%, Hausdorff95%, bottleneck->GT(disc dim),
#   H0 count, H1 count, H2 count
#
# Determinism: every cloud is seeded; the bisection matcher is a pure function of
# its scalar argument (fresh seeded rng each evaluation), so the whole script is
# reproducible. Geometric metrics mirror src/eval_geometry.py (both clouds
# normalized by the GT bbox diagonal).
#
# Scope: MEASUREMENT ONLY. No resampling method, no differentiable PH.
#
# Run:  $env:PYTHONUTF8=1 ; .venv\Scripts\python.exe experiments\topology_blindness.py

from __future__ import annotations

import csv
import json
import os
import sys

import numpy as np
from scipy.spatial import cKDTree

_TOPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # the topology/ package dir
sys.path.insert(0, os.path.dirname(_TOPO))                            # repo root -> `import topology` resolves

from topology import meshes, metrics, plots
from topology.persistence import persistence_from_points, persistence_from_reconstruction

SEED = 0
N_SAMPLES = 40_000
N_STAB = 20_000                          # samples for the stability sequence
HOLE_HALF_ANGLE = 0.6                    # case (iii) puncture size
OUT_DIR = os.path.join(_TOPO, "figures")
DIMS = (0, 1, 2)


# ── geometric metrics (mirror src/eval_geometry.py conventions) ──────

def geom_metrics(P_recon: np.ndarray, P_ref: np.ndarray) -> dict:
    diag = float(np.linalg.norm(P_ref.max(0) - P_ref.min(0)))
    d_r2ref, _ = cKDTree(P_ref).query(P_recon)
    d_ref2r, _ = cKDTree(P_recon).query(P_ref)
    return {
        "chamfer_pct": float((d_r2ref.mean() + d_ref2r.mean()) / diag * 100),
        "hausdorff95_pct": float(max(np.percentile(d_r2ref, 95), np.percentile(d_ref2r, 95)) / diag * 100),
        "hausdorff_pct": float(max(d_r2ref.max(), d_ref2r.max()) / diag * 100),
    }


def match_chamfer(build, target_pct: float, ref: np.ndarray,
                  lo: float, hi: float, iters: int = 22) -> float:
    """Bisect a scalar parameter so build(x)'s Chamfer to `ref` ~= target_pct.
    `build` must be monotone increasing in Chamfer over [lo, hi]."""
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        c = geom_metrics(build(mid), ref)["chamfer_pct"]
        lo, hi = (mid, hi) if c < target_pct else (lo, mid)
    return 0.5 * (lo + hi)


# ── case construction ────────────────────────────────────────────────

def _rng(s):
    return np.random.default_rng(s)


def build_cases() -> list[dict]:
    cases = []

    # (i) GENUS — blister (correct, b1=0) vs thin handle (wrong, b1=1)
    GT = meshes.sphere_cloud(N_SAMPLES, radius=0.5, rng=_rng(SEED + 1))
    B = meshes.sphere_with_handle_cloud(N_SAMPLES, radius=0.5, attach_angle=0.4,
                                        height=0.30, tube_r=0.03, rng=_rng(SEED + 2))
    tgt = geom_metrics(B, GT)["chamfer_pct"]
    h = match_chamfer(lambda x: meshes.bumped_sphere_cloud(
        N_SAMPLES, radius=0.5, cap_half_angle=0.5, height=x, rng=_rng(SEED + 3)),
        tgt, GT, 0.0, 0.8)
    A = meshes.bumped_sphere_cloud(N_SAMPLES, radius=0.5, cap_half_angle=0.5,
                                   height=h, rng=_rng(SEED + 3))
    cases.append(dict(
        key="i_genus", title="(i) Genus-0 vs genus-1  (a thin handle)", disc=1,
        A_desc="outward blister — genus 0 (correct)",
        B_desc="thin handle — genus 1 (WRONG)", GT=GT, A=A, B=B,
        param=f"blister height={h:.3f} matched to handle"))

    # (ii) COMPONENTS — scaled 2 spheres (correct, b0=2) vs bridged (wrong, b0=1)
    GT = meshes.two_spheres_cloud(N_SAMPLES, radius=0.35, gap=0.5, rng=_rng(SEED + 4))
    B = meshes.bridged_spheres_cloud(N_SAMPLES, radius=0.35, gap=0.5, tube_r=0.04,
                                     rng=_rng(SEED + 5))
    tgt = geom_metrics(B, GT)["chamfer_pct"]
    sc = match_chamfer(lambda x: meshes.scaled(GT, x), tgt, GT, 1.0, 1.06)
    A = meshes.scaled(GT, sc)
    cases.append(dict(
        key="ii_components", title="(ii) One vs two components  (a spurious bridge)", disc=0,
        A_desc="two components, scaled (correct)",
        B_desc="thin bridge merges them — one component (WRONG)", GT=GT, A=A, B=B,
        param=f"GT scaled x{sc:.4f} matched to bridge"))

    # (iii) VOID — blister (correct, void intact) vs hole (wrong, void broken)
    GT = meshes.sphere_cloud(N_SAMPLES, radius=0.5, rng=_rng(SEED + 6))
    B = meshes.sphere_with_hole_cloud(N_SAMPLES, radius=0.5,
                                      hole_half_angle=HOLE_HALF_ANGLE, rng=_rng(SEED + 7))
    tgt = geom_metrics(B, GT)["chamfer_pct"]
    h = match_chamfer(lambda x: meshes.bumped_sphere_cloud(
        N_SAMPLES, radius=0.5, cap_half_angle=HOLE_HALF_ANGLE, height=x, rng=_rng(SEED + 8)),
        tgt, GT, 0.0, 0.9)
    A = meshes.bumped_sphere_cloud(N_SAMPLES, radius=0.5, cap_half_angle=HOLE_HALF_ANGLE,
                                   height=h, rng=_rng(SEED + 8))
    cases.append(dict(
        key="iii_void", title="(iii) Closed surface vs punctured  (a hole)", disc=2,
        A_desc="outward blister — void intact (correct)",
        B_desc="punched hole — void destroyed (WRONG)", GT=GT, A=A, B=B,
        param=f"blister height={h:.3f} matched to hole (half-angle {HOLE_HALF_ANGLE})"))

    return cases


# ── evaluate one case ────────────────────────────────────────────────

def evaluate(case: dict) -> dict:
    GT, A, B = case["GT"], case["A"], case["B"]
    scale = float(np.linalg.norm(GT.max(0) - GT.min(0)))
    center = GT.mean(0)

    rg = persistence_from_points(GT, scale=scale, center=center)        # target diagram
    ra = persistence_from_reconstruction(A, scale=scale, center=center)  # entry point (b)
    rb = persistence_from_reconstruction(B, scale=scale, center=center)

    out = {"key": case["key"], "title": case["title"], "disc": case["disc"],
           "param": case["param"], "betti_gt": rg.betti_numbers(),
           "candidates": {}}
    for name, cloud, res, desc, ok in (
        ("A", A, ra, case["A_desc"], True),
        ("B", B, rb, case["B_desc"], False),
    ):
        g = geom_metrics(cloud, GT)
        dist = metrics.diagram_distances(res, rg, dims=DIMS)
        counts = res.significant_counts()
        out["candidates"][name] = {
            "desc": desc, "topology_ok": ok,
            "chamfer_pct": g["chamfer_pct"], "hausdorff95_pct": g["hausdorff95_pct"],
            "hausdorff_pct": g["hausdorff_pct"],
            "betti": res.betti_numbers(),
            "bottleneck": {d: dist[f"bottleneck_H{d}"] for d in DIMS},
            "wasserstein": {d: dist[f"wasserstein_H{d}"] for d in DIMS},
            "n_sig": {d: counts.get(d, 0) for d in DIMS},
        }
    out["_res"] = {"gt": rg, "A": ra, "B": rb}
    return out


# ── reporting ────────────────────────────────────────────────────────

def _fmt_table(results: list[dict]) -> str:
    hdr = ("| case | candidate | topo | Chamfer% | Hausd95% | bott→GT (disc) "
           "| H0 | H1 | H2 |\n"
           "|------|-----------|------|---------:|---------:|--------------:|---:|---:|---:|")
    lines = [hdr]
    disc_name = {0: "H0", 1: "H1", 2: "H2"}
    for r in results:
        d = r["disc"]
        for name in ("A", "B"):
            c = r["candidates"][name]
            b = c["betti"]
            tag = "OK " if c["topology_ok"] else "BAD"
            case_label = r["key"] if name == "A" else ""
            lines.append(
                f"| {case_label} | {name}: {c['desc']} | {tag} "
                f"| {c['chamfer_pct']:.3f} | {c['hausdorff95_pct']:.3f} "
                f"| {c['bottleneck'][d]:.4f} ({disc_name[d]}) "
                f"| {b[0]} | {b[1]} | {b[2]} |")
    return "\n".join(lines)


def gate_check(results: list[dict], cham_tol: float = 0.03,
               sep_factor: float = 3.0) -> list[dict]:
    """A case 'demonstrates blindness' when Chamfer ranks B equal-or-better than
    A (within cham_tol relative) while the discriminating-dimension bottleneck
    ranks B clearly worse (>= sep_factor x A and a margin above noise)."""
    flags = []
    for r in results:
        d = r["disc"]
        cA = r["candidates"]["A"]; cB = r["candidates"]["B"]
        chamfer_equal_or_inverted = cB["chamfer_pct"] <= cA["chamfer_pct"] * (1 + cham_tol)
        bA, bB = cA["bottleneck"][d], cB["bottleneck"][d]
        topo_separates = (bB >= max(bA * sep_factor, bA + 0.01))
        flags.append({"key": r["key"], "disc": d,
                      "chamfer_A": cA["chamfer_pct"], "chamfer_B": cB["chamfer_pct"],
                      "bott_A": bA, "bott_B": bB,
                      "chamfer_equal_or_inverted": bool(chamfer_equal_or_inverted),
                      "topo_separates": bool(topo_separates),
                      "passes": bool(chamfer_equal_or_inverted and topo_separates)})
    return flags


# ── stability time series (synthetic topology-break sequence) ────────
#   A reconstruction that geometrically drifts away from a sphere by growing a
#   handle. Chamfer rises smoothly; the topology metric stays flat until the
#   handle's loop becomes significant, then jumps — temporal topology-blindness.

def stability_demo() -> list[dict]:
    GT = meshes.sphere_cloud(N_STAB, radius=0.5, rng=_rng(SEED + 20))
    scale = float(np.linalg.norm(GT.max(0) - GT.min(0)))
    center = GT.mean(0)
    target = persistence_from_points(GT, scale=scale, center=center)

    heights = np.linspace(0.02, 0.45, 16)
    recons = [meshes.sphere_with_handle_cloud(
        N_STAB, radius=0.5, attach_angle=0.4, height=float(h), tube_r=0.03,
        rng=_rng(SEED + 30 + i)) for i, h in enumerate(heights)]
    steps = list(range(len(heights)))

    rows = metrics.topology_stability_series(recons, target, steps=steps, dims=DIMS)
    # overlay geometry (Chamfer-to-target) so the plot can contrast it with topology
    for row, cloud, h in zip(rows, recons, heights):
        row["chamfer"] = round(geom_metrics(cloud, GT)["chamfer_pct"], 4)
        row["handle_height"] = round(float(h), 4)
    return rows


# ── main ─────────────────────────────────────────────────────────────

def main() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"[topology-blindness] N={N_SAMPLES} samples/shape, seed={SEED}\n")

    cases = build_cases()
    results = [evaluate(c) for c in cases]

    table = _fmt_table(results)
    print(table + "\n")

    flags = gate_check(results)
    n_pass = sum(f["passes"] for f in flags)
    for f in flags:
        verdict = "PASS" if f["passes"] else "----"
        print(f"  [{verdict}] {f['key']:14s} "
              f"Chamfer A={f['chamfer_A']:.3f}% B={f['chamfer_B']:.3f}% "
              f"(B equal-or-better: {f['chamfer_equal_or_inverted']}) | "
              f"bottleneck H{f['disc']} A={f['bott_A']:.4f} B={f['bott_B']:.4f} "
              f"(separates: {f['topo_separates']})")
    print(f"\n[gate] {n_pass}/{len(results)} cases show Chamfer-equal-or-inverted "
          f"while topology separates (require >= 1).")

    # ── persistence-diagram figures (one per case) ───────────────────
    fig_paths = []
    for r in results:
        p = os.path.join(OUT_DIR, f"pd_{r['key']}.png")
        plots.save_case_diagrams(
            r["_res"]["gt"], r["_res"]["A"], r["_res"]["B"], p,
            case_title=r["title"],
            labels=("ground truth", f"A — {r['candidates']['A']['desc']}",
                    f"B — {r['candidates']['B']['desc']}"))
        fig_paths.append(p)
        print(f"[save] {p}")

    # ── stability time series + figure ───────────────────────────────
    stab = stability_demo()
    stab_csv = os.path.join(OUT_DIR, "stability_series.csv")
    metrics.write_series_csv(stab, stab_csv)
    stab_png = os.path.join(OUT_DIR, "stability_series.png")
    plots.save_stability_series(stab, stab_png, disc_dim=1,
                                title="Topology stability: a spurious handle grows on a sphere")
    print(f"[save] {stab_csv}\n[save] {stab_png}")

    # ── machine-readable results + markdown summary ──────────────────
    _save_json(results, flags, os.path.join(OUT_DIR, "blindness_results.json"))
    _save_summary(results, flags, n_pass, table, fig_paths, stab_png,
                  os.path.join(OUT_DIR, "summary.md"))

    if n_pass < 1:
        print("\n[FAIL] gate not met")
        return 1
    print("\n[OK] Phase-1 blindness demonstration complete.")
    return 0


def _save_json(results, flags, path):
    payload = {"seed": SEED, "n_samples": N_SAMPLES, "cases": [], "gate": flags}
    for r in results:
        payload["cases"].append({
            "key": r["key"], "title": r["title"], "disc_dim": r["disc"],
            "param": r["param"], "betti_gt": list(r["betti_gt"]),
            "candidates": {n: {k: v for k, v in c.items()} for n, c in r["candidates"].items()},
        })
    with open(path, "w") as f:
        json.dump(payload, f, indent=2, default=lambda o: list(o) if isinstance(o, tuple) else str(o))
    print(f"[save] {path}")


def _save_summary(results, flags, n_pass, table, fig_paths, stab_png, path):
    L = []
    L.append("# Phase 1 — Topology-blindness of Chamfer / Hausdorff\n")
    L.append("**Measurement-only harness.** No resampling method and no differentiable "
             "persistent homology — topology is computed (alpha complex, GUDHI) purely to "
             "MEASURE what geometric metrics miss.\n")
    L.append(f"- Samples per shape: **{N_SAMPLES:,}** (seeded, reproducible)")
    L.append(f"- Geometric metrics mirror `src/eval_geometry.py` (normalized by GT bbox diagonal)")
    L.append(f"- Topology metric: bottleneck distance of each candidate's persistence "
             f"diagram to the ground-truth diagram, per dimension\n")
    L.append("## Result table\n")
    L.append("In every case the two candidates have **equal Chamfer** to GT by construction "
             "(A's geometry is bisection-matched to B). `A` is topologically correct, `B` is "
             "topologically wrong. The discriminating bottleneck column separates them.\n")
    L.append(table + "\n")
    L.append("## Does each case demonstrate blindness?\n")
    L.append("A case counts when Chamfer ranks B **equal-or-better** than A, yet the "
             "discriminating-dimension bottleneck ranks B clearly worse.\n")
    dname = {0: "H0 (components)", 1: "H1 (loops/handles)", 2: "H2 (voids)"}
    for f, r in zip(flags, results):
        cA = r["candidates"]["A"]; cB = r["candidates"]["B"]; d = f["disc"]
        if f["bott_A"] < 1e-4:                        # feature absent from A entirely
            sep = (f"B={f['bott_B']:.4f} vs A≈0 — the wrong candidate carries a "
                   f"{dname[d].split()[0]} feature the correct one simply does not have")
        else:
            sep = f"**{f['bott_B'] / f['bott_A']:.0f}× larger** for the wrong candidate (A={f['bott_A']:.4f}, B={f['bott_B']:.4f})"
        L.append(f"- **{r['key']}** — disc dim **{dname[d]}**. "
                 f"Chamfer A={cA['chamfer_pct']:.3f}%, B={cB['chamfer_pct']:.3f}% "
                 f"(Hausdorff95 A={cA['hausdorff95_pct']:.3f}%, B={cB['hausdorff95_pct']:.3f}%); "
                 f"bottleneck→GT {sep}. "
                 f"{'**Blindness demonstrated.**' if f['passes'] else '_(weaker)_'}")
    L.append(f"\n**Gate: {n_pass}/{len(results)} cases** show Chamfer-equal-or-inverted while "
             f"topology separates (requirement: ≥ 1).\n")
    L.append("### Notes\n")
    L.append("- Cases (i) and (ii): Hausdorff95 *also* (slightly) prefers the topologically "
             "**wrong** candidate B — geometry is not merely tied but inverted.")
    L.append("- Case (iii): a closed shell's enclosed void (H2) only *fully* disappears under a "
             "gross hole, because the alpha-complex void fills at the radius scale. With a "
             "modest hole the Betti **count** stays 1 for both, but the **bottleneck distance** "
             "captures the void's collapsing death-time — the continuous metric is more "
             "sensitive than the discrete count. The blister (A) of identical Chamfer leaves the "
             "void intact (bottleneck≈0), so Chamfer cannot tell a benign bump from a punctured void.")
    L.append("\n## Figures\n")
    for r, p in zip(results, fig_paths):
        L.append(f"- `{os.path.basename(p)}` — persistence diagrams (GT / A / B), {r['title']}")
    L.append(f"- `{os.path.basename(stab_png)}` — topology stability series: Chamfer drifts "
             f"smoothly while bottleneck-H1 jumps when a spurious handle becomes significant.")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print(f"[save] {path}")


if __name__ == "__main__":
    raise SystemExit(main())
