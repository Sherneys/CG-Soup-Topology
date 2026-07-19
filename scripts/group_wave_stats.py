# scripts/group_wave_stats.py
# Group statistics for the advisor round-5 "two groups + means" wave,
# exactly as pre-registered in GROUP_WAVE_PLAN.md: per group, the mean +- sd
# over member shapes of the per-shape C0/C1 reduction factor computed from
# UNROUNDED seed-mean tails (the study's rounding convention), plus the
# verdict pass count. Reads topo3/report/results.json (regenerate first via
# experiments/topo_loss_report.py).
#
#   $env:PYTHONPATH = "D:\Project\CG-Soup-Topology\tools\gudhi311"   # (report)
#   python scripts\group_wave_stats.py

from __future__ import annotations

import json
import os

import numpy as np

DENTISTRY = os.environ.get("CGSOUP_ROOT", r"D:\Project\CG-Soup-for-Digital-Dentistry")
RESULTS = os.path.join(DENTISTRY, "output", "synth", "topo3", "report", "results.json")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "output", "group_wave_stats.json")

# Pre-registered group membership (GROUP_WAVE_PLAN.md). Paper names in
# parentheses; "kinkin" renders as "tom-yum pot".
GROUPS = {
    "loop (H1)": ["bob", "rockerarm", "eight"],
    "void (H2)": ["spot", "fandisk", "kinkin", "armadillo", "horse"],
}
PARITY_MULT = 1.15


def main():
    with open(RESULTS) as fh:
        res = json.load(fh)

    report = {}
    for gname, members in GROUPS.items():
        rows = []
        for shape in members:
            agg = res[shape]["aggregate"]
            c0, c1, c2 = agg["C0"], agg["C1"], agg["C2"]
            red = c0["mean"] / c1["mean"]
            parity = c1["chamfer_mean"] / c0["chamfer_mean"]
            beats_c2 = c1["mean"] < c2["mean"]
            passes = (c1["mean"] < c0["mean"]) and beats_c2 and (parity <= PARITY_MULT)
            rows.append({
                "shape": shape, "disc": res[shape]["disc_dim"],
                "C0": c0["mean"], "C0_sd": c0["sd"], "C0_tails": c0["tails"],
                "C1": c1["mean"], "C1_sd": c1["sd"], "C1_tails": c1["tails"],
                "C2": c2["mean"], "C2_nsig": c2["nsig_final"],
                "C0_nsig": c0["nsig_final"], "C1_nsig": c1["nsig_final"],
                "reduction": red, "chamfer_ratio": parity,
                "ranges_disjoint": max(c1["tails"]) < min(c0["tails"]),
                "pass": bool(passes),
            })
            print(f"  {shape:11s} H{res[shape]['disc_dim']}  "
                  f"C0 {c0['mean']:.4f}+-{c0['sd']:.4f}  "
                  f"C1 {c1['mean']:.4f}+-{c1['sd']:.4f}  "
                  f"({red:.2f}x)  C2 {c2['mean']:.4f}  "
                  f"parity {parity:.2f}  nsig C0/C1/C2 "
                  f"{c0['nsig_final']}/{c1['nsig_final']}/{c2['nsig_final']}  "
                  f"{'PASS' if passes else 'FAIL'}")
        reds = np.array([r["reduction"] for r in rows])
        gstat = {"members": rows,
                 "mean_reduction": float(reds.mean()),
                 "sd_reduction": float(reds.std(ddof=1)) if len(reds) > 1 else 0.0,
                 "min_reduction": float(reds.min()),
                 "max_reduction": float(reds.max()),
                 "n_pass": int(sum(r["pass"] for r in rows)),
                 "n": len(rows)}
        report[gname] = gstat
        print(f"  {gname:11s} GROUP MEAN {gstat['mean_reduction']:.2f}x "
              f"+- {gstat['sd_reduction']:.2f} "
              f"(range {gstat['min_reduction']:.2f}-{gstat['max_reduction']:.2f}), "
              f"pass {gstat['n_pass']}/{gstat['n']}\n")

    allr = [r for g in report.values() for r in g["members"]]
    spans = [r["reduction"] for r in allr]
    report["_external_span"] = {"min": float(min(spans)), "max": float(max(spans)),
                                "n_shapes": len(allr),
                                "n_pass": int(sum(r["pass"] for r in allr))}
    print(f"external wave span: {min(spans):.2f}x - {max(spans):.2f}x over "
          f"{len(allr)} shapes, pass {report['_external_span']['n_pass']}/{len(allr)}")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump(report, fh, indent=2)
    print(f"[out] {OUT}")


if __name__ == "__main__":
    main()
