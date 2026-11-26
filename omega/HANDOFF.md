# PROJECT OMEGA — session handoff, 2026-11-26

Everything below is on branch `claude/magical-gauss-wzgdqd` in
`tfawhellen-sudo/UFOAI`. Read this file first in a new session.

---

## 0. Standing constraints (carry these forward verbatim)

- FOIA / declassified / public data only. No stolen or classified material.
- No connecting to classified systems.
- No fabricated results. A negative result is reported negative.
- Do not file FOIA requests — draft them only.
- No noise with physics words attached.
- **No user-agent spoofing, no routing around proxy blocks.** The honest UA in
  use throughout is `omega-research/1.0 (academic UAP data study;
  non-commercial)`. Locating the same public data on a different host is
  research and is in scope; circumventing an access control is not.

---

## 1. What this session added

### 1.1 GEIPAN — the French state case file (the big acquisition)

`/fr/cnes/export/cas` on `www.geipan.fr` is a published bulk-export endpoint
linked from GEIPAN's own case-search page. It returns the complete French state
UAP case file.

- **3,404 cases**, 19 fields, **coordinates on every record**, 1937–2026.
- Official disposition on every case: **A 955 / B 1323 / C 1020 / D 106**.
- A = identified certain, B = probably identified, **C = unidentified for lack
  of information, D = unidentified despite adequate information.**
- Blue Book conflated C and D. GEIPAN separates them → **first ground-truth
  denominator in the project.**
- Saved: `data/raw/geipan/geipan_cases.json` (committed).

### 1.2 GEPAN Note Technique No. 16 — acquired, read, quoted

`CT/GEPAN-00013`, `ENQUETE 81/01`, *ANALYSE D'UNE TRACE*, 1 March 1983,
ISSN 0750-6694, **67 pp, 109,615 chars of extractable text**. Case
`1981-01-00849` TRANS-EN-PROVENCE (83) 8 Jan 1981, classified **D**.
Full 11-document dossier, 172 pages, 14.4 MB.

Two findings in the primary document that the secondary literature omits:

1. GEPAN's own lab table gives the spark-mass-spec reading as
   « Trace laissée sur le sol pouvant provenir d'un revêtement primaire
   (peinture) ayant été frotté » — **rubbed paint from "un corps de masse
   importante"**. Mechanically sufficient for every soil finding.
2. The INRA author **tested and rejected an ionising-radiation mechanism**:
   10⁶ rads of γ needed on *Arabidopsis* for equal-or-lesser pigment damage,
   and « L'action du rayonnement nucléaire ne présente donc pas d'analogie avec
   celle de la source énergétique impliquée ». Proposes **Mg²⁺ loss under an
   electric field** instead. Bears directly on Phase 2 and on the
   fallout-fogging alternative to arXiv:2604.00056.

Pigment loss: **30–50% active forms at 40 days**, β-carotene −57%,
violaxanthine −80%, correlated with distance from centre. GEPAN §8 explicitly
declines to treat any of it as confirming the witness.

Full quotes with section refs: `omega/reports/geipan_acquisition_and_disposition.md`

### 1.3 Two disposition results

**The unexplained residue fell 3.78×.** D-rate 0.0543 (≤1988) → 0.0144 (2007+),
z=+6.119, **p=9.4e-10**. C-rate 0.4955 → 0.2076. A+B 0.4502 → 0.7780. Not
caseload dilution (Spearman −0.1295, p=0.360, 52 years). Cause is in the data:
top modern identified cause is **sky lanterns (417)**, a product absent from
France before ~2005; then aircraft (93), **ISS (79)**. The toolkit changed, not
the sky.

