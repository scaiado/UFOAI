# PURSUE: codename extraction, document gaps, and what redaction looks like in OCR

**Status:** complete. `omega/codenames.py`, `omega/scrubbed.py`.
**Corpus:** `pursue-uap-documents-2026` (archive.org), `source:
https://www.war.gov/UFO/`, 3,376 manifest entries, 286 OCR'd documents scanned.

---

## 1. Codename extraction

49 codenames searched. Every entry carries an **attestation tier**, because
mixing documented programmes with claim-only names and with known forgeries is
how a list of "hits" becomes a list of noise.

| Tier | meaning |
|---|---|
| OFFICIAL | named in government records |
| CONTRACTOR | acknowledged industry/defence programme |
| ALLEGED | named by claimants, no primary document |
| FABRICATED | officially assessed a hoax or forgery |
| GENERIC | real term, not a programme — kept to measure base rates |

### Two corrections to the working list

- **Project Condign** is a UK Defence Intelligence Staff study, **1996–2000**,
  report released 2006 — *not* 1950–1953.
- **Teaball** was a USAF MiG-warning weapons-control centre in Southeast Asia,
  1972. It was SIGINT/radar fusion for air combat, **not** a UAP programme.
  Retained as GENERIC to measure its base rate.

Also flagged: **"glimmer glass"** has no primary document — it enters the record
through 2023– testimony. **"santa clause"** appeared in the working list
attributed to the user; it was never provided and is not searched.

### Present in the corpus

| Tier | codename | docs | hits |
|---|---|---|---|
| OFFICIAL | gepan | 4 | 56 |
| OFFICIAL | project grudge | 3 | 7 |
| CONTRACTOR | skunk works | 3 | 15 |
| GENERIC | bogey | 3 | 10 |
| OFFICIAL | oxcart | 2 | 265 |
| OFFICIAL | project twinkle | 2 | 2 |
| OFFICIAL | aquatone | 1 | 29 |
| OFFICIAL | sepra | 1 | 42 |
| OFFICIAL | stargate | 1 | 24 |
| OFFICIAL | project stork | 1 | 1 |
| ALLEGED | project pounce | 1 | 1 |
| ALLEGED | tr-3b | 1 | 1 |
| FABRICATED | mj-12 | 1 | 1 |

`blue book` 22 docs, `AARO` 44 docs, `robertson` 8 docs (direct grep).

### Absent — searched, zero occurrences, reported as zero

**One methodological correction first.** "AAWSAP" returns **0 documents** in the
text but appears in **43 filenames**. The documents spell the programme out —
`ADVANCED AEROSPACE WEAPON SYSTEM APPLICATIONS PROGRAM` — and never use the
acronym. The acronym is an archival label applied later. Not a gap; a lesson
about acronym-only searching.

With that excluded, the substantive absences from a 372-document Department of
War UAP release:

| Searched | docs | note |
|---|---|---|
| **moon dust** | **0** | Project Moon Dust — the USAF/State programme whose stated purpose was recovering objects of unknown origin |
| uaptf | 0 | UAP Task Force, 2020–2022 |
| aatip | 0 | as an acronym |
| kona blue | 0 | AARO-acknowledged proposed DHS successor programme |
| looking glass | 0 | |
| have blue, tacit blue | 0 | |
| senior crown / year / prom / span / ruby / trend | 0 | |
| grill flame, center lane, sun streak, star gate | 0 | ("stargate" compound: 1 doc) |
| serpo, majestic, mj-12 variants | 0 | consistent with being claim-only or forged |
| condign, condon committee, robertson panel | 0 | as exact phrases |

**The asymmetry worth noting:** `AARO` — the current office — appears in 44
documents. Its predecessor task forces (`UAPTF`, `AATIP` as acronyms) appear in
none, and `moon dust` in none. A release curated by the current office names the
current office.

### Codename discovery

Pattern `PROJECT|OPERATION|PROGRAM|CODENAME + <Capitalised>`, ≥2 occurrences,
not in the known list. Result: **nothing of substance.** The top hits are OCR
artefacts — `BOOSTER⏎COMMAND` (56), `BOOSTBR⏎COMMAND` (6), `BOOSTRR⏎COMMAND`
(2), `CUM` (11), `COM` (4), `QLI` (2). The one real find is **`INHERENT
RESOLVE`** (3) — the anti-ISIS operation, correctly detected and legitimately
not UAP-related.

**No undiscovered codenames were found.** That is the honest result, and it is
worth more than a list of plausible-looking inventions.

---

## 2. Redaction: invisible in OCR, visible in the margins

