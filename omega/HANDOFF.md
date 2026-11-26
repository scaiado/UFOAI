# PROJECT OMEGA — session handoff

*Updated 2026-11-26 (session 4). §1.14–1.15 and the rewritten §2–§5 are from
session 4; §1.12–1.13 from session 3; §1.9–1.11 from session 2; §1.1–1.8 from
session 1.*

Current branch: **`claude/gallant-lamport-0tu52r`** in `tfawhellen-sudo/UFOAI`
(session 3's `claude/magical-gauss-wzgdqd` was fast-forwarded into it; see §2).
Read this file first in a new session.

**Session 4 corrected numbers that earlier sections of this file state in their
own voice.** §1.4's ladder is superseded by §1.14 — the table in §1.4 carries the
seed-averaged values now, but if any figure disagrees, **§1.14 wins.**

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
Full dossier: 10 files, 177 pages, 14.4 MB (corrected 2026-11-26; earlier "11 documents, 172 pages" did not match the files). Write-up and replication: `omega/reports/nt16_writeup_and_replication.md`.

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

**SEED-AVERAGED IN SESSION 4 — use these, not the single draws.**
(`omega/reports/geipan_tier_seed_stability.md`)

| Tier | removed | **seed-averaged effect** | range | old single draw |
|---|---|---|---|---|
| L0 | nothing | **+0.3387 ± 0.0229** | 0.094 | +0.3494 |
| L1 | sentences naming GEIPAN/class | **+0.2771 ± 0.0300** | 0.109 | +0.3019 |
| L2 | + verdict lexicon | **+0.2628 ± 0.0318** | 0.109 | +0.3113 |
| L3 | + analyst-reasoning sentences | **+0.2333 ± 0.0308** | 0.113 | +0.2643 |
| L4 | + conjugated forms, length-matched | **+0.2135 ± 0.0276** | 0.109 | +0.2176 |
| L5 | + all numerals and quantity words | **+0.1972 ± 0.0271** | 0.104 | +0.1795 |

24 joint seeds per tier. **24/24 significant at every tier.** Adjacent tiers are
NOT distinguishable: within-tier range 0.094–0.113 vs tier steps of 0.016–0.020.

**The leak changes form at every tier**: verdict sentence (« Le GEIPAN classe ce
cas en D : Phénomène étrange à très étrange ») → verdict lexicon → conjugated
verb (`manquons` 163/1017 C vs **0/106** D) → cause noun → measurement density
(`mètres`, `secondes`, `environ` — which *is* the operational meaning of
"adequate information") → narrative length (0.6321 alone).

**42% ± 9% of the effect is identifiable leakage. The residual +0.1972 ± 0.0271
is reported as an UPPER BOUND, not as content** — not because the gradient has
not plateaued (that argument is WITHDRAWN; tier steps sit below seed noise) but
because the C/D criterion *is* informational adequacy, so no stripping rule can
remove from the text a property defined on the text.

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

### 1.9 BAASS Ten Month Report — independent 2009 corroboration of the D-reclassification

`DOW-UAP-D172`, 30 July 2009, the AAWSAP deliverable to DIA under contract
`HHM402-08-C-0072`. 497 pp, 1,086,965 chars. Archive.org still has **no text
derivative for D172**, so our OCR remains the only machine-readable copy.

**The result.** p283 ¶50 states the then-current public GEIPAN breakdown as
BAASS's own translation-triage count: « D cases: 205 cases for 23 regions.
C cases: 323 cases for 23 regions. » p219 confirms GEIPAN's own definition of D.

| | BAASS mid-2009 | 2026 ≤2007 | 2026 **full 1937–2026** |
|---|---|---|---|
| C | 323 | 588 | 1,020 |
| **D** | **205** | **75** | **106** |

**The D count fell in absolute terms, 205 → 106, a deficit of 99 measured
against the whole 90-year archive.** §1.3's D-rate result (3.78×, p=9.4e-10) is
a *rate* and so admits a denominator objection; **an absolute decrease cannot be
produced by adding cases.** GEIPAN added 2,104 post-2007 cases, of which only 31
were D. Independent third party, 17 years earlier, counting for an unrelated
purpose.

**Unresolved and reported as such:** the report's "over 1,650 investigations
1977–2007" does not reconcile with 1,155 (window) / 1,300 (≤2007). A
case-vs-testimony unit mismatch was tested and rejected, but weakly — the field
holds a title string, not a list. The D result is window-free and does not
depend on it. BAASS itself documented press inflation of a release size in the
same section (Danish Air Force: press said 15,000 reports, actual release 329
pages).

**Two defects found in the document.** "Entity Events ≈3,988" (23.1% of the
17,281-record MUFON CMS) is contradicted by its own facing-page table: CE total
2,233, CE3–5 = 333. And the classification percentages are computed on 8,753
classified records (50.65% of the database) without disclosing the base, showing
CE as 25.5% where it is 12.9%.

**Northern Tier is NOT a usable independent nuclear-proximity test set.** p315
states the method: UFOCAT/NIDS catalogue events "within 300 miles of an NT
location", no control set, no base rate. That is failure mode #3 and the design
already falsified for ICBM proximity. Not re-run. Its quantities are inside
chart images anyway (OCR recovered only "MA1, 41", "CE5, 4").

**Project Oral History is non-evidence by construction** — sources "warned that
unauthorized disclosure… would be vigorously denied."

**Keyword trap logged:** "3418 cases" is a private collection in a house in
Fortaleza, Brazil (p423), **not** GEIPAN's 3,404.

**OCR validation.** The cross-derivation check against archive.org's new
Release_07 derivatives **cannot run** — the sets are exactly complementary, zero
overlap, because D165 and D172 are the two files its deriver still fails on.
Reported null. Two validations do hold: the 20-cell MUFON table sums to a total
reproducing two independently-printed percentages to within 0.07 pp, and the
load-bearing `205` is attested twice, 64 pages apart (p219, p283).

Full report: `omega/reports/baass_ten_month_report.md`

### 1.10 The undisclosed D cases are the re-examined ones

`omega/geipan_revisit_disclosure.py`. Crossing `Document pour cas` with
`Cas revisité` **inside class D** localises §1.3's marginal finding:

| | revisited | not revisited | total |
|---|---|---|---|
| dossier published | 8 | 42 | **50** |
| **no dossier published** | **55** | **1** | **56** |

Revisit-rate 0.9821 undisclosed vs 0.1600 disclosed, **z = +8.605**, RR 6.14×.
**Not an era artefact** — holds inside every decade 1970s–2010s, and the
**Mantel-Haenszel OR stratified by decade is 209.10.** Stratification
*strengthens* it, the opposite of failure mode #6.

Supplies the mechanism tying §1.3 to §1.9: GEIPAN reopened D cases,
reclassified ~99 out of D, and among those still in D the reopened ones are the
unpublished ones.

**DIRECTION OF CAUSATION UNDETERMINED.** "You reopen the case you cannot resolve
from the file you have" fits the data exactly as well as "reopening withdraws
the file". The metadata cannot separate them; separating them needs the
documents, which is what is missing. `Cas revisité` semantics are undocumented,
n=106, one cell holds a single case.

Also **explains the power ceiling on the witness-level C-vs-D test**: the 56
absent D dossiers are not missing at random.

56 IDs with date/department/region/coordinates:
`data/processed/geipan/cada_targets.json`. CADA letters drafted (asking for
occulted versions from the outset, conceding privacy in full):
`omega/reports/cada_request_draft.md`. **Drafted, not filed.**

### 1.11 Operational lessons that cost real time this session

- **`except Exception: return None` cost a whole session.** It turned a
  persistent HTTP 504 into a generic "FAILED" (§2.2).
- **A pipeline reporting "0 failures" is claiming its error detection works,
  not that the data is good.** Two provinces came back with ZERO rows and were
  counted as successes, because HTTP 200 with no bindings is not an error. Wrong
  Q-ids: BC was Q1974 (correct **Q1973**), PE was Q1979 (correct **Q1978**).
  BC alone holds 47,585 places. Consistent with §1.7, where three of four gap
  findings were artefacts of our own ID parser.
- **Tesseract spawns an OpenMP thread per core by default.** N worker processes
  therefore put N×cores threads on `cores` cores. Measured on one 2480×3507 page
  of the GEIPAN corpus: **31,647 ms/page at the default, 2,090 ms/page with
  `OMP_THREAD_LIMIT=1`, byte-identical output.** 15×, i.e. 8.3 h → ~35 min.
  **Always set `OMP_THREAD_LIMIT=1` and parallelise at the process level.**
- **Wikidata's `mul` label code.** Labels identical across languages live under
  `mul`, and `FILTER(LANG(?l)="en")` excludes them. San Antonio and Arizona
  carry their names **only** under `mul`. Tiny in count (+25 on Texas) but it is
  exactly the big city names. Use `FILTER(LANG(?l) IN ("en","mul"))`.
- **`wdt:P625` returns only truthy coordinate statements.** San Antonio has
  none; its coordinate exists only as a statement node, so
  `p:P625/psv:P625` is required. That construct was **never** the timeout cause.
- **Generalising a timing test from a small case was an error.**
  `gazetteer_settlements.py` was built on a Rhode Island box that returned in
  8.3 s; a province-sized box answers 504. Recorded negative, not in pipeline.

### 1.12 Session 3 — the evidence vault, and four results

**`evidence_vault/` (145 MB, NOT gitignored, binaries force-added).** `archive/`
was merged into it so there is ONE durable tree. `evidence_vault/VAULT_MANIFEST.md`
is the living index and states for every empty section *why* it is empty.

Size rule: **a vault that cannot be pushed is not durable.** The 37 DIRD PDFs
are 1,779.6 MB and are NOT stored — the texts are, plus
`01_PURSUE_PRIMARY/FETCH_MANIFEST.json` with URLs, sizes and upstream SHA-1s.
Durable corpora now inside: periodicals 860 texts (29.9 MB gz), PURSUE server
OCR 286 (7.0 MB gz), TEP dossier (14 MB), trace controls (69 MB), NUFORC
unified (11.6 MB gz).

#### Result A — the 37 DIRDs are open-literature surveys

`omega/dird_analysis.py` · `omega/reports/dird_corpus.md`

| | |
|---|---|
| DIRDs mentioning UAP/UFO **at all** | **1 of 37** |
| open-literature citation markers | **1,541** |
| closed/internal citation markers | **56** |
| **ratio** | **27.5 : 1** |

**"The government funded NHI-level technology research" deflates to "a
threat-assessment office paid contractors to survey the open journals."** The
DIRDs are programme-scope evidence, not capability evidence. Authors are
anonymised `AAP Person N`, 31 distinct IDs in a block (1, 57, 58, 63–90).

**The exception, D128** *Anomalous Acute and Subacute Field Effects on Human
Biological Tissues* — 14 UAP refs, **14 closed citations (highest of any
DIRD)**, Appendix A is the **Schuessler Catalog of UFO-Related Human
Physiological Effects**. It concludes, verbatim, that injury patterns are
« congruent with the anomalous vehicle reports » and attributable to
**"real-world (although current and likely advanced beyond public information)
technologies"** — terrestrial RF/microwave energy deposition. A prosaic
conclusion reached inside the programme on its own data.

Its one exotic alternative is falsifiable: a craft's blackbody spectrum
**gravitationally blue-shifted** under spacetime manipulation → exposure up to
**soft X-rays**, i.e. an **ionising** signature.

**The structural gap, which is itself a finding.** TEP is the only
physical-trace case with full lab chemistry, and INRA **rejected** an ionising
mechanism there — but the TEP telex records `AUCUN EFFET RESSENTI PAR LE
TEMOIN`, no effect felt. **The project's two best evidence bases do not
overlap**: the case with trace chemistry had no human exposure; the document
with a human-exposure model has no trace chemistry. Re-analysis of either cannot
close it.

**Two new FOIA targets named in primary text:** `Technical Study 10.0 Human
Effects` (cited in D128, absent from the release, the only internal Technical
Study referenced in all 37); the AAWSAP-held Schuessler Catalog.

#### Result B — echo chamber re-grounded in primary publication

`omega/periodical_provenance.py` · `evidence_vault/07_PERIODICALS_PRIMARY/`

**860 issues, 72,057,926 chars, zero fetch failures.** MUFON/Skylook 485
(1967–2008), APRO Bulletin 260 (from Vol 1 No 1, 1952), CUFOS IUR 115. This
**lifts Phase 1's biggest stated limitation.**

Strict test (place + year + month within ±320 chars): **CONTROLS 4/4,
TARGETS 0/4.** Socorro 52 corroborated, Kecksburg 41, TEP 5, Exeter 4 —
Wright-Patterson 1951, Dallas 1965, Galesburg 1967 all **zero**. The three
apparent "Texas" hits were read individually and are all coincidence.

Relaxed test (year only, 400 chars): controls beat targets **10× to 127×**.
Weakest control is a *French* case in *US* bulletins (10 hits); strongest target
is Wright-Patterson, named 291 times across 147 issues, year-proximity ≈ 0.

**The corroboration is circular — six catalogues citing each other with nothing
underneath.** And "a small town in Texas" is **untestable by construction**: a
state plus an indefinite article is not a locus.

*Not nonexistence:* NICAP's *UFO Investigator*, *Flying Saucer Review*, CUFOS
case files and local newspapers are absent from the corpus.

#### Result C — redaction extent measured; §1.7 corrected

`omega/redaction_inline.py` · `omega/jp2_redaction.py` ·
`evidence_vault/05_SCRUBBED_CONTENT/README.md`

**§1.7 was incomplete.** It searched for the literal token `[REDACTED]` (6
occurrences in 326 docs) and concluded redaction is invisible in text. The
release **substitutes the exemption code in place of the withheld span**:
`AT 0823Z, (b)(1)1.4a TOOK OFF FROM OJMS VIA SLR`.

| mechanism | measurable from | count |
|---|---|---|
| inline exemption substitution | **text** | **982** across 55 of 326 docs |
| solid black bars in page image | JP2 only | **148** over 112 pages |

`DOW-UAP-D3` Arabian Gulf 2020 uses **both** — 104 inline at 17.10/1,000 chars
across all 10 deciles, plus 66 bars over 5.87% of page area.

**The stated reason is the finding.** E.O. 13526 §1.4: **1.4(a) military
plans/weapons/operations = 224**; 1.4(g) = 19; **1.4(c) intelligence
sources/methods = 1**. The withholdings are military operational detail, not
intelligence tradecraft.

White-out redaction was **tested and ruled out**. Numbering gaps, agency union:
**CIA-UAP 29/29, zero gaps** (the earlier CIA gaps were the `018`→`D020`
convention change); DOW-UAP 174, 37 missing, **D66–D73 reproduced**; NASA is
**two parallel series** (D1–D7 missing D3; D15–D32 missing D23–D29) and the 8–14
span is a boundary, not a gap. **D60/D63/D65 flanking the D66–D73 gap are
image-only**, and measure 0.48–0.97% dark with **zero bars** — clean scans.

#### Result D — Track 2 control set, and 4 of 10 sites cannot be controlled

`omega/track2_controls.py` · `evidence_vault/08_SATELLITE_ANOMALIES/README.md`

Control set built, **detection deliberately NOT run** — §5 item 5 makes the
order a design constraint and §6 records five claims falsified by absent
controls.

**TESTABLE:** Réunion 1.00, Rendlesham 0.73, Socorro 0.62, Trans-en-Provence
0.57, Saint-Mathias 0.50, Valensole 0.50.
**NOT CONTROLLABLE:** Cherry Creek 0.24, Cash-Landrum 0.20, Lavonia 0.13,
Newark Valley 0.12.

**Controllability is inversely proportional to local sighting density.** Newark
Valley has 658 sightings within 100 km and yields 2 clean controls from 17.
**This is the mechanism behind §6's falsified proximity claims, made
measurable:** in the US sighting field a candidate's neighbourhood already has
reports, so there is no comparison ground.

**TRACK 2 ON HISTORICAL SITES IS TEMPORALLY IMPOSSIBLE.** Sentinel-2 launched
June 2015; the candidates are 1964–1981 events — a **34–51 year gap**. TEP's
trace was visible at 40 days. Repoint Track 2 at the **34,898 geocoded
Sentinel-2-era NUFORC records**.

#### Result E — Tracks A–D: the "impossible" claims return clean nulls

`omega/deep_terms.py` · `evidence_vault/10_HIDDEN_BURIED/deep_terms.json`.
617 documents, context + frame recorded per hit (QUOTED_FICTION / HYPOTHETICAL /
THIRD_PARTY / PHYSICS_TERM / DIRECT).

**ZERO occurrences:** non-human personnel/employee/staff/officer/official ·
human-looking · indistinguishable from human · breakaway civilisation · shadow
government · organic robot · pseudo-human · security-clearance+non-human ·
**non-human biologic** · **crash retrieval** · simulation hypothesis · majestic ·
serpo · **glimmer glass** · kona blue · looking glass · **teaball** · **moon
dust** · immaculate constellation.

`MJ-12`: one hit, a citizen's letter *asking* a congressman about it.
What IS present is DIRD physics vocabulary (metamaterial 419, antigravity 236,
traversable wormhole 185) — a literature survey — plus Utah Ranch 64,
Skinwalker 40, Socorro 68, Cash-Landrum 15.

#### Codename index corrected

29 present of 58, over 559 docs. Two traps removed by reading **every**
occurrence: `aurora` 28→**3** (the rest are aurora borealis, a satellite
"AURORA II", NASA's Fast Auroral Snapshot Explorer, Gemini astronauts
describing auroras; the 3 survivors are all hedged — "alleged", "rumored",
"supposed"); `stargate` 27→**0** (the DIA wormhole paper, a URL, and a GEIPAN
witness naming a TV series). Three mechanisms: REQUIRE whitelist, VETO
blacklist, **DOC_VETO** at document scope. `project pounce` re-tiered
ALLEGED→OFFICIAL.

### 1.13 Operational lessons from session 3

- **`except Exception: return None` cost a session** (§2.2). A generic reason
  hides a persistent 504.
- **"0 failures" is a claim about error detection, not data.** Two provinces
  returned zero rows and counted as successes.
- **`\b` fails on `_`.** §1.7 documented this and it was **reproduced anyway** —
  zero hits for 37 DIRDs that are plainly there. Use `(?![0-9])`.
- **Zero-padding is a series marker; magnitude is not.**
- **Overlapping ranges = convention change (merge). Disjoint = parallel series
  (do not).**
- **`OMP_THREAD_LIMIT=1`** for tesseract: 31,647 ms/page → 2,090 ms/page,
  byte-identical. Always.
- **Memoise `toks()`** — permutation nulls re-tokenised unchanged text ~63,000
  times. 12,412× warm.
- **Significance ≠ power.** MDD here is 2.485σ (80% power); significance is
  1.645σ. An effect between them is *significant but underpowered*, not null.
- **Matched tiers vary ±0.1 across matcher seeds.** A single draw is not a point
  estimate.
- **A control screen whose coverage tracks the geography being screened is not a
  screen** (NUFORC alone passed French sites by absence of coverage).
- **Never pipe a background job through `head`** — SIGPIPE kills it.
- **A file can be tracked AND gitignored.** `git add` then silently refuses
  without `-f`, and the committed copy goes stale.

### 1.14 Session 4 — the debt paid, and two audits

**Environment first: the setup script WORKS. This was the open question.**
`UFOAI Omega research` (`env_018sxdcbBHMGqCRwh6KXDi6D`) was `is_current: true`,
and tesseract 5.3.4 + `fra` + poppler 24.02 + scipy 1.18.1 + sklearn 1.9.1 were
all present. Attributed, not assumed: scipy's `dist-info` was created 05:23
against a container boot of 05:21, so pip ran two minutes after boot. `fra` is
installed (its `traineddata` mtime is the upstream package's 2019 date, which is
not evidence either way — the dist-info timestamp is). `archive.org` and
`www.geipan.fr` both answer 200. **Start future sessions on this environment and
stop re-verifying the toolchain.**

#### 1. §1.4 seed-averaging — PAID
`omega/geipan_tier_seed_stability.py`, `omega/reports/geipan_tier_seed_stability.md`,
`evidence_vault/09_SEED_STABILITY/`.

The debt was **larger than §5 stated**. §5 named one seed (the length matcher,
`seed=5`). There are two: `balanced_cv_acc(seed=11)` downsamples the 1,020-case
C arm to 106, so **all six tiers** rested on a single draw, not just the two
matched ones. Both were swept, 24 seeds each; because the published value is a
low draw on both axes, L4/L5 also got a **joint** sweep varying both together —
neither marginal mean is the estimate.

| tier | was | **now** |
|---|---|---|
| L0 | +0.3494 | **+0.3387 ± 0.0229** |
| L1 | +0.3019 | **+0.2771 ± 0.0300** |
| L2 | +0.3113 | **+0.2628 ± 0.0318** |
| L3 | +0.2643 | **+0.2333 ± 0.0308** |
| L4 | +0.2176 | **+0.2135 ± 0.0276** (42nd pctile — that draw was fine) |
| L5 | **+0.1795** | **+0.1972 ± 0.0271** (38th pctile — a low draw) |

- **The residual ROSE.** The upper bound was understated, not inflated.
- **"51% is identifiable leakage" → 42% ± 9%.**
- **The L1 > L2 inversion was noise.** Seed-averaged the ladder is monotone;
  there was never anything to explain.
- **Adjacent tiers are NOT distinguishable.** Within-tier range 0.094–0.113;
  tier steps 0.016–0.020. Only the endpoints separate.
- **"The gradient has not plateaued" is WITHDRAWN** as the reason the residual
  is an upper bound. The real reason is stronger: the C/D criterion *is*
  informational adequacy, so no stripping rule can remove from the text a
  property defined on the text.
- **24/24 seeds significant at every tier.** Existence was never seed-dependent.

§5's inventory of affected documents was itself wrong — it named the BAASS,
Trans-en-Provence and DIRD reports, **none of which cite the number.** The real
list (tree-wide search for `0.1795|0.2176|0.6795|0.7176`) is `HANDOFF.md`,
`HANDOVER_PROMPT.md`, `geipan_acquisition_and_disposition.md`,
`geipan_cd_witness.md`, `geipan_cd_witness.py`. All corrected.

#### 2. Redaction slot analysis — what is withheld, not how much
`omega/redaction_slots.py`, `omega/reports/redaction_slots.md`,
`evidence_vault/05_SCRUBBED_CONTENT/redaction_slots.json`.

**The route in was structure, not grammar.** §5 proposed inferring the withheld
token's class from surrounding syntax. Unnecessary: the DOW mission reports are
**MISREP forms**, so a redaction sits in a **named field that states what was
removed**. 167 labels recur across ≥3 of 33 parsed forms.

| slot | withheld | released | rate |
|---|---|---|---|
| **CALLSIGN** | 98 | 10 | **0.91** |
| PERSONNEL | 131 | 78 | 0.63 |
| NARRATIVE | 79 | 115 | 0.41 |
| GEO | 40 | 105 | 0.28 |
| OPERATION | 42 | 119 | 0.26 |
| UNIT_ORG | 48 | 370 | 0.11 |
| TIME | 29 | 288 | 0.09 |

Never once released: Email 52, Full Name 33, Aircraft Callsign 33, Callsign 32,
Phone 28, Asset Type (Aircraft) 8, Number of Aircraft 4.
Released essentially always: Country Tasked 0/24, Activity Description 0/22,
Service 2/70, Rank 4/62, Wing 7/52, Takeoff Time 1/21, MAJCOM 1/20.

**The release gives which country, service, wing, rank, mission type and times,
and never which aircraft, under what callsign, how many, or who by name.** That
is ordinary OPSEC on force composition, **not concealment of phenomenon data** —
`Gentext`, which carries the UAP description, is released 115 times against 37
withheld. **Reported as a negative: it cuts against a suppression reading.**

Validated against the releasing authority's own exemption code (an independent
label): **443/575 = 77.0% agreement.** That is a FLOOR — 83% of the largest
disagreement class ((b)(6) on unit fields) is OCR field-absorption, a lost
bullet separator making a unit field swallow the next personnel field.