**The D arm is the least documented arm, and it survives stratification.**
Document-attachment share D 0.4528 vs A+B 0.9794 (z=−25.83). Within-era,
D-weighted **−0.5351** vs marginal −0.5265 — no Simpson reversal. 1977–1988:
**0.152 vs 0.993, p=3.5e-58.** The cases the French state calls genuinely
unexplained are the cases whose documents are not published. → CADA request
target (France's FOIA analogue), naming case IDs.

### 1.4 Failure mode #7 — criterion-definitional confounding

The C-vs-D narrative test needed five decontamination tiers to interpret:

| Tier | removed | bal.acc | effect | MDD |
|---|---|---|---|---|
| L0 | nothing | 0.8494 | +0.3494 | 0.107 |
| L1 | sentences naming GEIPAN/class | 0.8019 | +0.3019 | 0.107 |
| L2 | + verdict lexicon | 0.8113 | +0.3113 | 0.107 |
| L3 | + analyst-reasoning sentences | 0.7643 | +0.2643 | 0.108 |
| L4 | + conjugated forms, length-matched | 0.7176 | +0.2176 | 0.107 |
| L5 | + all numerals and quantity words | **0.6795** | **+0.1795** | 0.106 |

**The leak changes form at every tier**: verdict sentence (« Le GEIPAN classe ce
cas en D : Phénomène étrange à très étrange ») → verdict lexicon → conjugated
verb (`manquons` 163/1017 C vs **0/106** D) → cause noun → measurement density
(`mètres`, `secondes`, `environ` — which *is* the operational meaning of
"adequate information") → narrative length (0.6321 alone).

**51% of the effect is identifiable leakage. The residual +0.1795 is reported as
an UPPER BOUND, not as content, because the gradient has not plateaued.**

**A+B-vs-D is withdrawn as circular by construction**: top discriminators are
the *names of the explanations* — `lanternes` 254/2271 vs **0/106**, `bolide`
87 vs 0, `iss` 72 vs 0, `vénus` 121 vs 1. A resolved narrative states its
cause; an unresolved one cannot. Unrepairable, not fixable.

This **explains rather than contradicts Blue Book T3**: T3's compiler-prose
effect of +0.2504 sits inside the GEIPAN leakage range.

### 1.5 PURSUE Release_07/08 OCR'd — 1.9 MB newly machine-readable

Neither Release_07 nor Release_08 has archive.org text derivatives, which put
the most loaded documents in the corpus out of reach. **All 40 now OCR'd**
(tesseract 5.3.4, 300 dpi grayscale, `--psm 1`), committed to
`data/raw/pursue_ocr/txt/`:

- **`DOW-UAP-D172-BAASS_Ten_Month_Report_July-2009` — 1,086,965 chars.** The
  major AAWSAP deliverable. **Not yet analysed.**
- `DOW-UAP-D182` AAWSAP Statement of Work Aug 2008 (20,114)
- `DOW-UAP-D183` Correspondence from Senator Harry Reid, 24 June 2009
- `DOW-UAP-D184–D188` Reid engagement papers, SAP request review, DIA
  AATIP/AAWSAP memo, contract-deliverables review (21,024)
- `CIA-UAP-D024–D029`, all 1952: Approval in Principle; **Proposal to Consider
  Psychological Warfare Implications of UFO Related Issues** (25,683, memo to
  Director, Psychological Strategy Board, SECRET/Security Information,
  "Approved for Release 2026"); Summary Assessment of Flying Saucers; OSI
  Briefing; Assessment of National Security Issues; Official Diary Entry
- ~25 Air Intelligence Information Reports 1956–57 and Unresolved UAP Reports
  1949–66

### 1.6 Codename extraction — honest version

49 codenames, each with an attestation tier (OFFICIAL / CONTRACTOR / ALLEGED /
FABRICATED / GENERIC). **13 present, 36 absent and reported as zero.**
`data/processed/codenames/codename_index.json`.

Corrections made: **Condign is 1996–2000**, not 1950–53. **Teaball was a
Vietnam MiG-warning weapons-control centre**, not a UAP programme.
**"glimmer glass" has no primary document.** **"santa clause" was never
provided by the user and is not searched.** The ~800 `senior <noun>` entries
were fabricated and are not in the list.

Methodological correction: **AAWSAP appears in 43 filenames and 0 document
bodies** — the documents spell the programme out. Not a gap.

Real absences: **`moon dust` 0 docs**, `uaptf` 0, `aatip` 0 (acronym),
`kona blue` 0, `looking glass` 0, all `senior *` 0, `serpo`/`majestic` 0 —
while **`AARO` appears in 44**. Codename *discovery* found **nothing**; top
hits are OCR artefacts of `BOOSTER COMMAND`.

### 1.7 Redaction and gap audit

**Redaction is invisible in PURSUE text**: zero `[REDACTED]` markers, but **964
FOIA exemption citations across 48 documents** — (b)(1)=461 (classified
national defence), (b)(6)=401 (privacy), (b)(3)=81. Withholdings are applied to
the page image, so OCR returns nothing with no marker. **Detecting extent needs
JP2 page-image analysis, not text search** — `_jp2.zip` exists for all 298.

**Three of my first four gap findings were artefacts of my own ID parser** (a
trailing `\b` failing on `_`; CIA's mid-series convention change
`CIA-UAP-018`→`CIA-UAP-D020`; NASA's two parallel series `D1–D7` and
`D015–D032`; `DOW-UAP-PR` being sparse parallel numbering). Fixed in
`omega/scrubbed.py`. Surviving real gaps:

- **`DOW-UAP-D66`–`D73`** — eight consecutive, sitting inside a continuous
  block of 2020 Middle East mission reports (D60–D65 Persian Gulf / Strait of
  Hormuz / Iran; D74 Syria 2023, D75 Gulf of Aden 2024). **The single most
  specific, checkable gap in the release.** A gap is a gap, not a suppression —
  but it is nameable in a request.
- `NASA-UAP-D3`; `NASA-UAP-D23`–`D29`
- DOW-UAP-D: 32 missing of 211, density 0.848

**The archive holds 8 releases while its own description documents 6.**

### 1.8 NUFORC schema — corrected

Path (ephemeral scratchpad, see §3):
`.../scratchpad/uap/nuforc_dl/x/drastimehta-nuforc-ufo-event-sightings-csv/data/ufo_sightings.csv`

- **134,906 records**, not 137,094 (the higher figure is line count; quoted
  fields contain embedded newlines).
- Columns: `month_year_of_event, event_date_time, city, state_provinces, shape,
  duration, summary, posted`. **No latitude, no longitude, no country.**
- Country is parenthetical inside `city` (`Lachute (Canada)`) for 18,188 rows.
- **33,976 distinct `city|state` pairs.** Coverage curve: top 2,000 pairs = 53%
  of records, 4,000 = 65%, 8,000 = 77%.
- `corpus.Rec` has **no `state` and no `id`**. Fields are `uid, catalog,
  source, source_id, date_raw, year, month, day, prec, date_uncertain, lat,
  lon, location, country, desc, norm, refs, etype, attrs, credibility,
  duration, kv, summary, places`.

---

## 2. In flight when the session ended

Two background jobs were running and **did not finish**. Both resume cleanly —
each skips what already exists on disk.

### 2.1 `omega/geipan_harvest.py` — GEIPAN dossier harvest

**Purpose:** the C-vs-D test is unidentifiable on analyst prose (§1.4). The fix
is **witness-level text written before or independent of the verdict** —
gendarmerie procès-verbaux (`PV n°...`), `Compte rendu enquête`, lab reports.
Those are in the dossiers.

**Progress:** 74 of 141 case pages fetched (47 D cases with documents + 94
matched C cases). 0 files downloaded yet — phase 2 had not started.
Page cache preserved at `data/raw/geipan/pages_cache.tar.gz` (committed).

**Resume:**
```bash
cd /home/user/UFOAI
mkdir -p data/raw/geipan && tar xzf data/raw/geipan/pages_cache.tar.gz -C data/raw/geipan
python3 -I omega/geipan_harvest.py
```
Case pages are Drupal-rendered and take 3–28 s each, so the script batches 8 per
curl invocation to reuse the TLS connection. Static files answer in ~0.3 s.
Expect ~15 min for the remaining pages, then the file phase.

### 2.2 `omega/gazetteer.py` — Wikidata bulk gazetteer for NUFORC

**Purpose:** NUFORC ships no coordinates and Nominatim at 1 req/s is ~9.5 h for
33,976 pairs. `query.wikidata.org` is allowlisted and serves the same data in
bulk, one query per state/province (a nationwide query times out).

**Progress:** 0 of 66 files. **A bug was found and fixed but the fixed version
never ran** — Wikidata labels contain raw control characters, so
`json.loads(...)` threw `Invalid control character`. Now `strict=False`.
Each state query takes ~60 s, so a full run is ~66 min.

**Resume:** `python3 -I omega/gazetteer.py`

**Verify the fix first** — this is the one piece of code in the repo that has
not been observed working end to end.

---

## 3. Ephemeral data that will be lost — and how to get it back

The scratchpad is session-local. These must be re-fetched:

| What | Recovery |
|---|---|
| PURSUE manifest `pursue_meta.json` | `curl -A "$UA" -L "https://archive.org/metadata/pursue-uap-documents-2026"` |
| PURSUE 286 OCR'd `_djvu.txt` | `archive.org/cors/pursue-uap-documents-2026/<urlencoded path>`; `/download/` 302s to rejected datanodes — **use `/cors/`** |
| NUFORC CSV | archive.org / data.world `drastimehta/nuforc-ufo-event-sightings-csv` |
| Blue Book index XML, case OCR | `services/search/v1/scrape` with cursor — **not** `advancedsearch` (returns duplicates: 5,592 of true 10,764) |

**Already durable and committed:** the 40 OCR'd Release_07/08 texts, the GEIPAN
case database, the GEIPAN page cache, all analysis JSONs, all scripts, all
reports.

---

## 4. Environment

Allowlisted (17): `arxiv.org`, `export.arxiv.org`, `www.sidc.be`,
`earthquake.usgs.gov`, `en.wikipedia.org`, `earth-search.aws.element84.com`,
`query.wikidata.org`, `nominatim.openstreetmap.org`, `archive.org`,
`nuforc.org` (403s), `www.cropcircleconnector.com`, `services.swpc.noaa.gov`,
`www.geipan.fr`, `geipan.fr`, `cnes.fr`.

**Blocked:**
- `web.archive.org` — proxy 403. The CDX API exists nowhere else, so **Wayback
  snapshot comparison cannot run.** `archive.org/wayback/available` works but
  returns only the single closest snapshot, not a time series.
  `archive.org/cdx/...` 404s.
- `www.cnes-geipan.fr` — proxy 403. GEIPAN's second host, serves current forms.
  Nothing needed so far was behind it.
- An `update_environment` request to add both was **rejected by the
  environments service**. Do not re-ask in chat.

Notes: combined remove+add `update_environment` calls are rejected — do them
separately. `tesseract` 5.3.4 + `eng`/`fra` and `poppler-utils` were installed
this session via `apt-get update && apt-get install -y tesseract-ocr
tesseract-ocr-fra` — **they are NOT in a setup script and must be reinstalled.**

---

## 5. Next, in priority order

1. **Analyse the BAASS Ten Month Report** (1.09 MB, `data/raw/pursue_ocr/txt/`).
   The largest unexamined primary document in the project. Section 2 is
   "Project/Research Summary" with "BAASS Investigations" subsections. Read the
   table of contents first and decide what is testable.
2. **Finish `geipan_harvest.py`**, extract the PV/enquête text, and run the
   C-vs-D test on **witness-level text** rather than analyst prose. This is the
   first version of that test with a chance of being identified. Predict the
   outcome before running it.
3. **Verify and run `gazetteer.py`**, join to NUFORC, ingest as the modern-era
   arm (corpus has 62 geocoded day-precision 2000s events against 115,422).
4. **OCR the TEP image-only dossier files** — `Analyses2 INRA-R.pdf` (60 pp,
   full biochemical series), `PV n°28 (1981308305).pdf` (11 pp, gendarmerie),
   `Photos-R.pdf`. Use `-l fra`. The INRA series is the quantitative backing for
   the 30–50% pigment claim.
5. **Track 2 (Sentinel-2)** — requested repeatedly, never started. Build the
   **matched-landcover control set first**, then detect; tier T0–T3. STAC
   verified working (35-band L2A for Socorro) at
   `earth-search.aws.element84.com`. Top 10 Phase 9 sites: Socorro/Zamora,
   Rendlesham, St-Mathias, Newark Valley, Lavonia, Cherry Creek, Cash-Landrum,
   Valensole, Réunion, Trans-en-Provence.
6. **PURSUE redaction extent via JP2 page images** — the only way to measure it
   (§1.7). Contiguous dark/blank region detection.
7. **860 OCR'd periodicals** (MUFON 485, APRO 260, IUR 115) to re-ground Phase 1
   provenance chains in primary sources — lifts Phase 1's biggest stated
   limitation.
8. **Convergence matrix** for top 50 Phase 9 sites, each cell a test statistic
   with a stated null.
9. **NHI Proof Report** — 27-section structure specified earlier.

---

## 6. Established results so far (do not re-derive)

Falsified: nuclear proximity (contamination — 0.6% of records produced 100% of
a 13× effect); ICBM proximity (self-referential — the March 1967
Minot/Malmstrom cluster is the claim's own founding data); sacred-site
proximity (megalith ratio 1.004, p=0.56); light-code entropy; solar-cycle
periodicity; persistence (cross-pipeline geocoding artefact — Nominatim and
Hatch DMS agreeing on settlement centroids); all 7 behavioural-intelligence
tests T1–T7.

Blue Book T3: **null at adequate power**, p=0.2727, MDD 0.1169 vs 0.112 target.
Resolved arm itself significant (+0.0354, p=0.0017). **7× gradient from compiler
prose (+0.2504) to case record (+0.0354).**

Provenance collapse 1.39–1.46×, 77–80% single-sourced. Echo chamber 3.628 vs
null 5.130 (29% below chance, z≈−31); 12 events with 5–6 catalogues and zero
upstream roots.

Occupant taxonomy: no spatial (p=0.52) or temporal (p=0.53) segregation; era
χ²=70.4 p=1.5e-07, pseudo-human 46.1%→13.6% vs Grey →63.2%.

**Three nulls withdrawn as invalid:** global class-label permutation across
disjoint footprints; density matching at the wrong scale; outcome-conditioned
subsetting.

**Seven failure modes documented** — contamination; underpowered artefact;
self-referential source events; narrative convention; cross-pipeline geocoding
convergence; marginal-to-stratified collapse; and now **criterion-definitional
confounding** (§1.4).

arXiv:2604.00056 (Doherty, 31 Mar 2026, POSS-I plate transients, IRR 1.80,
permutation p=0.006, Earth-shadow deficit) **verified real**; does not conflict
with Phase 2 (different instruments). Untested alternative: radioactive fallout
fogging photographic emulsion — the Earth-shadow deficit is the discriminating
measurement. **Note §1.2: the INRA γ-benchmark argues against an ionising
mechanism at trace sites.**

13 FOIA letters drafted, not filed: `omega/reports/foia_request_drafts.md`.
**New targets from this session:** DOW-UAP-D66–D73; NASA-UAP-D3 and D23–D29;
and a French **CADA** request for the undisclosed D-case dossiers (§1.3).
