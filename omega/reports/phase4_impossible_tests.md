# PROJECT OMEGA — Phase 4: The Tests Nobody Has Run

**Code:** `omega/phase4.py`, `omega/phase4b.py` (corrections & audits).
**Output:** `data/processed/impossible_tests/phase4.json`

---

## 4A — Provenance-weighted signal test

Does the nuclear-proximity signal hide in any provenance stratum?
Decontaminated events, 500 km / 30 d, within-year conditional null, 4,000 perms.

| stratum | n | obs | exp | ratio | p |
|---|---|---|---|---|---|
| single-sourced (1 catalog) | 10,540 | 969 | 923.7 | 1.049 | 0.179 |
| corroborated (2–4 catalogs) | 5,259 | 591 | 583.4 | 1.013 | 0.396 |
| well-corroborated (≥5) | 818 | 69 | 84.6 | **0.816** | 0.913 |
| deep provenance (depth ≥10) | 266 | 38 | 43.6 | **0.871** | 0.715 |

**No stratum hides a signal.** The ratio *declines* monotonically with
corroboration — the best-attested events show 18% *less* nuclear proximity
than chance. A physical signal should strengthen with corroboration. This
closes Phase 2: the nuclear-proximity claim fails at every evidentiary level.

## 4B — Geographic hotspot persistence

**The first null model was degenerate and is withdrawn.** Drawing
pseudo-historical points from the pooled set draws ~99% modern points, and a
modern point always has a modern neighbour, so E[count] saturated at
n_historical and every z was ≈ −40. It measured nothing. Recorded here
because a reader of `phase4.json` will see those numbers.

Corrected null: permute the **era label within country**, holding fixed the
continental coverage shift (pre-1800 coverage is European; post-1950 is
US-dominated). Restricted to countries containing ≥3 events of both eras.

| comparison | radius | obs | exp | ratio | z | p |
|---|---|---|---|---|---|---|
| pre-1800 vs post-1950 (n=47 usable) | 50 km | 42.53 | 33.79 | 1.259 | +2.21 | 0.0145 |
| | 100 km | 113.04 | 95.34 | 1.186 | +2.11 | 0.0160 |
| | 250 km | 435.53 | 368.19 | 1.183 | +2.93 | 0.0015 |
| pre-1900 vs post-1950 (n=168 usable) | 50 km | 29.54 | 32.39 | **0.912** | −1.16 | 0.879 |
| | 100 km | 78.11 | 86.51 | **0.903** | −1.62 | 0.948 |
| | 250 km | 308.02 | 325.78 | 0.946 | −1.29 | 0.894 |

**Verdict: not evidence of persistence.** The pre-1800 effect (+18–26%) is
nominally significant but rests on **47 usable events**, and it *reverses*
when the historical window is widened to pre-1900 with 3.6× the sample. A
real geographic persistence effect cannot vanish and invert as power
increases. This fails an internal consistency check and should be treated as
an underpowered artifact until a properly geocoded ancient corpus exists.

The naive "top persistent hotspots" list (Ath, Leicester, Derby, Fleet,
Arras, Uxbridge — 260–306 modern events within 100 km) is simply a map of
modern European reporting density, which is why the label-permutation null
was necessary.

## 4C — Temporal spectral analysis and the solar cycle

Monthly series 1900–2000, n = 1,212 months, 31,810 events, mean 26.2/month,
peak 625 (July 1947).

**Annual cycle: χ² = 1,424.0, dof = 11, p < 1×10⁻³⁰⁰.**

| month | J | F | M | A | M | J | J | A | S | O | N | D |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| share | 7.2 | 6.5 | 7.7 | 7.1 | 6.6 | 7.0 | **11.6** | **11.0** | 9.0 | **10.7** | 8.7 | 6.9 |

A strong July–August–October peak, 1.8× the February trough. Consistent with
observer exposure (people outdoors on warm evenings), not with an exotic
driver.

**Periodogram (detrended by 25-month moving average):** the dominant peaks
are at **1.01 and 1.00 years** — the annual cycle. Remaining peaks (2.40,
1.77, 1.66 yr) sit at 13–16× median power and are not distinguishable from
the noise floor of a short autocorrelated series. **There is no 11-year
peak.**

**Solar cycle — and the second trap of this project:**

| test | statistic | p |
|---|---|---|
| naive Pearson (counts vs sunspot number) | r = +0.1131 | **7.98e-05** |
| naive Spearman | ρ = +0.1952 | 7.11e-12 |
| **phase-randomised surrogate** | r = +0.1131 | **0.348** |
| detrended residual vs sunspot | r = +0.0196 | 0.495 |

