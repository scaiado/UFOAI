# 05 — SCRUBBED CONTENT

## The correction to §1.7

§1.7 concluded: *"Redaction is invisible in PURSUE text: zero `[REDACTED]`
markers, but 964 FOIA exemption citations... Withholdings are applied to the
page image, so OCR returns nothing with no marker. Detecting extent needs JP2
page-image analysis, not text search."*

**That is incomplete.** It searched for the literal token `[REDACTED]`. The
release does not use it (6 occurrences in 326 documents). It substitutes the
exemption code **in place of the withheld span**, inline, in the text layer:

> `AT 0823Z, (b)(1)1.4a TOOK OFF FROM OJMS VIA SLR. (b)(1)1.4a PROCEEDED TO FRAGGED TASKING. AT 0649Z, (b)(1)1.4a WAS 7-LINED`

Each `(b)(1)1.4a` **is** a redaction, positioned exactly where the removed text
was, carrying its own justification. So extent **is** measurable from text.

## Two independent redaction mechanisms

| | mechanism | measurable from | count |
|---|---|---|---|
| **1** | inline exemption substitution in the text layer | text | **982** across 55 of 326 docs |
| **2** | solid black bars burned into the page image | JP2 only | **148** bars over 112 sampled pages |

**`DOW-UAP-D3` Mission Report Arabian Gulf 2020 uses both** — 104 inline
redactions (17.10 per 1,000 chars, spread over all 10 deciles) *and* 66 image
bars covering 5.87% of page area. It is the most heavily redacted document
examined.

24 of 55 documents are **DISTRIBUTED** (≥5 deciles touched — applied to running
narrative), not clustered in a cover-sheet legend.

## Exemptions actually cited

| exemption | count | |
|---|---|---|
| **(b)(1)** | **454** | classified national defence |
| **(b)(6)** | **431** | personal privacy |
| (b)(3) | 80 | withheld by other statute |
| (b)(7) | 11 | law enforcement |
| (b)(2) | 3 | internal personnel rules |
| (b)(5) | 2 | deliberative process |
| (b)(4) | 1 | trade secrets |

## The stated reason — E.O. 13526 §1.4 subsections

| subsection | count | category |
|---|---|---|
| **1.4(a)** | **224** | **military plans, weapons systems, or operations** |
| 1.4(g) | 19 | vulnerabilities of systems/installations/infrastructure |
| 1.4(c) | 1 | intelligence activities, sources, methods, cryptology |
| 1.4(e) | 1 | scientific/technological/economic re national security |

**This distribution is itself the finding.** The overwhelming majority of
classified withholdings in the UAP release are justified under **§1.4(a),
military plans and operations** — not §1.4(c), intelligence sources and methods,
which appears **once**. The withholdings are about military operational detail,
not about protecting intelligence tradecraft.

## JP2 image-layer measurement

`omega/jp2_redaction.py` · map in `jp2_redaction_map.json`. 15 documents,
112 pages. Method: grayscale → dark mask (<50) → connected components → keep
components ≥0.2% of page with fill ratio ≥0.80 **and** interior σ<40, which
separates a solid bar from a photograph. Every component is reported with its
fill, aspect and σ so the call is auditable.

| document | pages | dark% | bars | bar area% |
|---|---|---|---|---|
| **D3 Arabian Gulf 2020** | 7 | 8.21 | **66** | **5.87** |
| D108 Middle East 2025 | 8 | 4.84 | 33 | 1.90 |
| D107 Middle East 2025 | 8 | 4.71 | 27 | 1.58 |
| D109 Middle East 2022 | 6 | 4.55 | 22 | 1.71 |
| the other 11 | — | 0.48–1.84 | **0** | 0.00 |

**29 of 112 pages (25.9%) carry at least one solid dark bar.**

**White-out redaction was tested and is NOT used.** The first pass found zero
bars in D32 (59 `(b)(1)`), D27 (42), D25 (42) and D28 (35), which looked like a
detector gap — a detector finding nothing in a document citing 59 national-
defence exemptions is more likely incomplete than the document unredacted. White
excision detection was added (large near-white rectangles inside the page's own
ink bounding box). It returned essentially nothing. Those documents redact
**inline in the text layer only**, which the inline measurement above confirms:
D32 has 85 inline redactions across all 10 deciles.

## Numbering gaps

`numbering_gaps.json`. Agency union over 368 stems, PR series excluded.

| agency | n | range | missing | density | longest runs |
|---|---|---|---|---|---|
| CIA-UAP | 29 | 1–29 | **0** | 1.000 | — |
| DOE-UAP | 5 | 1–5 | 0 | 1.000 | — |
| **DOW-UAP** | 174 | 3–213 | **37** | 0.825 | **66-73**, 79-83, 29-31, 39-41, 45-47 |
| FBI-UAP | 40 | 1–43 | 3 | 0.930 | 34-36 |
| NASA-UAP | — | two parallel series | D3; D23–D29 | — | 8–14 is a boundary, not a gap |

**`DOW-UAP-D66–D73`, eight consecutive**, independently reproduced. It sits in
the 2020 Middle East mission-report block — and **D60, D63 and D65, the released
members of that block, are image-only with no text derivative**, so the most
specific gap in the release is surrounded by documents invisible to text
analysis. Their JP2s were measured: dark fractions 0.48–0.97%, **zero bars** —
they are clean scans, not redacted pages.

## ID-parser discipline

Four traps, all of which produced wrong answers before being fixed:
1. **`\b` fails on `_`** — underscore is a word character, so the boundary never
   fires. This returned **zero hits for 37 DIRDs that are plainly there.** §1.7
   documented this exact bug and it was reproduced anyway. Use `(?![0-9])`.
2. **Zero-padding is a style marker; magnitude is not.** `D017` vs `D17` is a
   convention change; `D17` vs `D170` is not.
3. **Overlapping ranges = convention change (merge). Disjoint = parallel series
   (do not merge).** Merging NASA's two series invents the 8–14 gap.
4. **`DOW-UAP-PR` is sparse parallel numbering** and is excluded from the union.
