# GEIPAN: the official-disposition corpus, and what it does to the T3 control

**Status:** complete. All figures reproducible from `omega/geipan*.py`.
**Data acquired 2026-11-26** from `www.geipan.fr` (allowlisted), honest user agent,
no credential use, no access-control circumvention. Bulk export is a published
endpoint the site links from its own search page.

---

## 1. What was retrieved

| Artifact | Endpoint | Result |
|---|---|---|
| Complete case database | `/fr/cnes/export/cas` | 1,857,770 B XLSX → **3,404 cases**, 19 fields |
| Trans-en-Provence dossier | `/fr/cas/1981-01-00849` | **11 documents, 14.4 MB, 172 pages** |
| Case-page document pattern | `/sites/default/files/<name>` | all dossier files fetchable |

The export was reachable from a link on GEIPAN's own case-search page
(`href="/fr/cnes/export/cas"`). The earlier conclusion that GEPAN/GEIPAN was
"entirely absent" was true of archive.org and false of the live site.

**Note:** document PDFs linked from the *portal* pages live on `www.geipan.fr`
(reachable). A second host, `www.cnes-geipan.fr`, serves current forms and is
**blocked by this environment's network policy** (proxy 403). Nothing needed for
this analysis was behind it.

### Schema (19 fields, all populated)

`ID Etude de Cas · Titre du Cas · Détails · Année · Identification ·
Classification · Code département · Observation date · Department ·
Document pour cas · Cas contenant des documents · Nouveau cas · Cas revisité ·
Latitude · Longitude · Phenomenon · Region · Temoignage associé · Type de cas`

Coordinates present on **3,404/3,404** cases. Years 1937–2026.

### Why this corpus matters more than its size suggests

GEIPAN is the only state UAP programme that publishes its complete case file
**with the official disposition attached to every case**, and its scheme splits
what Blue Book conflated:

| Class | Meaning | n |
|---|---|---|
| A | identified, certain | 955 |
| B | probably identified | 1,323 |
| C | unidentified **for lack of** information | 1,020 |
| D | unidentified **despite adequate** information | **106** |

Blue Book's "unidentified" bucket mixed C and D. GEIPAN separates them, holding
agency, era, country, language, investigator and write-up convention fixed. That
makes the decisive comparison available for the first time in this project: a
ground-truth denominator.

---

## 2. GEPAN Note Technique No. 16 — the primary source

`CT/GEPAN-00013` · `ENQUETE 81/01` · *ANALYSE D'UNE TRACE* ·
**NOTE TECHNIQUE No 16** · 1 March 1983 · ISSN 0750-6694 · 67 pp.
Case `1981-01-00849`, TRANS-EN-PROVENCE (83), 8 January 1981, **classified D**.

Complete dossier retrieved (page counts from the files):

| File | pp | Content | Text |
|---|---|---|---|
| `Note techn16-R.pdf` | 67 | the Note Technique itself | 109,615 chars |
| `Analyses2 INRA-R.pdf` | 60 | INRA biochemistry, full series | image-only |
| `PV n°28 (1981308305).pdf` | 11 | gendarmerie procès-verbal | image-only |
| `Analyse LDP-R.pdf` | 16 | LDP laboratory | 16,564 |
| `Analyses DER-R.pdf` | 5 | DER (EDF research) | 7,301 |
| `Analyses INRA-R.pdf` | 4 | INRA summary | 2,902 |
| `Analyses SNEAP-R.pdf` | 3 | SNEAP | 3,458 |
| `Photos-R.pdf` | 3 | site photography | image-only |
| `ALAT-R.pdf` | 2 | Army light aviation (helicopter check) | 4,464 |
| `Meteo-R2.pdf` | 1 | meteorology | 2,758 |

### 2.1 Soil — §6.2, *Synthèse des analyses de sol*

Four findings, in GEPAN's own words:

> « une forte pression mécanique a été exercée (probablement due à un choc) en
> surface »

> « l'apparition d'une modification de structure superficielle du sol (stries et
> érosion) »

> « un échauffement thermique du sol, peut-être consécutif au choc, dont la
> valeur n'a pas excédé 600° »

> « un éventuel apport de matériaux sous forme de traces décelables sur les
> échantillons analysés tel qu'une faible quantité de fer ou d'oxyde de fer sur
> grain de calcaire, et une faible quantité décelée de phosphate et de zinc »

The 600 °C ceiling is derived, not assumed: the CaCO₃ grains are not
"foisonnants", so no dissociation-and-recombination occurred.