#### 3. AAWSAP contract audit — the capstone deliverable is absent
`omega/aawsap_contract_audit.py`, `omega/reports/aawsap_contract_audit.md`,
`evidence_vault/01_PURSUE_PRIMARY/aawsap_contract_audit.json`.

**All 26 FY2009 deliverables are present.** D188 records 26 delivered; D117–D142
is exactly 26. Title matching cannot prove it (DIA retitled on publication) and a
square assignment matches everything by construction. The proof is that **the
release pseudonymised authors consistently across documents** — D188's Enclosure
1 gives `MP Person NN` per title, each DIRD names `AAP Person NN`, one namespace,
assigned by the government. **Author ID agrees 26/26, zero disagreements**, and
resolves the three pairs titles could not (D121=64, D132=57, D119=65).

**THE CAPSTONE IS MISSING.** D182 §11(d)'s Comprehensive Integrated Threat
Assessment has its own CLIN and money in both years — **0004 at $240,000, 1004
at $220,200, $460,200 contracted.** A corpus-wide search returns 4 hits, *all in
the contract documents themselves*. No report, no briefing, and D188's review of
deliverables to the DIRECTOR, DIA never mentions it. **Its due condition was
reached**: D116/P00005 extends the contract under FAR 52.217-8 to **21 Dec
2010**, and D150–D153 were published either side of that date. Most specific
checkable gap since D66–D73, and nameable by CLIN.

