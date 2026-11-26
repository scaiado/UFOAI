# GEPAN Note Technique No. 16 — write-up and replication

Case `1981-01-00849` TRANS-EN-PROVENCE (83), 8 Jan 1981, GEIPAN class **D**.
NT-16 = `CT/GEPAN-00013`, *ENQUÊTE 81/01 — ANALYSE D'UNE TRACE*, 1 March 1983,
ISSN 0750-6694 (NT16 p.1).

**Code:** `omega/tep_nt16_replication.py`, `omega/geipan_trace_null.py`
**Raw output:** `omega/reports/tep_nt16_replication_out.txt`, `…_replication.json`,
`omega/reports/geipan_trace_null_out.txt`
**Sources:** `evidence_vault/02_GEPAN_PHYSICAL_TRACES/Trans-en-Provence_1981/`
(dossier PDFs + text) and `data/raw/geipan/geipan_cases.json`.

**Citation convention.** "NT16 p.N" is the PDF page of `Note_techn16-R.pdf`.
The printed folio is one less (PDF p.50 carries "- 49 -"). Other documents are
cited as `file p.N`, PDF page. Every number used in the analysis was read from
the page image, not from OCR. Anything not read directly off a page is marked
**[INFERRED]**.

---

## 0. Bottom line

1. **The biochemistry reproduces.** 9 of 11 correlations NT-16 reports are
   recovered to ±0.01 from its own tables (§4.1). One table cell in NT-16 is a
   transcription error (E-1 chlorophyll B printed 0,930, INRA's handwritten
   original says 0,030); INRA computed from the correct value.
2. **The distance gradient survives every null model the data allow.** 13 of
   16 pigment and cofactor variables show |r| ≥ 0.811 against distance. Under
   joint relabelling of the six distances the expected count is 1.7, P = 0.0028.
   That is the smallest P this design can produce (2/720). It survives dropping
   the centre sample and controlling for leaf size (§4.4–4.6).
3. **The reported significance is overstated.** NT-16's P-values are one-sided
   parametric. One (ln PhA′/ΣChlA, N=5) is 50× too small. With six plants on one
   transect, no reported P can honestly be below 0.0028.
4. **The magnitudes behind the famous headline figures carry ±50% analytical
   error and no biological replicate.** Of the series-1 losses (exposed vs 20 m
   control), only β-carotene (−57% young, −50% aged) and violaxanthine in young
   leaves (−80%) clear analytical noise (CV 0.22, NT16 p.45). The chlorophyll
   losses (−27 to −33%) do not (§4.7).
5. **The "pattern" argument against ionising radiation is weaker than the
   prior project report said.** In series 1 the carotenoid-over-chlorophyll
   excess has a 95% analytical interval that includes no excess. In series 2 it
   holds from 1.5 m outward but **reverses at the centre** (§4.8).
6. **The soil mass spectrometry cannot support the zinc/phosphate "paint"
   reading.** The lab's two plates of the same soil disagree by a median factor
   of 23. Twenty-three of 24 elements fall outside the lab's own factor-3
   tolerance. Phosphorus is the only element enriched in the deposit on both
   plates, and one such element is what chance gives (null mean 1.16, P = 0.77).
   Zinc cannot be tested on the second plate (§5).
7. **At the database level, finding a trace does not predict class D. Looking
   for one does.** In GEIPAN's own narratives, cases where a ground search
   found a trace and cases where a search found nothing have the same D-rate
   (OR 1.0–1.1, P = 0.89). Searching versus not mentioning a search: era-adjusted
   OR 2.7, P = 0.015 (§6). That fits D meaning "adequate information". It is not
   evidence that traces mark unexplained events.
8. **Three factual errors in this project's earlier TEP report are corrected**
   (§3). The worst was the telex mark width ("14 cm"; it is 10 cm), which had
   created a discrepancy that does not exist.

What the data establish: **something produced a real, monotone biochemical
gradient along one six-plant transect, starting at that spot.** What they
cannot establish is the cause. The design has one transect in one direction,
no comparison transect from another point on the platform, a control series
collected 14 days later on the opposite side, and 40 days of foot traffic
before the main series was taken (§4.9).

