# C-vs-D on witness-level text — item 2

Scripts: `omega/geipan_harvest.py`, `omega/geipan_pv_extract.py`,
`omega/geipan_cd_witness.py`, `omega/geipan_cd_seed_stability.py`.
Results: `data/processed/geipan_pv/cd_witness_result.json`.

## The question

§1.4 / failure mode #7: the C-vs-D test on `Détails` is unidentifiable. That
field is GEIPAN analyst prose written after classification, the leak changes
form at every decontamination tier, so the L5 residual is reported as an upper
bound, not as content. **Seed-averaged in session 4 to +0.1972 ± 0.0271**
(was +0.1795, a single draw at the 38th percentile of its own sampling
distribution). The "gradient never plateaus" clause is withdrawn: tier steps are
an order of magnitude below within-tier seed noise. See
`omega/reports/geipan_tier_seed_stability.md`.

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

| corpus | tier | n/arm | mean effect | sd | seeds p<0.05 | sign flips |
|---|---|---|---|---|---|---|
| `pv` gendarmerie | W3 length | 21–23 | +0.0259 | 0.039 | **0/24 (0%)** | yes |
| `pv` gendarmerie | W6 qual+length | 12–18 | +0.1008 | 0.059 | 10/24 (42%) | yes |
| `enquete` GEIPAN | W3 length | 18–20 | +0.1499 | 0.101 | 14/24 (58%) | no |
| `enquete` GEIPAN | W6 qual+length | 18–20 | **+0.2321** | 0.068 | **22/24 (92%)** | no |

`questionnaire` is flat at every tier (max 1.22σ, n_D=19).

### The positive control works

**`enquete` W6 is a stable, strong, detectable effect**: 22 of 24 matcher draws
significant, mean +0.2321, median +0.2393, **minimum +0.05, never negative**.
At n/arm ≈ 19 the instrument has ~92% empirical power on that corpus.

That is what makes the `pv` numbers interpretable rather than a shrug. The same
pipeline, the same tier machinery, the same permutation null and comparable arm
sizes detect a real signal 92% of the time in GEIPAN's analyst reports — and at
the most controlled tier give **less than half the effect (+0.1008 vs +0.2321)
and 42% instead of 92%** in gendarmerie procès-verbaux. At W3 the gap is wider
still: 0% versus 58%.

**Ordering is consistent at both tiers: analyst prose > witness prose, by
2.3× at W6 and ~5.8× at W3.**

### But `pv` is not a clean null

W6 at 42% of draws significant with mean +0.1008 is not nothing. So the correct
statement is **not** "witness text carries no C/D signal". It is: *C/D is
robustly discriminable from GEIPAN's own analyst reasoning and only weakly and
unstably from the gendarmerie's record of what was seen, under identical
measurement.* Whether a smaller genuine witness-level effect exists is not
settled by 28 cases.

Note also that within `pv`, adding quality-matching **raised** the effect
(W3 +0.0259 → W6 +0.1008) while n/arm fell 22 → 16. Either a second suppression
or a small-n artefact; this corpus cannot tell them apart.

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

**PAID, session 4** — `omega/geipan_tier_seed_stability.py`,
`omega/reports/geipan_tier_seed_stability.md`.

§1.4's L4 (+0.2176) and L5 (+0.1795) were single length-matched draws with one
seed. This section's ±0.1 spread was the right diagnosis, and a second seed
dependency it did not name turned out to be larger: `balanced_cv_acc(seed=11)`
downsamples the 1,020-case C arm to 106, so **all six tiers** rested on a
single draw, not just the two matched ones.

24 joint seeds per tier (both seeds varied):

| tier | was | now |
|---|---|---|
| L4 | +0.2176 | **+0.2135 ± 0.0276** (42nd pctile — representative) |
| L5 | +0.1795 | **+0.1972 ± 0.0271** (38th pctile — a low draw) |

The residual **rose**. Leakage fraction fell from "51%" to 42% ± 9%. And the
ladder's adjacent tiers proved indistinguishable — within-tier range 0.094–0.113
against tier steps of 0.016–0.020.

## Disposition

- **Positive control established.** `enquete` W6: mean +0.2321, 22/24 draws
  significant, never negative, at n/arm ≈ 19. The instrument detects real signal
  at these sample sizes, so the weaker `pv` numbers are a measurement rather
  than an absence of measurement.
- **The contrast is the result.** Analyst prose separates C from D 2.3–5.8×
  more strongly than witness prose under identical treatment. This supports
  §1.4's core claim — that the analyst-prose signal is about the analyst — while
  leaving open whether a smaller witness-level effect exists.
- **`pv` is not a demonstrated null.** W3 is robustly null (0/24) but W6 is not
  (42%). 28 D cases cannot resolve an effect of the +0.197 size that matters.
- **The ceiling is disclosure, not method.** 28 of 106 D cases carry a PV, and
  §1.10 showed the 56 undisclosed D dossiers are the re-examined ones. The CADA
  request is the way to raise the power — `omega/reports/cada_request_draft.md`,
  56 named case IDs — not further tiering of this corpus.
- **§1.4 needs re-running with seed-averaged matching** before its L4/L5 numbers
  are quoted again. See the debt section above.
