# scripts/audit_paper2.py
# Full paper-2 audit (first run 2026-07-11, all checks passing): recompute
# every quantitative claim in paper2/ from the source result files
# (topo3/report/results.json, topo3/quicklook.json, h2_unified, crossover,
# ramp pilots; blindness cases spot-checked the same day), and statically
# check the LaTeX: labels/refs/cites/figure files/rendered-name hygiene
# (no rendered "kinkin"). Output: OK / MISMATCH per claim. RE-RUN THIS
# BEFORE ANY SUBMISSION; expected values are the ones printed in the paper.
#
#   D:\...\CG-Soup-for-Digital-Dentistry\.venv\Scripts\python.exe `
#       scripts\audit_paper2.py
import json
import math
import os
import re
import sys

DENTISTRY = os.environ.get("CGSOUP_ROOT",
                           r"D:\Project\CG-Soup-for-Digital-Dentistry")
D = os.path.join(DENTISTRY, "output", "synth")
T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P2 = os.path.join(T, "paper2")

def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)

RES = load(os.path.join(D, "topo3", "report", "results.json"))
QL = load(os.path.join(D, "topo3", "quicklook.json"))
H2U = load(os.path.join(D, "h2_unified", "report", "results.json"))
XO = load(os.path.join(D, "crossover", "report", "results.json"))

issues = []

def check(name, got, exp, tol=5e-5):
    if got is None:
        issues.append(f"MISSING  {name}: expected {exp}, source value not found")
        print(f"?? {name}: NOT FOUND (expected {exp})")
        return
    ok = abs(got - exp) <= tol
    mark = "OK" if ok else "MISMATCH"
    if not ok:
        issues.append(f"{mark} {name}: paper says {exp}, source says {got:.5f}")
    print(f"{mark:8s} {name}: paper {exp} | source {got:.5f}")

def welch(m1, s1, n1, m0, s0, n0):
    return abs(m0 - m1) / math.sqrt(s1 * s1 / n1 + s0 * s0 / n0)

# ---- discover aggregate keys ----
sample = RES["sphere"]["aggregate"]["C0"]
print("aggregate keys:", sorted(sample.keys()))

def agg(shape, arm):
    return RES[shape]["aggregate"][arm]

def g(shape, arm, *keys):
    a = agg(shape, arm)
    for k in keys:
        if k in a:
            return a[k]
    return None

MK = ("bott_tail_mean", "tail_mean", "bottleneck_tail_mean", "mean")
SK = ("bott_tail_sd", "tail_sd", "bottleneck_tail_sd", "sd")
CK = ("chamfer_mean", "chamfer_pct_mean", "chamfer")
NK = ("n", "n_seeds", "seeds")

def mean(shape, arm):
    return g(shape, arm, *MK)

def sd(shape, arm):
    return g(shape, arm, *SK)

def cham(shape, arm):
    return g(shape, arm, *CK)

def nseeds(shape, arm):
    v = g(shape, arm, *NK)
    return v if isinstance(v, (int, float)) else None

print("\n---- raw aggregates (for the record) ----")
for shape in RES:
    for arm in RES[shape]["aggregate"]:
        a = RES[shape]["aggregate"][arm]
        print(f"  {shape:13s} {arm:9s} " + " ".join(f"{k}={v:.4f}" if isinstance(v, float) else f"{k}={v}" for k, v in sorted(a.items())))

print("\n---- tab:main ----")
for shape, arm, exp_m, exp_s in [
    ("sphere", "C0", .0623, .0063), ("sphere", "C1", .0156, .0013),
    ("sphere", "C2", .1372, None), ("sphere", "C3", .0151, .0004),
    ("sphere", "C5", .0082, .0007),
    ("cube", "C0", .0582, .0046), ("cube", "C1", .0074, .0011), ("cube", "C2", .1346, None),
    ("torus", "C0", .0424, .0031), ("torus", "C1", .0180, .0016),
    ("torus", "C2", .0457, None), ("torus", "C3", .0155, .0015), ("torus", "C5", .0133, .0004),
    ("two_spheres", "C0", .0065, .0008), ("two_spheres", "C1", .0007, .0002),
    ("two_spheres", "C2", .0008, None),
    ("double_torus", "C0", .0264, .0000), ("double_torus", "C1", .0264, .0000),
    ("double_torus", "C2", .0264, None),
]:
    check(f"{shape} {arm} mean", mean(shape, arm), exp_m)
    if exp_s is not None:
        check(f"{shape} {arm} sd", sd(shape, arm), exp_s)

