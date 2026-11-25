# PROJECT OMEGA — Tracks 3, 4, 5, 6

**Code:** `omega/track35.py` (provenance), `omega/track46.py` (proximity).
**Outputs:** `data/processed/provenance/track3_deep_provenance.{json,csv}`,
`track5_echo_chamber.json`, `data/processed/convergence/track46.json`

---

# TRACK 5 — The echo chamber, mapped

## Per-catalog duplicate inflation

| catalog | records | events touched | unique | inflation | duplicate share |
|---|---|---|---|---|---|
| Hatch_UDB | 18,116 | 17,888 | 11,631 | 1.01 | 35.0% |
| Johnson | 8,689 | 8,515 | 3,329 | 1.02 | **60.9%** |
| EberhartUFOI | 7,901 | 7,670 | 4,453 | 1.03 | 41.9% |
| NICAP | 5,489 | 5,199 | 2,002 | 1.06 | **61.5%** |
| Overmeire | 3,693 | 3,615 | 1,928 | 1.02 | 46.7% |
| rr0 | 3,376 | 3,273 | 2,009 | 1.03 | 38.6% |
| **Magonia** | 923 | 908 | **41** | 1.02 | **95.5%** |
| **BlueBookUnknowns** | 584 | 571 | **8** | 1.02 | **98.6%** |
| Dolan | 285 | 281 | 61 | 1.01 | 78.3% |
| UFOEvidenceHall | 493 | 491 | 119 | 1.00 | 75.8% |
| WondersInTheSky | 478 | 476 | 351 | 1.00 | 26.3% |

**Echo span** (years between the earliest and latest compilation citing the
same event): mean 5.9, median 0, **max 73**. 21.7% of events have a span ≥10
years, 9.1% ≥25 years, 2.7% ≥50 years.

**Root sources** — the upstream primaries that the compilations actually draw
on — resolve to: Lumières dans la Nuit, APRO, Flying Saucer Review, MUFON,
CUFOS, NICAP, Project Blue Book, Vallée, named investigators (Sparks, Gross,
Rupplet, Randles), and contemporary newspaper morgues.

# TRACK 3 — Deep-provenance audit of the 917

917 events are attested in ≥5 catalogs. Each was traced through its citation
chain and classified by how many **independent upstream roots** it has, where
a root is a cited source that is not itself one of the compilations in this
corpus.

| class | n | share |
|---|---|---|
| MULTI-ROOT (≥2 upstream sources) | 762 | 83.1% |
| SINGLE-ROOT (all attestation traces to one source) | 143 | 15.6% |
| **UNVERIFIABLE (zero upstream roots — cites only other compilations)** | **12** | 1.3% |

Independent roots per event: mean 3.63, median 3, max 36.

## The null test — and the quantified echo chamber

Null: permute source attributions across events, preserving each event's
citation **count** and the corpus-wide source frequency distribution. If
citations were drawn independently from the available source pool, a
deeply-attested event would accumulate diverse roots.

| quantity | value |
|---|---|
| observed mean independent roots | **3.628** |
| null | **5.130 ± 0.048** |
| p (one-sided, observed ≥ null) | **1.0000** |

> **Observed source diversity is 29% BELOW chance (3.63 vs 5.13 expected,
> z ≈ −31).** Even among the most heavily corroborated events in the entire
> UAP literature, attestation is significantly *more concentrated* in a few
> upstream sources than random citation would produce. This is the echo
> chamber measured against a null for the first time.

## Most independently attested events

| roots | catalogs | span | date | event |
|---|---|---|---|---|
| **36** | 7 | 23 yr | 1896-11-25 | California airship wave |
| 15 | 7 | 43 yr | 1947-07-04 | Portland, Oregon |
| 15 | 7 | 62 yr | 1948-01-07 | Mantell |
| 13 | 9 | 43 yr | 1948-12-05 | — |
| 13 | 8 | 43 yr | 1980-12-28 | Rendlesham Forest |
| 12 | 6 | 23 yr | 1897-02-04 | Inavale, Nebraska |
| 11 | 8 | 54 yr | 1952-06-19 | Goose Bay AFB |
| 11 | 8 | 43 yr | 1948-09-30 | Gorman dogfight |
| 11 | 7 | 54 yr | 1959-06-27 | Boianai (Gill) |
| 10 | 9 | 54 yr | 1961-09-19 | Betty and Barney Hill |
| 10 | 8 | 43 yr | 1973-10-11 | Pascagoula (Hickson) |
| 10 | 7 | 73 yr | 1950-05-11 | McMinnville (Trent) |