---

## 1. The dossier — what is on disk

GEIPAN's export lists one document for this case, `Note techn16-R.pdf`
(`geipan_cases.json`, field `Document pour cas`). The full dossier retrieved in
session 2 has **10 files, 177 pages**. `HANDOFF.md §1.2` says "11-document
dossier, 172 pages". That count does not match the archive. The 10/177 figure
was counted from the files with `pdfinfo` this session. **[INFERRED]** The 11th
item may have been GEIPAN's web case page; nothing on disk corresponds to it.

| # | file | pp | author / body | date | content | text |
|---|---|---|---|---|---|---|
| 1 | `Note_techn16-R.pdf` | 67 | GEPAN (CNES) | 1 Mar 1983 (p.1) | the Note Technique | text layer, 109,615 chars |
| 2 | `PV_n°28_(1981308305).pdf` | 11 | Gendarmerie, Brigade de Draguignan / DIRCENGEND | telex 9 Jan 1981; PV closed 4 Feb 1981 (p.4) | telex (p.1), forwarding slips (pp.2–3), procès-verbal with site description and witness statement (pp.4–6), photo plates (pp.7–11) | image-only → OCR'd this session |
| 3 | `Analyses_INRA-R.pdf` | 6 | INRA Lab. de Biochimie, Montfavet | 15 Jan, 23 Jan, 13 Mar, Apr 1981 | cover letters to GEPAN and to the gendarmerie | image-only, handwritten parts |
| 4 | `Analyses2_INRA-R.pdf` | 60 | INRA (Dr B.) | 1981 (p.2) | full handwritten biochemical report; original of NT-16 §7 tables (e.g. p.15 = NT-16 Tab.1, p.23 = NT-16 Tab.2) | handwritten; OCR poor, tables read from images |
| 5 | `Analyse_LDP-R.pdf` | 16 | Laboratoire d'Analyses Physiques | 23 Oct 1981 (p.2) | cover letter, four spark-source mass spec sheets (pp.5, 8, 11, 14), spectra | element tables handwritten, read from images |
| 6 | `Analyses_SNEAP-R.pdf` | 3 | SNEAP | n.d. | microscopy, CAMECA microprobe: Fe/FeₓOᵧ plated on calcite grains, "frottement", heating estimate | text layer |
| 7 | `Analyses_DER-R.pdf` | 7 | University lab, electron diffraction (DER) | 12 Oct 1981; samples received 22 Apr 1981 (p.2) | BaCa(CO₃)₂, CaO₂·8H₂O, minor Fe₃O₄; monocrystalline phase in trace only | text layer |
| 8 | `ALAT-R.pdf` | 3 | ALAT (p.1–2); État-Major de l'Armée de Terre (p.3) | reply to GEPAN letter of 21 Jul 1981; second reply to letter of 12 Oct 1981 | Alouette II at 200 m around 16:30; inert tank-gun fire >25 km N | text layer |
| 9 | `Meteo-R2.pdf` | 1 | Météorologie Nationale, Aix | 27 Jul 1981 | 6.8 °C, RH 30%, wind SE 2 m/s, 2/8 cloud, no precipitation; distant lightning 11 Jan | text layer |
| 10 | `Photos-R.pdf` | 3 | GEPAN | — | site photographs | image |

---

## 2. Write-up of NT-16

### 2.1 Why GEPAN investigated (NT16 p.4–6)
GEPAN normally declined single-witness cases. It took this one because there
were two kinds of information to compare: the witness account and a physical
trace (p.4, p.6). The gendarmerie at A2 was called on 9 Jan. It attended at
11:30, photographed the marks and took soil and plant samples under the
*livret gendarmique* procedure (p.5). GEPAN learned of the case on 12 Jan,
after heavy weekend rain on 10–11 Jan. It chose not to go immediately (p.5;
rain also p.33). A private group, "XYZ", sent an investigator on 13 Jan (p.5).
GEPAN went on site on 17 Feb, at J+40 (p.19).

