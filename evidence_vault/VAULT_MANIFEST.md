# PROJECT OMEGA — EVIDENCE VAULT

**Living index. Updated whenever anything is added.**
Last updated: 2026-11-26.

## Why this exists

`data/raw/` and `data/processed/` are **gitignored**. Anything left there dies
with the container. That already cost the project the Trans-en-Provence dossier
once: §1.2 acquired it, and §5 item 4 had to re-queue the whole thing. This tree
is **not** gitignored. Binaries are force-added.

**Admission rule.** Everything here is one of:
- **(a)** a primary-source document,
- **(b)** a processed result expensive to regenerate, or
- **(c)** a cross-reference index joining multiple sources.

Nothing speculative. Nothing manufactured. If a measurement is null, it says so.

**Size rule.** A vault that cannot be pushed is not durable. Anything over
~80 MB is stored as a fetch manifest with exact URLs, sizes and upstream SHA-1s
instead of bytes. The 37 DIRD **PDFs** are 1,779.6 MB — they are *not* here; the
texts (3.4 MB) are, and `01_PURSUE_PRIMARY/FETCH_MANIFEST.json` reproduces the
PDFs in one command.

---

## 01_PURSUE_PRIMARY — **POPULATED**

Source: archive.org `pursue-uap-documents-2026` via `/cors/` (`/download/` 302s
to rejected datanodes). 51 files, zero fetch failures.

### `AAWSAP_DIRDs/` — 37 texts, D117–D153
The Defense Intelligence Reference Documents commissioned under AAWSAP. Each
opens *"Defense Intelligence Reference Document / Defense Futures"* with an ICOD
date, marked UNCLASSIFIED//FOR OFFICIAL USE ONLY. Complete, no gaps in D117–D153.

Notable titles: Traversable Wormholes Stargates and Negative Energy (D139) ·
Warp Drive Dark Energy and the Manipulation of Extra Dimensions (D138) ·
Antigravity for Aerospace Applications (D135) · Negative Mass Propulsion (D152) ·
Quantum Tomography of Negative Energy States in the Vacuum (D153) · Concepts for
Extracting Energy from the Quantum Vacuum (D142) · Metamaterials (D141) ·
Invisibility Cloaking (D122) · Advanced Space Propulsion Based on Vacuum
Spacetime Metric Engineering (D132) · The Role of Superconductors in Gravity
Research (D131) · An Introduction to the Statistical Drake Equation (D127) ·
**Anomalous Acute and Subacute Field Effects on Human Biological Tissues (D128)** ·
High Frequency Gravitational Wave Communications (D140) · Positron Aerospace
Propulsion (D123) · Aneutronic Fusion Propulsion I & II (D145/D146).

*Note: D125 is filed `AAWSA-DIRD` in the archive — a typo upstream, not ours.*

### `nuclear_facility/` — 5 PDFs + 5 texts
`DOE-UAP-D001` PANTEX image · `D002` James Tuck correspondence · `D003` Pajarito
astronomers · **`D004` Los Alamos Conference on Aerial Phenomena, 1949** ·
**`D005` Pantex Unidentified Object Incident Report, 2015**.
`DOE-UAP-D017` (Sandia) **is not in the manifest** — see §05.

### `range_fouler/` — 2 PDFs + 2 texts
`DOW-UAP-D089` Range-Fouler Debrief, Eastern US, **2020** ·
`DOW-UAP-D090` Range-Fouler Debrief, Eastern US, **2019**.

---

## 02_GEPAN_PHYSICAL_TRACES — **POPULATED**

### `Trans-en-Provence_1981/`
Case `1981-01-00849`, class **D**, 43.5°N 6.49°E. **10 files, 177 pages, 15 MB.**
GEPAN **Note Technique No. 16** = `CT/GEPAN-00013`, *ENQUÊTE 81/01 — ANALYSE
D'UNE TRACE*, 1 March 1983, ISSN 0750-6694, 67 pp, 109,615 chars.
Three files were image-only and are machine-readable here for the first time:
the 60-page INRA biochemical series, the 11-page gendarmerie telex, the plates.

**Labs (corrected — NOT LERM):** LDP spark mass spectrometry · SNEAP CAMECA
microprobe · D.E.R. university microscopy · INRA Montfavet plant biochemistry ·
ALAT aerial activity · Météorologie Nationale.

