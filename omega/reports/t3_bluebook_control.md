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