**The line that is almost never quoted.** GEPAN's own summary table gives the
spark-mass-spectrometry interpretation as:

> « Trace laissée sur le sol pouvant provenir d'un revêtement primaire
> (peinture) ayant été frotté »

and the visual/microprobe interpretation as:

> « Corps de masse importante ayant frotté le sol, et laissé un dépôt »

That is a **heavy painted object scraping the ground** — the laboratory's own
leading reading, printed in the report, and mechanically sufficient for every
soil finding above.

### 2.2 Vegetation — §7.5, INRA biochemistry

Author: the INRA Laboratoire de Biochimie; GEPAN reproduces his text verbatim
as §§7.1–7.5. Still measurable **40 days** after the event:

> « l'équipement pigmentaire chlorophyllien et caroténoïdien est affaibli de
> 30 à 50% en formes actives et enrichi en formes inactives ou dégradées. Les
> jeunes feuilles subissent la perte la plus importante au niveau du β carotène
> (-57%) et de la violaxanthine (-80%!) »

> « il existe des corrélations quantitatives entre les perturbations observées
> et la distance des prélèvements au centre du "phénomène" »

**And the radiation hypothesis, tested and rejected in the primary document.**
The INRA author benchmarked the pigment losses against γ-irradiated
*Arabidopsis thaliana* (Bös 1973), finding that 10⁶ rads are needed to produce
equal or *lesser* damage — then ruled the mechanism out on spectroscopic
grounds:

> « L'action du rayonnement nucléaire ne présente donc pas d'analogie avec celle
> de la source énergétique impliquée dans le phénomène observé. Par contre, une
> intensification spécifique de la transformation des chlorophylles en
> phéophytines et des chlorophyllides en phéophorbides (par perte de Mg++)
> pourrait être liée à l'action d'un champ énergétique de type électrique. »

This bears directly on two live threads in this project. It is an independent,
quantitative, primary-source rejection of an ionising-radiation mechanism at the
best-characterised physical-trace site on record — relevant to the Phase 2
nuclear-proximity falsification and to the fallout-fogging alternative raised
against arXiv:2604.00056. The proposed mechanism is **Mg²⁺ loss under an
electric field**, which is a testable chemistry claim, not a physics-flavoured
gesture.

### 2.3 GEPAN's own conclusion — §8

The report does **not** claim confirmation. Verbatim:

> « Au plan pédologique les conditions particulières du terrain ne permettaient
> guère une appréciation quantitative précise de masse, de pression,
> d'échauffement »

> « Les interprétations possibles (choc, frottement...) restent cependant trop
> diverses et vagues pour que l'on puisse considérer qu'elles fournissent une
> confirmation définitive des narrations du témoin. »

> « l'absence de preuve n'étant pas, là non plus, la preuve de l'absence, ceci
> ne suffit pas à certifier la véracité du témoignage. »

> « les connaissances actuelles sur les traumatismes que peuvent subir les
> végétaux, restent trop parcellaires pour que l'on puisse fournir dès à présent
> une interprétation précise et unique à ce remarquable faisceau de résultats. »

The famous case's own investigating agency recorded: a large-amplitude
mechanical-plus-thermal event, real distance-graded biochemical gradients, a
leading laboratory interpretation of *rubbed paint from a heavy mass*, and an
explicit refusal to treat any of it as confirming the witness account.

---

## 3. The disposition analyses

### 3.1 The unexplained residue fell 3.78× — and the cause is in the data

| Era | n | D-rate | C-rate | A+B rate |
|---|---|---|---|---|
| pre-1977 | 145 | 0.0621 | 0.6207 | 0.3172 |
| 1977–1988 | 628 | 0.0525 | 0.4666 | 0.4809 |
| 1989–2006 | 473 | 0.0698 | 0.3996 | 0.5307 |
| **2007+** | **2,158** | **0.0144** | **0.2076** | **0.7780** |

D-rate ≤1988 vs 2007+: 0.0543 → 0.0144, **diff +0.0400, z = +6.119,
p = 9.44 × 10⁻¹⁰, ratio 3.78×**. C-rate 0.4955 → 0.2076 (z = +15.24,
p = 2.0 × 10⁻⁵²). A+B 0.4502 → 0.7780 (z = −16.93, p = 2.5 × 10⁻⁶⁴).

Not caseload dilution: Spearman(annual caseload, D-rate) = −0.1295, p = 0.360
over 52 years.

**What changed is the explanation toolkit.** Top identified causes:

