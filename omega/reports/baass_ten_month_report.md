# DOW-UAP-D172 — BAASS Ten Month Report, 30 July 2009

**Document:** Bigelow Aerospace Advanced Space Studies deliverable to DIA under
contract `HHM402-08-C-0072`, covering 22 Sep 2008 – 31 Jul 2009. 497 pages,
1,086,965 chars. Every page carries a proprietary-restriction footer.

**Provenance:** PURSUE archive `pursue-uap-documents-2026`, Release_08. Archive.org
has **no server-side text derivative for D172** (Release_07 has since gained 28,
Release_08 still has none), so the OCR in `data/raw/pursue_ocr/txt/` — tesseract
5.3.4, 300 dpi grayscale, `--psm 1` — is the only machine-readable copy in the
project.

**Structure:** §1 org/infrastructure (p1), §2A investigations (p50), §2B contracts
(p109), §2C nine projects (p111), §3 strategic plan (p472), 4 appendices.
Nine projects: Physics (p114), Engagement (p158), Cooperation (p185), Blue Book
Materials (p190), Campus (p203), Oral History (p214), Database/Government Files
(p217), Northern Tier (p308), Colares/Brazil (p391).

---

## 1. RESULT — independent 2009 corroboration of the GEIPAN reclassification

`omega/baass_geipan_crosscheck.py`

§2C p283 ¶50 states the then-current public GEIPAN disposition breakdown as
BAASS's own translation-triage enumeration:

> « D cases: 205 cases for 23 regions. C cases: 323 cases for 23 regions. »
> *Note: These numbers may change as GEIPAN updates and releases new cases to
> the public.*

p219 confirms BAASS used GEIPAN's own definition — "68 of the 205 Category D
cases — the cases that remain unexplained after thorough investigations."

### The comparison

| | BAASS, mid-2009 | 2026 export, ≤2007 | 2026 export, **full 1937–2026** |
|---|---|---|---|
| **C** | 323 | 588 | 1,020 |
| **D** | **205** | **75** | **106** |

**The D count fell in absolute terms: 205 → 106, a deficit of 99, measured
against the entire archive across 90 years.**

This is the decisive form of the §1.3 result. §1.3 established that the D-*rate*
fell 3.78× (z=+6.119, p=9.4e-10) and ruled out caseload dilution by Spearman
(−0.1295, p=0.360). But a rate always admits a denominator objection. **An
absolute decrease in a count cannot be produced by adding cases.** GEIPAN added
2,104 cases after 2007 — of which only 31 were D (1.47%, against 75/1,300 =
5.77% for ≤2007) — and the total D count is still 99 below what a DIA contractor
counted in 2009 in a release covering only 1977–2007.

The corroboration is independent in the way that matters: a third party, writing
17 years earlier, with no stake in this project's hypothesis, counting for an
unrelated operational purpose (deciding what to translate).

### The mechanism is in GEIPAN's own metadata

The export carries a `Cas revisité` ("case revisited") flag:

| class | Non | Oui | revisit-rate |
|---|---|---|---|
| A | 907 | 48 | 0.0503 |
| B | 1256 | 67 | 0.0506 |
| C | 970 | 50 | 0.0490 |
| **D** | **43** | **63** | **0.5943** |

D revisit-rate 0.5943 vs 0.0500 for A+B+C, **z = +22.065**. A, B and C sit at a
flat 5% baseline; D is 12× that. GEIPAN's own bookkeeping records that D is the
class under active re-examination. The surviving 106 are not a stable residue —
59% of them have already been reopened once.

### Unresolved discrepancy — reported, not explained away

p219 also describes the release as "approximately 100,000 pages documenting over
**1,650 investigations** of UFO cases from 1977 through 2007." Our export holds
**1,155** cases in 1977–2007 and **1,300** at ≤2007. Ratio 0.70 / 0.79.

Three readings, and **we cannot currently distinguish them**:

1. **Secondary-sourced figure.** The 1,650 sits in a bulleted country survey,
   hedged "approximately"/"over", unlike the hand-counted 205/323 in ¶50. BAASS
   itself documented press inflation of a release size in the same section
   (p~250): the Danish Air Force was reported by "several news articles" to have
   released "some 15,000 reports"; BAASS found "these statements were later found
   to be false and misreported on" — the actual release was **329 pages**.
2. **Case merging.** `Nouveau cas` splits 552 Oui / 2,852 Non with undocumented
   semantics.