print("\n---- tab:gen ----")
for shape, exp in [
    ("spot", (.0521, .0081, .0237, .0000, .0652)),
    ("bob", (.0426, .0012, .0208, .0008, .0437)),
    ("fandisk", (.0538, .0022, .0052, .0008, .0571)),
]:
    c0m, c0s, c1m, c1s, c2m = exp
    check(f"{shape} C0 mean", mean(shape, "C0"), c0m)
    check(f"{shape} C0 sd", sd(shape, "C0"), c0s)
    check(f"{shape} C1 mean", mean(shape, "C1"), c1m)
    check(f"{shape} C1 sd", sd(shape, "C1"), c1s)
    check(f"{shape} C2 mean", mean(shape, "C2"), c2m)

print("\n---- reductions & sigmas ----")
def red(shape, a="C1", b="C0"):
    return mean(shape, b) / mean(shape, a)
for shape, exp in [("sphere", 4.0), ("cube", 7.9), ("torus", 2.3),
                   ("two_spheres", 9.5), ("spot", 2.2), ("bob", 2.1), ("fandisk", 10.4)]:
    check(f"{shape} reduction C0/C1", red(shape), exp, tol=0.06)
check("sphere C5 reduction", red("sphere", "C5"), 7.6, tol=0.06)
check("torus C5 reduction", red("torus", "C5"), 3.2, tol=0.06)

# Round-4 reporting policy (2026-07-17): Welch sigma is PRINTED only at
# n=5 (sphere 16.2 stays a hard check); the retired n=3 sigmas
# (cube 18.5, spot 6.1, bob 26.1, fandisk 35.7) are informational.
for shape, n0, n1, exp in [("sphere", 5, 5, 16.2), ("cube", 3, 3, None),
                            ("torus", 5, 5, None), ("spot", 3, 3, None),
                            ("bob", 3, 3, None), ("fandisk", 3, 3, None)]:
    nn0 = nseeds(shape, "C0") or n0
    nn1 = nseeds(shape, "C1") or n1
    s = welch(mean(shape, "C1"), sd(shape, "C1"), nn1, mean(shape, "C0"), sd(shape, "C0"), nn0)
    if exp:
        check(f"{shape} Welch C1 vs C0 (n={nn1},{nn0})", s, exp, tol=0.35)
    else:
        print(f"         {shape} Welch C1 vs C0 = {s:.1f} (not printed; n<5 or unquoted)")

print("\n---- round-4 range reporting (tab:gen brackets, cube prose, suppl Table S7) ----")
def tails(shape, arm):
    return agg(shape, arm)["tails"]

def check_range(name, vals, exp_lo, exp_hi):
    lo, hi = min(vals), max(vals)
    ok = abs(lo - exp_lo) <= 5e-5 and abs(hi - exp_hi) <= 5e-5
    mark = "OK" if ok else "MISMATCH"
    if not ok:
        issues.append(f"{mark} {name}: paper [{exp_lo},{exp_hi}], source [{lo:.5f},{hi:.5f}]")
    print(f"{mark:8s} {name}: paper [{exp_lo},{exp_hi}] | source [{lo:.5f},{hi:.5f}]")

def check_disjoint(name, c1_vals, c0_vals):
    ok = max(c1_vals) < min(c0_vals)
    mark = "OK" if ok else "MISMATCH"
    if not ok:
        issues.append(f"{mark} {name}: C1 max {max(c1_vals):.5f} !< C0 min {min(c0_vals):.5f}")
    print(f"{mark:8s} {name}: C1 max {max(c1_vals):.5f} < C0 min {min(c0_vals):.5f}")

def check_seedlist(name, vals, printed):
    # printed values are 4-dp roundings; allow a half-ulp at 4 dp
    ok = (len(vals) == len(printed) and
          all(abs(v - p) <= 5.05e-5 for v, p in zip(vals, printed)))
    got = [round(v, 4) for v in vals]
    mark = "OK" if ok else "MISMATCH"
    if not ok:
        issues.append(f"{mark} {name}: paper {printed}, source {got}")
    print(f"{mark:8s} {name}: paper {printed} | source {got}")