### 2.2 The site (NT16 p.6–16; PV p.4)
The site is a hillside property on terraces (*restanques*). The event took
place on the large terrace, "level 1". It is 31 m × 11 m: **3 m of bare
packed earth and 8 m of flattened grass** (PV p.4). It is "practically never
used, except sometimes for pétanque" (NT16 p.9). **Vehicles reach this terrace
by the dirt track** (p.9). The trace lies "close to the south-east entrance
(small dirt track)", on the packed-earth strip right next to the retaining
wall (p.28). No power or telephone lines are in view (p.9).

### 2.3 The testimony — four versions (NT16 p.17–27; PV p.1, p.5–6)

| detail | telex 9 Jan (PV p.1) | PV extract (NT16 p.17–18) | XYZ (NT16 p.18–19) | GEPAN 17 Feb (NT16 p.19–23) |
|---|---|---|---|---|
| time | **17H00** | — | "le soir tombant" | — |
| first cue | light whistle | light whistle | silent fall | sound "like a strong wind" (p.22) |
| distance | ~50 m | ~30 m at take-off | ~80 m, then 45 m | 30 m < d < 70 m (p.20–21) |
| size | Ø ~3 m | ~1.5 m high | 2–2.5 m high | Ø 2.5 m, h 1.7–1.8 m (p.22) |
| dust | "**aucune poussière soulevée**" | "a soulevé un peu de poussière" | dust displaced | not reported (p.27) |
| duration | ~1 min | — | — | 30–40 s (p.20) |

GEPAN notes for itself that the diameter/height ratio varies between versions:
1.42, 5.66 and 2.25 (p.22). It puts the differences down mostly to how the
investigators wrote the accounts up, because the witness had limited French
(p.21 fn., p.27). GEPAN's assessment: "une bonne cohérence générale". It finds
nothing that suggests invention, but notes "l'absence de preuve n'étant pas …
la preuve de l'absence" (p.27, p.66). The witness's own interpretation was
consistently "an unknown military machine" (p.25).

The dust contradiction is new to this project. The telex says no dust was
raised. The witness statement quoted in the same gendarmerie file says some
was.

### 2.4 The trace (NT16 p.28–31; PV p.1, p.4)
The gendarmerie recorded two concentric circles, 2.20 m and 2.40 m in
diameter, forming a ring 10 cm wide. On the ring were two diametrically
opposite sections of ~0.80 m showing "stries noires semblables à des traces de
ripage" (PV p.4; NT16 p.28). The telex gives the same marks: "deux arcs de
cercles ressemblant à des traces de ripage de pneumatiques — longueur : 80 cm —
largeur : 10 cm" (PV p.1). XYZ described "plutôt un fer à cheval" with regular
striations, "comme si on avait ripé un métal" (p.28). At J+40 the trace was
still visible, as a lighter arc-shaped zone of strongly compacted earth with a
crust about 1 cm thick (p.28).

### 2.5 Sampling (NT16 p.32–33, p.42–43; INRA2 p.4)
- **Soil:** P1 on the trace (gendarmerie, 9 Jan); P2 control, 3–4 m away on the
  terrace (GEPAN, 17 Feb) (p.33).
- **Vegetation, series 1:** N-4/N-8 (aged/young leaves) at 1.5 m on 9 Jan (J+1).
  Controls N-11/N-15 at 20 m on 23 Jan (J+15), requested by INRA (p.33, p.42).
  In Croquis 8 (p.32) the controls lie on the opposite side of the trace from
  the series-2 transect, in the direction of the house.
- **Vegetation, series 2:** E-1…E-8 on 17 Feb (J+40) along **a single
  transect** running east from the centre: d = 0, 1.5, 2.1, 3.5, 10, 10 m for
  the *Medicago minima* samples E-1–E-6. E-7 (thyme, 4.8 m) and E-8 (wild
  lettuce, 7.6 m) were not analysed in the tables (p.32, p.43; INRA2 p.4 Fig. 1).

### 2.6 Soil results (NT16 p.35–41)
- CNES microscopy: compacted calcareous crust 6–7 mm thick; curved striations
  from surface friction removing silica grains ("effet de ponçage"); a flint
  pushed in and planed flush (p.35).