Also established:
- **The contract ran two of five anticipated years.** D182 planned base + four
  option years to 30 Sep 2013. Actual: base, option year 1, then a three-month
  FAR 52.217-8 service extension to 21 Dec 2010. Options 2–4 never exercised.
- **What was released is DIA's published version, not the contractor's.** Each
  DIRD carries a DIA control number and `ICOD: 1 December 2009`; D188 predates
  the earliest by six weeks. The as-delivered BAASS research reports, and the
  §11(c) executive summaries, are unreleased.
- **The 60-day overview papers cost more than the reports they preview.** CLIN
  1002 ($4.76M) is 1.66× CLIN 1003 ($2.87M) and the contract's largest item.
  The only deliverable stating a threat judgement is 2.7% of the base year.
- Year one was **unclassified only**; 5 of 26 reports had outside review,
  including **three Sandia National Laboratories** staff; all reviews positive.
  FY2010 intent included "classified experimental verification by BAASS".

### 1.15 Operational lessons from session 4

1. **A background job's "completed, exit 0" was wrong three times.** With
   `nohup … &`, the harness notification fires when the *wrapper* exits, not the
   work. Each time, the python process was still running at 100% CPU and the
   result file was a stale copy from an earlier smoke test. **Verify with
   `ps -eo pid,etime,cmd` and the output file's mtime before reading a result.**
   To block properly: `until [ ! -d /proc/<pid> ]; do sleep 5; done`.