3. **Withdrawal from publication.**

Tested and rejected as an explanation: a case-study-vs-testimony unit mismatch.
All 1,155 window records are 1:1 on `ID Etude de Cas`. **Caveat: this is weak
evidence — `Temoignage associé` holds a single title string, not a delimited
list, so the field cannot settle the unit question either way.**

**The D result does not depend on this.** The full-archive comparison (205 vs
106) is window-free and immune to any definition of the 2009 release's extent.

Full A/B accounting cannot be closed: BAASS enumerated only C and D, because
only C and D were translation priorities.

---

## 2. Internal arithmetic consistency

`omega/baass_internal_consistency.py`. Prior-setting on the deliverable's care.

**Two real problems.**

**(a) "Entity Events ≈3,988" contradicts BAASS's own classification table.**
p238 reports 3,988 entity events in the 17,281-record MUFON CMS database —
23.1%, which would be an order of magnitude above any published entity-report
prevalence. But p239's own Vallée/Hynek table gives **CE total = 2,233**, and
CE3+CE4+CE5 (the entity-bearing levels) = **333**. Entity events cannot exceed
close encounters. 3,988 is 1.8× the whole CE class and 12× CE3–5. The single
most startling statistic in the document is contradicted by the table on the
facing page. Either "Entity Events" is a database flag with an undocumented and
much looser definition, or it is wrong. It is not usable as stated.

**(b) Percentages are computed on an undisclosed denominator.** The classified
records sum to **8,753** — 50.65% of the stated 17,281 total. The p239 pie chart
gives "CE 25.5%" and "AN 12.1%"; these reproduce on 8,753 (25.51%, 12.03%) and
not on 17,281 (12.92%, 6.09%). Correct arithmetic, undisclosed base: the reader
is shown 25.5% for a class that is 12.9% of the database.

**Minor / passing.**
- Canadian release p260: 264 CAPELLA + 353 spreadsheet = **617** vs stated 618. Off by one.
- Canadian release: 618 − 586 = 32, stated 32, "5%" → 5.18%. **Passes.**
- UK MoD p296 Table VII sums to **614** cases; Table VIII time-of-day sums to
  **563**. Gap 51 (8.3%). Completed-only rows sum to 466, i.e. *below* the
  time-of-day total by 97 — so Table VIII includes in-progress files. Not an
  error, but the tables are not on the same population.
- GEIPAN throughput p283: 68 cases ≈ 672 pages → 9.88 pp/case against a stated
  "about 9". 14 weeks at a stated 4 cases/translator/week → 1.21
  translator-equivalents; 33.2% of the 205 D cases done. Internally coherent.

---

## 3. NOT TESTABLE — and why

### Northern Tier reproduces a design this project already falsified

p315 states the method:

> "The data includes all UAP events currently in the BAASS data Warehouse from
> the National Institute of Developmental Science (NIDS); UFOCAT data; and the
> Canadian Government Release" … "only those incidents within **300 miles** of
> an NT location."

This is **failure mode #3, self-referential source events** — the design already
falsified for ICBM proximity, where the March 1967 Minot/Malmstrom cluster turned
out to be the claim's own founding data. UFOCAT and NIDS contain the 1975
Northern Tier events *because* they occurred at SAC bases; selecting catalogue
events near those bases measures the catalogue's inclusion criterion. And at a
300-mile radius the union of circles around the Northern Tier bases covers most
of the northern United States, so a high "within 300 miles" share is close to
arithmetically guaranteed. There is **no control set and no base rate** anywhere
in the section.

Not re-run. Re-running it would launder it.

Separately, Northern Tier's quantities live in **chart images** — Figures 50–53.
OCR recovered only fragments ("MA1, 41", "CE5, 4"). Recovering them needs JP2
page-image extraction, and given the design flaw that spend is not justified.

### Project Oral History is non-evidence by construction

p214: sources were "warned that unauthorized disclosure of the information, along
with attribution of source, would be vigorously denied." Unattributable,
unfalsifiable, and so recorded.

### Project Physics

26 papers contracted through EarthTech International, due 31 Jul 2009. The papers
are not in the release; only the contracting is documented.

### Administrative content

5,000 sq ft underground vault with 3-ft walls at the North Las Vegas Bigelow
facility, 47 hires, five buildings in escrow. Checkable in principle against
Clark County records; privacy-laden and tests nothing about the phenomenon.
Skipped.

---

## 4. KEYWORD TRAP — logged

