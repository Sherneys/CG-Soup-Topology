# PAPER 2 — ROUND 5b: THE GROUP WAVE — ADVISOR'S PICK EXECUTED SAME DAY (2026-07-19)

**The advisor's verdict on round 5 (relayed in Thai):** overall the
paper looks good; the one remaining criticism is result diversity
("มีแค่รูปโดนัทกับหม้อต้มยำ") — fix by presenting **two groups + group
means**. That resolves the round-5 science menu: not DTU/TnT/Objaverse,
but a broader external wave in the study's own two observable classes.

## What was run (all pre-registered BEFORE training: GROUP_WAVE_PLAN.md)

- **Pool**: 10 meshes from alecjacobson/common-3d-test-models @ 8a4f864
  + CGAL eight.off @ 47028cd (agent-downloaded with provenance; the
  release bundle will ship fetch scripts + pins, not foreign meshes).
- **Certificates** (the pot's chain, scripts/make_group_assets.py):
  PASS armadillo/horse/cheburashka (g0), rocker-arm (g1), eight (g2,
  both tessellations); **FAIL — excluded, never repaired**: beast, cow,
  max-planck, ogre, Utah teapot (open boundaries / non-manifold).
- **Staircase selection, pre-training**: loop group += rocker-arm
  (torus precedent: 1 of 2 loops clears @2048, H1-restricted) + eight
  (pot precedent: full (1,4,1) @8192, margins 1.69×/2.6×); void group
  += armadillo + horse ((1,0,1) at every M). Set aside with reasons on
  record: cheburashka (2nd capping H2 bar from 8192 → phantom-check
  ambiguity), eight-dense (license unstated; staircase corroborates).
- **36 runs** (C0/C1/C2 × 3 seeds × 4 shapes, blind config, additive
  tags), zero failures; report + quicklook regenerated.

## Results (pre-registered statistic; sources: results.json + group_wave_stats.json)

| group | members | mean ± sd | pass |
|---|---|---|---|
| loop (H1) | bob 2.05×, **rocker-arm 0.96× (null)**, **eight 1.54×** | **1.52× ± 0.55** | 2/3 |
| void (H2) | spot 2.19×, fandisk 10.38×, pot 3.88×, armadillo 4.12×, horse 3.76× | **4.87× ± 3.17** | 5/5 |

- **eight is the wave's headline**: baseline AND control read only 2 of
  the 4 certified loops (value pinned at .0249 = half loop-3's GT
  lifetime, seed-exact); the loss **restores the missing pair**
  (#sig 4/3/4) at 0.89× Chamfer — the analytic double torus's
  saturation was the representation's ceiling, not genus-2's.
- **rocker-arm is an honest no-headroom null, not a counterexample**:
  its one measurable loop is already baseline-correct (.0083 vs the
  .04–.05 band); the loss lands within noise (0.96×, parity 1.00),
  counts intact in every arm. Printed as observation 5 + the discussion
  axis ("nothing responds where nothing is broken").
- **armadillo/horse**: clean 4.1×/3.8× at better Chamfer; their C0
  pins (.0511/.0408, sd 0) are unmatched-target bounds = half the GT
  top-H2 lifetime — identities verified in the audit.
- External span 0.96–10.38 over 8 shapes; passing span 1.5–10.4.

## In print (body ends EXACTLY p8 again; audits ALL GREEN)

Grouped Table 2 with per-group mean rows (the advisor's ค่าเฉลี่ย);
§5.2 rewritten as six observations + group statistic; setup wave ¶
(certificate failures + pre-registration stated); abstract carries the
group means AND the honest null; suppl **§G** (provenance/staircases/
disposition, Tables S11/S12 — placed last so S1–S10 numbering is
untouched); Table S7 +4 per-seed rows; discussion/limitations counts
updated; teaser 0.78→0.74\textwidth to pay part of the page bill.
Accuracy fixes found on the way: the pot's "only protocol deviation"
claim (now shared with eight), the stale construction-vs-certificate
contrast, the probe §F span (2.1–10.4 → 1.5–10.4), and a
**comment-swallowed sentence-start** in setup.tex introduced by the
round-5 cert edit (the "rendered and budgeted…" fragment was missing
from the PDF in commit 3e829aa — repaired; re-check this bug class
before submission, the audit does not catch prose fragments).
audit_paper2.py extended: group-wave block (means recomputed from
results.json independently, seedlists, disjointness, pin identities).

## Round-5 leftovers CLOSED (2026-07-20): suppl §H "Robustness of the
## reporting choices" — re-analysis only, main untouched (still p8)

- **R6 (floor "arbitrary")**: every documented bundle decision recomputed
  from recorded GT clouds → unchanged for multiplier **k ∈ (5.12, 6.77)**
  (binders = the two features the paper already flags: double-torus tube
  0.85×, bob void 1.13×); Table S13 lists per-shape margins; the verdict
  metric itself is threshold-free. src: output/floor_sensitivity.json
  (scripts/floor_sensitivity.py).
- **R7 (pair-frozen stability)**: Fig S11 from the RECORDED refresh logs
  (no new runs): torus C6 = chronic 1-matched/1-unreached (the collapse
  mechanism, visualized); eight C1 = recruitment claims the two
  sub-threshold loops then hands them to matched as they turn
  significant; pot C1 = stable 1-bar plan. gabriel_fail = 0 in all
  three logs. Note: refresh schema exists only in runs from 2026-07-09
  (C6/C7 wiring) — original 3d C1 arms predate it.
- **R4 (cost/memory)**: persistence-step staircase 174 ms@2048
  (reproduces §3.2's recorded figure exactly) / 388 / 740 / 1,918 ms
  @20k = 11.0× cost for 9.8× points (≈ O(M log M)); GPU probe: whole-GPU
  peak 3,649 MiB (C0) vs 4,035 MiB (C1), **+386 MiB**, persistence on
  CPU. src: floor_sensitivity.json timing + output/mem_probe.json
  (mem_probe runs additive under output/synth/mem_probe).
- Skipped deliberately: W₂ eval column (bottleneck is the principled
  stability-backed choice; say so if a reviewer asks), contribution
  bullets (run-in kept — page budget), Hungarian A/B (provably
  coincides — already in print).
- audit_paper2.py extended again (§H window/margins/timing/memory);
  ALL GREEN. Suppl now 15 pp.

## Still owed by you (unchanged + one addition)

1. Send the Thai reply — **CONSOLIDATED Gmail draft
   r-4435680882078772474 created 2026-07-19** (covers rounds 4 + 5 +
   the group wave + the **SA-2026 poster question, deadline Jul 31**).
   Before sending: add your name at the bottom, and DELETE the two
   superseded drafts (r-1323288373779606130 and r-648741549389595318)
   so the wrong one can't go out.
2. Voice pass; OpenReview paper ID; 2027 kit swap; anonymized-code zip
   before the Sep 2 suppl deadline.
3. Optional (advisor may ask): a suppl render strip of the four new
   shapes (make_matrix_figure.py extension) — visual diversity.

**Thai addition for the reply (append to the round-5 block):**
ตามที่อาจารย์แนะนำ ได้ขยายชุดทดลองเป็น **2 กลุ่มพร้อมค่าเฉลี่ย** แล้ว
(pre-registered ก่อนรันทั้งหมด): กลุ่ม loop (bob, rocker-arm, eight
genus-2) เฉลี่ย 1.52×±0.55 และกลุ่ม void (spot, fandisk, หม้อต้มยำ,
armadillo, horse) เฉลี่ย 4.87×±3.17 — ผ่าน verdict 7/8 รูป โดย
rocker-arm เป็น null ที่ตรงไปตรงมา (baseline ถูกต้องอยู่แล้ว ไม่มี
headroom; loss ไม่ทำอันตราย) และ **eight เป็นไฮไลต์**: baseline เห็น
loop แค่ 2 จาก 4 แต่ loss กู้คืนครบ (4/3/4) — ตอบข้อกังขาเรื่อง double
torus ที่อิ่มตัวด้วย (เพดานอยู่ที่ representation ไม่ใช่ genus)
ตัวเลขทั้งหมดอยู่ใน Table 2 (จัดกลุ่ม + mean rows) และ suppl §G
กระดาษยังจบหน้า 8 พอดี audit ผ่านทุกข้อครับ

---

# PAPER 2 — ADVISOR ROUND 5 (Related Works + Revision list) — WRITING EXECUTED 2026-07-19; SCIENCE MENU AWAITING YOUR/ADVISOR CALL

**What arrived (2026-07-19, Downloads):** `Related Works.docx` (Thai:
§2-restructure table, a "thought tree" for the related-work narrative,
a dictated Introduction paragraph, 3 citations to re-check, + a
MeshSplatting suggestion) and `Revision list.docx` (Thai: 9-row
prioritized review table Critical→Minor + a "mandatory datasets"
section: DTU / Tanks-and-Temples / Objaverse).

## Citation audit — the round's headline: ALL FOUR REFERENCES ARE REAL
(first fully-grounded advisor round; contrast rounds 2–3)

- **MeshSplatting: Differentiable Rendering with Opaque Meshes —
  VERIFIED, CVPR 2026 ORAL** (arXiv:2512.06818; 10 authors Held, Son,
  Vandeghen, Rebain, Gadelha, Zhou, Cioppa, Lin, Van Droogenbroeck,
  Tagliasacchi; cvpr.thecvf.com/virtual/2026/poster/38397). Distinct
  from "Triangle Splatting+" (arXiv:2509.25122) — parallel subtitles,
  same author cluster; do not merge. ADDED to refs.bib
  (`held2026meshsplatting`) + one §2 contrast sentence.
- **Triangle Splatting — advisor RIGHT about 3DV 2026.** Bib upgraded
  @misc→@inproceedings: pp. 1248–1257, DOI 10.1109/3DV69130.2026.00123
  (CrossRef+dblp+Xplore agree); camera-ready has **11 authors** (Daniel
  Rebain added at position 6; Ghanem↔Vedaldi order differs from arXiv
  v1). The project page's BibTeX is stale — never copy it.
- **Radiant Triangle Soup** — real (in refs.bib since round 3,
  arXiv:2505.23642), but the advisor's "ICLR 2026 (submitted)" is NOT
  confirmable (dblp: CoRR-only and current through 3DV-2026 ingestion;
  OpenReview forum unindexed + fetch-blocked). Cited arXiv-only; NOW
  NAMED in main §2 with a description verified against the paper
  itself: soft connectivity forces = pairwise matched-edge vertex pulls
  + normal alignment (local continuity); no global topology measured;
  watertight extraction is their own stated limitation.
- **DiffSoup** — CVPR 2026 confirmed (virtual-site poster page; CVF
  page exists but bot-blocked). No proceedings page numbers anywhere
  yet — entry unchanged.

## Related-Works doc — EXECUTED (all writing; zero numbers touched)

- Intro ¶2 opens with the requested 2025–26 triangle-turn context
  (native graphics-pipeline fit, 3 cites) as a clause; the requested
  "our work addresses this gap" echo was already ¶3's closing sentence.
- §2 ¶1 position (iv): the return-to-native-triangles beat (splatted /
  soft-connected / rasterized by DiffSoup) + MeshSplatting as the
  *connected-side* counterpoint (deliberately NOT placed inside the
  soup list — that would misclassify it).
- §2 ¶3 (persistence): survey now closes "— yet never as the objective
  of an explicit triangle-based reconstruction" (his opening-sentence
  ask, merged for the page budget); "other, **complementary** entry
  points" (his tone item); named Radiant contrast sentence before the
  backward-pass paragraph, kept OUTSIDE the three-requirement partition
  (which scopes persistence neighbours only).
- Gap statement recut on his three axes (explicit triangles ×
  differentiable optimization × topology in the objective; pairwise
  intersections occupied, three-way one ours) — REPLACES the old
  punchline per his own instruction, merged with round-3's philosophy
  cut; suppl. Table S6 remains the matrix form.
- The "thought tree" was interpreted as narrative structure (two
  previously separate lineages meeting), not a printed figure — a
  literal diagram does not fit the p8-exact budget; if he wants it
  visual, offer a suppl. figure (S6 already maps the space as a table).
- **Page budget:** paid by a document-wide micro-trim pass (~15 wording
  trims, see git diff; every number + % src kept verbatim). Rebuild:
  **body ends EXACTLY p8**, refs pp9–11, zero overfull, suppl 12 pp
  rebuilt, `audit_paper2.py` ALL GREEN, zero rendered kinkin/TODO (the
  one suppl "ICLR" token = the legit ICLR-2024 survey cite).

## Revision list — claim-by-claim verdict (style of the round-3 table)

| # | Claim | Verdict | State |
|---|---|---|---|
| R1 | all-synthetic; pot "not blind" | half-true / garbled | Scope caveat already in abstract+§7 headline; protocol IS blind (frozen config), but the target certificate is inherent to a fixed-target method. **ADOPTED verbatim**: pot = "a controlled real-world proxy, not a blind test" (§4). Datasets → memo below. |
| R2 | "fails on open boundaries, hallucinates H2 void" | mischaracterization | That is OUR pre-registered §F delta, in print since round 4: the mouth caps at working α (the pot's mechanism); designed-rim-vs-noise-born-bars distinction + bar-filtering next step already in §7/§F. Legit residue: misspecified-target robustness → memo. |
| R3 | greedy lacks theory; C2 too aggressive; "add norm-matched control" | half-false | Matched term IS Hungarian-optimal; only recruitment is greedy and greedy≡optimal in every logged regime (single-bar missing set) + Lemma 1 — all in print. C2 IS the norm-matched control (same ρ, same channel) — the ask misreads the design; C2g gentler variant printed (§7). NEW & good: scrambled-target control → memo. |
| R4 | no wall-clock; O(M log M) ignores baseline | half-false | §5 Overhead ¶: 33–41 s baselines, +46 s fixed, 174 ms refresh, 46/(T+46) projection ≈7% — the projection is exactly baseline-relative. Missing: GPU memory, timing-vs-M curve → cheap batch. M guidance = the floor rule itself (§4, pot ran it prospectively). |
| R5 | Topology-GS missing; tone attacking; add implicit baselines | first two FALSE | Cited since round 3; partition promoted round 4; tone now literally "complementary". Implicit topology benchmark → recommend AGAINST this cycle (the §2 partition argument: inputs/outputs/cost regimes don't align; Table S6 positions them; right venue = the real-scan phase). |
| R6 | 1.15× and 6·r_med arbitrary; failure analysis shallow | pre-answered / partly fair | Parity: "never did any work — every passing arm ≤ baseline" is in print (§4). Floor: derived + validated (M^(−1/2) law, S10). Fair residue: floor-multiplier sweep (4–8×) re-analysis + spot failure-case figure → cheap batch. |
| R7 | pair-frozen stability unanalyzed; 3–5 seeds too few; i.i.d. noise unrealistic | partly fair | Refresh logs already record per-refresh matched/diag/recruit/unreached → pair-stability plot is FREE → cheap batch. Seeds n≥10 = real decision (below). §5 already says C7 ≠ scan realism; structured-noise C7d (region dropout) → memo. |
| R8 | unreadable, no bullets; eq (2) unclear; certification circular | partly fair | **FIXED**: eq (2) now defines p_i; certification independence explicit (exact simplicial homology × per-component Euler, neither the sampled alpha complex — src: make_kinkin_asset.py 5b/5c). RH list IS a numbered list + bolded run-in contributions (round-4 trade); itemize costs ~4 lines — skipped, say so in reply. |
| R9 | ratios mislead; no Wasserstein; no code | mostly false | Both tables print absolute mean±sd AND ×-ratios side by side. W₂ eval column → optional re-analysis. Code: release commitment printed §8; anonymized zip = your task before the Sep 2 suppl deadline. |

## The datasets ask — DECISION MEMO (the one thing that needs a call)

**The structural problem the AI table ignores: the method requires a
target diagram** (known or certified topology). DTU objects are
table-top scans with open bottoms and no GT topology; TnT scenes have
no meaningful Betti targets ("the genus of Barn"?); Objaverse random
50–100 is mostly non-watertight soup — the exact defect that excluded
ShapeNet (§4).

Feasible, honest versions (pre-registered-probe style, like §F):
1. **DTU object probe** (1–2 scans with clear void/handle structure):
   ingest→certify the reference surface exactly like the pot;
   staircase decides observable+M; C0/C1/C2 × 3 seeds. ~1–2 GPU-days
   incl. COLMAP glue. If certification of a noisy scan fails, that is
   itself a reportable §7 result. **Recommended IF the advisor accepts
   certified-target framing — it is his own "controlled real-world
   proxy" label applied to DTU.** Kills the Critical-row objection.
2. **Thingi10K genus sweep INSTEAD of Objaverse** (watertight subset,
   genus metadata, already cited): ~50 meshes × C0/C1 × 3 seeds ≈ 300
   toy-scale runs ≈ 1–2 GPU-days → the "topological error rate"
   statistic he wants, with real ground truth. **Recommended as the
   Objaverse replacement.**
3. **TnT scene-level: push back** — no target diagram exists at scene
   scale; defer to the dental/real-scan phase. Recommended: no.

Other new-science menu (advisor to pick, 3DV deadline Aug 28):
- **Scrambled/wrong-target control C8** (also answers R2's misspec
  robustness): torus+1 external × 3 seeds ≈ 1–2 GPU-h. Recommended.
- **Seeds n=10 on decisive shapes** (sphere, torus; all arms): ≈60 runs
  ≈ 2–3 GPU-h; every tab:main number changes → audit re-run;
  strengthens σ claims. Do only with advisor sign-off.
- **Structured-noise C7d** (plan-cloud region dropout): small code +
  ~1 GPU-h. Recommended over "SfM error" (needs a real pipeline).
- Hungarian-vs-greedy A/B: skip — they provably coincide here (single
  missing bar); Sinkhorn = different gradient design, future work.

**Cheap batch (no new training, no main-number changes — can run on
your word alone):** floor-multiplier sweep (re-threshold recorded
diagrams), pair-stability plot (existing logs → suppl fig), GPU
peak-memory + refresh-timing-vs-M staircase (loss-eval only, one §5
sentence), optional W₂ eval column, spot failure-case figure.
≈ half a day total.

## For the Thai reply (fold into the UNSENT Gmail draft
r-1323288373779606130 — it still carries round 4 + the SA-poster
question, **deadline Jul 31, now 12 days away**)

สรุปสำหรับอาจารย์ (draft, merge into the existing draft):
- ตรวจ 4 อ้างอิงแล้ว **จริงทั้งหมด**: MeshSplatting = CVPR 2026 oral
  (เพิ่มใน related work แล้ว); Triangle Splatting ตีพิมพ์ 3DV 2026 จริง
  (อัปเดต bib เป็นฉบับ camera-ready 11 คนแล้ว); Radiant Triangle Soup
  มีจริงและถูก cite อยู่แล้ว แต่สถานะ ICLR 2026 ยืนยันไม่ได้จากแหล่ง
  ทางการ จึง cite เป็น arXiv; DiffSoup CVPR 2026 ยืนยันแล้ว
- ปรับ Related Work ตามตารางของอาจารย์ครบ: ย่อหน้า triangle-turn ใน
  Introduction, ประโยคเชื่อม persistence→triangle, ตั้งชื่อ Radiant
  พร้อม contrast, ปิดท้าย section ด้วยช่องว่าง 3 มิติ (representation ×
  optimization × objective) — ทั้งหมดยังจบหน้า 8 พอดี, audit ผ่านหมด
- Revision list: หลายข้อมีในกระดาษอยู่แล้ว (ชี้ตำแหน่งให้ในตาราง NOTES);
  แก้เพิ่มแล้ว: นิยามตัวแปรสมการ (2), ความเป็นอิสระของ certificate,
  ป้าย "controlled real-world proxy" ตามคำของอาจารย์
- เรื่องชุดข้อมูล: DTU/TnT/Objaverse ติดปัญหาเชิงโครงสร้าง (วิธีเราต้องมี
  target topology) — เสนอทางที่ทำได้จริงก่อนเดดไลน์: (1) DTU probe แบบ
  ingest→certify 1–2 ฉาก (2) Thingi10K genus sweep แทน Objaverse
  (มี ground truth จริง) (3) TnT ขอเลื่อนไปเฟส dental — ขอให้อาจารย์
  เลือกรายการที่จะให้รัน (รายละเอียด+ต้นทุนใน NOTES)
- ย้ำคำถามโปสเตอร์ SA 2026 (เดดไลน์ 31 ก.ค.)

---

# PAPER 2 — ADVISOR ROUND 4 (mock review + figure specs) — EXECUTED 2026-07-17

**What arrived (2026-07-17, Downloads):**
`3DV2027_review_actionable_revisions.pdf` (an AI-generated mock 3DV
review — verdict "Weak Accept, borderline", 3 Major items, per-paragraph
table) + `Revision list (9).pdf` (advisor Thai: 5 figure specs, the
fandisk-vs-pot question for Fig 4, "check the page limit / draft me a
short outline", "example images lack texture", 2 AI actionable tables,
an AI restructure skeleton with placeholders).

## Audit verdict (vs round 3's 85–95% fabrications: this round is largely grounded)

- The mock review was generated against the REAL current main.pdf — its
  citation numbers [14]/[15]=gao2025genus/gao2026homology,
  [24]=jignasu2024stitch, [45]=shen2025topologygs match our alphabetical
  bibliography exactly; even the teaser's "0.977" is the real Table-S1
  punctured-void Chamfer.
- FALSE: "[90] Thingi10K lacks year" (refs.bib has year=2016, verified).
  Garbled: "232 boundary edges" (= 232 non-manifold junction edges; 50
  boundary after weld). PDF-2's [41]/[73] numbering is the SUPPL
  bibliography's. The Fig-4 spec's "double torus: baseline fuses loops"
  contradicts our data (saturated identically in every arm) and
  "phantom handles circled in C2" mislabels the mechanism (C2 DESTROYS
  features; phantoms = allocation-B2 4.4-vs-2 and spot's C0).
- `paper2/main.bbl` on disk is a stale pre-round-3 artifact — never
  diagnose from it; the PDF is fresh.

## What was executed (2026-07-17, all rebuilt + audited green)

**Title tempered** `Topology-Correcting` → **`Topology-Aware`** (both
docs; the advisor's own table asked for it; H0 null + floors ground it).

**Statistics hygiene (the review's cleanest hit):** Welch σ now quoted
only where both arms ran five seeds. tab:gen's n=3 σ column
(6.1/26.1/35.7/80.1σ) retired → verdicts rest on disjoint per-seed
ranges; **new suppl Table S7** (per-seed tails, run order, all
three-seed shapes incl. pot from quicklook) + reporting-policy sentence
in §4 + cube's 18.5σ replaced by ranges in prose. Double torus marked
descriptive (n=2). σ kept: sphere 16.2 (n=5), C6 0.6/12.4/1.5 (n=5).

**Figures (the round's core):**
- **Fig. 1 = teaser + qualitative matrix merged** (p1, in the title
  block via `\twocolumn[{\@maketitle …\captionof{figure}…}]` — a plain
  figure* defers to p2). Rows fandisk + tom-yum pot (the advisor's own
  lead pair), cols GT/C0/C2/C1, rendered from seed-0 `final_params.pt`
  by **NEW `scripts/make_matrix_figure.py`** (CPU raycast, neutral gray
  per the advisor's teaser spec; GT normalized into the scene frame —
  fandisk.obj is in raw CAD coords, scale 0.268).
  **Honesty decision:** the advisor's red-circled "phantom handles"
  don't exist visually (topology is a diagram READING) — each cell
  instead carries a **measured-count badge** (true #sig vs read;
  Okabe-Ito blue-outline=correct / filled-vermillion=wrong,
  grayscale-safe). Badge data = results.json nsig_final +
  quicklook nsig_H2, identical across seeds.
- **bob strip → suppl Fig. S8** (loop-class row of the matrix; β₁ 2→1
  under C2). fig:series → **suppl Fig. S6**; fig:tomyum → **suppl
  Fig. S7** (numbers preserved; S2–S5 numbering untouched by appending
  after S5). The blindness mini-table built mid-round was folded back
  to prose (all three probe ratios now inline in §2) once Fig. 1
  covered the visual form — suppl Table S1 unchanged.
- **NEW suppl Table S8**: ρ sweep + ramp-window numbers moved from
  main prose (the review asked for exactly this table).

**Main-text additions:** Lemma 1 (zero-gradient under absence, proof
sketch; separated from recruitment's *empirical* self-correction in §7);
greedy≡optimal justification from the refresh logs (missing-target set
is a single bar in every logged regime); "significant" defined at first
use in §3.1; per-refresh Gabriel claim strengthened (verified 2026-07-17:
**zero failures in all 5,560 logged refreshes** — scratchpad
gabriel_scan.py over every topo_loss_log.json with the refresh schema);
K=10 justified as amortization; C4 numbering-gap note in §3.5;
DiffSoup-implementation provenance in §4; tail window stated (last 3
dumps = steps 2,300–2,500, per topo_loss_report.py --tail default);
overhead projection 46/(T+46) (≈7% of a 10-min run); C7 framed as a
probe, not scan realism (+ non-Gaussian ack in §7); spot count-limit in
§7; **reproducibility statement** in §8 (release commitment approved by
author 2026-07-17); abstract rewritten top-down with the scope caveat
(synthetic/closed/known-target = not blind capture); RH1–3 now a
numbered list (review ask), contribution bullets run-in; suppl §D.7's
three-criteria partition promoted to §2 as the per-method infeasibility
argument (chosen over an empirical STITCH/Topology-GS comparison —
inputs/outputs/cost regimes don't align).

**Page fit:** body ends **exactly p8** again (refs pp9–11 main;
suppl now 12 pp, refs from p9). Paid by: fig:series+fig:tomyum+bob-row
to suppl, tab:gen single-column (all-PASS folded into caption; 2.3%
resizebox), pot-ingest mechanics compressed into suppl Table S4 (raw
6,318-vert count added there), ρ/window numbers → S8, and a
document-wide redundancy pass (~6 rounds; every number kept verbatim
with its % src; the only numbers that left main went to suppl tables).
Zero overfull hboxes in both docs. `audit_paper2.py` extended
(range-disjointness + printed-range + per-seed-list + C6-sd checks;
n=3 Welch checks downgraded to informational) — **all numeric checks
pass**; no rendered kinkin/TODO; anonymity intact.

## Round-4 completion state (updated 2026-07-17, second pass)

1. ~~Suppl pipeline+recruitment diagram + floor chart~~ **DONE**:
   **Fig. S9** (`scripts/make_pipeline_figure.py` — system block diagram
   + recruitment schematic inset, labeled schematic) and **Fig. S10**
   (`scripts/make_floor_figure.py` — floors vs M with the M^(-1/2) law;
   every plotted value transcribed from the RECORDED 2026-07-09 density
   sweep with sources, since regeneration is blocked, below). Main-text
   pointers added in §3.2 and §6; body still ends exactly p8.
2. **⚠→✔ SAC blocker WORKED AROUND (2026-07-17, later).** Windows Smart
   App Control (On) blocks gudhi **3.12.0**'s DLLs — but the verdicts
   are per-binary and the **gudhi 3.11.0 wheel passes**. Stable copy:
   `tools\gudhi311` (gitignored, next to tectonic), activated via
   `$env:PYTHONPATH = "D:\Project\CG-Soup-Topology\tools\gudhi311"`.
   **Numerical equivalence verified BEFORE use**: `density_bound.py`
   under 3.11.0 reproduces every recorded 3.12.0 number exactly
   (floors, tube lifetimes, 1.33× margin, r_med ratio 3.16, eval floor
   .0171). Version substitution recorded here for protocol
   transparency; SAC itself untouched (turning it off is irreversible
   — remains your call whether to bother now that the workaround
   holds). **Double-torus seeds 2–4 relaunched under 3.11** (exact
   pre-registered flags: `--shapes double_torus --seeds 2 3 4
   --conditions C0 C1 C2 --rhos 0.1 --steps 2500 --max_faces 2000
   --loss_dims 1`).
3. **Open-surface probe: EXECUTED AND PASSED (2026-07-17/18)** —
   `OPEN_SURFACE_PROBE_PLAN.md` end-to-end under the pre-registered
   design: bowls certified (disk topology, 1 rim, χ=1); staircase
   overruled our bowl_wide expectation (**both** bowls read one H2
   void; the designed rim's H1 never clears — recorded delta);
   backface check PASS (interior renders, no holes); C-matrix
   verdicts: **narrow 4.2× (.0588→.0138), wide 4.1× (.0560→.0137),
   both at better-than-baseline Chamfer with disjoint seed ranges;
   the control erases the wide bowl's void in 2/3 seeds and pays
   3.1–3.5× worse Chamfer.** In print: main §7's promise is now the
   result + abstract scope updated ("closed surfaces plus a first
   open-surface probe"); full account suppl §F (Tables S9/S10); audit
   extended, all green; body still exactly p8. The double-torus seed
   raise (item 2) also landed in print (n=5, saturation identical).
4. Voice pass (unchanged TODO(human) markers), paper ID, 2027-kit swap.

## Draft message to อาจารย์ (round 4 — merges the unsent round-3 reply; SEND THIS)

> เรียนอาจารย์ครับ
>
> ผมได้รับชุด revision รอบใหม่ (review report + revision list) ครบแล้ว
> และดำเนินการหลักเสร็จแล้วครับ ตรวจตัวเลขทุกตัวกับผลทดลองจริงก่อนใช้
> — รอบนี้เอกสาร AI แม่นกว่ารอบก่อนมาก (เลข citation ตรงกับ PDF จริง
> ทุกตัว) มีคลาดเคลื่อนเล็กน้อย เช่น entry Thingi10K มีปีอยู่แล้ว และ
> double torus ในสเปครูปที่ 4 — ผลจริงอิ่มตัวเท่ากันทุก arm จึงไม่มีภาพ
> ความต่างให้โชว์ครับ
>
> **จำนวนหน้า:** 3DV บังคับ 8 หน้ารวมรูป/ตาราง (หน้า references
> ไม่นับ, supplementary แยกส่ง 2 ก.ย.) — ตอนนี้เนื้อหาจบหน้า 8 พอดี
> หลังใส่รูปใหม่แล้วครับ
>
> **สิ่งที่ทำแล้วตามลิสต์อาจารย์:**
> 1. **รูป Teaser + Qualitative Matrix รวมเป็น Figure 1 หน้าแรก**
>    ("ภาพเดียวจบ" ตามคอนเซปต์อาจารย์): แถว fandisk + หม้อต้มยำ
>    (คู่ที่อาจารย์เสนอ) × คอลัมน์ GT / baseline / control / ours
>    เรนเดอร์จากผลเทรนจริง seed 0 — แถว bob (loop) อยู่ใน suppl Fig S8
>    เพราะพื้นที่ 8 หน้าครับ จุดสำคัญ: "phantom handles" วงแดงตามสเปค
>    ไม่มีให้เห็นในภาพจริง (topology เป็นค่าที่วัดจาก diagram ไม่ใช่สิ่ง
>    ที่ตามองเห็นเสมอ) ผมจึงใส่ป้ายตัวเลข #sig ที่วัดได้จริงในทุกช่องแทน
>    — ซื่อสัตย์กว่าและกรรมการตรวจสอบได้ครับ
> 2. **ลดชื่อเรื่องเป็น "Topology-Aware"** ตามตารางของอาจารย์
>    (ผล H0 null + measurement floor ทำให้ "Correcting" แรงเกินหลักฐาน)
> 3. **แก้สถิติทั้งเล่ม:** เลิกใช้ Welch σ กับ n=3 (ตาราง generality
>    เปลี่ยนเป็น per-seed ranges ที่แยกขาดกันทุกตัว + ตารางค่า per-seed
>    ใน suppl Table S7), เพิ่ม Lemma zero-gradient, ตาราง ρ/ramp sweep
>    (suppl Table S8), reproducibility statement, เกณฑ์แยกงานคู่แข่ง
>    3 ข้อจาก suppl D.7 ยกเข้า main แล้วครับ
> 4. **เรื่อง texture:** ภาพ training ตั้งใจเป็นสีเดียว (แยก channel
>    topology จาก photometric — ระบุในเปเปอร์) ส่วนรูป showcase
>    มี material ครับ (หม้ออะลูมิเนียมอยู่ suppl Fig S7; Figure 1 ใช้
>    เทาอ่อน studio ตามสเปคอาจารย์)
>
> **อัปเดตเพิ่ม (ทำเสร็จแล้วทั้งหมดครับ):** รูป pipeline + กราฟ
> measurement floor เข้า supplementary แล้ว (Fig S9/S10), double torus
> รันเพิ่มเป็น 5 seeds แล้ว (ผลอิ่มตัวเท่าเดิมทุก seed — ปิดข้อท้วง
> n=2), และ **open-surface stress test รันแล้ว ผ่านทั้งสองรูปทรง**:
> ชามเปิดปากแคบ/กว้างที่ตัดจากทรงกลม loss ลด error ของ void
> 4.2×/4.1× ที่ Chamfer ดีกว่า baseline โดย control ทำ void หายใน
> 2/3 seeds — เข้าเปเปอร์แล้วครับ (§7 + suppl §F; เนื้อหายังจบหน้า 8
> พอดี audit ผ่านหมด)
>
> **ค้างจากรอบก่อนครับ: SA 2026 poster (เดดไลน์ 31 ก.ค.)** อาจารย์
> อยากให้ส่งคู่ขนานไปด้วยไหมครับ
>
> ขอบพระคุณครับ

---

# PAPER 2 — ADVISOR ROUND 3 (AI revision package) — EXECUTED 2026-07-16

**What arrived (2026-07-16):** 4 public claude.ai artifacts
(`3DV_2027_REVISION_STRATEGY.md`, `PRIORITY_CHECKLIST_IMMEDIATE.md`,
`LITERATURE_REFERENCE_PLAN.md`, `EXECUTIVE_SUMMARY_REVISION_GUIDE.md`) +
`3DV_2027_FINAL_COMPLETE_PAPER-1 (1).pdf` (20 pp, an HTML artifact printed
via wkhtmltopdf). Same pattern as round 2: the advisor ran the submission
through an AI. The PDF is a REWRITE SKELETON (placeholders "FILL IN TABLE
2", "[7-44] ADD COMPLETE REFERENCES", "Revision Date: January 2025") — not
a draft to adopt.

## ⚠ Fabrications found (never paste its text)

| its claim | reality (checked against our sources) |
|---|---|
| random controls recover **"85–95%"** of the void gain (in its abstract+intro!) | from Table S2 (B0/B4/B5): cylinder ≈77%, sphere ≈90%, cube ≈101% — the paper's "most of the gain, small shape-dependent residual" is the correct wording |
| pot void clears floor at M=8192, "**3.1× denser** than std" | 8192/2048 = **4×**; 3.1× is the unrelated 20k-eval floor margin |
| pot challenges: "specular metallic BRDF confuses photometric loss", "no texture" | training renders are **constant-albedo diffuse** (`make_synthetic_scene.py shade_mesh`); the aluminium exists only in the showcase figure. "DiffSoup allocates triangles to specular regions" = invented |
| "p<.001 / p>.05" | we report Welch σ, not p-values |
| review-score projection 6.4→8.1/10, "+1.7–2.5 points" | theater; ignore |
| its reference list | Alliez under wrong venue; "DAVIS 3D Segmentation" does not exist; TanksAndTemples/Furukawa venues wrong |
| names hypotheses **H1/H2/H3** | collides with homology H0/H1/H2 in the same sentences → renamed **RH1–RH3** in print |

Several of its "additions" were already in the paper verbatim (discussion
mechanism sentences, all four "threats to validity" items, the classical
repair citations, figure error bands).

## What was adopted / adapted / rejected (this commit set)

**Adopted in MAIN (body still ends exactly p8; audit all-green, zero
overfulls):**
- intro reframed: decade-long implicit hypothesis → controlled test →
  null result → objective-centric reformulation; **RH1 (diagnosis) / RH2
  (specificity) / RH3 (complementarity)** named, each tied to its
  pre-designed condition (suppl §A / C2 / C5); results-preview ¶ and
  conclusion tag the RH verdicts; C2/C5 tagged in §3.5.
- related work: optimization-philosophy cut (geometry-/sampling-/
  topology-oriented) grafted onto the four-position map + pointer to new
  suppl Table S6.
- discussion now opens with "A local signal cannot carry a global
  property — sparse tugs can." (merged with the sparse-tugs ¶).
- **NEW concurrent-work citations** (see threat sweep below).
- Paid for by trims: three duplications removed (C2g numbers now printed
  only in Limitations; C6-sphere noise pair only in Limitations; "earns
  its keep" only in intro), stretch-case detail + C7 internals moved to
  suppl §B, fig widths 0.455→0.415 (series) and 0.405→0.365 (pot),
  wording tightened throughout. Every number kept with its % src.

**Adapted into SUPPL (now 10 pp incl. ~4 pp refs; builds clean):**
- §B: pot **challenge inventory (Table S4)** — honest rows only (raw-soup
  defects, certificate, sub-floor loops, flue-void floor rule, in-loop
  outcome); **floor staircase (Table S5)** (1,0,0)@2048/4096 →
  (1,0,1)@8192/20000, margin 1.20–1.23×; plus the moved stretch-case and
  C7-internals paragraphs.
- **NEW §D survey** "A decade of reconstruction, cut by optimization
  philosophy": Table S6 matrix (27 methods incl. the nearest concurrent
  work; the empty topology-objective cell is visually ours) + D.1–D.7
  prose. refs.bib 46 → **108 entries**, every new entry web-verified
  2026-07-16 with a provenance comment (6-agent sweep, 85 candidates →
  58 kept). supplementary.tex now emits its own bibliography.

**Rejected:** the rewrite PDF wholesale; Figure 1A paradigm cartoon (the
taxonomy prose does the work; fig:tomyum's cutaway already serves as the
challenge visual); 150–200-ref inflation (curated ~108); all fabricated
numbers above; "first of its kind"/"scientific discovery" superlatives.

## Post-commit verification (2026-07-17, clean tree @ `7f634e9`)

Independent full rebuild + re-audit after the round-3 commits — **all
green**:

- `audit_paper2.py`: every numeric check passes (main tables, generality
  table, pot row, reductions/σ, prose claims, allocation-study numbers,
  ramp pilots). Its "C5-vs-prior" line used to print a stale "(paper:
  ~.038, 4.6x)" annotation from before the 07-11 fix — the paper prints
  4.4× (source 4.37×); the annotation is now corrected in the script.
- tectonic: both docs compile clean; **zero overfull hboxes** in either
  log.
- PDF-extracted checks: body ends **exactly at p. 8**; supplementary is
  **10 pp**; zero rendered "kinkin"/"TODO"; fully anonymous (no author
  name/affiliation/email renders); paperID = ***** in both docs; suppl
  Tables S1–S6 and Figures S1–S5 all present and numbered in order.
- **New since the last record: main refs now fill pp. 9–11** — the
  round-3 concurrent-work cites pushed the final entry's three-line tail
  onto a near-empty p. 11. Compliant (3DV counts only the 8-page body;
  reference pages are free), purely cosmetic — re-glance after the voice
  pass / 2027-kit swap, pagination reflows anyway.
- refs.bib has carried two never-cited spares since the first skeleton
  (`edelsbrunner2010book`, `palfinger2022remeshing`); they render
  nowhere. Optional: cite Edelsbrunner–Harer as PH background during the
  voice pass, or leave them.
- **3DV 2027 author kit: still NOT posted** (3dvconf.github.io/2027 main
  + call-for-papers pages checked 2026-07-16). Keep the vendored 2026
  kit; re-check around early August.

## Concurrent-work threat sweep (de-risking, all web-verified 2026-07-16)

**Verdict: the novelty gap HOLDS** — no prior/concurrent work measures a
differentiable topological quantity of the *evolving surface* inside
*image-based* training under a *primitive budget*. Four near-misses are
now cited in main related work (a skimming reviewer would flag their
titles if uncited):

| work | what it actually does | our distinction |
|---|---|---|
| Topology-GS (AAAI 2025, `shen2025topologygs`) | PersLoss on barcodes of **rendered images** + PH-guided densification | image-space perceptual term; surface diagram unmeasured; adds primitives (no budget) |
| Gao et al. (3DV 2026 poster, `gao2025genus`) | high-genus mesh inverse rendering; genus fixed by Gauss–Bonnet-matched **template** | topology assumed a priori, never measured in the objective |
| Gao et al. (ICASSP 2026, `gao2026homology`) | PH computed **once** on a reference shape → camera placement | preprocessing prior, not a loss |
| STITCH (arXiv, `jignasu2024stitch`) | differentiable PH (β₀) on a live **implicit** surface | point-cloud input: no images, no primitives, no budget |

Also cited: Radiant Triangle Soup (`burgdorfer2025radiant`) — nearest
representation neighbor (soup + "soft connectivity forces", purely
geometric). Rebuttal one-liner: *they assume, prescribe, or render
topology; we measure the reconstruction's own diagram in the loss, under
a fixed budget.* Flagged for a library check (paywalled, unverifiable
here): TopoGen (CGF 2025), TopoNet (CGF 2022), "topology-enhanced
DeepSDF" (CAD 2026).

## Reviewer-FAQ bank (corrected from the package; safe for rebuttal)

- **"Why not a better geometric regularizer?"** C2 is exactly that, norm-
  matched through the identical channel — and it is destructive (pins the
  void 2.2× worse; erases the cube void; collapses a torus loop). The
  gentle variant is still 1.6× worse. Ordering C1 < C0 < C2g < C2.
- **"The allocation nulls are just bad priors."** B0–B5 include topology-
  informed fields at two widths plus width-matched random controls; the
  *best* torus arm is the random control (.0267 vs .0316), and
  concentration manufactures phantoms (4.4 vs 2). Structural, not a
  tuning failure. (Do NOT say "85–95%" — say "most of the gain,
  shape-dependent residual: cylinder 4.6σ, sphere 2.2σ, cube tie".)
- **"Only four external meshes; what about real scans?"** Acknowledged in
  §7; the pot is the ingest→certify dress rehearsal (232 junction-edge
  defects, 9 open shells → certified genus 3); bar-filtering
  boundary-born features is the named near-term step; a synthetic
  open-surface stress test comes first.
- **"CUDA noise 7–10% could mask effects."** Noise enters at resampling,
  before the loss; a loss-identical pair lands 6% apart; effects are
  2.1–10.4× with Welch σ from 6.1 to 80.1; C7/C7h shows graceful
  degradation under injected sensor noise.
- **"Recruitment is ad hoc."** It repairs a *proven* zero-gradient
  pathology of optimal matching; the toys probe its location-blindness;
  C6 shows it is load-bearing (torus win collapses to 0.6σ from baseline
  without it).
- **"Why no Neuralangelo/SuGaR comparison?"** Different cost regime
  (dense field / post-hoc extraction vs a fixed 700–2000-triangle
  budget); the philosophy table (suppl Table S6) positions them; a
  budget-matched comparison is future work, not a hidden loss.

## Draft message to อาจารย์ (round 3)

> เรียนอาจารย์ครับ
>
> ผมอ่านชุด revision ที่อาจารย์ส่งมา (4 ลิงก์ + PDF) ครบแล้วครับ
> แนวคิดหลัก — เปลี่ยน framing จาก "เพิ่ม topology loss" เป็น
> "allocation คือช่องทางที่ผิด ต้องแก้ที่ objective" — ผมเห็นด้วยและ
> ใส่ลงเปเปอร์แล้วครับ:
>
> 1. **Intro เขียนใหม่** ตามโครงที่แนะนำ: สมมติฐานเดิมของสาย
>    connectivity-free → ผลทดสอบ allocation (null result) → ย้าย
>    topology เข้า objective พร้อมตั้ง research hypotheses
>    **RH1/RH2/RH3** อย่างชัดเจน (ผมเปลี่ยนชื่อจาก H1–H3 เป็น RH1–RH3
>    เพราะ H1/H2 ชนกับ homology class ในประโยคเดียวกันครับ)
> 2. **Related work จัดกลุ่มตาม optimization philosophy**
>    (geometry- / sampling- / topology-oriented) พร้อมตาราง
>    methods-by-philosophy 27 วิธี (Table S6 ใน supplementary
>    เพราะ main จำกัด 8 หน้า)
> 3. **ตาราง stress-test ของหม้อต้มยำ** (Table S4) + ตาราง floor
>    protocol (Table S5) — ผมตัด 2 แถวของร่าง AI ออก
>    (specular BRDF / no texture) เพราะภาพ training จริงเป็น
>    diffuse สีเดียว โลหะมีเฉพาะในรูป showcase ครับ
> 4. **Literature survey เพิ่มเป็น 108 อ้างอิง** (curated ตามที่ตกลง
>    ~100 ไม่ถึง 150–200 ของร่าง) — ทุกรายการใหม่ตรวจกับ
>    arXiv/ACM/Crossref แล้ว เพราะร่าง AI มี citation ผิด/ไม่มีจริง
>    ปนอยู่ครับ
> 5. **สำคัญ:** ผมกวาดงานคู่แข่ง 2024–2026 เพิ่ม พบ 4 งานใกล้เคียง
>    ที่ต้อง cite กันโดน reviewer ท้วง (Topology-GS ของ AAAI'25,
>    งาน high-genus ของกลุ่ม Gu ที่ 3DV'26/ICASSP'26, และ STITCH)
>    — ตรวจแล้ว **ช่องว่างของเรายังอยู่**: ยังไม่มีใครวัด persistence
>    ของพื้นผิวจริงใน loss ระหว่าง train จากภาพ ภายใต้ triangle
>    budget ครับ
>
> ตัวเลขทุกตัวในเปเปอร์ยังตรง audit script เดิม, เนื้อหา main จบที่
> 8 หน้าพอดีตามเกณฑ์ 3DV ครับ ข้อเสนอบางส่วนของร่าง (คะแนน
> review ที่คาดการณ์, ตัวเลข 85–95%, M=8192 "3.1×") เป็นตัวเลขที่
> AI สร้างขึ้นเอง ผมแก้เป็นตัวเลขจริงจากผลทดลองแล้วครับ
>
> อีกเรื่องที่ค้างครับ: **SA 2026 poster (เดดไลน์ 31 ก.ค.)**
> อาจารย์อยากให้ส่งคู่ไปด้วยไหมครับ

---

# PAPER 2 — 10-YEAR RELATED-WORK SWEEP (advisor request, 2026-07-13 later)

**Advisor asked: หา related works 10 ปี ที่สนับสนุนหรือเห็นต่างกับแนวคิด
ใช้ DiffSoup มา reconstruct, ใส่เพิ่มก่อนส่ง — DONE (this commit).**

`related.tex` ¶1 is rewritten as a **four-position map of gradient-based
reconstruction (2018–2026)** — the "support or disagree" framing the
advisor asked for, as positions rather than a cite-dump. **16 new
references, EVERY entry web-verified 2026-07-13** against its arXiv
abstract page / CVF open-access listing / ACM DOI (provenance comment on
each entry in refs.bib; the grounding contract held — nothing cited from
memory, page numbers only where read off a publisher listing):

| # | position | stance on soup-based reconstruction | works added |
|---|---|---|---|
| (i) | Implicit / neural fields | **เห็นต่าง** — strongest counter-position: topology correct *by construction*; costs dense field evaluation + post-hoc mesh extraction | Occupancy Networks (CVPR'19), DeepSDF (CVPR'19), NeRF (ECCV'20), NeuS (NeurIPS'21), Neuralangelo (CVPR'23) |
| (ii) | Fixed-connectivity templates | **เห็นต่าง** — manifold by construction but genus frozen at the template's | Pixel2Mesh (ECCV'18), Point2Mesh (SIGGRAPH'20) |
| (iii) | Differentiable iso-surfacing | **เห็นต่าง** — the strongest modern alternative: topology via a volumetric scaffold, at grid cost | DMTet (NeurIPS'21), nvdiffrec (CVPR'22), FlexiCubes (SIGGRAPH'23), Shape-as-Points (NeurIPS'21, bridges soups→implicits) |
| (iv) | Connectivity-free primitive soups | **สนับสนุน** — our lineage: fastest, easiest to budget; even surface-minded members regularize only *geometry*, never measured topology | DIB-R (NeurIPS'19, lineage), DSS points (SIGGRAPH Asia'19), AtlasNet patches (CVPR'18), 2DGS (SIGGRAPH'24), SuGaR (CVPR'24) + already-cited 3DGS / Triangle Splatting / DiffSoup |

Punchline now in print: *(i) and (iii) solve topology representationally;
(iv) had not addressed it — the gap this paper fills at the soup's budget
and speed.*

**Page budget held: body still ends exactly at page 8** (references pp.
9–10, now 46 bib entries). The new paragraph was paid for with ~30 lines
of wording trims across intro/method/setup/results/discussion/
limitations/conclusion — **no number changed, every % src comment kept**;
`audit_paper2.py` re-run: all numeric checks pass, zero overfulls.
One content note for your voice pass: the conclusion's future-work list
was compressed to "next: open surfaces and real scans" (the full list
still lives item-by-item in §7), and setup's CUDA sentence now defers to
§7's Nondeterminism block instead of repeating it.

**Draft message to อาจารย์ (related-work sweep):**

> เรียนอาจารย์ครับ
>
> ตามที่อาจารย์แนะนำ ผมเพิ่ม related works ช่วง 10 ปี (2018–2026) ที่
> สนับสนุน/เห็นต่างกับแนวคิดใช้ triangle soup แบบ DiffSoup ในการ
> reconstruct ลงใน related work ของ paper 2 แล้วครับ — เพิ่ม 16 อ้างอิง
> (ตรวจ metadata กับ arXiv/CVF/ACM ครบทุกรายการ) จัดเป็น 4 กลุ่มครับ:
>
> 1. **Implicit fields** (เห็นต่างชัดที่สุด): Occupancy Networks, DeepSDF,
>    NeRF, NeuS, Neuralangelo — ได้ topology ถูกต้องโดยโครงสร้าง แต่แลกกับ
>    field หนาแน่นและต้อง extract mesh ภายหลัง
> 2. **Template deformation** (เห็นต่าง): Pixel2Mesh, Point2Mesh —
>    manifold เสมอ แต่ genus ถูกล็อกตาม template
> 3. **Differentiable iso-surfacing** (เห็นต่าง — คู่แข่งหลักในปัจจุบัน):
>    DMTet, nvdiffrec, FlexiCubes (+ Shape as Points) — ได้ topology ผ่าน
>    volumetric grid โดยจ่ายราคาที่ grid
> 4. **Primitive soups** (สนับสนุน — สายที่เราต่อยอด): DSS, AtlasNet,
>    3D/2D Gaussian Splatting, SuGaR, Triangle Splatting, DiffSoup —
>    เร็วที่สุดและคุม triangle budget ง่ายที่สุด แต่ยังไม่มีงานไหนวัด
>    topology จริง ๆ
>
> ข้อสรุปที่เขียนในเปเปอร์: กลุ่ม 1 และ 3 แก้ topology ด้วยตัว
> representation ส่วนกลุ่ม 4 ยังไม่เคยแก้ — ช่องว่างนี้คือสิ่งที่ paper 2
> เติม โดยยังรักษาความเร็วและ budget ของ soup ไว้ครับ เปเปอร์ยังอยู่ใน
> 8 หน้าตามเกณฑ์ 3DV ครับ

---

# PAPER 2 — 3DV 2027 SUBMISSION FORMAT (2026-07-13)

**VENUE DECIDED: อาจารย์ agreed with 3DV (you, 2026-07-13).** Timeline
(re-verified on the official 3DV 2027 site today): **papers due
2026-08-28**, supplementary 2026-09-02, preliminary notification
2026-10-27, final 2026-12-02, conference Apr 6–9 2027 (Thessaloniki).
Limit: **8 pages incl. figures/tables; reference-only pages free;
double-blind via OpenReview.** Risk chain unchanged: prelim negative →
CVPR 2027 (abstract ~Nov 15); SGP 2027 (~Feb/Apr, → CGF journal) stays
the natural second target.

**The promised template + anonymization + compression pass is DONE (this
commit).** What changed:

- **Style**: 3DV 2026 author kit (`cvpr.sty` + `ieeenat_fullname.bst`,
  vendored into `paper2/`). The 2027 kit was NOT posted as of 2026-07-13 —
  when it appears (expect `3dvconf.github.io/files/2027/author-kit-3DV2027.zip`),
  diff against the 2026 sty and swap; `\confYear` is already 2027.
- **Double-blind review mode**: `\usepackage[review]{cvpr}` renders
  "Anonymous 3DV submission / Paper ID *****" + confidential header +
  line numbers. The real author block is **commented out in main.tex** —
  restore it for the camera-ready. **Fill `\paperID` in BOTH main.tex and
  supplementary.tex after OpenReview registration.**
- **Page budget: body ends exactly at page 8**; references fill pp. 9–10
  (allowed). **Zero overfull hboxes** — the 3 pre-existing ones died with
  the reformat, as predicted.
- **supplementary.tex** (NEW, 3 pp, builds separately, same anonymous
  style; due Sep 2): §A allocation study (Tables S1/S2), §B diagnostics
  (Table S3, Fig. S1 pd-trajectories), §C additional figures + the repair
  gate (Fig. S2 generality trajectories, S3 sphere per-seed tails, **S4
  torus phantom check, S5 gate toys** — reordered 2026-07-13 so the tall
  gate figure stops stranding the phantom check alone on a 4th page;
  same-class floats place in source order). Main text cites them as
  "suppl. Fig. S1…S5 / Table S1…S3" in plain text (no \ref across docs).
- **Moved to supplementary** (numbers stay in the main text; figures and
  mechanism prose moved): the two appendices (as planned since 07-09),
  the §5.1 gate figure + its mechanism paragraph, fig:gen, fig:tails,
  fig:nsig. Main keeps tab:main*, fig:series*, tab:gen*, and the tom-yum
  pot figure (advisor's aluminium render).
- **Compression ~25% of prose**: every number verbatim, every `% src:`
  comment kept attached to its claim, all `TODO(human)` markers
  preserved. True redundancies merged: the pot paragraph folded into the
  observations paragraph; discussion's recruitment paragraph folded into
  the measurability paragraph (content also in results C6 ¶ + suppl §C).
  The advisor's §6–7 merge was NOT needed — both sections survive.
- **`scripts/audit_paper2.py` re-run after conversion: ALL numeric checks
  pass**; no rendered "kinkin", no rendered TODO, no missing
  refs/cites/figure files.
- **Build**: `tools\tectonic.exe` is a NEW stable copy (gitignored;
  the old temp-scratchpad copy can vanish any day).
  `cd paper2 && ..\tools\tectonic.exe main.tex` and
  `..\tools\tectonic.exe supplementary.tex`.

**Your remaining work:**
1. **Voice pass** — the `TODO(human)` spots are unchanged (abstract,
   intro, related, method notation, discussion). Prose got denser in the
   compression; read it as yours before submitting.
2. **OpenReview registration** when the portal opens → `\paperID` in both
   tex files.
3. **Swap the official 2027 kit** when posted (see above).
4. **Reply to อาจารย์**: 3DV confirmed. One dangling thread from your
   message: the **SA 2026 poster (deadline 2026-07-31)** proposal — he
   answered the venue question but not the poster; ask if you still want
   that parallel submission (it is novelty-safe and 18 days out).
5. Camera-ready (after acceptance): uncomment the author block, switch
   `[review]` → plain `cvpr`, consider regenerating the 130-dpi PNGs at
   print resolution.

The pre-conversion single-document 20 pp version is at commit `cadf36c`.

---

# PAPER 2 — CURRENT STATE (2026-07-11, superseded 2026-07-13: venue decided, 3DV format in)

**kinkin is now IN the paper, rendered as "the tom-yum pot"** (user
instructions 2026-07-11: "put the kinkin results in paper 2 before choosing
the venue", then "do not use kinkin as a name, use tomyum pot instead").
The rendered prose/table/caption say **tom-yum pot** everywhere; the
internal tags (`kinkin_*`), cert file and quicklook keys keep the kinkin
name so the grounding trail stays intact — mapping comments sit next to
every `% src:`. Do NOT confuse with the constructed CSG pot (`tomyum` in
the repo), which is not in the paper. It enters as the **fourth
external mesh**: setup describes the ingest→certify pipeline + the
floor-rule bundle density (M=8192, the study's only protocol deviation,
density-matched contract); the generality table gains the kinkin row
(C0 .0221±.0003 / C1 .0057±.0002 = 3.9× / C2 .0223 with β₂ 1→0 all seeds,
Chamfer 1.36× worse; PASS 80.1σ with the honest "non-overlapping seed
ranges" phrasing in prose); discussion gets the prospective-floor-rule
sentence; abstract/limitations/conclusion counts updated to four. Every
number carries a `% src:` comment (quicklook.json / kinkin_src_cert.json /
PHASE3_STATUS Post-3e). The frozen record itself is untouched — kinkin was
always additive tags in topo3.

**Aluminium figure (advisor's request) is in**: `fig:tomyum` (files
`figures/tomyum_pot_alu{,_cut}.png`), two panels
(exterior 3/4 view + dollhouse cutaway exposing the flue chamber = the H2
void), rendered by `scripts/make_kinkin_figure.py` — CPU ray-traced
(open3d RaycastingScene + metal shader; Filament offscreen needs EGL and
does not work on Windows), 1400², regenerate with the dentistry venv.
Float placement was fixed paper-wide while placing it: all results figures
were `[t]`-only and the tall toys figure jammed the whole float queue to
pp. 16–19; now `[tp]`, every figure lands beside its section (pot fig
p12, prose p13). Build: tectonic clean, no undefined refs, no rendered
TODOs, 20 pp; remaining overfulls are pre-existing (intro bullet, protocol
C0/…/C5 chain, tab:main width).

**Full recheck (2026-07-11, later): every number re-verified, five rendering
bugs fixed.** `scripts/audit_paper2.py` (vendored — **re-run before any
submission**) recomputes every quantitative claim from the source files:
tab:main, tab:gen, every Welch σ, all chamfer claims, C6/C7/C2g/ρ/ramp,
the appendix-A tables, the blindness cases, and the pot row — all pass.
Fixed in the same pass: (1) five **comment-swallowed sentence-starts**
(prose accidentally sitting on `% src:` lines, so the PDF rendered broken
fragments): method "We verify…", setup "The torus restricts…" and "CUDA
training is not bit-reproducible…", results "Overhead, honestly…",
appendix A "On the void class"; (2) C5-vs-prior-alone corrected
**4.6×→4.4×** (h2_unified B4 sphere is .0357, not ~.038); (3) the ρ triple
(.0181/.0172/.0177) is now labeled "matched seed-0 sweep" (PHASE3_PLAN App
C) so it cannot be misread against the five-seed C1 (.0156); (4) the stale
external-pilot src comment fixed (that quicklook.json was later overwritten
by the tomyum/kinkin quicklook; pilot tails now cited from results.json
seed-0 entries .0429/.0429/.0540); (5) GUDHI + alpha-complex citations
added in method (both entries already verified in refs.bib); (6) method's
"M=2048" now reads "unless the floor rule dictates a denser bundle".
Remaining known cosmetics: 3 pre-existing overfull hboxes (intro bullet,
protocol C0/…/C5 chain, tab:main width — venue compression will resolve);
2 uncited bib entries (edelsbrunner2010book, palfinger2022remeshing) and
18 unused report PNGs in figures/ (harmless).

**Venue: DECISION DEFERRED (user, 2026-07-11) until kinkin was in — now it
is, so the advisor message below can go.** The 3DV-only proposal is
superseded by the ACM-DL question; web-checked 2026-07-11 options:

| requirement | venue | deadline |
|---|---|---|
| Scopus proceedings OK (fastest) | **3DV 2027** (IEEE, Thessaloniki Apr 2027) | **2026-08-28** |
| same deadline, faster publication | WACV 2027 R2 (IEEE, conf Jan 4–8) | 2026-08-28 (reg Aug 21; decisions Oct 9) |
| literally ACM DL | SIGGRAPH 2027 conference track (7 pp excl. refs) | ~late Jan 2027 (2026 was Jan 22) |
| Scopus **journal** required | **SGP 2027** → CGF (Wiley, Q1) — best community fit of all | ~Feb + Apr 2027 (2026 double deadline Feb 4/Apr 15) |
| any ACM DL item in 2026 | SA 2026 Technical Communications (4 pp incl. refs) | 2026-07-27 (notify Sep 8) |

(3DV is IEEE — NOT in the ACM DL; SGP/EGSR/PG/EG publish in CGF/Wiley;
SoCG is LIPIcs. ACM DL ⇒ SIGGRAPH/TOG family only. ACM is fully OA since
2026-01-01 — if an ACM venue is chosen, ask the Chula library about ACM
Open membership, else an APC applies.)

**Draft message to อาจารย์ (updated 2026-07-11 — replaces the 3DV-only
draft):**

> เรียนอาจารย์ครับ
>
> อัปเดต paper 2 ครับ:
> 1. ผมใส่ผลของโมเดลหม้อต้มยำลงใน paper 2 เรียบร้อยแล้ว
>    (ในเปเปอร์ใช้ชื่อ tom-yum pot) — เป็น
>    external mesh ตัวที่ 4 ในตาราง generality (C1 ลด error ของ void
>    3.9 เท่าที่ Chamfer เท่ากัน, ทุก seed แยกขาดจาก baseline; ส่วน
>    control ทำลาย void ทั้ง 3 seeds และ Chamfer แย่ลง 1.36 เท่า)
>    พร้อมอธิบาย pipeline ingest→certify (weld → solidify → certify
>    genus 3 ด้วยการวัดจริง) ไว้ใน setup ครับ
> 2. เรื่อง texture aluminium ตามที่อาจารย์ขอ — ทำแล้วครับ รูปใน paper
>    เรนเดอร์หม้อเป็นวัสดุอะลูมิเนียม 2 มุม: ภายนอก และภาพผ่าครึ่ง
>    ที่เห็นช่องปล่องด้านใน (คือ H2 void ที่ loss แก้) ครับ
> 3. เรื่อง venue — ผมตรวจสอบ deadline และความตรงสายของ venue ฝั่ง ACM
>    ตามลิสต์ที่คุยกันครบทุกตัวแล้ว (เช็คจากเว็บทางการ ณ 11 ก.ค. 2026):
>
>    | Venue | Deadline ถัดไป | เหมาะกับงานเราไหม |
>    |---|---|---|
>    | SIGGRAPH Asia (Technical Papers) | ~พ.ค. 2027 (รอบ 2026 ปิดไปแล้ว 12 พ.ค.) | ตรงสายที่สุด แข่งสูงสุด |
>    | SIGGRAPH 2027 (conference track) | ~ปลาย ม.ค. 2027 | ตรงสาย และ track นี้รับงาน earlier-stage อย่างเป็นทางการ |
>    | I3D 2027 | ~ม.ค. 2027 | พอไปได้ ถ้าเสริมมุม interactive |
>    | SCA (★5) | ~เม.ย. 2027 (รอบ 2026 จัดไปแล้ว 8–10 ก.ค.) | ผิดสาย — animation/simulation ล้วน |
>    | HPG (★5) | ~เม.ย. 2027 (รอบ 2026 ปิด 8 เม.ย.) | ผิดสาย — GPU/rendering performance |
>    | MIG (★4) | 7 ส.ค. 2026 — ยังเปิด | ผิดสาย — CFP เป็น animation/games ไม่มีหัวข้อ geometry/reconstruction |
>    | ACM MM | ~เม.ย. 2027 (รอบ 2026 ปิด 1 เม.ย.) | อ่อน — reviewer สาย multimedia |
>    | VRST / ISS / ICMI / SUI | ปิดเกือบหมด (ISS รอบ 2 = 22 ก.ค.) | เป็น HCI ทั้งหมด งานเราไม่มี user/interface — ขอตัดครับ |
>    | SA 2026 Technical Communications | 27 ก.ค. 2026 | ได้เป็น short paper 4 หน้า ถ้าต้องมีผลงาน ACM ภายในปีนี้ |
>    | SA 2026 Posters | 31 ก.ค. 2026 | ส่งคู่ขนานได้ ไม่เสีย novelty ของเปเปอร์เต็ม |
>
>    ข้อสังเกตครับ: ดาวในลิสต์คือ prestige ภายในสาขาของแต่ละ venue
>    (SCA/HPG ห้าดาวสำหรับงาน animation/rendering) แต่เปเปอร์เราเป็น
>    geometry/reconstruction ถ้าส่งผิดสายจะตกตั้งแต่ scope ครับ
>
>    ข้อเสนอของผม: เปเปอร์เต็มยิง **SIGGRAPH 2027 conference track**
>    (~ม.ค. 2027) หรือ **I3D 2027** เป็นหลัก / ถ้ารอไหวและ dental
>    showcase เสร็จทัน ค่อยยิง **SIGGRAPH Asia 2027** (~พ.ค. 2027)
>    และระหว่างนี้ส่ง **SA 2026 Poster (31 ก.ค.)** ไว้ก่อนครับ
>
>    ทั้งนี้ขอเรียนถามยืนยันเกณฑ์ของหลักสูตรด้วยครับ: (ก) ต้องอยู่ใน
>    ACM Digital Library เท่านั้น หรืออยู่ใน Scopus ก็เพียงพอ — ถ้า
>    Scopus พอ **3DV 2027 (IEEE, deadline 28 ส.ค. 2026)** ยังเป็นตัวที่
>    เร็วและตรงสายที่สุดครับ และ (ข) จำเป็นต้องเป็นวารสารไหม — ถ้าต้อง
>    เป็นวารสาร **SGP 2027 (ตีพิมพ์เป็น Computer Graphics Forum,
>    วารสาร Wiley Q1, deadline ~ก.พ./เม.ย. 2027)** ตอบโจทย์ทั้งความ
>    ตรงสายและความเป็นวารสารครับ
> 4. และขอยืนยันอีกครั้งเรื่องส่ง paper 2 ก่อน paper 1 ครับ
>
> ขอบพระคุณครับ

**Your remaining work:** ~~send that message~~ (sent; advisor answered
**3DV** 2026-07-13); voice pass. ~~After venue confirmation: template +
double-blind + compression (delegable)~~ — DONE 2026-07-13, see the top
section.

---

# PAPER 2 — ADVISOR REVISION ROUND 2 (REVISION_GUIDE / red-marks docx / actionable table, answered 2026-07-09)

**⚠ READ THIS FIRST — the advisor's red-mark draft contains INVENTED numbers that contradict
our measured data. Do NOT paste his red text verbatim into anything.** The directives were
followed; the numbers were replaced with real ones:

| His drafted claim | Reality (measured) |
|---|---|
| "W2-without-recruitment: .0212, recruitment contributes ~15%, matched loss dominates" | **C6 (actually run, 5 seeds): .0411±.0038 = statistically BASELINE.** Recruitment carries essentially the whole torus win — his framing is inverted. Paper keeps the real result. |
| "Ramp pilot: alternative windows <2% variance" (no pilot existed) | **Pilot now actually run** (sphere, 3 seeds): 10–40% → .0154±.0017, 30–60% → .0179±.0019 vs default .0156±.0013 — within seed noise. Conclusion holds; numbers are now real (`ramp_1040/`, `ramp_3060/`). |
| "Chamfer parity = ε = 2% of bbox diagonal, 95% CI" | Not our rule. **Actual implemented rule now stated: Ch(C1) ≤ 1.15·Ch(C0) on seed means** — and it never did work (all passing arms ≤ baseline). |
| "Overhead ≈ 2% of training, negligible" | **Real: +46 s fixed on 33–41 s baselines = +115–138% on these tiny scenes.** Honest framing in paper: fixed cost, scales with M not scene, amortizes on real scenes. |
| "Nondeterminism ±3–5% baseline, ±1–2% C1 (guidance reduces variance)" | **Real CVs: 7–10% for baseline AND loss arms**; loss-identical re-run pair 6% apart. No variance-reduction claim. |
| Box 1 formulas ("H0 death: α=0", "H1 birth: circumradius(triangle)", "H2 birth: tetrahedron") | **Wrong case mapping.** Correct (now as equations in §3.2, from the code): edge = ½‖p₁−p₀‖ (H0 deaths, H1 births); triangle = ‖u‖‖v‖‖u−v‖/2‖u×v‖ (H1 deaths, H2 births); tetra via Ay=½diag(AAᵀ) (H2 deaths). |
| New 2026 references ("Leygonie 2025 multi-scale", "Cohen-Steiner 2026 surveys", "NeuroTopology") | **Not verifiable — almost certainly hallucinated. NOT cited.** Verified set unchanged. |

**Everything else from his round-2 list implemented (commit-tagged):** related-work now has
the allocation-channel summary ¶ (3 findings with numbers, main text) + the 3-novelty
differentiation ¶; L_photo inherited-unchanged sentence; circumradius equations (§3.2);
robustness alternatives sentence; ramp-window pilot (real runs) + justification (§3.4);
Chamfer-parity formal definition (§4); H1 geometric-intuition + H0 mechanism paragraphs;
control-pinning mechanism ¶ + **new Appendix B**: M-sensitivity table (M∈{512,1024,2048,4096};
double torus's 4 loops appear at 4096 ✓ bound confirmed) + **persistence-diagram trajectory
figure** (C0 drifts off target / C1 returns to it when the ramp activates / C2 pinned+dragged
with phantom carpet — his requested "pinning" visualization); overhead + nondeterminism with
real numbers; open-surface roadmap + template-free sketch (genus-target recommended; his
fabricated ".0185 genus-variant result" NOT adopted — untested, so stated as untested);
recruitment-guarantees limitation; **new §Conclusion** (was missing); **C3 on external shape
run** (bob: .0171±.0026 vs C1 .0208±.0008 — curriculum-free generalizes). Not done by choice:
his §6–7 merge (defer to venue compression), per-seed Chamfer table + recruitment pseudocode
block (supplementary candidates; equation + greedy-order prose cover it).

---

# PAPER 2 — ADVISOR REVISION RESPONSE (Revision list Paper KinKin.pdf, answered 2026-07-09)

All six items addressed the same day; use this table when you reply to อาจารย์:

| # | Advisor's item | What was done | Where |
|---|---|---|---|
| 1 | Companion-study dependence; B4 unverifiable | Paper 1 no longer referenced AT ALL (your instruction); the allocation study is reported first-hand in **Appendix A**, now including the **field's equations** (splat kernel, mass-preserving spread σ→sσ, w→w/s², both budget-parity levers) | `appendix_companion.tex` |
| 2 | `L_recruit` had no math | Explicit numbered equation: greedy argmin over the unclaimed pool (significant **+ sub-threshold** bars), same squared birth–death metric, without replacement, decreasing target persistence; recruited bars excluded from the diagonal term | `method.tex` §matching |
| 3 | Gabriel 100% is empirical; what if it fails? | Detachment policy stated: failing pair contributes **value but no gradient** → cannot inject wrong gradients or diverge; worst case one refresh without a tug. Stress test (item 4) then showed **zero failures in 2,400 noisy refreshes** — fallback exists but was never needed | `method.tex` §3.2 + results stress ¶ |
| 4 | No real/noisy data → suggested Gaussian-noise stress | **Ran it** (C7/C7h: σ = 0.5%/1% of diagonal ≈ 0.5/1.0 sample spacings, on the cloud the plan sees, every refresh; 12 runs): torus 2.0×/1.6× below baseline (C1: 2.3×), sphere 2.7×/1.9× (C1: 4.0×), correct #sig everywhere, Chamfer parity; recruitment absorbs the noise. Real open-surface data remains future work (limitations unchanged) | `setup.tex` protocol + `results.tex` stress ¶ |
| 5 | Draft remnants ("Deferred arms", dental) | Deleted from the paper | `limitations.tex` |
| 6 | Double-torus saturation lacks theory | Quantified floor: significant ⟺ lifetime > **6·r_med(M)**, r_med ∝ M^(−1/2) (measured 3.16 vs 3.13). Tube loops = 0.83–0.85× floor at M=2048 (need M≈3×10³; 3.1× at eval M=20000; binding constraint is the representation). Torus's 2nd loop clears by only 1.33× — the margin noise eats (links to the C6 recruitment finding). Reproducible: `experiments/density_bound.py` | `discussion.tex` measurability ¶ |

---

# PAPER 2 (`paper2/`) — SUBMIT-FIRST PLAN (2026-07-09)

**Your decision: submit paper 2 BEFORE paper 1.** The structural consequence — paper 2
may not *depend* on an unpublished companion — is resolved: **Appendix A ("The
allocation-channel study, in brief")** reports, with numbers, every allocation-study fact
paper 2 uses: the 3-case blindness result (now an explicit table; Chamfer-equal by
construction; bottleneck 35–40× apart), the prior arms + the void width-primacy table
(B0/B2/B3/B4/B5, 5 paired seeds, `h2_unified`), the torus failure (B5 .0267 best; B2
phantom handles #sig 4.4 vs true 2, `crossover`), and the B4 definition C5 reuses. Every
number carries a `% src:`. **Per your instruction (2026-07-09): paper 1 is NOT referenced
at all** — the `@unpublished` companion entry was removed; the study is presented
first-hand as our own prior experiments in Appendix A. ⚠ One obligation this creates:
if you later submit paper 1 as its own paper, disclose the overlap to both venues (a
non-rendered comment marks this in `appendix_companion.tex` and `refs.bib`). Build:
tectonic exit 0, zero rendered TODOs, no unresolved citations (3 cosmetic overfulls
remain; they die at venue reformat).

**Bib flags CLOSED (web-verified 2026-07-09, provenance comments in `paper2/refs.bib`):**
`tojo2026diffsoup` re-checked against arXiv 2603.27151 (title+authors exact) and
github.com/kenji-tojo/diffsoup ("(CVPR 2026)" in the title line) — if the entry you
*meant* to paste back then differed, say so, otherwise treat it as confirmed;
`held2025trianglesplatting` checked against arXiv 2505.19175 — title, year, and the
10-author list match exactly, order included. Also added (verified): Leygonie et al.
FoCM 22:1069–1131 (2022); Nigmetov & Morozov, DCG 2024, DOI 10.1007/s00454-023-00613-x.

**Venue plan (official dates verified 2026-07-09):** primary **3DV 2027** — papers due
**Aug 28, 2026**, supplementary Sep 2, preliminary notification **Oct 27**, final Dec 2,
conference Apr 6–9 2027 (Thessaloniki). Risk chain: if the Oct 27 preliminary decision
is negative, pivot to **CVPR 2027** (abstract deadline Nov 15, 2026 — three weeks later;
conf. June 2027); **EG 2027** (CFP pending, historically ~early Oct; conf. May 2027,
Lucca) is the graphics-community fallback if Aug 28 slips. SIGGRAPH Asia 2026 has
passed; SGP 2027 (~Apr) is topically ideal but 9 months out. 3DV is double-blind:
strip the author block, anonymize the "our allocation-channel study" self-references
(marked spots), move Appendix A to supplementary (marked in `appendix_companion.tex`).

**Still yours (the only blockers left):**
1. **Voice pass** — abstract, intro, related, discussion (`TODO(human)` comments mark them).
2. **Say the venue** → the template + anonymization + 8-page compression pass gets done for you.
3. ~~Author block~~ **DECIDED 2026-07-09: `viritphon.1234@gmail.com` stays in print** (corresponding author).
4. Paper 1 is now FULLY decoupled (not even cited). If you ever submit it separately,
   disclose the Appendix-A overlap to both venues.
5. *Optional pre-empt:* C1-without-recruitment training ablation (~15 runs, ~30 min GPU).

---

# NOTES_FOR_AUTHOR — paper draft (`paper/`)

**Status: framing decision made (you delegated it). The paper now carries the honest
"width is the value-add; topological targeting is not" story end-to-end (blindness lead →
method as study vehicle → width-primary voids & loops → explicit prescription). Judged a
dramatic restructure UNNECESSARY (below) and finished the framing with a crisp prescription;
title kept.** Grounded; no `\TODO{}`. Remaining: venue document class, voice pass
(abstract + related-work prose), optional 2c items, and **confirm the tojo2026diffsoup
bib entry** (your verbatim-paste block arrived empty — see the mechanical-pass log).

Grounding contract held throughout: every number carries a `% src:` comment naming
the results file it came from; citations are now REAL (filled + verified 2026-07-03,
below); author-only spots are `% TODO(human)` (R4).

---

## Mechanical pass (2026-07-03, your five-item list) — log + bib checklist

**Item 1 (DiffSoup cites): DONE — with ONE deviation you must check.** The
`<<<PASTE FULL BIBTEX ENTRY ...>>>` block in your instructions arrived **EMPTY**. Rather
than guess or stall, the entry was sourced from **arxiv.org/abs/2603.27151 + the authors'
GitHub (kenji-tojo/diffsoup, "(CVPR 2026)") + the ETH CDL publications page** — all agree:
Tojo, Bickel, Umetani, *DiffSoup: Direct Differentiable Rasterization of Triangle Soup for
Extreme Radiance Field Simplification*, CVPR 2026, arXiv:2603.27151. **Compare this against
the entry you meant to paste** (a `% NOTE(author, VERIFY)` sits on the entry in refs.bib);
CVPR-2026 proceedings pages are not yet assigned. Cites wired at:
(a) intro — placed directly on "an attractive such representation~[tojo]" (on the claim
itself, not merged into the pipelines bracket at the sentence end; zero rewording);
(b) related work — "The triangle-soup pipeline we build on~[tojo]";
(c) §3.2 opening — "The baseline resampler~[tojo]".
Provenance sentence added in **§3.2** (the ONE place), right after the lambda=0 reduction
sentence: our own implementation; bit-identical baseline at lambda_topo=0; all numbers are
w.r.t. it. No other new citations anywhere.

**Item 4 (abstract): DONE — 249 words** (mechanically counted after stripping LaTeX
markup; was ~450). Kept, in your priority order: blindness -> in-loop guidance +
persistence metric; method + concentrate<->spread scale + exact baseline reduction;
no-crossover + spread>=concentrate + width-carried (control recovers most; shape-dependent
void residual; small loop cost; H0 null); death-simplex-as-witness principle; compressed
prescription+caveat close. Dropped to the body: per-shape percentages (one 33--53%
headline kept), sigmas, phantom-handle numerics, B1 washout mechanics. No claim
strengthened.

**Item 3 (Figure 5): PREFERRED path — figure regenerated,** not caption-softened. New
`paper/figures/phantom.png` adds the B3 bars (all four low-dim shapes) and the B5 bar
(torus). Every plotted value read from disk, none invented:
`crossover/crossover_report/results.json` (B0/B2/B3/B4 nsig) + `crossover/report/
results.json` (torus B5 final_nsig). Drawn values: torus 2.0/4.4/2.0/2.0/2.0
(B0/B2/B3/B4/B5, true 2); double_torus all 2.0 (true 4); two_spheres all 2.0 (true 2);
three_spheres all 3.0 (true 3) — matches Tables 4/5. Script: session scratchpad
`regen_phantom.py`, style mirrors `crossover_report.py::fig_phantom` (B3 green / B5 purple
to match the other figures' palette). Caption: appended "(B5 was run on the torus only.)";
figure width 0.6->0.75\linewidth. The original run artifact in the dentistry repo is
untouched.

**Item 5 (Figure 1): PREFERRED path — enlarged to full text width** (pure LaTeX layout
change; no plotting script touched, no data altered). The three case images are now
stacked as three full-width rows (was 3 x 0.32\linewidth in one row), so each of the nine
persistence-diagram panels is ~3x larger. Caption gained "top to bottom:".

**Item 2 — bibliography verification checklist.** One correction to your premise: this
session DID have web access, and 9 entries were verified against publisher/arXiv/PMLR
pages (2026-07-03) — marked **[W]** with source. **[M]** = from model knowledge: verify
title/authors/venue/year fields against DBLP/DOI, page numbers listed are the ones to
check. **[O]** = pages intentionally omitted (not guessed) — add from DBLP if you want
them. Internal-consistency scan across all 28 entries: **no swapped volume/number, no
impossible page ranges, venue-naming and author-name ("Last, First") style uniform** —
nothing unambiguous left to normalize, so no bib content was changed by this item.

| # | key | status | what to verify |
|---|-----|--------|----------------|
| 1 | alliez2003anisotropic | [M] | pages 485-493; TOG 22(3) 2003 |
| 2 | attene2010repair | [W: DOI 10.1007/s00371-010-0416-3] | — |
| 3 | botsch2004remeshing | [M][O] | add pages (SGP 2004) |
| 4 | bruel2020toporecon | [W: DOI 10.1111/cgf.14079] | — |
| 5 | gabrielsson2020topologylayer | [W: proceedings.mlr.press/v108] | note: PMLR lists 4 authors (arXiv version has 6) — kept the published 4 |
| 6 | carriere2021optimizing | [M][O] | add pages (PMLR 139) |
| 7 | clough2022topoloss | [W: DOI 10.1109/TPAMI.2020.3013679] | — |
| 8 | cohensteiner2007stability | [M] | pages 103-120; DCG 37(1) 2007 |
| 9 | dunyach2013adaptive | [M][O] | add pages (Eurographics 2013 Short Papers) |
| 10 | edelsbrunner2010book | [M] | AMS 2010 (book) |
| 11 | edelsbrunner2002persistence | [M] | pages 511-533; DCG 28(4) 2002 |
| 12 | edelsbrunner1994alphashapes | [M] | pages 43-72; TOG 13(1) 1994 |
| 13 | garland1997qem | [M] | pages 209-216 (SIGGRAPH 97) |
| **14** | **held2025trianglesplatting** | **[W: arxiv.org/abs/2505.19175]** | **FLAG (as you asked): arXiv ID 2505.19175 + the 10-author list — human-verify** |
| 15 | hoppe1996progressive | [M] | pages 99-108 (SIGGRAPH 96) |
| 16 | hu2019topopreserving | [M][O] | NeurIPS 32 (2019) |
| 17 | ju2004repair | [M] | pages 888-895; TOG 23(3) 2004 |
| 18 | kato2018neural | [M] | pages 3907-3916 (CVPR 2018) |
| 19 | kerbl2023gaussians | [M] | pages 139:1-139:14; TOG 42(4) 2023 |
| 20 | laine2020nvdiffrast | [M] | pages 194:1-194:14; TOG 39(6) 2020 |
| 21 | liu2019softras | [M] | pages 7708-7717 (ICCV 2019) |
| 22 | loper2014opendr | [M] | pages 154-169 (ECCV 2014) |
| 23 | maria2014gudhi | [M] | LNCS 8592, pages 167-174 (ICMS 2014) |
| 24 | nicolet2021largesteps | [M][O] | TOG 40(6) 2021; add article number |
| 25 | palfinger2022remeshing | [W: DOI 10.1002/cav.2101] | — |
| 26 | poulenard2018shapematching | [W: DOI 10.1111/cgf.13487] | — |
| 27 | sharf2007topologyaware | [W: DOI 10.1145/1276377.1276431] | — |
| **28** | **tojo2026diffsoup** | **[W: arXiv 2603.27151 + GitHub + ETH CDL]** | **FLAG: your paste was EMPTY — confirm all fields vs your intended entry; CVPR-2026 pages TBD** |

No venue/year combination looked doubtful (TOG volumes match their years; CGF/DCG/TPAMI/
CAVW/TVC volume-year pairs consistent).

**Build:** `latexmk` is NOT on this machine (long-standing; see build-tools note) —
compiled with **tectonic: exit 0, no warnings**. Abstract word count verified 249.
Previews refreshed. DO-NOT-TOUCH respected: no table/number changed; §5-§6 prose untouched
except the Figure-5 caption sentence Item 3 authorizes; [4] positioning, peakedness
caveat, Limitations untouched.

---

## Citations + author block filled (2026-07-03, you asked for it)

- **Authors (main.tex):** Viritphon Chongpermwattanapol · Pizzanu Kanongchaiyos,
  Department of Computer Engineering, Faculty of Engineering, Chulalongkorn University,
  Bangkok, Thailand. ("Bangkok, Thailand" added by convention — drop if unwanted; emails/
  corresponding-author mark still `% TODO(human)`.)
- **refs.bib:** all 5 stubs replaced with **27 real entries**, organized by bucket.
  Metadata for the 9 less-standard entries verified against publisher/arXiv/PMLR pages
  this session (Palfinger CAVW 33(5); Triangle Splatting arXiv:2505.19175; Clough TPAMI
  44(12); Brüel-Gabrielsson CGF 39(5); Attene TVC 26(11); Topology Layer PMLR 108 —
  4 authors per PMLR, not the arXiv 6; Poulenard CGF 37(5); Sharf TOG 26(3)). Page
  numbers OMITTED (not guessed) where unverifiable (nicolet2021, botsch2004, dunyach2013,
  carriere2021).
- **§2 Related work:** the 4 buckets now carry drafted prose written to each bucket's
  "Establish:" note (notes kept as comments). **Revise in your voice** (`% TODO(human)`
  at the top of related.tex).
- **Wired in:** intro (diff-raster lineage + densify/prune pipelines; DiffSoup itself is
  ours/unpublished — comment marks where to cite it once public), limitations
  (differentiable-PH future work), method (persistence / GUDHI / alpha-complex
  foundations), setup (bottleneck-distance stability).
- **Verified:** tectonic exit 0, **no warnings** (one 0.2pt overfull in new §2 prose was
  reworded away) → `main.pdf` 804 KB; previews regenerated with pandoc `--citeproc`
  (authors + rendered author-date citations + references list confirmed in preview.html).
- **Full recheck pass (same day, "recheck paper"):** re-audited every table against the
  results files on disk — Table 3 + all §5.2 percentages recomputed from
  `h2_unified/report/results.json` (exact match, incl. Δ(B4−B5) sigmas' inputs); Table 4
  from `crossover/crossover_report/results.json` (torus/two_spheres/three_spheres match;
  double_torus pinned 0.026372, nsig 2 vs true 4 ✓); Table 5 incl. **B5 0.0267/nsig 2.0**
  from `crossover/report/results.json` ✓. **Found + fixed a factual error:** §4 seeds
  sentence said "3 for the H2 study, 5 decisive" — disk shows h2_unified ran **5 seeds for
  every shape×condition**; sentence corrected to "5 for the H2 study and the torus, 3 for
  the remaining crossover shapes". Also verified 2500 steps across all runs (dumps end at
  `step_02500.pt`) and resolved both `% TODO(human)` verify items in §4. Typo fixes:
  "(Figures 1)"→"(Figure 1)", one more em-dash spacing nit (results.tex). Re-grepped: no
  `\TODO{}`, no `??`, tectonic exit 0 / no warnings; previews refreshed.
- **Reference-section polish (same day, after PDF inspection):** added
  `\usepackage[numbers,sort&compress]{natbib}` + `plainnat` so citation brackets sort/
  compress (`[18, 20–22]`, was `[22, 18, 21, 20]`) — drop natbib if the venue class brings
  its own citation setup; brace-protected {Gaussian} in kerbl2023 (plain had lowercased it);
  fixed a pre-existing "features— intervals" dash-spacing nit in method.tex. Full PDF
  visually inspected page-by-page: all 27 entries + all in-text numbers point at the
  intended works; accented names render correctly.
- **Build tools (this machine, not on PATH):** tectonic + pandoc live in an old session
  scratchpad — `C:\Users\virit\AppData\Local\Temp\claude\D--Project-CG-Soup-Topology\dafb5831-69aa-41d4-a760-778a2f38db19\scratchpad\`
  (`tectonic_bin\tectonic.exe`, `penv\Lib\site-packages\pypandoc\files\pandoc.exe`).
  Temp dirs can get cleaned — consider installing tectonic properly or copying the
  binaries somewhere stable.

## Framing decision (you delegated it → I made it)

**Decision: keep the honest "prescription" framing; do NOT do a dramatic restructure.**
After the incremental honest edits the paper already leads with blindness, presents the
method as a controlled-study *vehicle* (not a winning system), and reports width-primary
results for both voids and loops. A "method-as-failure / blindness-as-sole-lead" restructure
would over-correct: (i) topological placement is not useless — it helps voids modestly
(cylinder 4.6σ, sphere 2.2σ); (ii) the concentrate↔spread study yields a genuine, useful
*prescription*. So I finished the framing rather than rebuilt it: sharpened the abstract
closing and intro to state the prescription explicitly ("spread, not concentrate; the gain
is width, not topological targeting — a width-matched non-topological prior does as well or
better"). **Title kept** ("Concentrate or Spread?…" is still apt; the width answer lives in
the body) — revisit only if you want the title to foreground "width." Grounded; tectonic
clean (788 KB) + previews refreshed.

---

## Revision pass (TASKS 1–3): torus B5 run + loop width×placement 2×2 — **BRANCH B**

**TASK 1 (ran, authorized):** torus B5 (wide non-topological, width-matched to B4's
σ=1.35, mass-preserved — the *same* B5 as the voids) at N=700, 5 paired seeds, 2500 steps,
exp `crossover`. Re-read B2/B3/B4 from source (match exactly). Torus 2×2 (bottleneck; #sig-H1, true 2):

| torus N=700 | B2 topo | B3 non-topo | B4 topo | **B5 non-topo** | B0 |
|---|--:|--:|--:|--:|--:|
| bottleneck | 0.0425 | 0.0397 | 0.0316 | **0.0267** | 0.0409 |
| #sig-H1 | 4.4 | 2.0 | 2.0 | 2.0 | 2.0 |

Width: B2→B4 −26%, B3→B5 −33% (both huge). Placement: non-topo **better** at both widths —
narrow B3<B2 (7.6σ), wide **B5<B4 (3.25σ)**. Best torus condition = **wide non-topological (B5)**.
Phantom handles (N=700) are narrow-topological-specific (only B2 inflates; B3/B4/B5 hold 2.0).
[src: crossover/report/results.json]

**Classification: BRANCH B** (loop spread-win is width, not placement) — and *stronger*
than B: topological placement is a small **cost** on the loop, not a null. Applied local
Branch-B wording: new torus 2×2 table (`tab:torus2x2`), rewrote §5.3 phantom paragraph,
clarified §5.3 "no crossover" (Δ=B4−B2 isolates width), abstract loop clause ("a wide
prior wins by width, not placement"), `fig:phantom2` caption, and reconciled the §6 loops bullet.

**TASK 2 NOT applied (data conflict, per R1):** its premise ("loop backfire is narrowness;
both narrow priors inflate") is from Fig 6 = **N=400**. At the primary **N=700** budget the
narrow-random B3 does NOT inflate (#sig 2.0) and beats B2 — so the phantom handles are
**narrow-topological-specific**, not generic narrowness. Writing "both narrow inflate" into
§5.3/abstract/intro would be false. Reverted this session's narrowness edits to the accurate
baseline; §6 now states the budget-nuanced truth (narrow-topological at N=700; narrowness
also at N=400). ISSUE-D's "narrowness, not placement" was an N=400-only artifact that the
fuller data reverse.

**⚠ FRAMING DECISION FOR YOU (STOP gate — NOT done):** loops + voids together now show
**width is the value-add; topological placement is at best a small shape-dependent help
(voids) and at worst a small cost (loops)**. Whether to keep the method-forward framing,
reposition the blindness result as the lead, or reframe the method as a (useful) negative
result is your call. I applied only local Branch-B wording; no overall reframe. Verified:
tectonic clean (787 KB) + previews refreshed.

---

## Revision pass (Items A–D) — writing fixes + Issue-D disk read

- **A (§6 reconciliation):** rewrote the "Voids…" and "Interpretation" paragraphs to carry
  the single principle "spread over the *support*," explaining the two observable regimes via
  support extent (void support ≈ whole surface → width-driven; loop support = thin tube →
  narrowness harmful), linked to the peakedness caveat. Void residual stated as tracking shell
  non-uniformity (cylinder 4.6σ > sphere 2.2σ > cube tie). Verified the abstract closing is
  consistent; minimal tweak ("for a void the support fills the surface, so width alone realizes
  it"; "harm from concentrating" → "from being narrow").
- **B (§5.2 "15–33%"):** blanket "both wide beat both narrow by 15–33%" was false for
  cross-pairs (B5-vs-B2 ≈9% cyl, ≈15% sph). Restricted to **matched-placement** widening
  (B4-vs-B2 18–33%, B5-vs-B3 15–33%) + explicit cross-pair caveat; caption fixed.
  [src: h2_unified/report/results.json]
- **C (§5.2 narrow topology):** replaced "topology gives nothing at narrow width" with the
  shape-specific truth — **cylinder** helps at BOTH widths (narrow B2-vs-B3 **7.8%**; wide
  4.6σ), **sphere** weak (narrow tie; wide 2.2σ), **cube** none (tie both). Summary: "real but
  shape-dependent, clearest for the cylinder." [src: h2_unified/report/results.json]
- **D (disk read):** VERIFIED tight_N400 torus final #sig-H1: B0 **2.0**, B2 **7.67**,
  **B3 5.67** — the narrow-*random* control ALSO inflates phantom handles. So the loop backfire
  is a **narrowness** effect (both narrow priors inflate), worse with topological placement
  (7.67 vs 5.67), **not specifically topological placement**. Softened §6 loops bullet + Fig-6
  caption. [src: tight_N400/report/results.json]
- **D step 3 (FLAG, no run):** the torus has **no wide-random (B5) arm** on disk (only
  B0/B2/B3/B4 @ N=700), so the loop side lacks the full width×placement 2×2 the voids have.
  Completing it = a **torus B5 run** (wide-random at B4's width, N=700, 5 seeds) ≈ **5 runs,
  ~10 min GPU** + report. **Not started — your call.**
- Verified: structure OK; tectonic clean (exit 0, no overfull); `main.pdf` 784 KB + previews refreshed.

---

## ITEM 3 — B3 WIDTH CONFOUND: **RESOLVED via option (i)** — claim did NOT survive; paper reframed

**Resolved (ran the width-matched control B5).** The "specifically topological" claim
is **not supported**: the void gain is **primarily kernel WIDTH**, not topological
placement. At B4's width, a non-topological control (B5) recovers most of the gain;
placing the wide prior at the topological locus adds only a small, shape-dependent
residual — **cylinder ~4.6σ, sphere ~2.2σ, cube tie** (B4−B5 = −0.0042 / −0.0017 /
+0.0003). The paper was **reframed** to the honest width×placement 2×2 (§5.2 retitled
"…the gain is mostly width, not topological placement"; abstract, §1, §6, §4 B5
defined, and Limitations all updated), every number `% src`'d to
`h2_unified/report/results.json`. Code: `build_random_field(sigma_abs=…)` + condition
**B5** in the eval harness (`ensure_fields` / `condition_flags` / `b5_kind`). The
diagnosis that led here is kept below for the record.

### Diagnosis (for the record)

The headline "the void gain is *specifically topological*" rests on B4 (spread topo)
beating B3 (non-topo control). **B3 is not width-matched to B4**, so that gap is
confounded with spread width.

**Code (`methods/topo_importance.py`, `build_random_field`):** B3's kernel width is a
*fixed* `sigma = sigma_frac * scale` with `sigma_frac=0.22` (scale = bbox diagonal),
independent of the spread scale `s`; it never uses B4's `s*sigma`. (`ensure_fields`
builds B3 via `build_random_field(gt, …)` with defaults; `--b3_mode curvature` is an
alternate non-topo control, unused — the runs used `random`.)

**Measured widths (`h2_unified/fields/*.npz`):**

| shape | B2 σ (s=1) | B4 σ (s=3) | B3 σ (0.22·scale) | B3/B4 |
|---|--:|--:|--:|--:|
| sphere | 1.00 | 3.00 | 0.76 | 0.25 |
| cube | 0.58 | 1.73 | 0.44 | 0.25 |
| cylinder | 0.61 | 1.84 | 0.52 | 0.28 |

B3 is ~4× narrower than B4 (and ~0.8× B2). The paper's pattern — **B4 (wide topo) beats
B3; B2 (narrow topo) ties B3** — is consistent with "wide beats narrow" as much as
"topology beats non-topology" (the two *narrow* priors tie; only the *wide* one wins).
There is no *wide non-topological* control, so the width-controlled topology attribution
is not established.

**Options (your call — no run started):**
- **(i) Add control B3-spread + re-run (resolves it).** A non-topological field widened
  to B4's σ (mass-preserved: `build_random_field` with `sigma_frac`≈0.85, or a `--b3_spread`
  flag), so **B4 vs B3-spread** isolates topology from width. Minimal: add B3-spread for the
  3 H2 shapes at N=1200, seeds 0–4, and compare to the existing `h2_unified` B4 (same seeds)
  → **15 runs ≈ ~15–20 min GPU** + report; cleanest: a fresh paired B4+B3-spread batch → 30
  runs ≈ ~30–40 min. Needs a small code addition (widened random control).
- **(ii) No run — soften the claim.** Replace "specifically topological" with what the
  current controls license ("a spread topological prior outperforms *both* a concentrated
  topological prior and non-topological densification"), and add a Limitation naming the
  width confound and B3-spread as the control that would resolve it. **Writing only.**

**Outcome:** you chose (i). The B5 run showed the void gain is width-primary (above), so
the "specifically topological" wording was removed and the paper reframed to the honest
width×placement result. *Optional:* the title still says "Topological Resampling Priors";
given the width-primary finding you may want to revisit it — left as your call.

**Also this pass (writing, done, compiles clean):** *Item 1* — intro central-finding
de-staled (29–40%→**33–53%**; win attributed to *spread*, not concentrate; src→`h2_unified`).
*Item 2* — §6 "Voids (2-D): mild" bullet reworded "under-covers / incomplete-coverage" →
"**under-protects / incomplete-protection**" to match the peakedness caveat.

---

## ISSUE 1 — DATA SPLICE: **RESOLVED via option (a)** (re-run → one unified H2 table)

**Resolved.** Re-ran B0/B1/B2/B3/B4 × {sphere,cube,cylinder} @ N=1200, **5 paired
seeds** → `output/synth/h2_unified/`. §5.2 now shows ONE authoritative paired-seed
table; §5.3's H2 rows use the *same* run; the abstract is de-spliced; §6 updated.
**The clean 5-seed run REVISED the H2 claim** (worth your attention): concentrate (B2)
does **not** robustly beat the non-topological control — it *ties* B3 on sphere and
cube (wins only cylinder), so concentrate's gain is generic densification. The
**topology-specific** void win is carried by **spread (B4)**: B4 beats baseline
(33–53%), the non-topo control (19–32%), and concentrate (18–33%) for all three voids,
at better geometry; B1≈B0 (washout). The old 3-seed "concentrate beats control 29–40%"
was a small-sample artifact — exactly the risk you flagged. Original diagnosis kept
below for the record.

### Original diagnosis (for the record)

Tables 3 (§5.2) and 4 (§5.3) report the same nominal conditions with different
numbers because they are **separate runs under CUDA non-determinism** — confirmed by
tracing every value to its `results.json` and counting seed dirs on disk:

| paper location | values | results.json | run dir | seeds |
|---|---|---|---|---|
| Table 3 sphere | B0 .0602 / B2 .0403 / B3 .0505; Cham .92/1.02 | topo2/report/ | topo2 | **3** |
| Table 3 cube | .0618 / .0368 / .0457; Cham 2.00/1.58 | h2_generalize/report/ | h2_generalize | **3** |
| Table 3 cylinder | .0592 / .0422 / .0446; Cham 1.67/1.60 | h2_generalize/report/ | h2_generalize | **3** |
| Table 4 sphere | B0 .0525 / B2 .0448 / B4 .0377 / B3 .0472 | crossover/crossover_report/ | crossover_N1200 | **5** |
| Table 4 cube | .0565 / .0378 / .0324 / .0496 | crossover/crossover_report/ | crossover_N1200 | **3** |
| Table 4 torus | B0 .0409 / B2 .0425 / B4 .0316 / B3 .0397 | crossover/crossover_report/ | crossover (N700) | **5** |
| §6 torus N=400 #sig 7.7 (kept, labeled indep. sweep) | — | tight_N400/report/ | tight_N400 | **3** |
| §6 torus N=700 B2 .0448 / #sig 3.7 (**removed** from §6) | — | tight_N700/report/ | tight_N700 | **3** |
| §5.2 "29–40%" | 33 / 40 / 29% | topo2 + h2_generalize/report/ | topo2 + h2gen | **3** |

**Your hypothesis is CONFIRMED.** Table 3 = the concentrate study (topo2 +
h2_generalize, 3 seeds, B0/B2/B3, **no B4**). Table 4 = the crossover (crossover_*,
B0/B2/B3/B4, **mixed 5/3 seeds**). The torus@N700 B2 splice = tight_N700 (3 seeds,
.0448 / #sig 3.7) vs crossover (5 seeds, .0425 / #sig 4.4).

**Unified run on disk? NO.** `crossover_N1200` has sphere (5 seeds) + cube (3 seeds)
with B0/B2/B3/B4 at N=1200 — but (i) **no cylinder exists with B4 anywhere** (cylinder
is only in h2_generalize: B0/B2/B3, 3 seeds), and (ii) sphere=5 vs cube=3 seeds is not
one paired-seed set. So no single run covers sphere/cube/cylinder × B0–B4 at one N + one
seed set.

**Options (your call — I will NOT start (a) on my own):**
- **(a) Re-run → one authoritative H2 table.** B0/B1/B2/B3/B4 × {sphere,cube,cylinder}
  @ N=1200, ≥5 paired seeds, one batch, feeding both §5.2 and §5.3; makes the abstract's
  "concentrate 29–40%, spread improves further" a valid single-run claim.
  **Cost:** 3 × 5 × 5 = **75 training runs** ≈ ~1 min each → **~75–90 min GPU**, + fields
  (~1 min) + report (~15–20 min) ≈ **~1.5–2 h** wall. (Drop B1 → 60 runs ≈ ~75 min.)
- **(b) No re-run → merge + relabel.** One table explicitly labelled **"two runs
  (3-seed concentrate study; 5/3-seed crossover)"**; **remove the abstract's cross-run
  "improves further" splice**; re-quote the headline as **B4-vs-its-own-B0 within the
  crossover only**: sphere **−28%** (B4 .0377 vs B0 .0525), cube **−43%** (B4 .0324 vs
  B0 .0565) [crossover/crossover_report/results.json]; cylinder has no B4 so stays
  concentrate-only (Table 3). **Cost:** writing only.

**Done:** §5.2/§5.3/abstract/§6 were rewritten to `h2_unified` (H2) + the crossover
run (low-dim), every number `% src`'d; no cross-run splice remains. The stale
`crossover.png` signed-Δ figure was dropped (its role is now the Δ column of the
crossover table); `phantom.png` (torus, low-dim) is kept. Figures
`sphere/cube/cylinder_bottleneck.png` + `sphere_geometry.png` were refreshed from
`h2_unified`.

## Revision pass (this review) — writing fixes applied (ISSUES 2–4)

- **ISSUE 4** — §5.2 retitled **"Topology helps voids (H2)"** (was "…concentrating
  helps voids"); the bridge to §5.3 reworded to "spreading is the better *form* of this
  help" (the cross-run "improving further on the concentrated result" splice removed).
- **ISSUE 2** — §6 (`sections/mechanism.tex`) fully rewritten: retitled **"Why
  spreading wins, and why concentration's harm depends on dimension"**; the "Voids
  reward concentration" subsection replaced by **"Voids: a real, topology-specific
  benefit, maximized by spreading"** (covering the whole shell *is* spreading;
  concentrating on the void-tetra under-covers it); the reward/punish framing replaced
  by the **fabrication asymmetry** (over-tessellating one locus fabricates a spurious
  same-dim feature → catastrophic 1-D loops, mild 2-D voids, null 0-D components); the
  section is now consistent with its closing "spread over the support" paragraph. The
  spliced torus@N700 number was dropped; the torus backfire now cites the crossover
  (Table 4) for N=700 and the **independent** budget sweep (tight_N400, 3 seeds) for N=400.
- **ISSUE 3** — peakedness caveat added to **Limitations** ("What the spread scale
  varies (limited dynamic range)") and the **§6 mechanism hedged** up front: the effect
  is the *peakedness* of keep-map protection, not literal coverage (death scales are
  O(shape size)). Wording pulled from `PHASE2B_CROSSOVER.md`; not overstated.
- **Left untouched** (per your DO-NOT-TOUCH list): §5.1 blindness / 40×–35× / H1
  divide-by-zero; B3 framing; H0 null; double_torus inconclusive; mass-preservation &
  cleanliness; `\cite{TODO-…}` placeholders; Limitations honesty.
- **Verified:** structure checker OK; **tectonic recompiles clean** (exit 0, no
  overfull/errors) → `paper/main.pdf` regenerated (701 KB).

## 0. What I changed when you said "finish with your recommendation"

You authorized reconciliation **option (A): revise the thesis to what the data
show.** The lean B4 + double_torus runs on disk **refute** the original
"concentrate is the right bias / dimensional crossover" framing, so I rewrote the
claim-bearing parts to the data-supported thesis:

> **A spread topological prior dominates: it is at least as good as concentrating
> at every feature dimension and strictly better for voids and loops; there is no
> dimensional crossover. What depends on dimension is the *harm* from
> concentrating (catastrophic for H1 loops → phantom handles, mild for H2 voids,
> immaterial for H0 components).**

Files revised to this: **abstract + title** (`main.tex`), **intro** central finding
(`intro.tex`), **§5c** (now the grounded crossover results, not a scaffold,
`results.tex`), **§6** interpretation (`mechanism.tex`), **limitations**
double_torus (`limitations.tex`). §5a (blindness) and §5b (H2 win) were already
grounded and are unchanged except a forward pointer.

**You must review the rewritten abstract + title in your own voice** — they are my
draft (`% TODO(human)` at `main.tex:55`; title note at `main.tex:32`). I kept the
question title "Concentrate or Spread?"; you may prefer the assertive
**"Spread, Don't Concentrate: …"**.

---

## 1. Build status & command

- **Still NOT compiled** — no TeX toolchain on this machine (`latexmk`/`pdflatex`/
  `tectonic` absent). I could not verify "latexmk clean."
- **Structure re-checked OK** after all edits: every `{}`/`\begin`/`\end` balanced,
  no non-ASCII in visible (non-comment) text, all caption braces on code lines.
- **Build:** `cd paper && latexmk -pdf main.tex` (needs: graphicx, booktabs,
  multirow, amsmath, amssymb, xcolor, hyperref). Document class is placeholder
  `article` — swap to your venue (`main.tex:32`).

---

## 2. Real work left for you

### 2a. Citations — **DONE 2026-07-03** (real, verified; see the dated section up top)
All 5 stub keys replaced with 27 real entries in `refs.bib`; §2 prose drafted to the
bucket intent notes (revise in your voice).

| old key | replaced by |
|---|---|
| `TODO-diffrast` | loper2014opendr, kato2018neural, liu2019softras, laine2020nvdiffrast |
| `TODO-soup` | kerbl2023gaussians, held2025trianglesplatting, nicolet2021largesteps, palfinger2022remeshing |
| `TODO-topo-recon` | sharf2007topologyaware, ju2004repair, attene2010repair, bruel2020toporecon |
| `TODO-ph-loss` | gabrielsson2020topologylayer, hu2019topopreserving, clough2022topoloss, carriere2021optimizing, poulenard2018shapematching |
| `TODO-remesh` | hoppe1996progressive, garland1997qem, alliez2003anisotropic, botsch2004remeshing, dunyach2013adaptive |
| *(new, foundations)* | edelsbrunner2002persistence, cohensteiner2007stability, edelsbrunner2010book, edelsbrunner1994alphashapes, maria2014gudhi |

### 2b. Front matter & voice
| loc | item | status |
|---|---|---|
| main.tex:39 | author list + affiliations | **DONE 2026-07-03** (emails still TODO) |
| main.tex:32 | venue document class (currently `article`) | open |
| main.tex:55 | review the (rewritten) abstract wording in your voice | open |
| title note (main.tex:32) | keep "Concentrate or Spread?" or switch to "Spread, Don't Concentrate" | open |
| related.tex | related-work prose | **drafted 2026-07-03** — revise in your voice |

### 2c. Minor verify / optional (all `% TODO(human)`)
| loc | item |
|---|---|
| setup.tex:46 | state cube/cylinder Betti provenance (scene gt_mesh target diagrams) |
| setup.tex (seeds) | **DONE 2026-07-03 — was WRONG, fixed.** Old text said "3 for the H2 study; 5 decisive"; disk says h2_unified = **5** seeds everywhere, torus = 5, other crossover shapes = 3. §4 now states that; `% src(VERIFIED)` comment added |
| setup.tex (steps) | **DONE 2026-07-03 — verified.** All run dirs (h2_unified + crossover incl. double_torus) end at `step_02500.pt`; no schedule differed |
| results.tex:68 | optional: exact step where #sig-H1 flips 0→1 (`figures/stability_series.csv`) |
| method.tex:24 | optional feature-localization figure |
| method.tex:50 | cite/appendix the mass-invariance & s=1-identity checks |
| method.tex:81 | confirm keep-map/densify detail level (formulae vs algorithm box) |
| limitations.tex:12 | add a real/captured scene if you run one |

---

## 3. Grounding map (R1 audit — every written number → file)

| section | numbers | source |
|---|---|---|
| §5a blindness (Tab 1) | Chamfer/Hausd95/bottleneck, 40×, 35× | `figures/summary.md` (raw `figures/blindness_results.json`) |
| §5b H2 (Tab 2): sphere .0602/.0403/.0505, Chamfer .92/1.02 | | `…/output/synth/topo2/report/results.json` |
| §5b H2 (Tab 2): cube .0618/.0368/.0457 (Cham 2.00/1.58); cylinder .0592/.0422/.0446 (1.67/1.60); −33/40/29% | | `…/output/synth/h2_generalize/report/results.json` |
| §5b nulls: two_spheres B2 .0072 vs B3 .0057; torus B2 .0456 ≈ B0 .0457 | | `…/output/synth/topo2/report/results.json` |
| **§5c crossover (Tab 3): all B0/B2/B4/B3, Δ, #sig, Chamfer** | | `…/output/synth/crossover/crossover_report/results.json` |
| §6 backfire: torus N=400 B2 .0367/#sig 7.7, N=700 B2 .0448/#sig 3.7 | | `…/output/synth/tight_N400/report/summary.md`, `…/tight_N700/report/summary.md` |
| §4 target Betti | | `tests/test_betti.py` (9/9) + `topology/meshes.py` |

> Please spot-check a few against the files — I read them this session, but you are
> the final guarantor of R1. In particular the §5c numbers are from the **lean**
> crossover run (5 seeds on decisive arms, 3 elsewhere); state that scale if a
> reviewer asks, and note `double_torus` is reported **inconclusive**, not as support.

---

## 4. Figures (`paper/figures/`, read-only copies; originals untouched)

| file | from |
|---|---|
| pd_i_genus / pd_ii_components / pd_iii_void / stability_series .png | `$TOPO_ROOT/figures/` |
| sphere_bottleneck, sphere_geometry .png | `…/topo2/report/` |
| cube_bottleneck, cylinder_bottleneck .png | `…/h2_generalize/report/` |
| torus_betti_N400.png | `…/tight_N400/report/torus_betti.png` |
| **crossover, phantom, parity, bottleneck_vs_N .png** | `…/crossover/crossover_report/` |

(`parity.png` and `bottleneck_vs_N.png` are copied but not yet `\includegraphics`'d
— add them if you want a geometry-parity or budget-sweep figure in §5c.)
