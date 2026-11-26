# PROJECT OMEGA — Phase 9: Physical-Trace Site Dossiers

**Status:** delivered. **Code:** `omega/phase9.py`.
**Outputs:** `data/processed/soil_assay/soil_assay_targets.{json,csv}` (1,917 sites),
`data/processed/soil_assay/retained_sample_leads.json` (346 leads).

---

## 1. Method

Events from the deduplicated catalog with coordinates and a parseable year are
scored on deposited-material evidence from two sources: Hatch's trace codes
(`SMP` sampling 5.0, `RDA` radiation 5.0, `DRT` soil/dirt 4.0, `TRC` traces
4.0, `VEG` plants 3.0, `LND` landing 2.0, `ANI` animals 1.5, `INJ` injury 1.5)
and eight text-derived substrate classes (residue, radiation, burn, depression,
ring, soil, magnetic, vegetation death). Score is multiplied by corroboration
(n_catalogs), provenance depth and credibility. Threshold ≥ 4.0.

**Decontaminated with the Phase 2 rule.** The first run ranked **Hiroshima
(#8), Nagasaki (#24) and Tunguska (#3)** in its top 25 — atomic bombings and a
10-megaton-class airburst score high on "physical traces" for entirely
ordinary reasons. These, along with meteorite falls, eruptions and aircraft
crashes, are now excluded. 12 sites removed.

Result: **1,917 candidate sites.** By decade: 1950s 332, 1960s 474, 1970s 660,
1980s 171, 1990s 194. By country: USA 323, France 161, Brazil 55, Britain 46,
Canada 43 — and **933 with no country field**, which is the main obstacle to
site location.

## 2. Top 15 priority sites

| # | score | date | lat | lon | cat | codes | site |
|---|---|---|---|---|---|---|---|
| 1 | 98.7 | 1964-04-24 | 34.0444 | −106.8945 | 9 | DRT,LND,RDA,SMP,TRC | Socorro NM (Zamora) |
| 2 | 89.4 | 1980-12-28 | 52.1111 | 1.3889 | 8 | ANI,DRT,INJ,LND,RDA | RAF Woodbridge / Rendlesham |
| 3 | 61.7 | 1973-10-06 | 45.4889 | −73.2500 | 5 | DRT,INJ,LND,SMP,TRC | St-Mathias-de-Chambly QC |
| 4 | 57.5 | 1964-04-24 | 42.0667 | −76.3500 | 8 | DRT,LND,RDA,SMP,TRC | Newark Valley NY (Wilcox) |
| 5 | 57.4 | 1964-06-30 | 34.4333 | −83.1000 | 5 | INJ,RDA,TRC | Lavonia GA (Parham) |
| 6 | 56.5 | 1965-08-19 | 42.2667 | −79.0833 | 8 | ANI,DRT,LND,TRC,VEG | Cherry Creek NY (Butcher) |
| 7 | 55.1 | 1980-12-29 | 30.0278 | −95.0833 | 8 | INJ,RDA,TRC | Cash–Landrum TX |
| 8 | 54.5 | 1957-07-30 | 43.3500 | −80.3000 | 7 | DRT,INJ,LND,TRC,VEG | Galt ON |
| 9 | 52.5 | 1975-11-02 | 44.1722 | −93.2445 | 2 | DRT,LND,RDA,TRC,VEG | Medford MN |
| 10 | 51.9 | 1968-07-31 | −21.2000 | 55.5833 | 6 | LND,RDA,TRC | La Plaine des Cafres, Réunion (Fontaine) |
| 11 | 51.4 | 1965-03-15 | 26.4167 | −81.4167 | 6 | ANI,INJ,LND,SMP,TRC | Everglades FL (Flynn) |
| 12 | 50.6 | 1965-01-12 | 48.9333 | −122.7000 | 7 | DRT,LND,TRC | Custer WA |
| 13 | 50.6 | 1980-09-30 | −38.0667 | 147.0833 | 6 | ANI,DRT,LND,SMP,TRC | Rosedale VIC |
| 14 | 50.5 | 1966-09-13 | 46.2111 | −97.8333 | 7 | DRT,LND,TRC | Rotenberger ND |
| 15 | 49.9 | 1975-01-12 | 40.8000 | −74.0000 | 5 | DRT,LND,SMP,TRC,VEG | North Hudson Park NJ (O'Barski) |

(Valensole 1965 — Maurice Masse — ranks 18 at 49.3.) The scoring independently
reproduced the physical-trace canon, which is a sanity check on the weighting.

## 3. Assay design — a correction to the brief

The brief asked for "iridium, osmium, **plutonium-244**, other extraterrestrial
markers." **Pu-244 is the wrong test.** It is an r-process primordial nuclide
used as a marker in deep-sea ferromanganese crusts over megayear timescales,
not a soil signature of a vehicle.

The cosmochemical standard for non-terrestrial origin is **mass-independent
isotope anomaly**: all solar-system material falls on a mass-fractionation
line; material formed around another star does not. Assays are specified
accordingly:

- **Residue / metallic fragment:** PGE suite by ICP-MS (Ir, Os, Pt, Pd, Ru, Rh)
  with Ir/Os compared to chondritic 1.0–1.1; **Cr (⁵⁴Cr/⁵²Cr) and Ti
  (⁵⁰Ti/⁴⁶Ti) by MC-ICP-MS — this is the diagnostic test**; oxygen
  three-isotope (δ¹⁷O vs δ¹⁸O) against the terrestrial fractionation line;
  SEM-EDS for unequilibrated phases.
- **Radiation cases:** HPGe gamma spectrometry for Cs-137, Co-60, Am-241,
  Ra-226 — note these are **exclusion** tests: their presence indicates mundane
  contamination. ²³⁵U/²³⁸U against natural 0.00725; AMS for Fe-60/Al-26 only if
  an anomaly appears.
- **Burn cases:** thermoluminescence/OSL on quartz to bound peak temperature;
  magnetic susceptibility vs depth; XRD for quartz→cristobalite (>1000 °C).
- **Depressions:** bulk density and penetrometer transect against a paired
  off-site control; micromorphology thin-section.
- **Rings / vegetation:** node elongation and cell-wall expansion in affected
  stems (the microwave signature); magnetite microsphere counts.

Every soil assay requires a **paired off-site control at matched depth**.
Without it the result is uninterpretable.

## 4. The strategically better track: retained samples, not sites

**Digging a 60-year-old field is a poor bet, and the physics says so.** A thin
surface deposit from 1964 has had six decades of ploughing, leaching,
bioturbation and freeze–thaw. PGE and isotope anomalies in a surface layer
disperse below detection. Nothing in the ranking above changes that.

But `SMP` marks **346 events where material was collected at the time.** Those
samples went to APRO, NICAP, CUFOS, Project Blue Book, or university
laboratories. **Surviving archived material is orders of magnitude more likely
to be assayable than in-situ soil**, and it carries chain-of-custody that a
fresh dig never will.

`retained_sample_leads.json` lists all 346 with their catalog provenance as
archive leads. The highest-value physical-evidence action in this project is
not fieldwork — it is **locating the retained samples from Socorro (1964),
Valensole (1965), Delphos KS (1971), Trans-en-Provence (1981, the best-documented
case with French government laboratory analysis), and Rosedale (1980)** in the
CUFOS/APRO collections and the GEPAN/SEPRA files, and submitting them for
modern MC-ICP-MS work that was not available when they were taken.

## 5. Limitations

1. **Site access is UNVERIFIED for every row.** Current land use cannot be
   checked here — that needs imagery or land-registry access. The field is
   present and explicitly unpopulated rather than guessed.
2. 933 of 1,917 sites have no country field; coordinates derive from Hatch's
   arcminute place-name geocoding, so effective accuracy is **~2–20 km** (see
   Phase 5 §1.2). **That is not good enough to find a trace site.** Site-level
   work requires the original case file, not this catalog.
3. Trace codes are Hatch's judgements; text classes are regex over prose.
4. Scores rank *catalog evidence for a trace*, not probability of recoverable
   anomalous material, which is far lower.