| Marker | docs | occurrences |
|---|---|---|
| `[REDACTED]` / `[DELETED]` / `[WITHHELD]` brackets | **0** | **0** |
| FOIA exemption citations `(b)(n)` | 48 | 964 |
| block glyphs (█▓▒░) | 7 | 19 |
| "withheld/denied in full/part", "released in part" | 3 | 4 |
| classification banners in body text | 62 | 403 |

FOIA exemptions cited: **(b)(1) = 461** (classified national defence),
**(b)(6) = 401** (personal privacy), **(b)(3) = 81** (statutory),
(b)(7) = 10, (b)(4) = 5, (b)(2) = 4, (b)(5) = 2.

**The finding: PURSUE redactions cannot be detected from the text.** Zero
bracket markers. The withholdings are whiteout or blackout applied to the page
image, so OCR simply returns nothing where content was removed — no marker, no
gap, no artefact. The only textual trace is the exemption citation printed in
the margin, present in 48 of 286 documents.

Any method that looks for `[REDACTED]` in this corpus returns zero and reports
"unredacted." It is redacted: 964 exemption citations say so. **Detecting the
extent requires page-image analysis** (contiguous high-density dark or blank
regions in the JP2 scans), not text search. The `_jp2.zip` derivatives are in
the manifest for all 298 OCR'd documents, so this is buildable.

### Text quality

OCR is good: garble fraction median **0.0034**, p90 0.0114, max 0.0407. Nothing
here suggests tampering — the worst files are 1950s carbon copies
(`CIA-UAP-D020 Memorandum on Unconventional Aircraft Sightings 1955`, 0.0407).

51 documents under 1,500 characters. Nearly all legitimate: `FBI-Photo-B2`
through `B24` are photographs (5–21 chars of OCR noise).
`DOW-UAP-D085_Transmission-of-CIA-Scientific-Advisory-Panel-Rept_1953` at **14
chars** is the exception worth a look — a transmittal for the Robertson Panel
report with essentially no extractable text.

---

## 3. Document-number gaps

**Three of my first four gap findings were artefacts of my own ID parser.**
Recorded here because the correction is the useful part:

1. A trailing `\b` in the ID regex failed whenever a number was followed by `_`
   (`CIA-UAP-D020_Memorandum`), since `_` is a word character. This silently
   dropped half the corpus. Fixed.
2. **CIA switched conventions mid-series** — `CIA-UAP-018` then
   `CIA-UAP-D020`. Parsed as two series, this manufactured 18 phantom gaps.
   Merged: **1–29 complete, zero gaps.**
3. **NASA runs two independent series** — `D1`–`D7` (Apollo/Skylab) and
   `D015`–`D032` (Gemini, zero-padded). Treated as one, this manufactured a
   7-long phantom run. Split.
4. **`DOW-UAP-PR` is sparse parallel numbering**, not a sequence: only PR20,
   PR130, PR131 exist. Span-based gap counting over it produced a nonsense
   "109 missing." Now flagged `sparse_series` and never gap-counted.

### Corrected result (full 3,376-entry manifest)

| Sequence | present | range | missing | density |
|---|---|---|---|---|
| CIA-UAP | 29 | 1–29 | **0** | 1.000 |
| DOE-UAP-D | 5 | 1–5 | 0 | 1.000 |
| DOS-UAP-D | 2 | 1–2 | 0 | 1.000 |
| ODNI-UAP-D | 1 | 1–1 | 0 | 1.000 |
| NASA-UAP-VM | 6 | 1–6 | 0 | 1.000 |
| NASA-UAP-D (Apollo) | 6 | 1–7 | **1** (D3) | 0.857 |
| NASA-UAP-D (Gemini) | 11 | 15–32 | **7** (23–29) | 0.611 |
| **DOW-UAP-D** | **179** | **3–213** | **32** | **0.848** |

DOW-UAP-D missing: 9, 11, 13, 15, 21, 22, 24, 26, 29–31, 34, 36, 37, 39–41,
43, 45–47, 53, 59, **66–73**, 76.

Runs of ≥3: 29–31, 39–41, 45–47, and **66–73 (eight consecutive)**.

### The one gap worth asking about

**DOW-UAP-D66 through D73.** Eight consecutive numbers, and the documents on
either side are a continuous operational block:

| ID | Document |
|---|---|
| D60 | Mission Report, Persian Gulf, August 2020 |
| D61 | Mission Report, Persian Gulf, August 2020 |
| D62 | Mission Report, Strait of Hormuz, September 2020 |
| D63 | Mission Report, Strait of Hormuz, October 2020 |
| D64 | Mission Report, Iran, November 2020 |
| D65 | Mission Report, Persian Gulf, July 2020 |
| **D66–D73** | **not published** |
| D74 | Mission Report, Syria, November 2023 |
| D75 | Mission Report, Gulf of Aden, July 2024 |