| pre-1989 A+B | n | 2007+ A+B | n |
|---|---|---|---|
| *cause not recorded* | 212 | **Lanterne thaï** | **417** |
| Vénus | 18 | Avion | 93 |
| Lune | 15 | **ISS** | **79** |
| Rentrée atmosphérique | 14 | Bolide | 68 |
| Météoroïde | 10 | Ballon | 64 |
| Avion | 7 | Avion de ligne | 57 |
| | | Vénus | 49 |
| | | Satellite | 47 |

The single largest category of modern French UAP reports is **sky lanterns** — a
consumer product absent from France before roughly 2005, trivially identifiable
once an investigator knows to look for it. Saying "that was the ISS at 21:43"
requires pass-prediction databases that did not exist in 1978; the 2012
Draguignan case in this very corpus is resolved by an attached `Calsky passage
ISS.pdf`.

This is the strongest version of the "residue tracks investigator capability"
claim I have been able to construct, and it is measured on official state
dispositions rather than catalogue prose. **It does not show the phenomenon
changed. It shows the toolkit did.**

### 3.2 The D arm is the least documented arm — and it survives stratification

Share of cases with documents attached:

| Era | D | A+B | C | D−(A+B) | p |
|---|---|---|---|---|---|
| pre-1977 | 1.000 (9) | 1.000 (46) | 1.000 (90) | 0.000 | — |
| 1977–1988 | **0.152** (33) | 0.993 (302) | 0.993 (293) | −0.842 | 3.5 × 10⁻⁵⁸ |
| 1989–2006 | **0.242** (33) | 0.992 (251) | 0.989 (189) | −0.750 | 2.5 × 10⁻⁴³ |
| 2007+ | 0.839 (31) | 0.974 (1,679) | 0.991 (448) | −0.136 | 5.8 × 10⁻⁶ |

Marginal −0.5265 (z = −25.83); **D-size-weighted within-era −0.5351**. No
Simpson reversal — the stratified estimate is slightly *larger*.

