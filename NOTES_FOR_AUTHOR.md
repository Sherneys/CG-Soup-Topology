# NOTES_FOR_AUTHOR — paper draft (`paper/`)

**Status: framing decision made (you delegated it). The paper now carries the honest
"width is the value-add; topological targeting is not" story end-to-end (blindness lead →
method as study vehicle → width-primary voids & loops → explicit prescription). Judged a
dramatic restructure UNNECESSARY (below) and finished the framing with a crisp prescription;
title kept.** Grounded; no `\TODO{}`. Remaining: venue document class, voice pass
(abstract + related-work prose), optional 2c items.

Grounding contract held throughout: every number carries a `% src:` comment naming
the results file it came from; citations are now REAL (filled + verified 2026-07-03,
below); author-only spots are `% TODO(human)` (R4).

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
