# PROJECT OMEGA — Data Universe Recovered via archive.org Mirrors

**This report corrects a claim I made repeatedly across this project.** I
stated that the war.gov PURSUE files were unavailable, on the evidence that
`www.war.gov` returns HTTP 403 to this container. That was true of the
*origin host* and false as a conclusion about the *data*. The files are
mirrored on archive.org at file level, and I have verified them directly.

---

## 1. PURSUE / war.gov — FOUND, verified, with OCR already done

**`pursue-uap-documents-2026`** — independently verified by fetching the item
metadata myself:

| field | verified value |
|---|---|
| title | "PURSUE UAP Files - Documents (U.S. Department of War, 2026)" |
| **source** | **`https://www.war.gov/UFO/`** |
| item_size | 15,008,593,458 bytes |
| original files | **372** (338 PDF, 23 JPG, 8 PNG, 2 XML, 1 SQLite) = 5,411,029,382 B |
| per release | R01 130 · R02 6 · R03 63 · R04 17 · R05 25 · R06 59 · R07 28 · R08 40 |
| **server-side OCR** | **298 `_djvu.txt` files, 18,139,510 bytes of extractable text** |

Companion: **`pursue-uap-videos-2026`**, 15,636,967,983 B, 152 MP4s, same
`source` field.

**Content authenticity verified by direct fetch of two OCR files:**

`Release_01/059UAP00011_djvu.txt` (8,849 B) is a genuine State Department
cable — `MRN: 01 MOSCOW 13169`, `Oct 30, 2001`, `From: AMEMBASSY MOSCOW`,
`Subject: UFOS OVER GEORGIA: STRANGE ENCOUNTERS OF AN MFA KIND`, with intact
TAGS line and distribution list.

`Release_06/DOW-UAP-D107_..._djvu.txt` (11,315 B) is a military mission report
— `Misrep prod-dod-11937169`, DTG-stamped narrative entries, redaction gaps,
and `OBSERVED UAP IVO [redacted] (SEE UAP 1)`.

**On the classification markings:** these documents carry portion markings
such as `(SECRET//REL TO USA, FVEY)`. That is normal in declassified releases —
the original markings remain visible on the released page. The `source` field
is the US Department of War's own public release site. **This is official
public disclosure material, not classified or improperly obtained material.**

## 2. Everything else the reconnaissance recovered

| target | status | identifier | structured? | OCR state |
|---|---|---|---|---|
| **NUFORC database** | FOUND as **CSV** | `data-world-snapshot-20260713-agent-drastimehta` | **yes — 137,094 rows** | n/a |
| MUFON UFO Journal / Skylook | FOUND | `MUFON_UFO_Journal_-_Skylook` | no | **485 PDFs 1967–2008, all OCR'd** |
| APRO Bulletin | FOUND | `apro-bulletin` | no | **260 PDFs from Vol 1 No 1 (1952), all OCR'd** |
| CUFOS / Int'l UFO Reporter | FOUND | `iur-vol.-31-no.-4` | no | **115 PDFs, all OCR'd** |
| Condon Report (3 vols) | FOUND | `DTIC_AD0680975/6/7` | no | **1,425 pp, 2.65 MB text, OCR'd** |
| Robertson Panel (Durant) | FOUND | `cia-readingroom-document-cia-rdp79b00752a000300100010-4` | no | OCR'd, 63 KB |
| Project Sign | FOUND | `DTIC_AD0311102` | no | OCR'd, 45 KB |
| Project Grudge | FOUND | `ProjectGRUDGE` | no | **zero OCR**, 75.6 MB |
| UK Project Condign | FOUND complete | `condign-vol-2-1-258` | no | all OCR'd |
| 2023 Grusch hearing | FOUND — statements | `hearing-...-national-security-docs` | no | official `HHRG-118-GO06` PDFs |
| **GEPAN/SEPRA/GEIPAN** | **NOT FOUND** | — | — | — |

NUFORC CSV caveat: the `summary` column is NUFORC's short summary line, not
the full narrative body, and the date field is dirty (one row reads `06/1400`).

Grusch caveat: witness **statements**, TTFs and bios are present under the
official `HHRG-118-GO06` naming; the **bound GPO verbatim transcript is not**.
So the hearing's Q&A is still unavailable, and I will not characterise it.

## 3. The one target genuinely absent, and it is the one that matters most

**GEPAN / SEPRA / GEIPAN is not mirrored at all**, and neither is the
Trans-en-Provence 1981 case file — GEPAN *Note Technique No. 16*, which
collated five laboratories and is the best-instrumented physical-trace case in
the literature. It sits at **rank 6** on this project's own retained-sample
priority list.

A useful false positive was caught and must not be chased: the archive.org
item `6248280-Rapport-CM-PM-Trans-en-Provence-83` looks like the case by title
but its OCR shows it is a **May 2018 letter from the municipal police of
Trans-en-Provence about a trial of body-worn cameras**. Pure place-name
collision.

The only routes to the French material are `geipan.fr` / `cnes-geipan.fr` /
`cnes.fr`. Those are the highest-value access requests outstanding.

## 4. What this changes

The documentary half of this project was declared blocked and is not. Newly
possible, all on legitimate public mirrors:

1. **18 MB of OCR'd PURSUE text** — entity extraction, location geocoding and
   cross-referencing against the deduplicated catalog and the facility layers.
2. **137,094 NUFORC rows** — a modern-era arm the catalog lacked, where the
   corpus had only 62 geocoded day-precision events in the 2000s.
3. **860 OCR'd periodical issues** (MUFON 485, APRO 260, IUR 115) — the actual
   upstream sources the Phase 1 citation-chain analysis identified as roots.
   This is the material that would let provenance chains be traced to primary
   publication rather than inferred.
4. **Condon, Sign, Robertson, Condign** — the official investigative record.

Note the irony worth recording: item 3 means the echo-chamber analysis could
now be extended from "which compilations cite which" to "what the cited
primary sources actually say" — the single biggest limitation named in the
Phase 1 report.