# tab:gen bracket column (printed to 4 dp)
for shape, c0r, c1r in [("spot", (.0429, .0584), (.0237, .0237)),
                        ("bob", (.0413, .0437), (.0200, .0216)),
                        ("fandisk", (.0515, .0559), (.0042, .0058))]:
    check_range(f"{shape} C0 range", tails(shape, "C0"), *c0r)
    check_range(f"{shape} C1 range", tails(shape, "C1"), *c1r)
    check_disjoint(f"{shape} ranges disjoint", tails(shape, "C1"), tails(shape, "C0"))
# cube prose ranges (§5.1)
check_range("cube C0 range (prose)", tails("cube", "C0"), .0551, .0636)
check_range("cube C1 range (prose)", tails("cube", "C1"), .0064, .0086)
check_disjoint("cube ranges disjoint", tails("cube", "C1"), tails("cube", "C0"))
# suppl Table S7 per-seed values (run order, 4 dp)
check_seedlist("S7 spot C0", tails("spot", "C0"), [.0429, .0584, .0550])
check_seedlist("S7 spot C1", tails("spot", "C1"), [.0237, .0237, .0237])
check_seedlist("S7 bob C0", tails("bob", "C0"), [.0429, .0413, .0437])
check_seedlist("S7 bob C1", tails("bob", "C1"), [.0200, .0207, .0216])
check_seedlist("S7 fandisk C0", tails("fandisk", "C0"), [.0540, .0515, .0559])
check_seedlist("S7 fandisk C1", tails("fandisk", "C1"), [.0058, .0055, .0042])
check_seedlist("S7 cube C0", tails("cube", "C0"), [.0560, .0551, .0636])
check_seedlist("S7 cube C1", tails("cube", "C1"), [.0071, .0064, .0086])
check_seedlist("S7 two_spheres C0", tails("two_spheres", "C0"), [.0060, .0074, .0062])
check_seedlist("S7 two_spheres C1", tails("two_spheres", "C1"), [.0007, .0009, .0005])
check_seedlist("S7 two_spheres C2", tails("two_spheres", "C2"), [.0009, .0009, .0006])
check("C6 sphere sd (tab:main round 4)", sd("sphere", "C6"), .0005)

print("\n---- prose claims ----")
check("sphere C2g mean", mean("sphere", "C2g"), .0972)
check("sphere C2g sd", sd("sphere", "C2g"), .0169)
check("sphere C2 2.2x worse", mean("sphere", "C2") / mean("sphere", "C0"), 2.2, tol=0.05)
check("sphere C2g 1.6x worse", mean("sphere", "C2g") / mean("sphere", "C0"), 1.6, tol=0.05)
check("sphere chamfer C1", cham("sphere", "C1"), 0.46, tol=0.006)
check("sphere chamfer C0", cham("sphere", "C0"), 0.50, tol=0.006)
check("cube chamfer C1", cham("cube", "C1"), 0.92, tol=0.006)
check("cube chamfer C0", cham("cube", "C0"), 1.05, tol=0.006)
check("two_spheres chamfer C1", cham("two_spheres", "C1"), 0.54, tol=0.006)
check("two_spheres chamfer C2", cham("two_spheres", "C2"), 1.94, tol=0.006)
check("torus C5 chamfer", cham("torus", "C5"), 0.502, tol=0.002)
check("torus C3 chamfer", cham("torus", "C3"), 0.495, tol=0.002)
check("rho .03 sphere", mean("sphere", "C1_r0.03"), .0181)
check("rho .3 sphere", mean("sphere", "C1_r0.3"), .0177)
print(f"         NOTE rho .1 prose says .0172; table C1 = {mean('sphere','C1'):.4f}")
check("C6 torus mean", mean("torus", "C6"), .0411)
check("C6 torus sd", sd("torus", "C6"), .0038)
n_c6 = nseeds("torus", "C6") or 5
print(f"         C6 torus vs C0 Welch = {welch(mean('torus','C6'), sd('torus','C6'), n_c6, mean('torus','C0'), sd('torus','C0'), nseeds('torus','C0') or 5):.1f} (paper 0.6)")
print(f"         C6 torus vs C1 Welch = {welch(mean('torus','C6'), sd('torus','C6'), n_c6, mean('torus','C1'), sd('torus','C1'), nseeds('torus','C1') or 5):.1f} (paper 12.4)")
check("C6 sphere mean", mean("sphere", "C6"), .0166)
print(f"         C6 sphere vs C1 Welch = {welch(mean('sphere','C6'), sd('sphere','C6'), nseeds('sphere','C6') or 5, mean('sphere','C1'), sd('sphere','C1'), nseeds('sphere','C1') or 5):.1f} (paper 1.5)")
for shape, arm, em, es in [("torus", "C7", .0210, .0018), ("torus", "C7h", .0259, .0022),
                            ("sphere", "C7", .0235, .0009), ("sphere", "C7h", .0328, .0013)]:
    check(f"{shape} {arm} mean", mean(shape, arm), em)
    check(f"{shape} {arm} sd", sd(shape, arm), es)
