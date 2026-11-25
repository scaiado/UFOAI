# PROJECT OMEGA — Phase 2: The Nuclear-Proximity Test

**Status:** complete — **the claim does not survive.**
**Code:** `omega/phase2.py` (tests), `phase2b.py` (pair audit), `phase2c.py` (decontaminated).
**Outputs:** `data/processed/nuclear_proximity/permutation_tests.json`, `decontaminated.json`

---

## 1. Design

**Data.** Deduplicated events from Phase 1 (inclusive linkage) with
coordinates and day-precision dates: **n = 16,718**. Detonations from
`nuclear_tests.json` with coordinates and day-precision dates: **n = 2,039**
(1,458 with yields; USA 1,032, USSR 715, France 198, Britain 45, China 45).

**Null model: space-time permutation (Kulldorff).** Sighting *dates* are
permuted across sightings with every location held fixed. This is the correct
null here because it automatically controls **all purely spatial
confounding** — population, military presence, media density, observer
distribution — since the spatial marginal is unchanged. The temporal marginal
is also unchanged (the 1952 flap still exists). Only the space-**time**
association is tested. 10,000 permutations; 12 windows; Bonferroni
α = 0.05/12 = 0.00417.

Two nulls were run, because one is not enough:

- **GLOBAL** — dates permuted corpus-wide. Confounded by era: Nevada testing
  and the 1950s sighting flap coincide in time for unrelated reasons.
- **CONDITIONAL** — dates permuted *within calendar years*, preserving annual
  sighting totals exactly. This removes the era confound and is decisive.

The distinction mattered. Under the global null, wide windows returned
*strongly negative* results (1000 km/180 d ratio 0.82, z = −8.62) — an
artifact, because the large sighting flaps fall in relative testing lulls.
The conditional null returns ratios of ~1.00 for the same windows. Anyone
reporting the global result alone would publish a spurious *anti*-correlation.

**Exact fast algorithm.** Under date permutation the geometry never changes,
so sightings are grouped by the exact set of detonations within radius *r*,
and in-window detonation counts are precomputed for every date in the pool.
One permutation then costs a single gather-and-sum rather than 34 M distance
computations.

## 2. First-pass result (contaminated)

Conditional null, full n = 16,718:

| window | obs | exp | ratio | z | p |
|---|---|---|---|---|---|
| 50 km / 1 d | 6 | 0.5 | **13.18** | +8.07 | **0.00010** ✓ |
| 50 km / 7 d | 10 | 1.7 | **5.99** | +4.77 | **0.00080** ✓ |
| 50 km / 30 d | 18 | 6.3 | **2.86** | +3.08 | **0.00370** ✓ |
| 100 km / 1 d | 7 | 0.7 | **9.36** | +7.13 | **0.00010** ✓ |
| 100 km / 7 d | 15 | 3.1 | **4.85** | +4.96 | **0.00040** ✓ |
| 100 km / 30 d | 25 | 12.5 | 2.00 | +2.21 | 0.02840 |
| 500 km / 7–90 d | — | — | 1.01–1.04 | <1.1 | ns |
| 1000 km / 30–180 d | — | — | 0.99–1.00 | <1.7 | ns |

Five windows significant after Bonferroni correction, with effect sizes up to
13×. **Stopping here would have "confirmed" the claim.** The observed counts
(6, 7, 10, 15, 18) are tiny, so every contributing pair was audited.

## 3. Why it is spurious — the pair audit

Three contamination mechanisms, none of which is UAP activity.

**C1 — CIRCULARITY. The catalogs contain the detonations themselves as
events.** Verbatim records that the matcher scored as "UAP sightings within
2 km and 0 days of a nuclear test":

| date | catalogs | description (verbatim) |
|---|---|---|
| 1945-07-16 | Eberhart, Hatch, Majestic, Overmeire, rr0 | "The first detonation of a nuclear weapon (an implosion-style plutonium-based bomb) takes place at the Trinity site…" |
| 1945-08-06 | Eberhart, Hatch, Majestic, Overmeire | "An atomic bomb (a fission weapon containing 64 kilograms of Uranium-235, Little Boy) is detonated 1,900 feet above Hiroshima…" |
| 1945-08-09 | Eberhart, Hatch, Majestic, Overmeire | "Another atomic bomb (Fat Man) is dropped on Nagasaki, Japan, by Bockscar" |
| 1954-03-01 | Eberhart, Hatch, Johnson, Majestic | "Castle Bravo is the most powerful nuclear device detonated by the US…" |

Testing this corpus against the detonation table partly tests the detonation
table **against itself**.

**C2 — OBSERVATION-OPPORTUNITY BIAS.** The surviving genuine reports come
from observers *stationed at test sites during tests*: Yucca Flat NV, Frenchman
Flat NV, Nellis AFB, Maralinga. Date permutation controls spatial confounding,
but it cannot control this, because the observers' presence at that location
is **caused by** the test programme. This is not removable from catalog data.

