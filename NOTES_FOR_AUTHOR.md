# PAPER 2 — CURRENT STATE (2026-07-09, end of day)

**Experimental record FROZEN at git tag `paper2-results-freeze`** — everything
from here is prose/format only. Both advisor revision rounds answered (tables
below). A Thai reply message to อาจารย์ is drafted (in the session log /
ask Claude to reproduce it) — it requests the two pending sign-offs:
**(1) paper 2 before paper 1, (2) 3DV 2027 (deadline Aug 28)** — and flags the
recruitment-story correction for his explicit agreement. Your remaining work:
send that message, then the voice pass. After venue confirmation: template +
double-blind + 19 pp → 8 pp compression (delegable).

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