The naive test says p = 8×10⁻⁵. **The correct test says p = 0.35.** Both
series are strongly autocorrelated and both trend upward across the 20th
century; naive correlation of two autocorrelated series massively overstates
significance. Phase-randomised surrogates preserve the sighting series'
power spectrum (hence its autocorrelation) while destroying its phase
relationship to the solar series. Under that null the observed r sits
comfortably inside the distribution (null |r| 95th percentile = 0.200).

> **There is no solar-cycle correlation in UAP report rates.** This is the
> second time in this project that a naive test returned p < 1e-4 and the
> correct null returned nothing — after the nuclear-proximity test. Both
> would have been reported as discoveries by the specified method.

## 4D — The "light code" hypothesis, tested

**First formal information-theoretic test of structured encoding in UAP
light descriptions.**

Design: extract ordered colour-token sequences from descriptions; compare
observed bigram conditional entropy H(c₂|c₁) against a **within-report
shuffle** null, which preserves each report's colour composition exactly and
destroys only the order. Encoded information makes order predictable and so
lowers conditional entropy below the null.

n = 4,489 reports with ≥2 colour mentions; 12,430 colour tokens.
Frequencies: red 2,797 · white 2,706 · blue 1,538 · green 1,472 ·
orange 1,143 · black 928 · yellow 898 · silver 535 · gold 96 · amber 90 ·
purple 88 · pink 81 · violet 58.

| quantity | value |
|---|---|
| unigram entropy H(colour) | 3.0056 bits |
| observed conditional entropy H(c₂\|c₁) | **2.8817 bits** |
| within-report shuffled null | 2.8989 ± 0.0069 bits |
| one-sided p | **0.0060** |
| information gain over unigram | +0.1238 bits (+4.1%) |
| gain over shuffled null | +0.0172 bits (**+0.6%**) |
| zlib compressed size, observed vs shuffled | 9,758 vs 9,821 ± 26, p = 0.010 |

**The order is statistically non-random (p = 0.006).** So the hypothesis is
not trivially false — and this is the first time it has been measured. But
the bigram audit shows exactly what the order *is*:

| obs/exp | obs | exp | bigram |
|---|---|---|---|
| **4.50** | 190 | 42.2 | black → black |
| **3.41** | 55 | 16.1 | silver → silver |
| 2.05 | 115 | 56.1 | yellow → orange |
| 1.81 | 214 | 117.9 | blue → green |
| 1.75 | 184 | 105.4 | green → green |
| **1.72** | 395 | 229.5 | **red → green** |
| 1.70 | 110 | 64.8 | orange → orange |
| 1.31 | 162 | 123.2 | blue → blue |

The deficit decomposes into three mundane components:

1. **Self-repetition** — the largest effects by far are a colour repeating
   within one report (black→black 4.50×, silver→silver 3.41×). A report
   saying "black triangle … the black object" is not a transmission.
2. **Spectral adjacency / near-synonymy** — yellow↔orange, red↔orange.
3. **Aircraft navigation lighting** — red→green at 1.72× (395 vs 229 expected).
   Port red, starboard green is the international convention on every
   aircraft and vessel. In a corpus of aerial observations this is the single
   most expected colour pair in existence.

**Symmetry test** (an encoding has direction; a collocation does not): the
top pairs are either exactly symmetric by construction (self-pairs) or weakly
asymmetric (red→green 1.94 fwd/rev, white→red 0.95 — i.e. symmetric).
Nothing shows the strong directionality a code requires.

**Specificity control:** the same test on direction/compass words — a word
class that cannot plausibly be an NHI code — returns H_obs = 2.6130 vs null
2.6117 ± 0.0075, **p = 0.575**. No structure. So the colour effect is a real
measurement and not an artifact of the method; its *content* is simply
English and aviation convention.

> **Verdict: there is no light code.** Colour order in UAP reports carries
> 0.6% more structure than chance, and 100% of that structure is accounted
> for by within-report repetition, spectral near-synonyms, and the red/green
> navigation-light pair. The hypothesis is now measured rather than
> asserted, and it is falsified at the level the data can address.

## Limitations

1. 4B remains underpowered: only 47–168 geocoded historical events survive
   the dual-era country restriction. A geocoded *Wonders in the Sky* corpus
   would be the single highest-value addition.
2. 4C covers 1900–2000 only; the pre-1900 series is too sparse for monthly
   spectral analysis, and post-2000 coverage in this corpus collapses (62
   geocoded day-precision events in the 2000s).
3. 4D tests colour *sequence* order only. It does not test flash timing,
   pulse intervals or spectral content, because the corpus records prose, not
   photometry. A real test of temporal light structure requires instrument
   data (all-sky photometry), not sighting reports.
4. All four tests inherit Phase 1's ~90–93% linkage precision.