Eight mission reports from the 2020 Middle East window, numbered and not
released. **A gap is a gap, not a suppression** — ID sequences skip for mundane
reasons: merged exhibits, withdrawn duplicates, numbers reserved and unused. But
this one is specific enough to name in a request, which is the point of the
exercise. Likewise `NASA-UAP-D3` (single, between two Apollo transcripts) and
`NASA-UAP-D23`–`D29`.

---

## 4. Releases 7 and 8 are undocumented by the archive itself

The item description states **six** releases, May 8 – September 18, 2026, and
"Files are organized by release (Release_01 … Release_06)". The manifest holds
**eight**: `Release_07` (308 entries, 28 source PDFs) and `Release_08` (40
entries, 40 source PDFs) were added after the description was written.

Their contents are the politically loaded end of the release:

**Release_07** — `DOW-UAP-D155`–`D182`: Air Intelligence Information Reports,
1953–1957, from foreign stations (Saudi Arabia, Guam, Italy, Canada, Germany,
Morocco) plus `Unresolved UAP Report Catalina Island 1952/1953`.

**Release_08** — two clusters:

- `CIA-UAP-D024`–`D029`, all 1952: *Approval in Principle — Research Concerned
  with UFOs*; ***Proposal to Consider Psychological Warfare Implications of UFO
  Related Issues***; *Summary Assessment of Flying Saucers*; *Office of
  Scientific Intelligence Briefing on Flying Saucers*; *Assessment of National
  Security Issues Relating to Flying Saucers*; *Official Diary Entry on Flying
  Saucers*.
- `DOW-UAP-D184`–`D213`: the AAWSAP/Senator Reid papers — *AAWSAP Talking Paper
  for Senator Reid Engagement, May 2009*; *Review of AAWSAP Special Access
  Program Request, November 2009*; *DIA Information Memorandum on AATIP/AAWSAP,
  December 2010*; *Review of AAWSAP Contract Deliverables, October 2009* — plus
  ~25 Air Intelligence Information Reports (1956–1957) and Unresolved UAP
  Reports (1949–1966).

**None of Release_07 or Release_08 has OCR.** They are in the manifest as
`Image Container PDF` (23) and `Additional Text PDF`, with no `DjVuTXT`
derivative. 286 of 338 distinct PDFs carry extractable text; the ~52 without are
concentrated in these two late releases. That is an archival artefact — the
derivatives were never generated — not a withholding, and it means the
**AAWSAP/Reid material and the 1952 CIA psychological-warfare assessments are
the least machine-readable part of the corpus.** They need local OCR. That is
the highest-value remaining ingestion task in this corpus.

---

## 5. NUFORC schema (Route 4)

Located at
`/tmp/claude-0/-home-user/f0aebeb3-1b62-5042-9067-46af83ba9a9d/scratchpad/uap/nuforc_dl/x/drastimehta-nuforc-ufo-event-sightings-csv/data/ufo_sightings.csv`

Corrections to the working assumptions:

- **134,906 records**, not 137,094. The higher figure is the line count;
  quoted fields contain embedded newlines.
- Columns are `month_year_of_event, event_date_time, city, state_provinces,
  shape, duration, summary, posted`. **There is no latitude, no longitude and
  no country column.** Any plan assuming `latitude`/`longitude`/`country`/
  `comments`/`date_posted` fails.
- Country is encoded inside `city` as a parenthetical — `Lachute (Canada)` —
  for 18,188 rows. 317 rows have no city at all.
- **33,976 distinct `city|state` pairs.** At Nominatim's 1 req/s that is ~9.5
  hours of geocoding, which is the real cost of making this corpus spatial.
  Geocode the pairs, not the rows.
- 115,422 records are post-2000; coverage runs to August 2021. A `1400` year
  value is a data error (the upstream description reads "August 2021 to June
  1400").
- `corpus.Rec` has **no `state` and no `id`** field. The fields are `uid,
  catalog, source, source_id, date_raw, year, month, day, prec,
  date_uncertain, lat, lon, location, country, desc, norm, refs, etype, attrs,
  credibility, duration, kv, summary, places`.

Ingestion is viable and worth doing — it is the modern-era arm the master
catalogue lacks (62 geocoded day-precision 2000s events against 115,422 here) —
but it is a geocoding job before it is an analysis job.

---

## 6. Reproduction

```bash
python3 -I omega/codenames.py    # -> data/processed/codenames/codename_index.json
python3 -I omega/scrubbed.py     # -> data/processed/scrubbed/scrubbed_content_report.json
```