Analysis: `omega/reports/geipan_trans_en_provence.md`; write-up and replication
(2026-11-26): `omega/reports/nt16_writeup_and_replication.md`.

`tep_dossier_pageocr_2026-11-26.tar.gz` — page-by-page tesseract (fra, 300 dpi)
of the seven image-only or handwritten-table files (INRA ×2, PV, Photos, LDP,
SNEAP, DER), one `.txt` per PDF page so citations can name a page. OCR of
handwriting is poor; every number used in the replication was read from the
page image, not from this OCR.

### `other_lab_cases/` — the matched control set
All five other physical-sample cases in the 3,404-case archive, 16 files, 75 MB.
**TEP is the only class-D one.** The rest resolved to: lightning ×2, aircraft
lavatory ice, a distress flare, and a German WWII Nebelwerfer.

`lab_analysis_cases.json` — the 20 "analysis"-document cases, filenames read.
`cada_targets.json` — the 56 undisclosed D cases, 55 of which carry
`Cas revisité = Oui` (z=+8.605, MH OR 209 by decade).

---

## 03_RETAINED_SAMPLES — **PARTIAL**

`priority_434.json` / `.csv` — **434 events**, `priority_score` ranked. Top:
Socorro/Zamora 1964, Delphos 1971, Eagle River 1961.

**Carries its own `scope_limit`, quoted verbatim:** *"extant/custody/assay
columns are UNVERIFIED; the archives that would settle them (CUFOS, APRO,
GEPAN/SEPRA, university collections) are not reachable from this environment."*

**ABSENT: the "1,917 ranked soil assay targets."** No such artefact exists in
this repository — zero mentions anywhere in `omega/`. Not built, not lost.
Per-case subfolders (Socorro, Delphos, Eagle River, Cherry Creek, Cash-Landrum)
are **not** created, because no per-case primary documents have been acquired
for them. Creating empty named folders would imply evidence that is not held.

---

## 04_CODEWORD_INDEX — **POPULATED**

`codename_index.json` — **29 present of 58 searched**, over 559 documents in four
corpora. Every entry tiered OFFICIAL / CONTRACTOR / ALLEGED / FABRICATED /
GENERIC. 29 searched and **reported as zero**, including `aawsap` (the documents
spell it out; `baass` appears 1,551 times), `moon dust`, `kona blue`, `looking
glass`, `project serpo`, every `senior *`, `majestic-12`, `uaptf`.

**Two keyword traps removed by reading every occurrence:**
- `aurora` 28 → **3** hits. Rejects: aurora borealis, a satellite "AURORA II",
  NASA's Fast Auroral Snapshot Explorer, Gemini astronauts describing auroras.
  The 3 survivors are all hedged — *"alleged"*, *"rumored"*, *"supposed"*.
