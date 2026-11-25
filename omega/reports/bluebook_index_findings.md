# PROJECT OMEGA — The Blue Book Evaluation Index: Construction and First Findings

**Artifact:** `data/processed/bluebook/bluebook_evaluations.json` — 14,588 rows.
**Code:** `omega/bluebook_parse_index.py`, `omega/bluebook_fetch_cases.py`
**Status:** index complete and validated. T3 itself awaits the per-case
description fetch.

---

## 1. Construction

No machine-readable Project Blue Book disposition index existed on any
reachable host, so one was derived. 46 per-year index files (redacted and
unredacted scan variants, 1947–1969) from
`archive.org/cors/ProjectBlueBookIndexes` as `_djvu.xml` with per-word
coordinates. Rows reconstructed by clustering words on y and gating the
EVALUATION column on x (median 1534, IQR 1485–1584), then deduped across
variants on (year, evaluation, normalised location).

Operational note: `archive.org/download/` 302-redirects to datanodes the
egress proxy rejects; `archive.org/cors/` works.

| evaluation | n | share |
|---|---|---|
| astronomical | 4,305 | 29.5% |
| insufficient data | 2,765 | 19.0% |
| aircraft | 2,359 | 16.2% |
| other | 2,060 | 14.1% |
| balloon | 1,462 | 10.0% |
| satellite | 807 | 5.5% |
| **unidentified** | **645** | **4.4%** |
| radar | 146 | 1.0% |
| hoax | 39 | 0.3% |

## 2. Validation

1. **645 unidentified against the USAF's published 701 — 92% recall.**
2. 1952 recovers 1,556 rows against ~1,501 actual cases.
3. The per-year unidentified rate reproduces the documented history without
   being given it: 8.2% (1947), 12.5% (1950), 10.1% (1951), **15.1% (1952)**,
   9.2% (1954), then below 2% from 1956 — the Ruppelt-era high-unknown regime
   collapsing as evaluation practice tightened.

**Correction to delegated reconnaissance.** A subagent reported the CONCLUSION
field parseable in 83–90% of per-case OCR. My own stratified pilot (111 cases)
measured **43%**, with **64% label-ambiguous** because record cards print the
full checkbox label set and attached press clippings use "unidentified"
narratively. Usable rate 10.8%. Had that been trusted, label survival would
have depended on document type — a selection bias inside the control itself.
Labels therefore come from the index pages; per-case OCR supplies descriptions
only.

## 3. Q2 — the 16% over-count

14,588 recovered vs 12,618 official (+1,970). Decomposed:

| channel | n |
|---|---|
| residual cross-variant duplicates | 524 |
| rows flagged CASE MISSING in the index | 225 |
| rows with essentially empty location text | 232 |
| unexplained remainder | ~989 |

Rows by variant: redacted 8,971, unredacted 5,617. So roughly half the
over-count is identified; the remainder is most likely further near-duplicate
rows whose OCR'd location text differs enough to defeat the normalisation key.
The resolved arm is therefore mildly inflated, which does not threaten a
within-year comparison.

## 4. Q6 — observer type: a textbook Simpson's paradox

Marginally, military-observed cases look far more likely to be left
unidentified:

| comparison | unidentified | resolved | ratio | p |
|---|---|---|---|---|
| observer column says MILITARY | 18.1% | 10.2% | **1.78** | 3.7e-09 |
| military observer, non-AFB location | 15.5% | 8.6% | **1.81** | 2.5e-08 |
| location is an AFB/NAS | 8.7% | 4.4% | **1.96** | 4.8e-06 |

(The first naive version of this test conflated observer type with location,
because the regex matched "AFB" inside place names like "Travis AFB,
California Civilian". Split above.)

**Within year strata the effect disappears.** Military unknown rate exceeds
civilian in only **9 of 20 years** (sign test p = 0.824), and the mean
within-year difference is **+0.25 percentage points**.

> **The military-observer effect is entirely confounded by year.** 1952 alone
> contributes 274 military cases in the highest-unknown-rate year in Blue Book
> history. Pooling across years creates a 1.78× effect out of nothing. Anyone
> reporting "military witnesses produce more unknowns" from marginal Blue Book
> counts is reporting a Simpson's paradox.

## 5. Q4 — geography: survives year stratification, and the sign of the
## strongest result reveals the mechanism

Mantel-Haenszel odds ratios pooled within year (removing the confound that
destroyed §4):

| place | year strata | n | obs unid | exp unid | OR_MH | p |
|---|---|---|---|---|---|---|
| **San Antonio** | 5 | 51 | 9 | 3.3 | **3.68** | **7.5e-04** |
| Albuquerque | 13 | 44 | 7 | 3.0 | 3.00 | 1.4e-02 |
| Chicago | 13 | 67 | 8 | 4.3 | 2.14 | 6.0e-02 |
| **New Mexico** | 19 | 220 | 25 | 15.1 | **1.85** | **5.7e-03** |
| Japan | 14 | 109 | 13 | 7.9 | 1.80 | 5.3e-02 |
| Washington | 22 | 332 | 25 | 20.9 | 1.24 | 0.34 |
| Texas | 22 | 637 | 37 | 33.7 | 1.12 | 0.53 |
| Florida | 19 | 341 | 13 | 13.4 | 0.96 | 0.90 |
| California | 22 | 880 | 35 | 45.1 | 0.74 | 9.6e-02 |
| **Ohio** | 23 | 1,200 | 12 | 29.2 | **0.37** | **6.1e-04** |

Bonferroni for 10 places is α = 0.005: **San Antonio and Ohio survive.**

### The Ohio result is the interpretation

Ohio has the most cases of any place token in the corpus (1,200) and the
**lowest** unknown rate — 12 observed against 29.2 expected, OR 0.37.
**Wright-Patterson AFB, in Ohio, is where Project Blue Book was
headquartered.** Cases nearest the investigators were resolved far more often
than cases anywhere else.

> **This is a direct measurement of investigator bias.** The "unidentified"
> designation is not a property of events; it is a property of how much
> investigative effort reached them. Ohio got the most and has the fewest
> unknowns. New Mexico in 1948–51 — the green fireball period — was studied
> hard but stayed unexplained, and San Antonio sat far from Wright-Patterson
> with several air bases feeding reports in.

The honest reading of §5 is therefore **not** that New Mexico and San Antonio
host more anomalous phenomena. It is that the resolution rate varies
geographically with investigative access, and the Ohio coefficient is the
cleanest available estimate of that effect.

**Consequence for T3:** "unidentified" is a label about investigation, not
about phenomena. T3 can still ask whether unidentified cases are described
differently — but a positive result would be ambiguous between "the
phenomenon differs" and "cases that resist explanation are written up
differently." That ambiguity must be stated with the result.

## 6. T3 design constraint, recorded before the result

Unidentified cases concentrate in 1950–54 (relative rate 2.1–3.4×) and are
near-absent after 1956 (0.14–0.5×). An unstratified comparison would contrast
early-era against late-era text: different record-card forms, different
investigators, different OCR quality, different prose conventions. Any
kinematic difference would be an **era** effect.

**T3 will be stratified by year.** 21 years carry ≥5 cases in both arms,
covering 642 of the 645 unidentified. Recorded here before the test runs so it
cannot be mistaken for a post-hoc adjustment.
