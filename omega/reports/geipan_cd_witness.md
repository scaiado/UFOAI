# C-vs-D on witness-level text — item 2

Scripts: `omega/geipan_harvest.py`, `omega/geipan_pv_extract.py`,
`omega/geipan_cd_witness.py`, `omega/geipan_cd_seed_stability.py`.
Results: `data/processed/geipan_pv/cd_witness_result.json`.

## The question

§1.4 / failure mode #7: the C-vs-D test on `Détails` is unidentifiable. That
field is GEIPAN analyst prose written after classification, the leak changes
form at every decontamination tier, and the gradient never plateaus — so the
L5 residual of **+0.1795 is reported as an upper bound, not as content.**

The intended fix was text written before or independent of the verdict:
gendarmerie procès-verbaux from the dossiers.

## What the corpus turned out to be

Harvest: 146 of 150 target cases, 290 files. But the document classes are not
what their filenames suggest. Measured on the OCR'd text:

| class | n | GEIPAN/CNES header | gendarmerie | verdict language |
|---|---|---|---|---|
| `enquete` | 37 | **34 (92%)** | 18 (49%) | **34 (92%)** |
| `pv` | 38 | 9 (24%) | **35 (92%)** | 23 (61%) |
| `questionnaire` | 25 | **24 (96%)** | 2 (8%) | **24 (96%)** |

A *Compte rendu d'enquête* is GEIPAN's **own** investigation report — CNES
letterhead, numbered sections; one in this corpus is dated **07/06/2024 for a
2018 observation**. *Questionnaire technique* is likewise a GEIPAN instrument.
Only the procès-verbal is authored outside GEIPAN and before its verdict.

Had this gone unchecked the test would have separated the arms on documents
containing the verdict, looked like a result, and been failure mode #7 again.

**Attrition:** 106 D cases → 50 with any published document → 46 with usable
witness text → **28 with a gendarmerie PV**, against 51 C. §1.10 established
that the 56 D cases with no published dossier are the **re-examined** ones, so
the missing 78 are not missing at random.

## One pipeline, because the alternative tracked the label

Extraction OCRs everything through tesseract `-l fra` at 300 dpi and never uses
the embedded text layer as text. Reason, measured — share of documents carrying
an embedded text layer by decade:

| 1950s | 1960s | 1970s | 1980s | 1990s | 2000s | 2010s | 2020s |
|---|---|---|---|---|---|---|---|
| 0% | 0% | 19% | 38% | 79% | 69% | 77% | **95%** |

D cases skew older (§1.3: D-rate 0.0548 in the 1970s vs 0.0155 in the 2010s), so
"pdftotext first, OCR if short" would have split the corpus along a line almost
perfectly correlated with the class label — structurally the cross-pipeline
defect that falsified the persistence result.

Final: 223 documents, 222 usable, **4,310,567 chars**.

## Premise checks

**The §1.4 leak is genuinely gone.** `manquons` — 163/1017 C vs 0/106 D in
analyst prose — is **0/28 D and 0/51 C** in the PVs. `gendarmerie` appears in
89%/84%, confirming provenance. A residual asymmetric leak exists (`geipan` 29%
D vs 8% C; `cnes` 39% vs 12%), which W1/W2 strip.

**OCR quality does not track the label** (z=+1.258). **Length emphatically
does**: D PVs median 1,353 tokens vs C 691, z=+3.431 — the information-adequacy
confound, since D means *unexplained despite adequate information*.

## Result — the like-for-like comparison

Single-draw tiers are unreliable here (see below), so the load-bearing numbers
are the **24-seed** distributions at a fixed tier.

**W3, length-matched, 24 matcher seeds:**

| corpus | n/arm | mean effect | sd | seeds p<0.05 | sign flips |
|---|---|---|---|---|---|
| `pv` gendarmerie | 21–23 | **+0.0259** | 0.039 | **0/24 (0%)** | yes |
| `enquete` GEIPAN | 18–20 | **+0.1499** | 0.101 | **14/24 (58%)** | no |

At the same tier, same transformation, comparable arm sizes: **GEIPAN's analyst
reports discriminate C from D; gendarmerie procès-verbaux do not.**

`questionnaire` is flat at every tier (max 1.22σ, n_D=19).

## Suppression — and it inverts the expectation

In `enquete` the effect is **invisible unmatched** (W0 +0.0667, p=0.1331) and
appears only once length is controlled (W3 mean +0.150; the single main-run
draw reached +0.2607 at 2.80σ, the only above-MDD row in 21 tiers, corroborated
by W4 +0.2381 and W6 +0.2393).

D enquête reports run 2,526 tokens against C's 1,291. The length difference was
**masking** a discriminating vocabulary, not creating one.

So: **controlling length in analyst prose reveals signal; controlling length in
witness prose removes it.** That is the opposite of the confound pre-registered
for this test, and the opposite of §1.4's finding in `Détails`.

## Corrections to this session's own reporting

**Single matched draws were unrepresentative in both directions.** Enquête W3's
headline +0.2607 sits near the **maximum** of its 24-seed range (+0.3429); the
typical draw is +0.125. PV W3's −0.0444 sits at the **minimum** of its range;
the typical draw is +0.024. Both were read as point estimates. Enquête is
therefore **not** a clean positive control — it is a real but modest and
variable effect, significant in 58% of pairings.

**Significance and power were conflated in the first version of the script.**
MDD here is 2.485σ (80% power at one-sided α=0.05); the significance threshold
is ~1.645σ. An effect between them is *significant but underpowered*, not
"indistinguishable from null". PV W0 (+0.1621, p=0.0017, 2.12σ) was briefly
mislabelled a null. Fixed; `tier()` now returns a three-way disposition.

**"The tier sequence carries no gradient information" was too strong.** Seed
noise at a fixed tier spans 0.136 (PV W3); the main run's tier-to-tier spread is
0.211. Seed noise accounts for most but not all of it. The accurate statement:
**no gradient can be read from one draw per tier.**

## Debt this creates for §1.4

§1.4's **L4 tier (0.7176, +0.2176) was a single length-matched draw with one
seed**, and the L5 residual of +0.1795 — the project's stated upper bound on
content — rests on the same single-draw matching. If matched tiers vary by ±0.1
across seeds, those point estimates carry uncertainty the handoff does not
record. **Length-matched tiers need seed-averaging; the existing ones were not
averaged.** This should be re-run before §1.4's numbers are quoted further.

## Disposition

- **Not a demonstrated null for witness text, and not a content result either.**
  The PV corpus is robustly null at W3 (0/24 seeds significant) but PV W6 is
  not (mean +0.1008, 10/24 significant, n/arm 12–18), so the corpus is not
  uniformly empty and double-matching may select an odd subset.
- **The honest ceiling is set by disclosure, not by method.** 28 of 106 D cases
  carry a PV; the MDD runs 0.19–0.27 against §1.4's 0.107 and against the
  +0.1795 effect size of interest. The test is power-limited by the
  non-disclosure measured in §1.10, which is itself the finding.
- **The CADA request is the way to raise the power**, not further tiering of
  this corpus: `omega/reports/cada_request_draft.md`, 56 named case IDs.