check("torus C7 2.0x below", mean("torus", "C0") / mean("torus", "C7"), 2.0, tol=0.05)
check("torus C7h 1.6x below", mean("torus", "C0") / mean("torus", "C7h"), 1.6, tol=0.05)
check("sphere C7 2.7x below", mean("sphere", "C0") / mean("sphere", "C7"), 2.7, tol=0.05)
check("sphere C7h 1.9x below", mean("sphere", "C0") / mean("sphere", "C7h"), 1.9, tol=0.05)
check("bob C3 mean", mean("bob", "C3"), .0171)
check("bob C3 sd", sd("bob", "C3"), .0026)

print("\n---- tom-yum pot row (quicklook, key kinkin) ----")
kk = [r for r in QL if r["shape"] == "kinkin"]
def rows(cond):
    return [r for r in kk if r["cond"] == cond]
def msd(vals):
    m = sum(vals) / len(vals)
    v = sum((x - m) ** 2 for x in vals) / (len(vals) - 1)
    return m, math.sqrt(v)
c0 = [r["tail_bottleneck_H2"] for r in rows("C0")]
c1 = [r["tail_bottleneck_H2"] for r in rows("C1")]
c2 = [r["tail_bottleneck_H2"] for r in rows("C2")]
m0, s0 = msd(c0); m1, s1 = msd(c1); m2, s2 = msd(c2)
check("pot C0 mean", m0, .0221); check("pot C0 sd", s0, .0003)
check("pot C1 mean", m1, .0057); check("pot C1 sd", s1, .0002)
check("pot C2 mean", m2, .0223, tol=1e-4)
check("pot reduction", m0 / m1, 3.9, tol=0.05)
print(f"         pot Welch C1 vs C0 = {welch(m1, s1, 3, m0, s0, 3):.1f} (paper 80.1)")
ch0 = msd([r["chamfer_pct"] for r in rows("C0")])[0]
ch1 = msd([r["chamfer_pct"] for r in rows("C1")])[0]
ch2 = msd([r["chamfer_pct"] for r in rows("C2")])[0]
check("pot chamfer parity C1/C0", ch1 / ch0, 0.99, tol=0.006)
check("pot chamfer C2/C0 1.36x", ch2 / ch0, 1.36, tol=0.006)
print("         pot nsig H2:", {c: [r["nsig_H2"] for r in rows(c)] for c in ("C0", "C1", "C2")})
# Round-4 range reporting for the pot (tab:gen bracket + §5.2 prose + S7)
check_range("pot C0 range", c0, .0218, .0223)
check_range("pot C1 range", c1, .0056, .0059)
check_disjoint("pot ranges disjoint", c1, c0)
check_seedlist("S7 pot C0", c0, [.0218, .0223, .0223])
check_seedlist("S7 pot C1", c1, [.0059, .0056, .0056])
check_seedlist("S7 pot C2", c2, [.0223, .0223, .0223])

