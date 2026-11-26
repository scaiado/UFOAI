# PROJECT OMEGA — Phase 1: The Provenance Collapse

**Status:** complete. **Date:** 2026-11-25.
**Inputs:** `ufo_data/bin/*.json` (richgel999/ufo_data), 26 event catalogs.
**Code:** `omega/corpus.py`, `omega/dedupe.py`, `omega/phase1.py`, `omega/phase1_stats.py`
**Outputs:** `data/processed/provenance/master_catalog.json` (strict),
`master_catalog_inclusive.json`.

---

## 0. Correction to the stated input size

The headline figure of **69,185 records is not 69,185 events.** Decomposition:

| component | n | is it an event record? |
|---|---|---|
| 26 event catalogs | **52,710** | yes |
| `eberhart_openai.json` | 7,900 | no — NER annotations *of* Eberhart rows |
| `openai_results.json` | 6,534 | no — NER annotations |
| `nuclear_tests.json` | 2,041 | no — detonation reference table |
| total | 69,185 | |

All downstream analysis uses **n = 52,710**. Date parsing succeeds on
**52,670 (99.92%)** — far above the 78% a naive year-regex suggests —
because the corpus mixes `m/d/yy`, `m/d/yyyy`, `m/yyyy`, bare `yyyy`, and
`-1` sentinels for unknown components. Precision breakdown: 46,995 day,
3,734 month, 1,941 year, 40 none. Geocoded: 18,051 (Hatch only).

## 1. Method

Record linkage, not naive deduplication. Three stages.

**1.1 Candidate generation (two independent generators)**
- *Text*: global IDF fit, word 1–2 grams, sublinear TF; sparse cosine within
  year blocks (±1 year for pre-1900 or year-precision rows); floor 0.05.
  → 626,606 pairs.
- *Place/date*: exact (year, month, day) × shared **specific** place token,
  independent of wording. → 8,046 additional pairs.

The second generator is **required**. The corpus contains two
irreconcilable registers: Hatch's telegraphic style (*"2 observer(s). Bright
red disk going low over farm."*) and Johnson's prose (*"A bright red disc was
sighted moving low over a farm in Avellino, Italy."*). These are the same
event with near-zero lexical overlap. A text-similarity floor alone silently
discards them — the recall probe found Trans-en-Provence, the Lubbock Lights,
Haneda AFB and Minot AFB all being lost this way.

**1.2 Why lexical, not semantic, similarity**
The specification called for `all-MiniLM-L6-v2` at cosine 0.85. That is the
wrong instrument. Sentence embeddings measure *semantic* similarity, and
"bright light hovered over farmland, Ohio" vs "…, Texas" score >0.90. It would
merge thousands of distinct events and report a badly inflated collapse
factor. Recopied catalog entries are identified by *date and place*, with
wording as corroboration. (It was also untestable here: `huggingface.co`
is blocked by the container network policy, so no model could be fetched.)

**1.3 Decision rule**
Required: date compatible — tolerance set by *precision*, not era
(±1 d day-precision, ±31 d month, ±183 d year; pre-1900 widens only the
coarse precisions, ±2 d for day-precision). Veto: both geocoded and >150 km
apart (400 km pre-1900). Then tiers:

| tier | condition |
|---|---|
| T0_intra_strict | same catalog, cos≥0.60 ∧ jac≥0.40 ∧ shared place |
| T1_geo | both geocoded within limit |
| T2a_place_specific | shared *specific* place token ∧ both day-precision |
| T2b_place_coarse | shared place token is country/state-level → needs text |
| T3_text | one side has no place info → needs mid text support |
| T4_textoverride | place names conflict → needs high text support |

Text support is graded 0–3 from IDF cosine, char-4-gram Jaccard, and
rare-token overlap, computed **after** stripping catalog boilerplate
(`(NICAP: 09 - RADAR Cases, Code: R, Rating: 5)`, `(Translated from French)`),
which otherwise inflates cosine between unrelated entries sharing a template.

Transitive closure is guarded: connected components are rejected and
re-split under complete linkage if geographic spread exceeds 1.5× the limit
or date spread exceeds 400 days (112–164 components split).

**1.4 The decisive calibration finding**
An 80-pair hand-adjudicated development sample split sharply by catalog:

| pair type | correct | precision |
|---|---|---|
| **cross-catalog** | 42 / 45 | **93%** |
| **same-catalog** | 4 / 35 | **11%** |

A catalog compiler has already deduplicated their own list. Two entries in
one catalog are presumptively two *distinct reports* — Hatch listing Liège
and Grivegnée separately on 1974-09-10 is two sightings, not one.
**Duplication is a cross-catalog phenomenon.** Intra-catalog merging was
therefore restricted to near-identical text (NICAP listing one case under two
section headings), which accounts for only 99 of 27,653 accepted pairs.

This was then confirmed independently by base rates. Same-day + shared
specific place token occurs in:
- **2.31%** of *within*-catalog same-day pairs (47,154 pairs)
- **12.15%** of *cross*-catalog same-day pairs (158,101 pairs)

a **5.3× excess**. Under coincidence the two rates would match; the excess
implies ~81% of cross-catalog same-day/same-place pairs are duplications,
agreeing with the hand count (17/20).

## 2. Validation (held-out, disjoint from calibration)

| sample | n | correct | precision |
|---|---|---|---|
| strict rule, fresh draw | 59 | 55 | **93.2%** (95% CI ≈ 84–98%) |
| T4_textoverride tier | 18 | 17–18 | ~97% |
| inclusive-only additions | 30 | 27 | **90.0%** |

