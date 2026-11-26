# What the UAP mission reports actually withhold

*Project Omega, session 4. §5 item 2. Source: 326 PURSUE release texts, of which
41 are DOW mission reports (MISREP forms); 33 parsed with ≥10 fields.
Script: `omega/redaction_slots.py`. Data:
`evidence_vault/05_SCRUBBED_CONTENT/redaction_slots.json`.*

---

## 1. The route in was structure, not grammar

§1.7 counted 982 inline exemption substitutions and stopped at extent. §5 item 2
proposed recovering the *class* of withheld content from surrounding grammar —
`AT 0823Z, (b)(1)1.4a TOOK OFF FROM OJMS VIA SLR` gives the removed token as the
subject of "took off", so a platform or callsign.

That works, but it is the harder road and it was not needed. The DOW mission
reports are **MISREP forms**, and a redaction sits inside a **named field**:

```
• Major Command (MAJCOM): AFCENT
• Combatant Command (COCOM): (b)(1)1.4a
• Aircraft Callsign: 1.4a
• Full Name: (b)(3), 130b, (b)(6) 1.4a
```

The form label states what was removed. No inference is required. 167 field
labels recur across ≥3 documents, which makes the schema stable enough to
compute a **per-field withholding rate** over 33 documents.

Three things follow that a count of redactions cannot reach: a rate per field, a
validation against the government's own exemption code, and a value domain for
fields that are withheld in one document and released in another.

## 2. What is withheld, by slot class

582 withheld field instances against 1,647 released, 226 unreadable, 1,367 empty.
Overall withholding rate over decidable instances: **582/2,229 = 0.261**.

| slot | withheld | released | rate | dominant exemptions |
|---|---|---|---|---|
| **CALLSIGN** | 98 | 10 | **0.91** | `1.4a` 75, `(b)(1)1.4a` 18 |
| PERSONNEL | 131 | 78 | 0.63 | `(b)(6)` 133, `(b)(3)` 41 |
| NARRATIVE | 79 | 115 | 0.41 | `1.4a` 73, `(b)(1)` 67 |
| WEAPON_SENSOR | 32 | 77 | 0.29 | `(b)(6)` 21, `(b)(1)1.4a` 11 |
| GEO | 40 | 105 | 0.28 | `1.4a` 30, `(b)(1)1.4a` 20 |
| OPERATION | 42 | 119 | 0.26 | `1.4a` 21, `(b)(1)1.4a` 18 |
| COUNT_QTY | 13 | 76 | 0.15 | `(b)(1)1.4a` 16 |
| UNIT_ORG | 48 | 370 | 0.11 | `(b)(6)` 45, `(b)(1)` 22 |
| TIME | 29 | 288 | 0.09 | `(b)(1)` 40, `(b)(6)` 15 |
| CLASSIFICATION | 1 | 41 | 0.02 | `(b)(1)1.4a` 2 |

**Aircraft identity is withheld 10× more often than mission time or unit.**

## 3. The protected class, stated exactly

**Never once released, across every document in which the field appears:**

| field | withheld | class |
|---|---|---|
| Email | 52 | personnel identity |
| Full Name | 33 | personnel identity |
| Aircraft Callsign | 33 | aircraft identity |
| Callsign | 32 | aircraft identity |
| Phone Number | 28 | personnel identity |
| Call Sign | 8 | aircraft identity |
| Asset Type (Aircraft) | 8 | force composition |
| Number of Aircraft | 4 | force composition |
| BE Number (if NTISR) | 4 | target reference |

**Released essentially always:**

| field | w/r | field | w/r |
|---|---|---|---|
| Country Tasked | 0/24 | Activity Description | 0/22 |
| Last Engine Shutdown Time | 0/21 | Precoord Effectiveness | 0/23 |
| Time-off Station DTG | 0/20 | Report Type | 0/23 |
| Service | 2/70 | Rank | 4/62 |
| Unit | 5/54 | Wing | 7/52 |
| Mission Type | 5/39 | MAJCOM | 1/20 |
| Takeoff Time DTG | 1/21 | Declassification Date | 3/21 |

So the release says **which country, which service, which wing, which rank, what
mission type, and what times** — and never **which aircraft, under what
callsign, how many of them, or who by name**.

### This cuts against a suppression reading

The withholding pattern is force composition and personnel identity. It is
**not** the observation. `Activity Description` is released 22/22,
`Precoord Effectiveness` 23/23, and the `Gentext` narrative — which carries the
actual UAP description — is released 115 times against 37 withheld.

That is the profile of ordinary operational security, not of a programme
concealing phenomenon data. **Reported as a negative.** The thing a suppression
hypothesis predicts would be most protected — the description of what was seen —
is the thing most consistently released, while the thing routine OPSEC always
protects — which airframe, whose callsign, how many, crewed by whom — is
protected absolutely.

## 4. Calibration against the releasing authority's own code

The exemption code is an **independent label**, applied by the releasing
authority, not by me. If the form-slot reading is sound it should agree with it.

Scoring 575 tokens (`NARRATIVE` and `UNCLASSIFIED_SLOT` excluded — a redaction
inside free prose has no inferable slot, so these are excluded rather than
scored as wrong):

- **slot consistent with the cited exemption: 443 (77.0%)**
- inconsistent: 132 (23.0%)

`(b)(6)` privacy lands on `Email`/`Full Name`/`Phone Number`; `1.4a` military
plans lands on callsigns, operations and geography. The slot reading recovers
the government's own classification three times in four.

**77% is a floor, not an estimate.** The largest single disagreement is
`(b)(6)` on `UNIT_ORG` (45 tokens), and **83% of those are OCR field-absorption**
— the bullet separator was lost, so a unit field swallowed the following
personnel field:

```
Wing = 432 AEW (b)(3), 130b, (b)(6) 1.4a      <- Full Name's codes
Service = Air Force (b)(6) 10/20/25 002 SECRET//REL...
```

Those are parser artifacts, not privacy claims about unit designators.

## 5. Checks run before any of the above was believed

Two passes were discarded first. Both failures are recorded because they are the
reason the numbers above are usable.

1. **A legibility proxy that was the wrong instrument.** Scoring OCR quality by
   the share of all-alphabetic tokens ranked the modern mission reports as
   *worse* than degraded 1950s FBI scans, because it penalised `0823Z`,
   `SECRET//REL` and `432 AEW` — correct military format, not damage. Replaced
   with document-type gating on the MISREP section spine.

2. **OCR variants counted as releases.** The first marker regex matched only
   clean `(b)(n)`, so `(b}(6)`, `(bl(6}`, `fbl{6\` and bare `! 1.4a` were scored
   as *released values*. That produced "Email: 15 released" and
   "categorically protected fields: 0" — both artifacts. The corrected detector
   is OCR-tolerant and adds an explicit **UNREADABLE** class, so damaged text is
   never counted as disclosure. 226 instances are unreadable and carry no claim.

3. **Portion markings vs substitutions.** A bare `1.4a` after a classification
   banner — `(S//REL) 1.4a WAS EFFECTIVE` — is a portion marking stating that
   paragraph's classification reason, not a substitution for removed text.
   Measured: **7 of 498 bare marks (1.4%)**, all in narrative fields. Excluded.
   The confound was real but negligible; it was measured rather than assumed.

## 6. What this does not claim

No withheld value is reconstructed. Every statement rests on text the government
released, read against itself. The per-field rates are rates over the 33 parsed
MISREP forms, not over the whole 326-text release. `Gentext` is a container
field: its 0.41 rate means "some redaction somewhere in the narrative", not that
41% of narrative text is withheld.