**C3 — REPORT FRAMING.** The report text references the test: *"3 silver
ovoids hover 600 M over atomic test 20 minutes before blast"*; *"four to six
flying discs passed through the mushroom cloud created after an Atomic bomb
test blast"*; *"Atomic test in progress"*; *"Follows atomic tests."* The
coincidence is part of why the record exists.

**Pair inflation.** One Yucca Flat 1951-10-30 sighting pairs with seven
separate detonations (Able, Baker, Charlie, Dog, Easy, Sugar, Uncle) inside
30 days. The 18 "pairs" at 50 km/30 d are ~6 distinct events.

## 4. Decontaminated result

C1 and C3 were removed by explicit rule: 14 records that *are* detonations or
weapons-programme milestones, and 87 whose description references atomic
testing. **101 records removed — 0.6% of 16,718.** Clean n = 16,617.

| window | obs | exp | ratio | z | p (conditional) | verdict |
|---|---|---|---|---|---|---|
| 50 km / 1 d | **0** | 0.1 | 0.00 | −0.22 | 1.000 | null |
| 50 km / 7 d | **0** | 0.3 | 0.00 | −0.40 | 1.000 | null |
| 50 km / 30 d | **0** | 1.0 | 0.00 | −0.80 | 1.000 | null |
| 100 km / 1 d | **0** | 0.3 | 0.00 | −0.55 | 1.000 | null |
| 100 km / 7 d | **0** | 1.5 | 0.00 | −0.97 | 1.000 | null |
| 100 km / 30 d | 2 | 6.2 | 0.32 | −1.09 | 0.939 | null |
| 500 km / 7 d | 380 | 396.2 | 0.96 | −0.67 | 0.750 | null |
| 500 km / 30 d | 1,629 | 1,594.6 | 1.02 | +0.57 | 0.282 | null |
| 500 km / 90 d | 5,042 | 5,021.9 | 1.00 | +0.22 | 0.421 | null |
| 1000 km / 30 d | 4,019 | 4,036.2 | 1.00 | −0.18 | 0.572 | null |
| 1000 km / 90 d | 12,251 | 12,432.7 | 0.99 | −1.31 | 0.906 | null |
| 1000 km / 180 d | 24,299 | 24,514.2 | 0.99 | −1.59 | 0.943 | null |

**Zero of twelve windows shows any excess. 0.6% of the records produced the
entire effect.**

### Yield correlation (clean, 500 km / 30 d)

| yield band | n tests | obs | exp | ratio | p |
|---|---|---|---|---|---|
| 0–10 kt | 607 | 323 | 297.2 | 1.087 | 0.256 |
| 10–100 kt | 603 | 543 | 538.4 | 1.009 | 0.434 |
| 100–1000 kt | 158 | 54 | 59.8 | 0.902 | 0.736 |
| ≥1 Mt | 88 | 1 | 2.9 | **0.346** | 0.963 |

**The gradient runs backwards.** A physical attraction mechanism predicts
*more* clustering at higher yield; the data show monotonically *less*, with
megaton-class tests at ratio 0.35. This is independent evidence against any
energy-coupled mechanism.

### Type correlation (clean, 500 km / 30 d)

| type | n tests | obs | exp | ratio | p |
|---|---|---|---|---|---|
| atmospheric/air | 497 | 398 | 395.2 | 1.007 | 0.467 |
| underground | 1,502 | 1,231 | 1,197.8 | 1.028 | 0.153 |
| underwater | 10 | 0 | 0.0 | — | 1.000 |

No difference. Atmospheric tests — visible for hundreds of kilometres — show
no more sighting excess than underground ones.

## 5. Conclusion

> **The claim that UAP reports cluster around nuclear detonations is not
> supported. The apparent correlation is entirely an artifact of catalog
> contamination: the compilations include the detonations themselves as
> events, and the remaining proximate reports were generated by observers
> stationed at test sites whose descriptions reference the test. After
> removing 0.6% of records, the effect size falls from 13× to zero across all
> twelve space-time windows, and the yield gradient is inverted.**

Effect size after decontamination, 500 km/30 d: ratio 1.02
(95% null interval 0.95–1.06). The data are consistent with **no association**.

## 6. Limitations — and what is NOT tested

1. **C2 is not removable.** Observation-opportunity bias at test sites cannot
   be controlled with catalog data. The honest statement is that the corpus
   *cannot* test the detonation-proximity claim cleanly, and that what signal
   exists is fully explained without an anomalous cause.
2. **This does not test the missile-FACILITY claim.** The Malmstrom AFB
   Oscar-Flight incursion testimony (Salas and others) concerns ICBM launch
   control facilities, not detonations. That record was itself removed as a C3
   contaminant here — correct for this test, but it means the facility claim
   is **untested**. It requires a silo/LCF coordinate layer the corpus lacks.
   This is the single highest-value follow-up (Phase 5).
3. Geocoding is Hatch-dominated, so the geocoded subset is not a random
   sample of the corpus.
4. Only 1,458 of 2,039 detonations carry yields; yield bands are therefore
   partial.
5. Decontamination by regex is conservative in one direction: it removes real
   sightings that merely *mention* atomic context. The signal vanishes anyway.