- SNEAP microprobe: iron (free or oxide), about 1 µm thick, "plaqué" on calcite
  grains along the striations. It is not alloyed with Cr, Mn or Ni (p.38;
  SNEAP p.2).
- DER electron diffraction: a monocrystalline constituent found in P1 and not
  in P2. Heating to 1000 °C for 2 h did not reproduce it (p.38, p.40).
- Ion mass spectrometry (faculty lab): black particles with phosphate ions
  63/79 and a polymeric carbon matrix, "semblent être des résidus de
  combustion" (p.39).
- LDP spark-source: "peu de différence significative entre le sol témoin et
  le sol sur lequel un dépôt est visible". Zn and P are read as "pouvant
  provenir d'une peinture noire primaire à base de Carbon black" (p.39). The
  summary table says "Trace laissée sur le sol pouvant provenir d'un revêtement
  primaire (peinture) ayant été frotté" (p.41).
- Synthesis (p.40): strong mechanical pressure "probablement due à un choc";
  surface structural change; **heating below 600 °C**, since CaCO₃ did not
  dissociate; possible trace deposit of Fe/FeO, phosphate and zinc.

### 2.7 Biochemistry (NT16 p.42–65; written by INRA's Dr B., p.42)
Pigments, photosynthetic cofactors, lipids, sugars and amino acids were
analysed by thin-layer nanochromatography (p.44). Key claims:
- Series 1, at 1.5 m against the 20 m controls: ChlA −33%, ChlB −28%,
  pheophytin −31% "grande homogénéité"; β-carotene −50 to −57%; violaxanthine
  −80% in young leaves (p.45; table p.46).
- Series 2: concentrations correlate with distance from the centre. Fits use
  d, 1/(d+1), ln(d+1) and a Hill-type sigmoid (p.50–60). The vitamin-A-like
  derivative appears only at d = 0 (p.58–59). Sucrose falls 15–25% and glucose
  rises 30% near the centre (p.62–63).
- Conclusion (p.64–65): active pigment forms 30–50% lower and inactive forms
  higher at J+40. Arabidopsis seedlings would need 10⁶ rad of γ for comparable
  or smaller changes. "L'action du rayonnement nucléaire ne présente donc pas
  d'analogie avec celle de la source énergétique impliquée". The author
  suggests Mg²⁺ loss under "un champ énergétique de type électrique".

### 2.8 GEPAN's conclusion (NT16 p.66–67)
GEPAN concludes that "an event of great magnitude" occurred, causing mechanical
deformation, heating and perhaps trace deposits. It also says the possible
interpretations, "(choc, frottement…)", are "trop diverses et vagues" to
confirm the witness, and the biochemistry is "un remarquable faisceau de
résultats" with no single interpretation. GEPAN calls for systematic programmes
characterising physico-chemical interactions. "Cette enquête … pose plus de
questions qu'elle n'apporte de réponse" (p.67).

**Note on anonymisation.** The witness is "Monsieur C" throughout, but NT16
p.66 prints a near-complete surname, and the gendarmerie forms carry partial
initials. This report does not reproduce the name. The same standing rule
applies as for the pseudonyms in the AAWSAP release.

---

## 3. Corrections to this project's earlier records

| claim (where) | primary source says | status |
|---|---|---|
| telex marks "80 cm × **14 cm**" (`geipan_trans_en_provence.md` §2, §3) | "LONGUEUR : 80 CM — LARGEUER : **10** CM" (PV p.1, read from image) | **wrong.** No discrepancy with the gendarmerie sketch's 0.10 m (NT16 p.29) or the PV's 10 cm ring (PV p.4). |
| telex time "17H08" (same §2) | "17H**00**"; zeros are slashed (PV p.1) | wrong (OCR misread Ø as 8) |
| circular "CM NR **9.600** … 2/8/1968" (same §2) | "C M NMR **32.600** MA/GEND.T. DU 2/8/1968" (PV p.1) | number wrong; date right |
| "11-document dossier, 172 pages" (`HANDOFF.md §1.2`) | 10 files, 177 pages on disk | count wrong |
| "pheophytin −31%" as one figure (both reports) | −31% in aged leaves, **−40% in young** (NT16 p.46) | incomplete |
| "the carotenoid-to-chlorophyll ratio is inverted … the sharper discriminator" (`geipan_trans_en_provence.md` §4) | holds in series 1 at 1.5 m but within analytical noise, and reverses at d = 0 in series 2 (§4.8) | **overstated** |
| NT-16 Tab.2 E-1 Chl B = 0,930 (NT16 p.50) | 0,030 in INRA's original (INRA2 p.23) | NT-16 transcription error |
| EMAT letter dates the event "8 janvier **1980**" (ALAT-R p.3) | 8 Jan 1981 everywhere else | clerical error in the source |

