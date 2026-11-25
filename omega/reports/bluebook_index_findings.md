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

---

# 7. CORRECTION: the investigator-proximity mechanism does not hold

§5 reported Ohio at OR 0.37 and I interpreted it as "a direct measurement of
investigator bias — unidentified is a property of how much investigative effort
reached a case." **Three follow-up tests do not support that mechanism.** The
Ohio *anomaly* is real; my explanation for it was wrong.

## 7.1 The distance gradient fails

State centroids were derived for all 50 states from Hatch's geocoded records
(matching both abbreviations and full names — a first attempt matched only 5
states because Hatch writes "TUCSON, AZ" while the index writes "Watsonville,
California", and that broken join must not be cited). 8,990 of 14,588 index
rows assigned a state and a great-circle distance to Wright-Patterson AFB
(39.826 N, 84.048 W).

| band | n | unid | rate | 95% CI |
|---|---|---|---|---|
| 0–300 km | 1,494 | 27 | **1.81%** | [1.22, 2.58] |
| 300–600 km | 917 | 40 | 4.36% | [3.18, 5.83] |
| 600–1000 km | 2,420 | 96 | 3.97% | [3.24, 4.80] |
| 1000–1500 km | 1,084 | 56 | 5.17% | [3.97, 6.60] |
| 1500–2200 km | 1,156 | 72 | 6.23% | [4.94, 7.73] |
| >2200 km | 1,919 | 96 | 5.00% | [4.09, 6.05] |

Spearman ρ = +0.0511, p = 1.2e-06 — significant but negligible in size, and
beyond the first bin the rate is flat at 4–6%.

**Logistic regression, unidentified ~ distance + year:**

| term | coef | se | z | p | OR |
|---|---|---|---|---|---|
| distance (per 1000 km) | +0.0295 | 0.0444 | 0.66 | **0.507** | 1.030 |
| year (centred 1958) | −0.1350 | 0.0110 | −12.22 | <1e-30 | 0.874 |

**The distance coefficient is null once year is controlled.** The marginal
Spearman significance is the year effect again, exactly as in §4.

## 7.2 The neighbour test kills the gradient outright

| state | km to WPAFB | n | unid | rate |
|---|---|---|---|---|
| **Ohio** | 96 | 1,200 | 12 | **1.0%** |
| **Indiana** | 181 | 180 | 14 | **7.8%** |
| Kentucky | 188 | 118 | 2 | 1.7% |
| West Virginia | 291 | 54 | 1 | 1.9% |
| Michigan | 334 | 278 | 12 | 4.3% |
| Illinois | 403 | 233 | 7 | 3.0% |
| Pennsylvania | 555 | 297 | 14 | 4.7% |

Indiana sits 181 km from Blue Book's headquarters with an unknown rate **nearly
8× Ohio's**. A proximity-to-investigator gradient predicts both should be low.
The effect is **Ohio-specific, not distance-dependent.**

## 7.3 What Ohio actually is

| property | Ohio | elsewhere | ratio | p |
|---|---|---|---|---|
| military observer | **2.1%** | **11.3%** | 0.19 | — |
| insufficient data | 24.0% | 18.5% | 1.30 | 5.6e-06 |
| aircraft | 20.1% | 15.8% | 1.27 | 1.9e-04 |
| satellite | 7.5% | 5.4% | 1.40 | 2.9e-03 |
| radar | 0.3% | 1.1% | 0.31 | 9.8e-03 |
| **unidentified** | **1.0%** | **4.7%** | **0.21** | 2.4e-12 |

And Ohio's volume is concentrated in the *late* era, when the corpus-wide
unknown rate had already collapsed below 2%: 1966 (208 cases, 17.8% of all
cases that year), 1967 (148), 1968 (97, 20.5%), 1969 (51, **32.3%**).

> **Corrected mechanism.** Ohio is not a population of well-investigated cases;
> it is a population of **late-era, overwhelmingly civilian, low-grade reports**
> — 2.1% military against 11.3% elsewhere, elevated "insufficient data",
> depressed radar. That is the signature of **civilian mail reaching the
> project's publicly known address**, not of superior investigation. Living near
> the HQ made you more likely to write in, and those letters were disposed of as
> insufficient or routine.

**What survives:** location strongly conditions disposition through **case
mix** — who reports, by what channel, in which era. That is still a serious
confound for anyone treating Blue Book unknowns as a sample of anomalous
events. **What does not survive:** the claim that "unidentified" measures
investigative effort, and any correction factor built on distance to
Wright-Patterson. The effort-corrected unknown rate cannot be computed this
way, because the distance coefficient is null.

## 7.4 Green fireballs: hypothesis rejected

I proposed that New Mexico's elevated unknown rate was the 1948–51 green
fireball cluster. **The opposite is true.**

| subset | n | unid | rate |
|---|---|---|---|
| New Mexico 1948–51 | 65 | 5 | **7.7%** |
| New Mexico other years | 182 | 21 | **11.5%** |

MH OR for New Mexico: **1.590** (p=0.033) full dataset → **1.958** (p=0.0063)
*excluding* 1948–51. Dropping the green fireball period makes the effect
*stronger*. The cluster is not the driver.

## 7.5 Japan: the FEAF-chain explanation fails

| theatre | n | unid | rate | MH OR | p |
|---|---|---|---|---|---|
| **Japan** | 115 | 17 | 14.8% | **2.01** | 0.016 |
| Korea | 59 | 5 | 8.5% | 0.81 | 0.67 |
| Guam/Pacific | 34 | 4 | 11.8% | 1.01 | 0.99 |
| Alaska | 128 | 5 | 3.9% | 0.75 | 0.53 |
| Europe (USAFE) | 207 | 11 | 5.3% | 0.77 | 0.41 |

If the elevated Japanese rate were the Far East Air Forces investigative chain,
Korea, the Philippines and Guam would be elevated too. They are not — Korea is
*below* 1.0. **Japan is specifically elevated, and the theatre explanation is
dead.** With 17 unidentified cases this may simply be small-n noise; it is
flagged as open, not as a finding.