Residual error modes, all identified and three fixed: pre-1900 day tolerance
too loose (merged distinct 1897 airship events); aggregate "summary" rows
("Sweden recorded over 1,000 ghost rocket sightings") matching specific
events — now vetoed unless both dates are day-precise; empty location fields
forcing text-only matching — now backfilled by extracting place names from
description prose.

Because precision and recall genuinely trade off, the result is reported as
an **interval** from two linkages, not a point estimate.

## 3. Results

### 3.1 The collapse factor

| linkage | independent events | collapse | redundant records |
|---|---|---|---|
| strict (high precision) | **37,878** | 1.392× | 14,832 (28.1%) |
| inclusive (high recall) | **36,129** | 1.459× | 16,581 (31.5%) |

> **52,710 catalog records correspond to 36,100–37,900 independent events.
> The collapse factor is 1.39×–1.46×. Between 28% and 32% of all records in
> the combined UAP literature are redundant copies of an event already
> recorded elsewhere.**

### 3.2 The finding that matters more than the collapse factor

| appears in | strict | inclusive |
|---|---|---|
| **1 catalog only** | 30,119 (**79.5%**) | 27,660 (**76.6%**) |
| 2 catalogs | 4,652 (12.3%) | 4,946 (13.7%) |
| ≥3 catalogs | 3,107 (8.2%) | 3,523 (9.8%) |
| ≥5 catalogs | 745 (2.0%) | 917 (2.5%) |
| ≥10 catalogs | 3 (0.01%) | 2 (0.01%) |

**~77–80% of all recorded UAP events rest on a single catalog's word.**
Fewer than 2.5% have been independently picked up by five or more
compilations. The echo chamber is real but *bounded* at ~1.4×; the larger
structural problem is the opposite of what was hypothesised — not mass
duplication, but **mass single-sourcing**.

### 3.3 Which catalogs inflate (inclusive linkage)

| catalog | records | unique events contributed | % unique |
|---|---|---|---|
| Hatch_UDB | 18,116 | 11,631 | 64% |
| Johnson | 8,689 | 3,329 | 38% |
| EberhartUFOI | 7,901 | 4,453 | 56% |
| NICAP | 5,489 | 2,002 | 36% |
| Overmeire | 3,693 | 1,928 | 52% |
| rr0 | 3,376 | 2,009 | 60% |
| **Magonia (Vallée 1969)** | 923 | **41** | **4.4%** |
| **BlueBookUnknowns** | 584 | **8** | **1.4%** |
| UFOEvidenceHall | 493 | 119 | 24% |
| Dolan | 285 | 61 | 21% |
| WondersInTheSky | 478 | 351 | 73% |

**Vallée's *Passport to Magonia* catalog and the Blue Book Unknowns are now
almost entirely absorbed** — 95.6% and 98.6% of their entries respectively
appear in at least one other compilation. They are not independent evidence
in any analysis that also uses Hatch, Johnson or Eberhart; they are upstream
of them. Hatch's *U* database is the single largest source of genuinely
unique events (11,631), and *Wonders in the Sky* is the most independent
catalog in the corpus (73% unique) because nothing else systematically
covers pre-1800 material.

### 3.4 Circular citation

A mutual-citation cycle was detected between **Eberhart ↔ Johnson** (each
compilation references the other at ≥3 events). Top citation edges show the
true upstream primaries are Lumières dans la Nuit, APRO, FSR, MUFON, CUFOS,
NICAP, Project Blue Book, Vallée, and newspaper morgues.

### 3.5 Method sanity check

The deepest-provenance ranking was computed purely from citation-lineage
counts, with no case-fame input. It independently reproduced ufology's canon:
1896-11-25 California airship wave (depth 42), Rendlesham Forest 1980-12-28
(32), Socorro/Zamora 1964-04-24 (31), Exeter 1965-09-03 (27), Mantell
1948-01-07 (27), Trindade 1958-01-16 (27), Springfield MO 1897-04-16 (25),
Flatwoods/Desvergers 1952-08-19 (24), Roswell 1947-07-06 (24), Boianai/Gill
1959-06-27 (22), Valensole 1965-07-01 (22), McMinnville/Trent 1950-05-11
(21), Kelly-Hopkinsville 1955-08-21 (21), Villas Boas 1957-10-15 (20),
Battle of Los Angeles 1942-02-24 (20), Portage County 1966-04-17 (20).

That the method rediscovers the canon from citation structure alone is
evidence the linkage is tracking real evidentiary weight.

## 4. Limitations

1. **Geocoding is 34% and non-random** — essentially only Hatch. The T1_geo
   veto therefore cannot protect most cross-catalog comparisons.
2. **Precision is ~90–93%, not 100%.** Roughly 1 in 11 merges is wrong; at
   n≈20,000 accepted pairs that is on the order of 2,000 bad merges. The
   strict/inclusive interval is the honest expression of this.
3. **Recall is unmeasured in absolute terms.** The probe measured recall
   inside a high-prior pool, not corpus-wide. True event count may be below
   36,129.
4. **"Independent" means "not traceably copied."** Two compilers using the
   same 1952 newspaper are counted as two catalogs. Provenance depth
   partially corrects this; it does not eliminate it.
5. Catalog publication years are hand-coded from `ufo_data/README.md` and
   order lineages only approximately.