---

## 4. Replication — biochemistry

### 4.1 Reproducing the reported statistics from NT-16's own tables

| relation (page) | NT-16 r | recomputed r | NT-16 P | our P, 2-sided / 1-sided |
|---|---|---|---|---|
| ΣChlA ~ d (p.50) | +0.6868 | +0.686 | — | 0.132 / 0.066 |
| ΣChlA/ΣChlB ~ d (p.51) | +0.7509 | +0.788 | 0.031 | 0.063 / **0.031** |
| ΣChlA/ΣChlB ~ 1/(d+1) (p.51) | −0.891 | −0.893 | 0.0039 | 0.017 / 0.008 |
| ΣPhA/ΣChlA ~ 1/(d+1) (p.51) | +0.990 | +0.990 | — | 0.00016 |
| PhA′/ΣChlA ~ 1/(d+1) (p.51) | +0.993 | +0.993 | — | 0.00007 |
| ln(PhA′/ΣChlA) ~ ln(d+1), N=5 (p.52) | 0.916 | −0.916 (drop E-4) | **0.00028** | 0.029 / **0.0145** |
| β-carotene ~ d (p.52 Tab.3) | 0.945 | 0.945 | 0.0022 | 0.0044 / **0.0022** |
| lutein ~ d (p.52 Tab.3) | 0.871 | 0.871 | 0.012 | 0.024 / **0.012** |
| ln Tq ~ ln(d+1) (p.60 Tab.8) | −0.973 | −0.972 | 0.00054 | 0.0011 / **0.00056** |
| ln Tc ~ ln(d+1) (p.60 Tab.8) | −0.951 | −0.952 | 0.0018 | 0.0034 / **0.0017** |
| ln C-P ~ ln(d+1) (p.60 Tab.8) | −0.961 | −0.962 | 0.0011 | 0.0022 / **0.0011** |

- The numbers are internally consistent. **INRA's reported P-values are
  one-sided parametric** (bold matches), which NT-16 does not say.
- One reported P is wrong by a factor of 50: ln(PhA′/ΣChlA) with N=5, reported
  0.28×10⁻³, true one-sided value 0.0145. NT-16 does not say which point was
  dropped. Dropping E-4 is the only deletion that reproduces |r| = 0.916.
  **[INFERRED]**
- The NT-16 table prints E-1 Chl B as 0,930. **INRA's handwritten original
  (INRA2 p.23, Tableau 8, nmol/mg) reads 0,030.** With 0,030 the reported
  −0.891 reproduces (−0.893), and so does the text's "Chl B shows no
  significant correlation" (r = −0.12). With 0,930 neither does (−0.955 and
  −0.55). The analysis uses the INRA value.

### 4.2 Effect sizes with uncertainty (series 2, N = 6)
Fisher-z 95% intervals on the recomputed correlations:
β-carotene ~ d **r = +0.945 [+0.58, +0.99]**; lutein +0.871 [+0.20, +0.99];
PhA′/ΣChlA ~ 1/(d+1) +0.993 [+0.93, +1.00]; ln Tq −0.972 [−1.00, −0.76];
ln Tc −0.952 [−1.00, −0.62]; ln C-P −0.962 [−1.00, −0.69].
ΣChlA ~ d +0.686 [−0.28, +0.96] **includes zero**.
ΣChlA/ΣChlB ~ d +0.788 [−0.07, +0.98] **includes zero**.