print("\n---- open-surface probe (round-4 new science; suppl §F + main §7) ----")
for shape, exp in [("bowl_narrow", (.0588, .0035, .0138, .0013, .1249)),
                   ("bowl_wide",   (.0560, .0098, .0137, .0003, .0770))]:
    c0m, c0s, c1m, c1s, c2m = exp
    check(f"{shape} C0 mean", mean(shape, "C0"), c0m)
    check(f"{shape} C0 sd", sd(shape, "C0"), c0s)
    check(f"{shape} C1 mean", mean(shape, "C1"), c1m)
    check(f"{shape} C1 sd", sd(shape, "C1"), c1s)
    check(f"{shape} C2 mean", mean(shape, "C2"), c2m)
    check_disjoint(f"{shape} ranges disjoint",
                   tails(shape, "C1"), tails(shape, "C0"))
check("bowl_narrow reduction (main §7 4.2x)", red("bowl_narrow"), 4.2, tol=0.06)
check("bowl_wide reduction (main §7 4.1x)", red("bowl_wide"), 4.1, tol=0.06)
check("bowl_narrow chamfer C1/C0", cham("bowl_narrow", "C1") / cham("bowl_narrow", "C0"), 0.89, tol=0.006)
check("bowl_wide chamfer C1/C0", cham("bowl_wide", "C1") / cham("bowl_wide", "C0"), 0.87, tol=0.006)
# suppl Table S10 per-seed triplets (run order)
check_seedlist("SF bowl_narrow C0", tails("bowl_narrow", "C0"), [.0619, .0550, .0593])
check_seedlist("SF bowl_narrow C1", tails("bowl_narrow", "C1"), [.0137, .0126, .0151])
check_seedlist("SF bowl_wide C0", tails("bowl_wide", "C0"), [.0448, .0602, .0630])
check_seedlist("SF bowl_wide C1", tails("bowl_wide", "C1"), [.0141, .0136, .0135])
print("         bowl nsig:", {s: {c: agg(s, c)["nsig_final"]
                                  for c in ("C0", "C1", "C2")}
                              for s in ("bowl_narrow", "bowl_wide")})

# ---- round-5 group wave (2026-07-19): grouped tab:gen + means + §G ----
print("\n---- round-5 group wave (grouped tab:gen + group means + suppl §G) ----")
for shape, exp in [("rockerarm", (.0083, .0004, .0087, .0015, .0113)),
                   ("eight",     (.0249, .0000, .0162, .0017, .0249)),
                   ("armadillo", (.0511, .0000, .0124, .0001, .0511)),
                   ("horse",     (.0408, .0000, .0109, .0022, .0408))]:
    c0m, c0s, c1m, c1s, c2m = exp
    check(f"{shape} C0 mean", mean(shape, "C0"), c0m)
    check(f"{shape} C0 sd", sd(shape, "C0"), c0s)
    check(f"{shape} C1 mean", mean(shape, "C1"), c1m)
    check(f"{shape} C1 sd", sd(shape, "C1"), c1s)
    check(f"{shape} C2 mean", mean(shape, "C2"), c2m)
check("eight reduction (1.5x)", red("eight"), 1.5, tol=0.06)
check("armadillo reduction (4.1x)", red("armadillo"), 4.1, tol=0.06)
check("horse reduction (3.8x)", red("horse"), 3.8, tol=0.06)
check("rockerarm null (0.96x)", red("rockerarm"), 0.96, tol=0.006)
check("rockerarm chamfer parity 1.00",
      cham("rockerarm", "C1") / cham("rockerarm", "C0"), 1.00, tol=0.006)
check("eight chamfer 0.89", cham("eight", "C1") / cham("eight", "C0"), 0.89, tol=0.006)
check("armadillo chamfer 0.88",
      cham("armadillo", "C1") / cham("armadillo", "C0"), 0.88, tol=0.006)
check("horse chamfer 0.90", cham("horse", "C1") / cham("horse", "C0"), 0.90, tol=0.006)
for s in ("eight", "armadillo", "horse"):        # rockerarm = null, overlap by design
    check_disjoint(f"{s} ranges disjoint", tails(s, "C1"), tails(s, "C0"))
