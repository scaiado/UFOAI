# Paying the §1.4 seed-averaging debt

*Project Omega, session 4. §5 item 1. Script:
`omega/geipan_tier_seed_stability.py`. Data:
`data/processed/geipan/geipan_tier_seed_stability.json` (L4/L5, all three
sweeps) and `..._FULL6.json` (all six tiers).*

---

## The debt

§1.4 published the C-vs-D decontamination ladder as six effects and read it as a
decay gradient, with the L5 residual **+0.1795** adopted as the project's upper
bound on content. Every one of those six numbers was a **single draw**.

There were **two** seed dependencies, not the one §5 identified:

1. **Matcher seed** — `geipan_t3_final.length_matched(data, tol=0.12, seed=5)`
   pairs each D case to a random length-eligible C case. `seed=5` was a default
   nobody varied. Affects L4, L5.
2. **Downsample seed** — `balanced_cv_acc(..., seed=11)` shuffles each arm and
   keeps `m = min(arm sizes)`. The C arm holds 1,020 cases and D holds 106, so
   **every unmatched tier rests on a 106-of-1,020 draw decided by one integer.**
   Affects L0–L3, and rides on top of the matcher draw at L4/L5.

The second was not in the handoff's statement of the debt. It is the larger
exposure, because it touches all six tiers rather than two.

24 seeds per sweep, 200 permutations per draw.

## Corrected ladder

| tier | §1.4 single draw | **seed-averaged** | range across seeds | published draw's percentile |
|---|---|---|---|---|
| L0 raw | +0.3494 | **+0.3387 ± 0.0229** | 0.0939 | 62nd |
| L1 class sentences out | +0.3019 | **+0.2771 ± 0.0300** | 0.1085 | 79th |
| L2 + verdict lexicon | +0.3113 | **+0.2628 ± 0.0318** | 0.1085 | 92nd |
| L3 + analyst reasoning | +0.2643 | **+0.2333 ± 0.0308** | 0.1133 | 79th |
| L4 + conjugated, len-matched | +0.2176 | **+0.2135 ± 0.0276** | 0.1089 | 42nd |
| L5 + numerals/quantities | **+0.1795** | **+0.1972 ± 0.0271** | 0.1041 | 38th |

L0–L3 are downsample sweeps (unmatched tiers have no matcher seed). L4/L5 are
**joint** sweeps, varying both seeds together.

### Why a joint sweep was necessary

The two marginal sweeps disagreed at L5, because each holds the *other* seed at
its published value and the published value is a low draw on both axes:

| L5 sweep | mean ± sd |
|---|---|
| matcher varied, CV fixed at 11 | +0.2077 ± 0.0275 |
| CV varied, matcher fixed at 5 | +0.1848 ± 0.0197 |
| **both varied (the estimate)** | **+0.1972 ± 0.0271** |

The joint mean falls between the marginals, as it should. Neither marginal is
the estimate; quoting either would have substituted one arbitrary choice for
another.

## Four corrections

**1. The L5 residual rises. +0.1795 → +0.1972 ± 0.0271.**
The published figure sat at the 38th percentile of the joint distribution — a
low draw. The project's upper bound on content was *understated*, not inflated.

**2. "51% of the effect is identifiable leakage" → 42% ± 9%.**
Recomputed from the seed-averaged endpoints: 1 − 0.1972/0.3387 = 0.418, with
uncertainty propagated from both sds. Less of the raw effect is attributable to
identifiable leakage than §1.4 claimed.

**3. L4 needs no correction.** +0.2176 against a joint mean of +0.2135 ± 0.0276,
at the 42nd percentile. That draw was representative.

**4. The §1.4 L1 → L2 inversion was noise.** §1.4 had L2 (+0.3113) *above* L1
(+0.3019), which invited explanation. Seed-averaged, L1 (+0.2771) sits above L2
(+0.2628) and the ladder is monotone. There was nothing to explain.

## The finding that matters more than any single number

**Adjacent tiers are not distinguishable.** Within-tier range across seeds is
0.094–0.113. The entire L0 → L5 decay is 0.142. So:

- L3 → L4 = 0.0198
- L4 → L5 = 0.0163

Both are **an order of magnitude smaller than the noise in either tier.** Only
the endpoints separate. The ladder supports "stripping identifiable leakage
roughly halves the effect" and supports nothing finer. Any reading that treats a
single tier step as evidence — that the gradient "has not plateaued", for
instance — is reading noise.

**What is robust: 24/24 seeds reach p<0.05 at every one of the six tiers.** The
existence of the residual separation never depended on a seed. Only its
magnitude was overprecise, and the direction of the error was to overstate the
decay — the published ladder drew high at L1 (79th), L2 (92nd) and L3 (79th) and
low at L5 (38th), steepening the apparent gradient from both ends at once.

## Inventory correction

§5 item 1 stated that +0.1795 is quoted in `HANDOFF.md`,
`omega/reports/baass_ten_month_report.md`,
`omega/reports/geipan_trans_en_provence.md` and `omega/reports/dird_corpus.md`.
**The last three do not cite it.** A tree-wide search for `0.1795`, `0.2176`,
`0.6795` and `0.7176` returns `HANDOFF.md`, `HANDOVER_PROMPT.md`,
`geipan_acquisition_and_disposition.md`, `geipan_cd_witness.md`,
`geipan_cd_witness.py`, and the stored JSON. Those are what this session
corrected.

## Interpretation, restated for the record

The GEIPAN C-vs-D separation survives every decontamination tier that could be
built, at **+0.197 ± 0.027**, with 24/24 seeds significant. Roughly 42% of the
raw +0.339 is identifiable leakage. The residual remains an **upper bound on
content**, not a measurement of it — not because the gradient failed to plateau
(that reading is withdrawn; tier steps are below noise) but because the
criterion separating C from D is *itself* informational adequacy, and no
stripping rule can remove a property defined on the text from the text.