### 4.3 Null model A — exact permutation
All 720 orderings of the six distance labels were enumerated, keeping the tie
at d = 10. Because of that tie, the smallest attainable two-sided p is
**2/720 = 0.0028**. β-carotene, PhA′/ΣChlA and the three cofactor relations
reach that floor. ΣChlA ~ d (0.072) and ΣChlA/ΣChlB ~ d (0.067) do not reach
0.05.

### 4.4 Null model B — forking paths
INRA tried d, 1/(d+1) and ln(d+1) and reported whichever fitted best. The test
statistic here is the maximum |r| over all three transforms, recomputed under
every permutation. Results: ΣChlA, PhA′/ΣChlA, β-carotene, Tq, Tc and C-P stay
at p ≤ 0.0056. Lutein (0.056), the violaxanthine group (0.069), PhA (0.12),
protochlorophyllide (0.12–0.33) and **ΣChlB (0.75)** do not.

### 4.5 Null model C — joint relabelling (the multiple-comparison control)
All 16 variables come from the same six extracts, so they are not independent
tests. The distance labels were therefore permuted **once for all variables
together**, and each relabelling counted how many variables reach max |r| ≥
0.811 (the 2-sided 5% critical value for N=6). **Observed 13/16. Null mean
1.69, 95th percentile 8. P = 0.0028**, the design floor. The gradient is not
a multiple-testing artefact.

### 4.6 Robustness
- **Drop the centre sample (E-1).** Most relations hold on the five remaining
  points: β-carotene r = 0.93, PhA′/ΣChlA 0.95, Tq −0.95, ΣChlA ~ d rises to
  0.97. The gradient does not rest on E-1 alone. Lutein and the
  chlorophyll a/b ratio weaken (P 0.07–0.17).
- **Spearman.** ρ = ±0.986 for ΣChlA, PhA′/ΣChlA, β-carotene, Tq, Tc and C-P.
  This is a perfect monotone ordering apart from the tied pair.
- **Leaf development.** INRA flagged this itself (NT16 p.43–44). Fresh mass
  per leaf is unrelated to distance (r = +0.11). Partialling it out strengthens
  every relation (e.g. β-carotene 0.945 → 0.979).

### 4.7 Series 1 — the headline percentages, with uncertainty
Each cell is **one pooled sample**. The only stated precision is "coefficients
de variation atteignent C = 0,22 pour 3 mesures" (NT16 p.45). That is
analytical, not biological, variation. INRA2 p.15 (the original of Tab.1)
carries pencilled exposed/control ratios but no replicate values. The
intervals below are therefore a **lower bound** on the true uncertainty
(Monte Carlo, 200k draws).

| pigment | young: % change [95%] | aged: % change [95%] | γ 10⁶ rad (p.64) |
|---|---|---|---|
| Chl A | −33 [−66, +30] | −33 [−66, +30] | −30 |
| Chl B | −27 [−63, +42] | −28 [−63, +41] | −46 |
| Pheophytin A | −40 [−69, +17] | −31 [−64, +34] | — |
| **β-carotene** | **−57 [−78, −17]** | **−50 [−74, −3]** | −20 |
| Lutein | −13 [−55, +70] | −29 [−64, +37] | −30 |
| **Violaxanthine** | **−80 [−90, −61]** | −35 [−67, +25] | −40 |

- Only β-carotene (both ages) and young-leaf violaxanthine exclude zero.
- **"Enriched in inactive forms" is not visible in series 1.** The
  pheophytin/chlorophyll A ratio falls 10% in young leaves and rises 3% in aged
  leaves. In series 2 it is the strongest signal (PhA′/ΣChlA at E-1 is 0.49,
  against 0.02–0.19 elsewhere).
- **Design confounds, from the documents.** Exposed plants were picked on
  J+1 and controls on J+15 (NT16 p.42). The controls were 20 m away on the
  opposite side (Croquis 8, p.32). Storage before analysis therefore differed
  by about two weeks. Leaf amounts also differ: young control 25.1 mg dry
  against exposed 51.7 mg (p.43). None of these is separable from "exposure".