check_seedlist("S7 rockerarm C0", tails("rockerarm", "C0"), [.0088, .0082, .0079])
check_seedlist("S7 rockerarm C1", tails("rockerarm", "C1"), [.0090, .0070, .0100])
check_seedlist("S7 rockerarm C2", tails("rockerarm", "C2"), [.0112, .0112, .0115])
check_seedlist("S7 eight C0", tails("eight", "C0"), [.0249] * 3)
check_seedlist("S7 eight C1", tails("eight", "C1"), [.0169, .0175, .0142])
check_seedlist("S7 eight C2", tails("eight", "C2"), [.0249] * 3)
check_seedlist("S7 armadillo C0", tails("armadillo", "C0"), [.0511] * 3)
check_seedlist("S7 armadillo C1", tails("armadillo", "C1"), [.0124, .0125, .0123])
check_seedlist("S7 armadillo C2", tails("armadillo", "C2"), [.0511] * 3)
check_seedlist("S7 horse C0", tails("horse", "C0"), [.0408] * 3)
check_seedlist("S7 horse C1", tails("horse", "C1"), [.0124, .0083, .0118])
check_seedlist("S7 horse C2", tails("horse", "C2"), [.0408] * 3)
print("         eight nsig C0/C1/C2:", agg("eight", "C0")["nsig_final"],
      agg("eight", "C1")["nsig_final"], agg("eight", "C2")["nsig_final"],
      "(paper: [2,2,2]/[4,3,4]/[2,2,2])")
print("         rockerarm nsig all arms:",
      {c: agg("rockerarm", c)["nsig_final"] for c in ("C0", "C1", "C2")})
print("         armadillo/horse C2 nsig (beta2 1->0):",
      agg("armadillo", "C2")["nsig_final"], agg("horse", "C2")["nsig_final"])
# pre-registered group means, recomputed from results.json (ddof=1),
# independently of output/group_wave_stats.json
loop_reds = [red(s) for s in ("bob", "rockerarm", "eight")]
void_reds = [red(s) for s in ("spot", "fandisk", "kinkin", "armadillo", "horse")]
lm = sum(loop_reds) / len(loop_reds)
ls = (sum((x - lm) ** 2 for x in loop_reds) / (len(loop_reds) - 1)) ** 0.5
vm = sum(void_reds) / len(void_reds)
vs = (sum((x - vm) ** 2 for x in void_reds) / (len(void_reds) - 1)) ** 0.5
check("loop group mean 1.52x", lm, 1.52, tol=0.005)
check("loop group sd 0.55", ls, 0.55, tol=0.005)
check("void group mean 4.87x", vm, 4.87, tol=0.005)
check("void group sd 3.17", vs, 3.17, tol=0.005)
passing = [red(s) for s in ("bob", "eight", "spot", "fandisk", "kinkin",
                            "armadillo", "horse")]
check("passing span low 1.5x", min(passing), 1.5, tol=0.06)
check("passing span high 10.4x", max(passing), 10.4, tol=0.06)
# pin-bound identities (main §5.2 obs 2/4; suppl §G): C0 mean equals half
# the GT top lifetime at the eval density (cert staircase M=20000)
for shape, key, idx, exp_pin in [("eight", "top_H1", 2, .0249),
                                 ("armadillo", "top_H2", 0, .0511),
                                 ("horse", "top_H2", 0, .0408)]:
    cert = load(os.path.join(D, "_meshes", f"{shape}_src_cert.json"))
    row = [r for r in cert["staircase"] if r["M"] == 20000][0]
    half = row[key][idx] / 2
    check(f"{shape} C0 pin == GT half-life", mean(shape, "C0"), half, tol=2e-4)
    check(f"{shape} pin as printed", half, exp_pin, tol=1e-4)

print("\n---- appendix A: h2_unified + crossover + blindness ----")
hk = sorted(next(iter(H2U["summary"]["sphere"].values())).keys())
print("h2_unified arm keys:", hk)
def h2(shape, arm):
    a = H2U["summary"][shape][arm]
    for k in MK:
        if k in a:
            return a[k]
    return None
for shape, exp in [("sphere", (.0535, .0546, .0438, .0440, .0357, .0374)),
                   ("cube", (.0579, None, .0409, .0403, .0273, .0270)),
                   ("cylinder", (.0545, None, .0440, .0477, .0360, .0402))]:
    for arm, e in zip(("B0", "B1", "B2", "B3", "B4", "B5"), exp):
        if e is not None:
            check(f"h2u {shape} {arm}", h2(shape, arm), e)