**"3418 cases" is not GEIPAN.** It sits 14 away from our GEIPAN total of 3,404
and will match any numeric or proximity search for it. p423: it is a **private
collection in an investigator's house in Fortaleza, Brazil** (Centro de Pesquisas
Ufológicas), "three rooms filled with over 50 years of investigations to include
3418 cases." Second keyword trap caught in this corpus after §1.6's
`BOOSTER COMMAND` OCR artefacts.

---

## 5. Documented negative worth recording

p~190, Project Blue Book Materials / NORAD: in March 2009 BAASS approached NORAD
for JANAP 146 pilot reports covering the previous decade and

> "was told that no such data exists. Further, [redacted] was told that in spite
> of clearly written regulations on the books that mandated the reporting of
> unusual encounters with advanced aerospace vehicles by military pilots, no such
> reports had been received by NORAD."

A mandated reporting channel with an empty archive, on the record, in 2009.

---

## 6. Contract and vendor facts established

- `HHM402-08-C-0072` awarded **22 Sep 2008**. 12 designated technical areas:
  lift, propulsion, control, power generation, spatial/temporal translation,
  materials, configuration/structure, signature reduction (optical/IR/RF/
  acoustic), human interface, human effects, armament (RF and DEW), other.
- **MUFON**: contract `081006-1` (four papers: lift, propulsion, control, human
  effects); Purchase Agreement **20 Feb 2009** for cases, investigations,
  eyewitness contact details and database. ~1,000 volunteer investigators.
- **Documatica**: `081110-1` (Project Capella plan of action); `090109-1` —
  deliver the **668-case NIDS database** with classifications, 8 days of
  on-site Capella training, and **"to initiate contact with CNE-GEIPAN with a
  view to gaining access to their UAP database."**
- **EarthTech International**: the 26 Project Physics papers.
- MUFON CMS initiated mid-2003; 17,281 records at 30 Jun 2009; **excludes**
  MUFON's 13,000 reports from 1969 to mid-2003.
- Project Cooperation p185 records an intent to "alter the official programmatic
  status of the BAASS operation" to afford "deeper cover" and let participants
  work "without important need to know (NTK) restrictions."

---

## 7. Carried forward as testable, not yet run

1. **Blue Book**: the cited USAF factsheet 12,618 sightings / 701 unidentified
   (5.56%) against our index (10,764 true unique per §3). The relayed
   "possibly 4,000 miscategorized as IFOs" is 5.7× the official unidentified
   count — situate against T3's null and its 7× prose-to-record gradient.
2. **Monthly-report rollup**: D169 (Mar 2009), D170 (Apr 2009), D171 (Jun 2009)
   fall inside this report's window. Cross-check claimed figures against the
   monthlies they summarise.
3. **Claim decay**: D175, *BAASS Self-Assessment of UAP Analysis Capabilities*,
   Nov 2010 — 15 months later, same organisation, same subject.
4. **668-case NIDS database** — named deliverable; check whether it is in PURSUE.

---

## 8. OCR validation of D172

**The cross-derivation check cannot run. Reported as null.**

Archive.org has, since the previous session, derived text for 25 Release_07
documents — `DOW-UAP-D155` through `D181` — which raised the possibility of
validating our tesseract output against an independent derivation. It does not
work: the two sets are **exactly complementary**. Archive.org derived D155–D181
*except* D165 and D172; our OCR covers D165, D172 and D182–D213. Overlap is
**zero documents**. D165 and D172 are precisely the two files in that range
archive.org's deriver still cannot handle, which is why we OCR'd them in the
first place.

**Two validations that do work, both favourable.**

**(a) The arithmetic checks are an OCR test on the numerals.** §2's MUFON CMS
check summed a 4-class × 5-level table of 20 independently-OCR'd integers to
8,753, and the document's separately-printed pie-chart percentages reproduce on
that total to within 0.07 pp (CE 25.51% vs stated 25.5%; AN 12.03% vs stated
12.1%). Twenty corrupted digits do not sum to a total that reproduces two
independently-printed percentages. The numerals in this document read correctly.

**(b) The load-bearing figure is attested twice, 64 pages apart.** The D count
appears at **p219** ("BAASS has translated and analyzed 68 of the 205 Category D
cases") and again at **p283** ("D cases: 205 cases for 23 regions"). Two
independent passages, two different sections, same figure. `323` appears twice
and `68` thirteen times. The §1 result does not rest on a single OCR'd token.