- `stargate` 27 → **0**. It is the DIA wormhole paper (figure: *"A Stargate in
  Times Square"*), a URL, and a GEIPAN witness naming a TV show. The real
  programme is `star gate` (8 hits), corroborated by `grill flame`,
  `center lane`, `sun streak`.

---

## 05_SCRUBBED_CONTENT — **POPULATED**

`numbering_gaps.json` · `redaction_report.json` · `redaction_report.txt` ·
`image_only_docs/index.json`. Produced by `omega/scrubbed_v2.py`.

### Numbering gaps, agency union (368 stems)

| agency | n | range | missing | density | longest runs |
|---|---|---|---|---|---|
| CIA-UAP | 29 | 1–29 | **0** | 1.000 | — |
| DOE-UAP | 5 | 1–5 | 0 | 1.000 | — |
| DOS-UAP | 2 | 1–2 | 0 | 1.000 | — |
| **DOW-UAP** | 174 | 3–213 | **37** | 0.825 | **66-73**, 79-83, 29-31, 39-41, 45-47 |
| FBI-UAP | 40 | 1–43 | 3 | 0.930 | 34-36 |
| ODNI-UAP | 1 | 1–1 | 0 | 1.000 | — |
| USG-UAP | 2 | 1–2 | 0 | 1.000 | — |

**CIA-UAP is complete, 29 of 29.** The apparent CIA gaps in earlier work were
entirely the `CIA-UAP-018` → `CIA-UAP-D020` convention change.

**NASA is two PARALLEL series, not one with a hole:** `D1–D7` missing **D3**, and
`D15–D32` missing **D23–D29**. The empty span 8–14 between them is a boundary,
not a gap — reporting it as one is the §1.7 artefact.

**`DOW-UAP-D66–D73`, eight consecutive, independently reproduced.** It sits
inside the 2020 Middle East mission-report block, and **D60, D63 and D65 — the
released members of that same block — are image-only with no text derivative.**
So the most specific gap in the release is surrounded by documents that are
themselves invisible to text analysis.

### Markings over 326 text documents

`decl_date` 68 docs/486 · `banner_S` 53/360 · **`foia_b6` 43/409** (privacy) ·
`banner_C` 39/196 · `portion_S` 30/197 · **`banner_TS` 24/76** · `foia_b3` 21/79 ·
`cav_FOUO` 20/101 · `cav_NOFORN` 13/238 · **`foia_b1` 11/454** (classified
national defence) · `cav_SCI` 10/27 · `redact_mark` **5/6** · `portion_TS` 1/25 ·
`cav_ORCON` 1/1 · `cav_BYEMAN` 1/3.

**`redact_mark` at 5 docs / 6 hits confirms §1.7:** explicit `[REDACTED]` markers
are effectively absent while 454 `(b)(1)` citations exist. Withholdings are
applied to the **page image**, so OCR returns nothing and leaves no marker.
**Redaction EXTENT is therefore not measurable from text** — it needs the JP2
page images, which exist for all 298 documents (1,358 MB for the DIRDs alone).
`image_only_docs/` lists the 23 declared image-only stems.

---

## 06_NUFORC_MODERN_ARM — **POPULATED**

`nuforc_unified.json.gz` — **134,906 records**, of which **123,771 geocoded
(91.7%)**, every one at **day precision**. Provenance recorded per record in
`kv.GeocodeSource`: 115,890 Wikidata (85.9%), 7,881 Nominatim (5.8%).
107,012 are from 2000 onward.

Gazetteer behind it: 1,740,621 entries across 67/67 admin units, zero query
failures, after five distinct bugs (two wrong Q-ids, truthy-only `wdt:P625`,
`mul`-coded labels, oversized responses, admin unit absent from its own result
set).

*Note: 134,906 is the record count. The 137,094 figure is a line count inflated
by embedded newlines inside quoted fields.*

---

## 07_PERIODICALS_PRIMARY — **EMPTY, NOT ACQUIRED**

MUFON 485 / APRO 260 / IUR 115 = 860 issues. §5 item 7 lists these as **to do**;
they have never been fetched. Nothing is lost — nothing was held.

## 08_SATELLITE_ANOMALIES — **EMPTY, NOT STARTED**

No SKYWATCH T0/T1 dataset exists in this repository (zero mentions in `omega/`).
§5 item 5 records Track 2 Sentinel-2 as *"requested repeatedly, never started"*.
The STAC endpoint `earth-search.aws.element84.com` is verified reachable and
allowlisted; the **matched-landcover control set must be built before detection**,
per the standing design.

## 09_WHISTLEBLOWER_TESTIMONY — **EMPTY, RE-FETCHABLE**

`data_universe_recovered.md` records the 2023 Grusch hearing statements as found
on archive.org under official `HHRG-118-GO06` naming, **but the bound GPO
verbatim transcript as NOT available.** The files lived in `data/raw/` and are
gone. Re-fetchable from archive.org.

## 10_HIDDEN_BURIED — **EMPTY**

Reserved for material recovered by legitimate deep parsing: `sitemap.xml`,
HTML comments, meta tags, inline JS data in pages the server serves us.

**Scope note, stated plainly.** Reading `robots.txt` to *respect* it is in scope.
Fetching paths a site's `robots.txt` disallows is circumventing an access
control, which the standing constraints exclude — *"Locating the same public
data on a different host is research; circumventing an access control is not."*
So `robots.txt` will not be mined for forbidden paths.

---

## Network reality, for whoever picks this up

Allowlisted (8): `archive.org`, `www.geipan.fr`, `geipan.fr`, `cnes.fr`,
`query.wikidata.org`, `nominatim.openstreetmap.org`,
`earth-search.aws.element84.com`, `en.wikipedia.org`.

**Not reachable, so the following are blocked rather than pending:** `war.gov`,
`aaro.mil`, `nuforc.org` (403s anyway), `cia.gov`, `fbi.gov`, `nro.gov`,
`nasa.gov` reading rooms, `arxiv.org`, `web.archive.org`. GitHub access is
scoped to named repositories. Any task requiring those hosts needs them
allowlisted first.