print(f"         C5-vs-prior-alone: sphere C5 {mean('sphere','C5'):.4f} vs B4 {h2('sphere','B4'):.4f} = {h2('sphere','B4')/mean('sphere','C5'):.2f}x (paper: 4.4x)")
def xo(arm):
    a = XO["summary"]["torus"][arm]
    for k in MK:
        if k in a:
            return a[k]
    return None
for arm, e in [("B0", .0409), ("B2", .0425), ("B3", .0397), ("B4", .0316), ("B5", .0267)]:
    check(f"crossover torus {arm}", xo(arm), e)
a_b2 = XO["summary"]["torus"]["B2"]
print("         crossover B2 full:", {k: (round(v, 4) if isinstance(v, float) else v) for k, v in a_b2.items()})
a_b0 = XO["summary"]["torus"]["B0"]
print("         crossover B0 full:", {k: (round(v, 4) if isinstance(v, float) else v) for k, v in a_b0.items()})

BL = load(os.path.join(T, "figures", "blindness_results.json"))
print("         blindness raw:", json.dumps(BL)[:600])

print("\n---- ramp pilots ----")
for name, exp_m, exp_s in [("ramp_1040", .0154, .0017), ("ramp_3060", .0179, .0019)]:
    q = load(os.path.join(D, name, "quicklook.json"))
    vals = [r[k] for r in q for k in r if k.startswith("tail_bottleneck")]
    m, s = msd(vals)
    check(f"{name} mean", m, exp_m)
    check(f"{name} sd", s, exp_s)
    print(f"         {name} rows: {len(vals)}")

# ================= LaTeX static checks =================
print("\n---- latex: labels / refs / cites / figures ----")
tex = {}
for root, _, files in os.walk(P2):
    for f in files:
        if f.endswith(".tex"):
            p = os.path.join(root, f)
            tex[os.path.relpath(p, P2)] = open(p, encoding="utf-8").read()

def strip_comments(s):
    out = []
    for line in s.splitlines():
        i = 0
        while True:
            j = line.find("%", i)
            if j < 0:
                out.append(line)
                break
            if j > 0 and line[j - 1] == "\\":
                i = j + 1
                continue
            out.append(line[:j])
            break
    return "\n".join(out)

all_src = "\n".join(tex.values())
vis = {k: strip_comments(v) for k, v in tex.items()}
all_vis = "\n".join(vis.values())

labels = re.findall(r"\\label\{([^}]+)\}", all_vis)
refs = re.findall(r"\\(?:auto|page)?ref\{([^}]+)\}", all_vis)
dup = {x for x in labels if labels.count(x) > 1}
print("duplicate labels:", dup or "none")
missing_ref = sorted({r for r in refs if r not in labels})
print("refs to missing labels:", missing_ref or "none")
unused_labels = sorted({l for l in labels if l not in refs})
print("labels never referenced:", unused_labels or "none")

bib = open(os.path.join(P2, "refs.bib"), encoding="utf-8").read()
bibkeys = set(re.findall(r"@\w+\{([^,\s]+)\s*,", bib))
cites = set()
for m in re.findall(r"\\cite[tp]?\*?(?:\[[^\]]*\])?\{([^}]+)\}", all_vis):
    cites.update(k.strip() for k in m.split(","))
print("cites with no bib entry:", sorted(cites - bibkeys) or "none")
print("bib entries never cited:", sorted(bibkeys - cites) or "none")

figs = set(re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", all_vis))
fdir = os.path.join(P2, "figures")
missing_figs = sorted(f for f in figs if not os.path.exists(os.path.join(fdir, f)))
print("includegraphics missing files:", missing_figs or "none")
onclean = sorted(f for f in os.listdir(fdir) if f.endswith(".png") and f not in figs)
print("figure files never included:", onclean or "none")

for k, v in vis.items():
    for pat, why in ((r"kinkin", "rendered kinkin"), (r"\\TODO\{", "rendered TODO macro")):
        for m in re.finditer(pat, v, re.I):
            ln = v[: m.start()].count("\n") + 1
            print(f"HYGIENE  {k}:{ln}: {why}")

print("\n---- summary ----")
print(f"{len(issues)} numeric issues") if issues else print("all numeric checks passed")
for i in issues:
    print(" *", i)