So: the 106 cases the French state says are genuinely unexplained are, in the
two middle eras, precisely the cases whose underlying documents are **not
published** (15–24% vs ~99%). This is a measured, not asserted, limit on
public-record verification, and it converts directly into a CADA request
(France's FOIA analogue) naming specific case IDs. It also closes 2007+, where
the deficit shrinks to −0.136 — the publication practice changed, not the
classification.

Trans-en-Provence is one of the documented minority, which is part of why it
dominates the literature: it is the D case that can be audited.

---

## 4. The C-vs-D test, and failure mode #7

The obvious test: both C and D are officially unidentified, so does the narrative
of a D case differ from a C case? If "strangeness" is real, this is where it
lives.

It took five decontamination tiers to find out what that test measures, and the
answer is a new failure mode.

> **SEED-AVERAGED, session 4.** The single-draw figures first published here
> are superseded. Each tier below is the mean of 24 seeds; see
> `omega/reports/geipan_tier_seed_stability.md`. **Adjacent tiers are not
> distinguishable** — within-tier range across seeds is 0.094–0.113 while the
> whole L0→L5 decay is 0.142, so no single tier step carries information.

| Tier | what is removed | **seed-averaged effect** | range | superseded single draw |
|---|---|---|---|---|
| L0 | nothing (raw) | **+0.3387 ± 0.0229** | 0.094 | +0.3494 |
| L1 | sentences naming GEIPAN or a class | **+0.2771 ± 0.0300** | 0.109 | +0.3019 |
| L2 | + verdict lexicon | **+0.2628 ± 0.0318** | 0.109 | +0.3113 |
| L3 | + all analyst-reasoning sentences | **+0.2333 ± 0.0308** | 0.113 | +0.2643 |
| L4 | + conjugated leak forms, **length-matched** | **+0.2135 ± 0.0276** | 0.109 | +0.2176 |
| L5 | + every numeral and quantity word | **+0.1972 ± 0.0271** | 0.104 | +0.1795 |

Balanced design, 106 per arm, 5-fold CV. 24 seeds per tier, 200
label-permutation nulls per draw. **24/24 seeds reach p<0.05 at every tier** —
the separation's existence never depended on a seed; only its magnitude was
overprecise. The L1 > L2 inversion in the original table was noise: seed-averaged
the ladder is monotone.

**Each tier found more leakage, and the leak changed form each time:**

1. **L0→L1: the verdict is in the text.** Every narrative ends with it —
   `« Le GEIPAN classe ce cas en D : Phénomène étrange à très étrange / de
   consistance moyenne à forte »`, against
   `« Le GEIPAN classe de cas en C : manque de précisions »`. D narratives:
   59.4% contain *non identifié/inexpliqué* vs 9.3% of C. C narratives: 32.1%
   contain *manque d'informations/précisions* vs **0.0%** of D.

2. **L3→L4: the verdict survives conjugated.** `manquons` appeared in 163/1,017
   C cases and **0/106** D cases; `informations` 179 vs 3; `récent` 56 vs 0. My
   L2 lexicon caught the noun and missed the verb.

3. **The A+B-vs-D comparison is circular and is withdrawn, not fixed.** Its top
   discriminators are the *names of the explanations*: `lanternes` 254/2,271 vs
   **0/106**, `lanterne` 92 vs 0, `bolide` 87 vs 0, `iss` 72 vs 0, `vénus` 121
   vs 1, `ballons` 92 vs 0, `lâcher` 95 vs 0. A resolved narrative states its
   cause; an unresolved narrative cannot. Stripping every cause-noun would
   delete the content of the resolved arm itself, so this test cannot be
   repaired — only abandoned.

4. **L4→L5: the leak reappears as measurement density.** Toward D:
   `estimée` 12/106 vs 2, `mètres` 26 vs 12, `secondes` 42 vs 20, `environ` 36
   vs 16, `masse`, `disparaître`. Toward C: `angulaire` 2 vs 9, `faible` 9 vs
   26, `courte`, `rien`, `peut`, `ans`. D narratives contain *quantities*; C
   narratives contain *hedges and absences*. But "the narrative contains
   quantities" **is** the operational meaning of "adequate information" — the
   criterion that separates D from C. Length alone reached 0.6321.

### Verdict

**42% ± 9% of the raw effect is identifiable leakage (+0.3387 → +0.1972). A
residual of +0.1972 ± 0.0271 survives everything I could strip.** Both figures
are seed-averaged over 24 draws; the originally published 51% and +0.1795 came
from single draws, and the +0.1795 sat at the 38th percentile of its own
sampling distribution.

I am not reporting that residual as event content — but **the "gradient has not
plateaued" argument is withdrawn.** Tier-to-tier steps (L3→L4 = 0.020,
L4→L5 = 0.016) are an order of magnitude below within-tier seed noise (0.094–
0.113), so the apparent continuing decay was not measurable. The reason the
residual is not content is different and stronger: the criterion separating C
from D *is* informational adequacy, so no stripping rule can remove from the
text a property defined on the text. The correct reading is an **upper bound** — the true
content difference between GEIPAN's data-poor and anomalous arms is *at most*
+0.18 on balanced accuracy, and plausibly less, with the test confounded in a
way that cannot be fully removed from analyst prose.

This is neither the null I expected nor a positive. It is a third outcome, and
it earns a place beside the six failure modes already documented:

> **Failure mode #7 — criterion-definitional confounding.** When the arms of a
> comparison are *defined by* information content, and the measured text *is*
> the information, no amount of lexical decontamination identifies the
> comparison. Leakage does not sit in a fixed vocabulary you can delete; it
> migrates — verdict sentence → verdict lexicon → conjugated verb → cause noun →
> measurement density → narrative length. Each strip reveals the next layer.

**Relation to Blue Book T3.** T3 returned null at adequate power (p = 0.2727,
MDD 0.1169 vs a 0.112 target) and identified a 7× gradient from compiler prose
(+0.2504) to case record (+0.0354). GEIPAN does not contradict that; it explains
it. The Blue Book compiler-prose effect of +0.2504 sits squarely inside the
GEIPAN leakage range (+0.18 to +0.35), and the GEIPAN tiers show *what the
compiler-prose effect is made of*.

**How to actually run this test.** Not on analyst summaries. On witness-level
text written before or independently of the verdict: questionnaires,
gendarmerie procès-verbaux, laboratory reports. Those are in the dossiers, and
the dossiers are now fetchable — a harvest of all 106 D cases plus a 120-case
matched C sample is running. That is the first version of this test with a
chance of being identified.

---

## 5. Reproduction

```bash
python3 -I omega/geipan.py              # load, class distribution, G1-G3
python3 -I omega/geipan_t3.py           # balanced permutation test
python3 -I omega/geipan_decontam.py     # tiers L0-L3
python3 -I omega/geipan_t3_final.py     # tiers L4, L5
python3 -I omega/geipan_harvest.py      # dossier harvest (D arm + matched C)
```

Outputs under `data/processed/geipan/`. Raw data and dossiers under
`data/raw/geipan/`.