## The unverifiable set

**12 events appear in 5–6 separate catalogs while every single citation points
at another compilation inside this same corpus.** Zero upstream roots. These
have the *appearance* of strong corroboration and no traceable origin at all —
e.g. Galesburg IL 1967-03-09 (6 catalogs), a "small town in Texas" 1966-09-05
(6 catalogs), Dallas TX 1965-08-04 (5 catalogs), Wright-Patterson AFB
1951-06-01 (5 catalogs). Full list in `track3_deep_provenance.json`.

# TRACKS 4 & 6 — Facility-class proximity

## Layers acquired (Wikidata, coordinates present)

| layer | n |
|---|---|
| megalithic sites (stone circles, dolmens, tumuli) | 4,022 |
| US military bases | 948 |
| US airbases | 486 |
| nuclear test sites | 398 |
| nuclear power plants | 387 |

(Stone-circle and dolmen queries hit the 2,000-row cap, so the megalith layer
is a large sample rather than a census.)

## The null problem, and a null I had to withdraw

UAP reports and human infrastructure both concentrate where people are, so
"are sightings closer to bases than to random points?" is guaranteed to return
a spurious effect. My first fix — holding the pooled facility set fixed and
permuting class labels globally — **was also invalid**, and the output
diagnosed itself: every class came back p = 1.0000 with ratios 1.95–5.84. The
classes have disjoint geographic footprints (US-only military layers vs
Europe-only megaliths), so a mixed random label subset covers more of the
event distribution than any single class can, and everything looks "farther
than chance." Recorded here because the broken numbers are in the commit
history.

**Corrected null:** permute class labels **within 5° spatial cells**, which
preserves each class's geographic footprint and tests only class identity.

| class | n | obs median km | null median km | ratio | z | p |
|---|---|---|---|---|---|---|
| megalithic site | 4,022 | 75.2 | 74.9 | 1.004 | +0.10 | 0.559 |
| US military base | 948 | 309.2 | 279.2 | 1.108 | +0.98 | 0.919 |
| US airbase | 486 | 333.2 | 305.9 | 1.089 | +0.89 | 0.803 |
| nuclear test site | 398 | 792.6 | 843.1 | 0.940 | −0.69 | 0.317 |
| nuclear power plant | 387 | 126.2 | 124.3 | 1.016 | +0.38 | 0.674 |

**All five null** (Bonferroni α = 0.01).

> **UAP report locations are not specifically closer to military bases,
> airbases, nuclear power plants, nuclear test sites, or megalithic sites than
> to generic human infrastructure in the same region.** The megalith result
> (ratio 1.004, p = 0.56) is a direct falsification of the ancient-sacred-site
> proximity hypothesis that underpins the glyph and sacred-geometry programme.

## Descriptive proximity (no null — this is not a test)

| within | share of events |
|---|---|
| 5 km of any catalogued facility | 11.93% |
| 10 km | 21.71% |
| 25 km | 43.40% |
| 50 km | 63.32% |
| 100 km | 78.70% |

Median distance to nearest catalogued facility: **31.7 km**. These numbers look
striking and mean nothing on their own — they are what two population-following
distributions produce. The stratified test above is the actual result.

## Limitations

1. Megalith, military and airbase layers are Wikidata coverage, which is
   uneven by country and far from a census.
2. Sighting coordinates are Hatch's arcminute place-name geocoding (±2–20 km),
   which makes the 5 km and 10 km descriptive bands unreliable.
3. The class-specificity design cannot detect an effect shared by *all*
   infrastructure classes; it is deliberately blind to generic
   infrastructure proximity, which is unidentifiable without a population model.
4. Nuclear test sites are overwhelmingly remote (median 792 km from any
   report), so that layer has little power.