2. **Check the instrument before believing a negative.** An affiliation
   cross-check returned 0/8 "unconfirmed", which looked like a failed
   reconciliation. The DIRDs carry **no institution line at all** — the metric
   was impossible, not failing. Replacing it with the author-pseudonym check
   gave 26/26.
3. **An OCR-legibility proxy ranked clean text as damaged.** Scoring by share of
   all-alphabetic tokens penalised `0823Z`, `SECRET//REL` and `432 AEW` —
   correct military format. It called the modern mission reports worse than
   degraded 1950s FBI scans.
4. **A non-hit in garbage is not evidence of disclosure.** The first marker
   regex matched only clean `(b)(n)`, so `(b}(6)`, `(bl(6}` and bare `! 1.4a`
   were scored as RELEASED — fabricating "categorically protected fields: 0".
   Habit #2's complement: an explicit **UNREADABLE** class is required.
5. **A greedy best-match is not an assignment.** It gave D135 to two different
   titles and D123 to two more, inflating the match count while the true
   counterparts went unclaimed. Use `scipy.optimize.linear_sum_assignment`, and
   remember a square assignment matches everything by construction — the count
   is then structural and proves nothing without an independent identifier.
6. **Two FOIA targets were withdrawn before they stood.** "No PMP and no monthly
   status reports were released" was false: D168 is a consolidated PMP and
   D169/D170/D171/D173 are monthly reports. Check filenames before asserting a
   gap.
