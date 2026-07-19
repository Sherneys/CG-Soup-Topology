# Group wave — pre-registered plan (advisor round-5 follow-up)

Date: 2026-07-19 (written BEFORE any candidate was trained).
Advisor instruction (relayed by the author, Thai): the paper reads well;
the one remaining criticism is result diversity — "only the donut and the
tom-yum pot"; fix by presenting **two groups** of shapes **with group
means**.

## Design (fixed before measurement)

**Groups = the study's two observable classes** (the "donut" and "pot"
classes, promoted to populations):

- **Loop group (H1)** — external genus-known meshes whose expected loops
  clear the 6·r_med significance floor at a feasible density.
  Existing member: bob. Target: +2–3 new members.
- **Void group (H2)** — external genus-known meshes whose discriminating
  observable is the enclosed void. Existing members: spot, fandisk,
  tom-yum pot. Target: +2–3 new members.

**Candidate pool** = whatever downloads cleanly from
alecjacobson/common-3d-test-models (+ eight.off if obtainable):
rocker-arm, armadillo, max-planck, cheburashka, horse, cow, beast, ogre,
eight. The pool is fixed by availability, not by outcome.

**Selection rule (pre-training, staircase-only):**
1. Certificate must pass (closed, oriented, edge-manifold, single body
   preferred; exact simplicial homology == Euler prediction). Failures
   are reported and excluded — never repaired (the pot remains the one
   solidify story).
2. Observable class and density come from the density staircase (the
   pot's pre-registered rule, unchanged): a shape joins the loop group
   iff its expected H1 bars are significant at M=2048 (bob precedent);
   it joins the void group iff its H2 void is significant at the
   smallest working M in {2048, 4096, 8192} (kinkin precedent — the
   bundle is then built at that M, `--bundle_n`). A shape whose expected
   features never clear any tested floor is excluded WITH its staircase
   published (the double-torus/ShapeNet precedent).
3. Selection happens strictly BEFORE training; no shape is dropped after
   its C-matrix has run.

**Protocol (identical to the existing generality wave — zero tuning):**
C0/C1/C2, seeds 0 1 2, rho=0.1, ramp 0.2:0.5, 2500 steps, K=10,
class budgets: loop group N=700 (`--max_faces 700`), void group N=1200;
`--loss_dims 1` only when the staircase shows the H2 void sub-floor at
the working M (torus/tomyum precedent); scenes 48 views / 200 px via the
unchanged builder. Runs are additive topo3 tags.

**Verdict rule:** unchanged (C1 < C0 and < C2 at Chamfer parity 1.15,
counts checked). Failures are printed as failures.

**Group means (the advisor's "ค่าเฉลี่ย"):** per group, the mean ± sd
over member shapes of the per-shape C0/C1 reduction factor, computed
from UNROUNDED seed-mean tails (the study's rounding convention), plus
the pass count. Existing members (bob; spot, fandisk, pot) are included
in the group statistics; analytic-family shapes stay in tab:main and are
NOT mixed into the external group means.

## Execution record (filled as steps complete)

- [x] downloads + licenses (2026-07-19; alecjacobson/common-3d-test-models
  @ 8a4f864 + CGAL eight.off @ 47028cd; per-mesh provenance in the agent
  report, README copy in the session scratchpad)
- [x] certificates + staircases (make_group_assets.py; summary json at
  output/group_assets_summary.json; certs at _meshes/<key>_src_cert.json)
  - certified: armadillo g0 (1,0,1)@all M; horse g0 (1,0,1)@all M;
    cheburashka g0; rockerarm g1 b=(1,2,1); eight g2 b=(1,4,1) [CGAL];
    eightdirectional g2 b=(1,4,1) [license unstated]
  - certificate FAILURES (excluded, never repaired): beast (duplicate
    directed edge), cow (odd chi), max-planck (161 open edges), ogre
    (200), teapot (160) — the honest-exclusion record the wave needs
- [x] **selection per rule 2 — RECORDED BEFORE TRAINING (2026-07-19):**
  - LOOP group += **rockerarm** (one of two loops clears the floor at
    M=2048: top H1 0.0929 vs floor 0.0613, second 0.0204 sub-floor
    everywhere feasible, void also sub-floor at 2048 → torus/tomyum
    precedent: bundle 2048, `--loss_dims 1`, N=700)
  - LOOP group += **eight** (CGAL, genus 2: staircase reads the FULL
    exact (1,4,1) from M=4096; at the chosen M=8192 margins are
    comfortable — 4th loop 0.0478 vs floor 0.02822 = 1.69x, void 2.6x →
    kinkin precedent: `--bundle_n 8192`, full bundle, N=700; the fat
    genus-2 counterpoint to the saturated thin analytic double torus)
  - VOID group += **armadillo**, **horse** (exact (1,0,1) at EVERY
    tested M; bundle 2048, no dim restriction, N=1200)
  - eligible but NOT selected, on staircase grounds recorded pre-run:
    **cheburashka** (qualifies at 2048 (1,0,1) but a second capping H2
    bar becomes significant from 8192 (0.0300 vs floor 0.0271; 0.0312
    vs 0.0171 at 20k) — a pot-flue-type concavity reading that would
    make the evaluation-density phantom check ambiguous; cert kept);
    **eightdirectional** (denser retessellation of the same genus-2
    shape, license unstated — CGAL copy preferred for print; its
    staircase corroborates eight's observable class at 8192)
- [x] scenes built (rockerarm/eight/armadillo/horse, 48 views 200 px,
  2026-07-19)
- [x] C-matrices run (36 runs, additive topo3 tags, zero failures;
  bundle preflights matched the pre-registered staircases exactly:
  rockerarm 1×H1@2048, eight 4×H1+1×H2@8192, armadillo/horse 1×H2@2048)
- [x] group means + paper integration (2026-07-19). **Outcome, per the
  pre-registered statistic** (scripts/group_wave_stats.py →
  output/group_wave_stats.json; verdicts topo3/report/results.json):
  - loop group: bob 2.05x PASS; **rocker-arm 0.96x FAIL = no-headroom
    null** (C0 already .0083, parity 1.0029, counts intact in every
    arm — §4's imperfection criterion unmet); **eight 1.54x PASS with
    count restoration** (C0/C2 read 2 of 4 loops, C1 4/3/4; C0/C2 pin
    .0249 = half loop-3's GT lifetime) → mean 1.52x ± 0.55, 2/3 pass
  - void group: spot 2.19 / fandisk 10.38 / pot 3.88 / armadillo 4.12 /
    horse 3.76, all PASS at better Chamfer; armadillo/horse C0 pin at
    .0511/.0408 = half the GT top-H2 lifetime (seed-exact) → mean
    4.87x ± 3.17, 5/5 pass
  - external span 0.96–10.38 over 8 shapes, 7/8 pass
  - in print: grouped main Table 2 + mean rows, §5.2 six observations,
    setup wave ¶, abstract group means + honest null, suppl §G (Tables
    S11 staircases / S12 disposition), Table S7 +4 rows; body ends
    EXACTLY p8, zero overfull, audit_paper2.py extended (group-wave
    block incl. recomputed means + pin identities) ALL GREEN.