### 4.8 The carotenoid-versus-chlorophyll pattern
INRA's argument against radiation rests on carotenoids being hit harder than
chlorophylls (p.64–65). Results:
- **Series 1.** Double ratio (β-car exp/ctl)/(ChlA exp/ctl) = 0.64 young,
  0.75 aged. Analytical 95% intervals are [0.25, 1.64] and [0.30, 1.92].
  Neither excludes 1, so no excess is resolved.
- **Series 2.** β-carotene/ΣChlA = 0.097, 0.103, 0.132, 0.150, 0.189 from 1.5 m
  to 10 m (r = +0.91). Carotenoids are relatively more depleted near the trace,
  as INRA says. **But at the centre E-1 the ratio is 0.251**, the highest of
  all. There chlorophyll is the more depleted pigment, which is the reverse
  pattern.
- The γ benchmark compares cotyledons of *Arabidopsis* grown from irradiated
  seed with field leaves of *Medicago* 40 days after an unknown exposure
  (p.64). It is a qualitative analogy, not a dose estimate. The prior report's
  "β-carotene 2.67× worse than a megarad" is arithmetic on two
  non-commensurable numbers and should not be quoted as a dose comparison.

### 4.9 What the design cannot exclude
All of this is documented in the dossier. How much each factor matters is
**[INFERRED]**:
- **One transect, one direction** (INRA2 p.4 Fig. 1; NT16 p.32). The
  comparison that would separate "distance from the trace" from "position on
  the terrace" was never run: the same transect from a sham centre elsewhere on
  the platform.
- **The transect runs along the packed-earth strip at the foot of the
  retaining wall** (PV p.4; NT16 p.28, p.32). Light, moisture and soil depth can
  vary along a wall. Nothing in the dossier measures them.
- **Foot traffic between J+1 and J+40.** Gendarmes, XYZ, the press,
  neighbours and GEPAN all visited (NT16 p.5, p.25). Trampling is heaviest at
  the point everyone came to see. Compaction stress on *Medicago* is a
  candidate cause of a gradient centred on the trace, and the dossier does not
  test it.
- **Vehicle access.** The trace is next to the terrace's vehicle entrance (NT16
  p.9, p.28). The marks resembled tyre scrub to the gendarmes (PV p.1, p.4). A
  vehicle manoeuvring there is consistent with the abrasion, the compaction and
  the black primer-like residue. It does not on its own explain a 40-day
  pigment gradient, and the witness saw no vehicle.

---

## 5. Replication — soil (LDP spark-source mass spectrometry)

There are four result sheets, read from the page images: soil, plate 4571
(LDP p.5); deposit, plate 4571 (p.8); deposit, plate 4574 (p.11); soil, plate
4574 (p.14). The lab states the analysis is "semi-quantitative … à un facteur
trois près", with no sensitivity correction (p.4, p.7, p.10, p.13).
**[INFERRED]** that 4571 and 4574 are two plates of the same two samples. The
sample names are identical and the cover letter speaks of "deux échantillons"
(p.2).

- **Replicate disagreement.** Same soil, two plates: median |ratio| ×23,
  maximum ×154 (Ba). Fe is 2,240 ppm on one plate and 14.4% on the other. Rb is
  65 against 3,340. **23 of 24 quantified elements exceed the lab's own ×3
  tolerance.** The deposit replicates agree better (median ×3.3). Plate 4574
  also gives the soil 61% carbon, which is not physical for an argilo-calcareous
  soil (p.14). If the plates are *not* replicates, the alternative is that two
  different soils were both labelled "terre" without saying which is the
  control. That leaves the soil-versus-deposit contrast undefined.
- **Which elements are enriched?** The plate-wide offset (+0.27 dex on 4571,
  −0.66 dex on 4574) was removed first. The two plates then barely agree on
  which elements are enriched in the deposit (Spearman ρ = +0.30, P = 0.16).
  **Phosphorus is the only element enriched by more than ×3 on both** (×5.5 and
  ×20 after centring). A null that shuffles element labels on one plate gives
  1.16 such elements on average, and P(≥1) = 0.77. One consistent element is
  what chance produces.