7. **`data/processed/` is gitignored (`.gitignore:6`).** Session 2's lesson
   recurred live — the seed-stability JSON would have been lost. It is in
   `evidence_vault/09_SEED_STABILITY/`.

---

## 2. In flight when session 4 ended

**NOTHING.** Every background job completed and was verified complete by process
state, not by notification. Working tree clean, all pushed. Last commit on
`claude/gallant-lamport-0tu52r`.

**Branch note:** session 3's work was on `claude/magical-gauss-wzgdqd` at
`ede32f9`. Session 4's assigned development branch was
`claude/gallant-lamport-0tu52r`, so that branch was fast-forwarded to `ede32f9`
and all session-4 commits sit on it. Both branches exist on the remote;
`claude/gallant-lamport-0tu52r` is the current tip.

## 3. Ephemeral data — what is DURABLE, and what is not

**Everything expensive is in `evidence_vault/` (now ~145 MB + the session-4
additions, committed).**

| in the vault, no re-fetch needed | size |
|---|---|
| 860 periodical texts (MUFON/APRO/IUR) | 29.9 MB gz |
| PURSUE server OCR, 286 docs | 7.0 MB gz |
| 37 AAWSAP DIRD texts | in-tree |
| TEP dossier, 10 files / 177 pp | 14 MB gz |
| trace-control dossiers, 16 files | 69 MB gz |
| NUFORC unified, 134,906 recs | 11.6 MB gz |
| GEIPAN case DB, codename index, 434-list | in-tree |
| **seed-stability sweeps (session 4)** | `09_SEED_STABILITY/` |
| **redaction slot analysis (session 4)** | `05_SCRUBBED_CONTENT/redaction_slots.json` |
| **AAWSAP contract audit (session 4)** | `01_PURSUE_PRIMARY/aawsap_contract_audit.json` |

