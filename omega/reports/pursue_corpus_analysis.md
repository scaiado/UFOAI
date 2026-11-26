# PROJECT OMEGA — The PURSUE Corpus: What Is Actually In It

**Source:** archive.org mirror `pursue-uap-documents-2026`, metadata `source`
field `https://www.war.gov/UFO/`. **286 of 298 server-side OCR files fetched,
17.9 M characters.** Official public disclosure material.
**Code:** `omega/pursue_analyze.py` · **Output:** `data/processed/pursue/pursue_extraction.json`

---

## 1. Composition

| release | docs | character |
|---|---|---|
| Release_01 | 106 | FBI case files, State Department cables, historical Air Force files 1946–1950s |
| Release_02 | 6 | CIA 1973 USSR report, **DOE PANTEX**, Sandia correspondence, Pajarito astronomers |
| Release_03 | 53 | CIA files incl. the **Scientific Advisory Panel (Robertson) report 1952–53**, U-2 overhead-reconnaissance history, German flying-disc article |
| Release_04 | 14 | CIA 1955 memoranda, **DOE Los Alamos Conference on Aerial Phenomena 1949**, **DOE Pantex Unidentified Object Incident Report 2015**, **Navy Range Fouler debriefs 2019 & 2020** |
| Release_05 | 20 | CIA Puerto Rico 1965, DOS Brazil cables Nov 1963, **Intelligence Review of Ghost Rocket Incidents 1947** |
| Release_06 | 59 | Tremonton film files, **37 AAWSAP DIRDs**, Mission Reports Iraq 2022 and Middle East 2025 |
| Release_07 | 28 | Air Intelligence Information Reports by country 1953–57, **Utah Ranch Investigation Report April 2010** |

122 of 286 documents mention UAP/UFO; 138 carry classification markings; 27
carry DTG timestamps; 4 carry MGRS grid references.

Year mentions peak at **1947** (14 docs), then 1965, 1948, 1952, 1963, 1964,
**2009** (8 each) — a bimodal corpus: the historical investigative record, and
the 2009–2011 AAWSAP programme.

## 2. The AAWSAP DIRD set — 37 documents, the most significant content

These are the Defense Intelligence Reference Documents commissioned under the
Advanced Aerospace Weapon System Applications Program. Titles include:
Traversable Wormholes, Stargates and Negative Energy · Warp Drive, Dark Energy
and the Manipulation of Extra Dimensions · Antigravity for Aerospace
Applications · Negative Mass Propulsion · Concepts for Extracting Energy from
the Quantum Vacuum · Quantum Tomography of Negative Energy States in the Vacuum ·
The Role of Superconductors in Gravity Research · Invisibility Cloaking ·
Programmable Matter · Metamaterials · Positron Aerospace Propulsion ·
Inertial Electrostatic Confinement Fusion · An Introduction to the Statistical
Drake Equation.

This is the BAASS/AAWSAP material, present as primary documents.

## 3. A trap: the "biologic language" result decomposes to nothing

A keyword pass finds **73 of 286 documents (25.5%) containing biological
evidence language**, with the heaviest concentrations in:

| hits | document |
|---|---|
| 215 | D150 — AAWSAP DIRD, *Quantum Computing and Utilizing **Organic Molecules** in Automation* |
| 90 | D119 — AAWSAP DIRD, ***Biomaterials*** |
| 59 | D128 — AAWSAP DIRD, *Anomalous Field Effects on Human **Biological** Systems* |
| 54 | D136 — AAWSAP DIRD, ***Biosensors** and BioMEMS* |
| 51 | D130 — AAWSAP DIRD, *Technological Approaches to Controlling External Devices* |

> **None of these concern recovered non-human biologics.** They are
> commissioned literature surveys on biotechnology topics. The word
> "biologic" appears because the subject *is* biology-adjacent engineering.
> Reported without reading the titles, "73 documents contain biological
> evidence language, concentrated in documents about biomaterials and field
> effects on human biological systems" would read as a bombshell and mean
> nothing of the kind.

Likewise "lab analysis" (85 docs, 29.7%) and "material/debris" (58 docs,
20.3%) are dominated by the same technology-survey vocabulary.

One genuine item in that set: **D128, *Anomalous Acute and Subacute Field
Effects on Human Biological Systems***, is the DIRD on injury from field
exposure — the Cash-Landrum class of claim, properly in scope.

## 4. Coordinate cross-reference: essentially null

Only **7 of 286 documents** yield parseable coordinates; 25 unique after
deduplication. Against 17,823 geocoded catalog events:

| band | PURSUE coords within |
|---|---|
| 10 km | 1 (4.0%) |
| 25–100 km | 3 (12.0%) |
| 250 km | 5 (20.0%) |

Median distance to nearest catalog event: **460.6 km.**

And the single sub-10 km "match" is trivial: PURSUE `38.8669, −77.0003` →
catalog `1952 WASHINGTON, DC`, 0.04 km apart. That is the 1952 Washington
flap, and the coordinate is simply Washington. The 224–440 km "matches" in
Ghana, Togo and Cameroon come from AAWSAP DIRD papers on lasers and hypersonic
tracking — almost certainly figure or table values my decimal-degree regex
mistook for coordinates. **The coordinate cross-reference yields no finding.**

## 5. What this genuinely changes

The nuclear question. Phase 2 closed the detonation-proximity claim as
untestable in catalogs, because the catalogs contain the detonations
themselves. Phase 5 closed the missile-facility claim because the catalog held
only the claim's founding events. **The PURSUE release contains
nuclear-facility UAP incident documentation that the catalogs do not:**

- **DOE-UAP-D005** — Pantex Unidentified Object Incident Report, **2015**
  (Pantex is the US nuclear weapons assembly plant)
- **DOE-UAP-D004** — Los Alamos Conference on Aerial Phenomena, **1949**
  (the green fireball conference)
- **DOE-UAP-D001/D002/D003** — PANTEX imagery, James Tuck correspondence,
  Pajarito astronomers
- **DOW-UAP-D017** — General correspondence of Sandia

That is primary-source material on the exact question the catalogs could not
address, from the agency that operates the facilities. It does not make the
statistical claim testable — these are individual incident documents, not a
population with a denominator — but it is the first evidentiary route into the
nuclear question that is not catalog-contaminated.

Also notable as primary documents: **DOW-UAP-D089/D090**, Navy "Range Fouler"
debriefs 2019 and 2020; **DOW-UAP-D174**, Utah Ranch Investigation Report
April 2010 (the AAWSAP Skinwalker Ranch investigation); **DOW-UAP-D102/D103**,
Project Blue Book's own file on the 1952 Tremonton film.

## 6. Limitations

1. 12 of 298 OCR files were not retrieved; ~40 of 338 PDFs are image-only and
   carry no OCR at all, so the corpus analysed here is ~85% of the release text.
2. OCR quality on 1940s–50s typescript is poor; entity extraction inherits that.
3. The coordinate regex produced false positives from technical-paper numerics,
   which is why §4 reports no finding rather than a weak one.
4. Classification portion markings are present throughout, as is normal for
   declassified releases; the source is the government's own public release site.