- **Zinc** is 8.6 against 88 ppm on plate 4571, but on plate 4574 both values
  are upper bounds only (<140, <665). The zinc half of "zinc + phosphate primer"
  rests on one plate.
- **Iron** is not consistently enriched (×1.5, ×0.7). The Fe evidence comes
  from SNEAP's microprobe, which shows µm-scale Fe plated in the striations
  (SNEAP p.2; NT16 p.38). That is a spatial observation, not a bulk one, and
  is the stronger evidence of material transfer by friction.

**Verdict.** The mechanical evidence is from microscopy and microprobe and
needs no bulk chemistry: compaction, striations, a planed flint, Fe smeared on
grains, heating below 600 °C. The "primer paint" attribution rests on bulk
P/Zn readings whose replicate error is larger than the effect. It should be
quoted as LDP's hypothesis (LDP p.2), not as a finding.

---

## 6. Database null — does a reported trace predict class D?

Source: `data/raw/geipan/geipan_cases.json`, 3,404 cases, narrative field
`Détails`. Cases were classed POSITIVE (trace reported found), NEGATED
("aucune trace au sol…") or NONE. **Every POSITIVE and NEGATED hit was read.**
Nine were reclassified by hand, with reasons in `OVERRIDE`: five were
satellite or aircraft *ground tracks*, two generic sentences, two negation
misfires. Recall was not measured. Traces described in other words are in
NONE.

| class | n | D | D-rate |
|---|---|---|---|
| POSITIVE (trace found) | 17 | 2 | 0.118 [exact 95% 0.015, 0.364] |
| NEGATED (searched, none found) | 43 | 5 | 0.116 |
| NONE | 3,344 | 99 | 0.030 |

- **Found vs not found:** OR 1.01 (Fisher P = 1). Mantel–Haenszel over eras
  (≤1988 / 1989–2006 / 2007+) gives OR 1.14, P = 0.89.
- **Trace found vs everything else:** era-adjusted MH OR 2.35, CMH P = 0.25.
  Within-era label permutation, 20k: P = 0.24.
- **Searched (found or not) vs not mentioned:** crude OR 4.33 (P = 0.0023).
  **Era-adjusted MH OR 2.71, CMH P = 0.015.**

Whether a trace was *found* makes no measurable difference to the odds of D.
Whether anyone *searched the ground* does. This matches `HANDOFF §1.4`: D
means "adequate information", and a site investigation produces information.
**[INFERRED]** The physical-trace signal at archive level is an
investigation-effort signal. Trans-en-Provence is one of the two POSITIVE/D
cases; the other is Valensole 1965.

---

## 7. What would actually discriminate

1. **Sham-centre transect.** The single cheapest test the 1981 design lacked:
   identical sampling outward from a random point on the same terrace, same
   day. It cannot be done retroactively at this site. It is the
   protocol requirement for any future trace case.
2. **INRA's raw chromatograms.** INRA2 holds spectra and chromatogram figures
   (e.g. pp.12, 14, 17–22) but no replicate values. A request for the series-2
   replicate data, if any survive, would let §4.7 replace the analytical lower
   bound with a real interval. This is a candidate addition to
   `cada_request_draft.md`, drafted and not filed.
3. **LDP plate identity.** The question of whether 4571/4574 are replicate
   plates or different samples is answerable only from LDP's records. Without
   that answer §5 cannot be tightened.
4. **Compaction/trampling control.** A published dose–response for *Medicago*
   pigments under soil compaction would test the trampling alternative in §4.9
   directly against INRA's numbers. Not yet searched for.

---

## 8. Reproduce

```
python3 -I omega/tep_nt16_replication.py > omega/reports/tep_nt16_replication_out.txt
python3 -I omega/geipan_trace_null.py   > omega/reports/geipan_trace_null_out.txt
```
Deterministic: exact enumeration plus seeded Monte Carlo. Requires numpy and
scipy. Page images for re-checking any transcribed value: `pdftoppm -r 120 -f N
-l N -png <file>.pdf out` on the files in
`evidence_vault/02_GEPAN_PHYSICAL_TRACES/Trans-en-Provence_1981/geipan_trans-en-provence_1981-01-00849.tar.gz`.