**Still ephemeral, and cheap to rebuild:**

| what | recovery | cost |
|---|---|---|
| the 286 PURSUE texts, unpacked | `tar xzf evidence_vault/01_PURSUE_PRIMARY/pursue_server_ocr_286.tar.gz` into a scratch dir, then pass it as `OMEGA_PURSUE_TXT` | seconds |
| `data/raw/pursue_ocr/txt` (40 OCR'd Release_07/08 docs) | re-OCR via `omega/pursue_ocr.sh` | ~40 min |
| NUFORC raw CSV | `archive.org/cors/data-world-snapshot-20260713-agent-drastimehta/nuforc-ufo-event-sightings-csv.zip` | 1 min |
| Wikidata gazetteer, 1.74 M entries | `python3 -I omega/gazetteer.py` | ~20 min |
| DIRD **PDFs** (1,779.6 MB — deliberately not stored) | `01_PURSUE_PRIMARY/FETCH_MANIFEST.json` | ~30 min |

**NOTE:** `omega/redaction_slots.py` and `omega/aawsap_contract_audit.py` read
the PURSUE texts from `$OMEGA_PURSUE_TXT` (falling back to
`data/raw/pursue_ocr/txt`). Untar the vault copy and set that variable.

## 4. Environment

**`UFOAI Omega research`** (`env_018sxdcbBHMGqCRwh6KXDi6D`), personal, 8 hosts:
`archive.org`, `www.geipan.fr`, `geipan.fr`, `cnes.fr`, `query.wikidata.org`,
`nominatim.openstreetmap.org`, `earth-search.aws.element84.com`,
`en.wikipedia.org`. Package managers and MCP hosts allowed.

**The setup script is VERIFIED WORKING as of session 4** — tesseract 5.3.4 with
`fra`, poppler 24.02, scipy 1.18.1, sklearn 1.9.1, installed ~2 min after boot.
Do not re-litigate this; just use it.

**Blocked, unchanged:**
- `web.archive.org` — proxy 403. The CDX API exists nowhere else, so **Wayback
  snapshot comparison cannot run.** `archive.org/cdx/...` 404s.
- `www.cnes-geipan.fr` — proxy 403.
- An `update_environment` request to add both was **rejected by the environments
  service.** Do not re-ask in chat.
- `war.gov`, `aaro.mil`, `nuforc.org`, CIA/FBI/NRO/NASA reading rooms,
  `arxiv.org`, ESA WorldCover.

**Worth asking the user for:** `arxiv.org` (to verify the VASCO/Doherty chain
from source rather than memory) and a landcover raster host (Track 2 matching is
currently a spectral proxy).

Note: combined remove+add `update_environment` calls are rejected — do them
separately.

---

## 5. Next, in priority order

### 1. **Per-area assignment of the 37 DIRDs** — finishes the contract audit
§7 of `aawsap_contract_audit.md` reports area coverage as **untrustworthy and
flagged not to quote**: a keyword map puts one report into several areas, so the
counts are inflated. The qualitative finding (no contracted area went
undelivered) stands. A clean one-area-per-report assignment, read from each
document's own framing rather than its title, closes the only loose end in that
audit. 37 documents, all on disk. Cheap and bounded.

### 2. **Draft the CLIN-named FOIA requests** — the audit produced five targets
`aawsap_contract_audit.md` §8. The sharpest is the **Comprehensive Integrated
Threat Assessment, CLIN 0004 and CLIN 1004, contract HHM402-08-C-0072** — a
deliverable identified by line item, priced twice, whose due condition
(21 Dec 2010, per D116/P00005) was reached, absent from a release containing all
37 subsidiary reports. Then the per-area Project Management Plans (~24, the
contract's largest line item at $8.36M), the ~20 missing monthly status reports,
the as-delivered BAASS versions with their §11(c) executive summaries, and the
Sandia reviews in D188 Enclosure 2. Add to `omega/reports/foia_request_drafts.md`.
**Drafted, not filed.**

### 3. **Redaction slots on the FY2010 DIRD wave and the 1950s scans**
`redaction_slots.py` covers 33 MISREP forms. 226 field instances are UNREADABLE
and carry no claim; the 1950s FBI scans (14 hits) were excluded by the spine
gate. Two extensions: re-OCR the worst forms at higher dpi to convert UNREADABLE
into decidable, and build a prose-mode slot reader for the non-form documents,
which is the original §5 item-2 grammar approach now that the structural route
is exhausted.

### 4. **OCR the 23 declared image-only PURSUE docs** (`_imgonly` suffix),
including the D60/D63/D65 mission reports. `tesseract -l eng`, and
`OMP_THREAD_LIMIT=1`. These would feed straight into the slot analysis.

### 5. **Track 2, REPOINTED** — historical sites are temporally impossible
(34–51 yr gap). Run the existing control methodology on the **34,898 geocoded
Sentinel-2-era NUFORC records**. Control set code: `omega/track2_controls.py`.

### 6. **Remaining periodical work** — the 860 texts are vaulted. Build the full
provenance graph for the 434-event retained-sample list, tracing each to its
earliest primary source.

### 7. **NHI Proof Report** — write it last, from the vault.

### Blocked, not pending
The retained-sample assay is blocked on *physical custody*, not chemistry —
CUFOS/APRO/GEPAN/university archives are unreachable. Wayback snapshot
comparison is blocked on `web.archive.org`.

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
