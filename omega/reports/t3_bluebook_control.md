# PROJECT OMEGA — T3: The Blue Book Resolved-vs-Unidentified Control

**Status: NULL, and underpowered. The null does not settle the question.**
**Code:** `omega/bluebook_parse_index_v2.py`, `omega/t3_run.py`
**Labels:** `data/processed/bluebook/bluebook_evaluations_v2.json`

---

## 1. What T3 was for

Phase 6 found kinematic sequence structure in Hatch's catalog prose at
**+0.2504 bits (8.19% of channel entropy, p = 0.0005)** — the only substantive
positive in that phase. The MID control (Hatch's own "likely
misidentification" flag) reproduced it at 4.48%, and the size-matched
difference sat at p ≈ 0.050 on n = 178. T3 was built to settle it with the
USAF's own disposition labels, because it is the one test where a positive
could not be narration, selection, contamination, self-reference, or
geocoder agreement.

## 2. The join, and its ceiling

Blue Book's index pages carry `DATE | LOCATION | OBSERVER | EVALUATION` but no
description; the per-case OCR carries descriptions but, as measured, an
unusable label channel (43% header presence, 64% label-ambiguous). So labels
come from the index and descriptions from the case files, joined on location
and year.

Two fixes raised the usable arm, and a third lowered it:

| step | clean UNIDENTIFIED labels |
|---|---|
| partial identifier set (advancedsearch paging returned duplicates) | 76 |
| full identifier set via the scrape API (10,764, not 5,592) | **157** |
| adding month to the key (tighter, but fails more often) | 130 |

The binding constraint is that **the index's case numbers are too OCR-garbled
to join on** — they read as `/O47`, `(089`, `70902`, `(oSa` — and the
archive.org identifiers key on NARA naIds instead. There is no shared exact
key. Ceiling: ~130 clean unidentified labels → **~76 usable sequences** after
the ≥2-descriptor filter.

## 3. Result

Year-matched subset (8 years with ≥2 cases in both arms, 1948–1955):
**UNID = 50, RES = 467.**

| arm | n | H(k₂\|k₁) | shuffled null | gain | p |
|---|---|---|---|---|---|
| UNIDENTIFIED | 50 | 2.2186 | 2.2583 ± 0.0730 | **+0.0397** | 0.301 |
| RESOLVED | 467 | 2.7092 | 2.7146 ± 0.0170 | **+0.0054** | 0.366 |

Size-matched comparison (resolved subsampled to n = 50, 120 draws):

| quantity | value |
|---|---|
| UNIDENTIFIED gain | +0.0491 bits |
| size-matched RESOLVED gain | +0.0072 ± 0.0795 bits |
| one-sided p (UNID ≥ RES) | **0.2645** |

**Null.** And T3d found **no descriptor unique to either arm** — ratios span
0.51 (`k_split`) to 1.62 (`k_rotate`), consistent with noise at n = 50.

## 4. Power — why this null is not a verdict

| quantity | value |
|---|---|
| sd of the size-matched resolved gain | 0.0795 bits |
| minimum detectable difference (α=0.05, ~80% power) | **≈0.199 bits** |
| the effect Phase 6 suggested (MID vs non-MID) | **0.112 bits** |

**The minimum detectable difference is 1.8× the effect being looked for.**
Even at the join's full ceiling (~76 usable unidentified) the MDD would be
~0.16 bits — still above 0.112. **This join cannot settle T3 at any
achievable n.** Stated before the test was run and confirmed by it.

## 5. The incidental finding, which is more informative than the test

**Neither arm of Blue Book's own case text shows significant kinematic
sequence structure at all** — UNID +0.0397 (p=0.30), RESOLVED +0.0054
(p=0.37). In Hatch's catalog prose the same measurement on the same
descriptors gave **+0.2504 bits at p = 0.0005**, a 6–46× larger effect.

> **The kinematic "grammar of departure" is a property of catalog prose, not
> of case records.** Hatch and Johnson write narrative arcs — hover, then
> accelerate, then climb, then vanish. Blue Book record cards are bureaucratic
> forms, and their OCR is fragmentary. The structure lives in the compiler's
> sentence, not in the event.

This supports Phase 6's narrative-convention verdict from an independent
direction, and it does so despite T3's own low power, because it is a
comparison of **effect magnitudes across corpora** (0.0054–0.0397 vs 0.2504)
rather than a significance test on 50 cases.

## 6. What would settle T3

The per-case **checkbox Record Cards** (pre-1962, the highest-volume years)
cannot be labelled from text OCR — the OCR emits the printed label set
(`Was Balloon / Probably Balloon / Possibly Balloon …`) and never which box is
marked. Mark detection on the JP2/PDF scans would label those cases directly,
removing the index join entirely and raising the labelled arm roughly
fivefold. That is a vision task on image scans, not a text task, and it is the
single identified path to a properly powered T3.

## 7. Limitations

1. n = 50 in the unidentified arm; MDD 1.8× the target effect.
2. Only 8 years have ≥2 cases in both arms, all 1948–1955, so the test is
   effectively an early-era test.
3. Labels inherit the index's OCR error and the location-token join's
   ambiguity; conflicting-label cases (1,207 + 285) were dropped, and that
   exclusion may not be random with respect to case type.
4. Kinematic descriptors are regex over OCR of bureaucratic forms, where
   recall is lower and noisier than over catalog prose — which is itself part
   of why the two corpora differ.

---

# 8. T3 COMPLETED AT ADEQUATE POWER — AND IT IS NULL

The targeted fetch finished: **5,253 case texts**, giving a T3 dataset of
**2,390 cases (UNID = 120, RES = 2,270)** across 21 years with ≥2 cases in
both arms. This supersedes §3–§4, which ran on n = 50.

## 8.1 Result

| arm | n | H(k₂\|k₁) | shuffled null | gain | p |
|---|---|---|---|---|---|
| UNIDENTIFIED | 120 | 2.4886 | 2.5481 ± 0.0415 | +0.0595 | 0.0815 |
| RESOLVED | 2,257 | 2.6486 | 2.6840 ± 0.0079 | **+0.0354** | **0.0017** |

Size-matched comparison (resolved subsampled to n = 120):

| quantity | value |
|---|---|
| UNIDENTIFIED gain | +0.0567 bits |
| size-matched RESOLVED gain | +0.0347 ± 0.0467 bits |
| one-sided p (UNID ≥ RES) | **0.2727** |

## 8.2 Power — the test is now adequate

| quantity | value |
|---|---|
| sd of the size-matched resolved gain | 0.0467 bits |
| **minimum detectable difference** (α=0.05, ~80% power) | **0.1169 bits** |
| the effect Phase 6 suggested | **0.112 bits** |

**MDD ≈ target effect.** Unlike the n = 50 run, this test could have detected
the Phase 6 effect size had it been present. It is not present.

> **T3 is settled. Unidentified Blue Book cases do not carry more kinematic
> sequence structure than resolved ones (p = 0.27), at a power level that
> would have detected the hypothesised effect.** The one test designed to be
> immune to all six documented failure modes — narration, selection,
> contamination, self-reference, geocoder convergence, marginal-to-stratified
> collapse — returns null.

## 8.3 T3d: no descriptor distinguishes the arms

Ten descriptors, Fisher exact, Bonferroni α = 0.005:

| descriptor | UNID | RES | ratio | p | verdict |
|---|---|---|---|---|---|
| k_ascend | 21.7% | 13.2% | 1.64 | 0.0133 | nominal |
| k_fast | 15.8% | 8.9% | 1.79 | 0.0146 | nominal |
| k_rotate | 17.5% | 13.8% | 1.27 | 0.279 | null |
| k_hover | 31.7% | 26.7% | 1.19 | 0.246 | null |
| k_vanish | 73.3% | 66.8% | 1.10 | 0.163 | null |
| k_pace / k_turn / k_erratic / k_split / k_descend | — | — | 0.79–1.00 | 0.50–1.00 | null |

**None survives correction.** The two nominal survivors then die under year
stratification — the sixth failure mode, holding yet again:

| descriptor | strata | MH odds ratio | z | p |
|---|---|---|---|---|
| k_fast | 21 | 1.479 | +1.53 | 0.126 |
| k_ascend | 21 | 1.486 | +1.72 | 0.086 |

## 8.4 The decisive version of the narrative-convention finding

At n = 2,257 the **RESOLVED** arm shows *statistically significant* sequence
structure: +0.0354 bits, p = 0.0017.

> **Acknowledged balloons, aircraft, meteors and satellites carry the same
> kinematic grammar, at the same magnitude, as the unknowns.** The structure
> is real and measurable — and it is a property of describing a receding
> aerial object, not of the object being unexplained.

And the magnitude scales with how narrative the writing is:

| corpus | register | sequence structure |
|---|---|---|
| Hatch catalog prose (Phase 6) | compiler narrative | **+0.2504 bits** (p=0.0005) |
| Blue Book case text, resolved | bureaucratic form + OCR | +0.0354 bits (p=0.0017) |
| Blue Book case text, unidentified | bureaucratic form + OCR | +0.0595 bits (p=0.08) |

A **7× gradient** from compiler prose to case record, with the resolved and
unidentified arms of the case records indistinguishable from each other. The
"grammar of departure" lives in the writer.

## 8.5 Standing

With T3 null at adequate power, the catalog-based programme is complete. Every
major claim tested in this project is either falsified or explained by a
mundane mechanism, and the control designed to be immune to all identified
artifacts found nothing. The §6 proposal (checkbox mark detection to raise the
labelled arm fivefold) is **no longer necessary for T3** — the test is
adequately powered as run. It would only be needed to chase an effect smaller
than 0.117 bits, and no hypothesis in the literature predicts one.
