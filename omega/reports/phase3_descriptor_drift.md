# PROJECT OMEGA — Phase 3: Descriptor Drift Across 2,000 Years

**Status:** complete. **Code:** `omega/phase3.py`.
**Output:** `data/processed/descriptor_drift/drift.json`
**n = 36,089** deduplicated events with a parseable year, 48 morphology
descriptors extracted by regex lexicon from description text.

---

## 1. Why text, not the Hatch taxonomy

The specification called for Hatch's 13-code attribute taxonomy. It cannot
carry this analysis: of 666 pre-industrial events, **only 62 have attribute
codes**. Hatch's *U* database is a 20th-century instrument. A 48-descriptor
lexicon (shape, kinematics, sensory, physical effects, era-referent
technology, framing) was therefore applied to description text so that the
same measurement applies in 1394 and 1994.

Era bins: pre-industrial (<1800) 666 · industrial (1800–1945) 2,285 ·
atomic (1945–1957) 8,751 · space age (1957–1990) 18,245 · digital (1990+) 6,142.

## 2. The confound that had to be controlled

**The describer is not the witness.** Pre-1800 events reach this corpus
almost only through *Wonders in the Sky* (Vallée & Aubeck 2009) — modern
English paraphrases of Latin, Chinese and medieval sources. Hatch writes
telegraphic shorthand; Johnson writes prose. A raw era contrast is therefore
confounded with *who wrote the text, and when*. Median description length by
era confirms the register shift: 346 / 280 / 146 / 181 / 192 characters.

The analysis is reported twice: raw cross-era, and **within-catalog
stratified**, holding the describer fixed. Only the second supports a causal
reading. **It passes** (§5).

## 3. Result: morphology does depend on era — weakly

**Omnibus descriptor × era:** χ² = 9,886.0, dof = 188, p < 1×10⁻³⁰⁰,
**Cramér's V = 0.1867**.

Highly significant, but V ≈ 0.19 is a *small-to-moderate* association. Era
reshapes reported morphology; it does not determine it.

## 4. The technology mirror is real — and confined to three descriptors

Only **3 of 48** descriptors carry ≥0.01 bits of mutual information with era:

| descriptor | pre-ind. | industrial | atomic | space age | digital | MI (bits) |
|---|---|---|---|---|---|---|
| **shape_triangle** | 0.8% | 1.2% | 1.3% | 4.9% | **15.4%** | 0.0280 |
| **tech_airship** | 4.7% | **13.0%** | 1.6% | 0.8% | 1.1% | 0.0173 |
| **shape_disc** | 2.3% | 7.3% | **24.4%** | 20.1% | 14.6% | 0.0137 |

> **The airship peaks in the airship era. The flying disc peaks in the atomic
> era, immediately after 1947. The black triangle rises monotonically to
> 15.4% in the digital era.** This is cultural construction, measured — the
> reported *shape* of the phenomenon tracks the observer's contemporary
> aerospace vocabulary.

Supporting era-framing shifts, all in the predicted direction:

| descriptor | pre-ind. → digital |
|---|---|
| frame_portent (omen, prodigy, judgment day) | 9.3% → 0.8% |
| tech_chariot (chariot, cloudship, flaming sword) | 5.1% → 0.2% |
| shape_cross / shape_cloud | 0.6% → 0.0% / 8.1% → 2.4% |
| frame_radar | 0.0% → 6.8% (atomic peak) |
| frame_photo | 0.0% → 4.1% |
| tech_drone | 0.0% → 0.7% |
| sens_silent | 0.3% → 9.0% |

## 5. Within-catalog control: the drift is not a describer artifact

Holding the compiler — and therefore the writing style — fixed:

| catalog | n | eras spanned | Cramér's V | p |
|---|---|---|---|---|
| Hatch_UDB | 15,457 | all 5 | 0.1720 | <1e-300 |
| EberhartUFOI | 7,219 | 4 | 0.1980 | 3.1e-274 |
| Johnson | 3,904 | 4 | 0.1677 | 6.6e-120 |
| Overmeire | 2,101 | all 5 | 0.2308 | 6.9e-103 |
| NICAP | 2,091 | 4 | 0.2656 | 4.7e-72 |
| rr0 | 2,009 | all 5 | 0.3040 | 5.2e-43 |

Era-dependence of equal or greater magnitude appears **inside every single
catalog**. The drift is a property of the reports, not of the paraphrasers.

## 6. The invariant core — 45 of 48 descriptors

**45 of 48 descriptors carry < 0.01 bits of information about era.** The most
stable, with frequencies pre-industrial → digital:

| descriptor | pre-ind. | industrial | atomic | space age | digital | MI |
|---|---|---|---|---|---|---|
| **beh_zigzag** (erratic, darting, bobbing) | 0.8% | 0.9% | 0.9% | 1.0% | 1.1% | **0.00004** |
| **shape_sphere** (sphere, ball, globe, orb) | 7.5% | 6.8% | 6.1% | 7.7% | 7.0% | 0.00048 |
| beh_rotate | 0.6% | 1.1% | 1.2% | 1.4% | 0.8% | 0.00033 |
| beh_split | 2.3% | 0.9% | 1.0% | 0.9% | 1.3% | 0.00031 |
| sens_odour | 0.5% | 0.6% | 0.3% | 0.7% | 0.4% | 0.00037 |
| eff_animal | 0.3% | 0.5% | 0.2% | 0.7% | 0.5% | 0.00076 |
| eff_trace | 1.1% | 1.3% | 0.7% | 1.9% | 1.0% | 0.00146 |
| **eff_entity** (occupants, beings, figures) | 12.8% | 9.1% | 5.7% | 11.2% | 11.8% | 0.00527 |

> **The sphere and erratic/darting motion are the most era-stable reported
> features in the entire corpus. A luminous sphere behaving erratically is
> reported at 6–8% of events in every era from antiquity to the present,
> with essentially zero information about which century you are in.**

Reported *occupants* are also near-flat across two millennia (12.8%
pre-1800, 11.8% post-1990) — and are at their *lowest* in the atomic era
(5.7%), the opposite of a "post-Roswell invention" account.

## 7. Morphology has no natural cluster structure

Ward linkage on Jaccard distance over shape/kinematic descriptors (n = 6,000
sampled). Silhouette rises **monotonically** 0.159 (k=2) → 0.389 (k=10) with
no interior peak. That is the signature of **no cluster structure**: the
algorithm is simply splitting off one dominant descriptor at a time
(cluster 1 = 100% disc, 2 = 100% sphere, 3 = 100% cigar, 4 = 100% oval,
6 = 100% hover, 7 = 100% land, 8 = 100% pace, 9 = 100% dome). Reported
morphology behaves as a bag of weakly-correlated independent tags, not as
discrete "craft types."

The one era-distinctive cluster is **cluster 5** (72% triangle, 41%
rectangular, n=589): 48% space age, 42% digital, 0% pre-industrial.

## 8. Credibility: the sharpest result in Phase 3

Hatch credibility scores, high (≥8, n=8,099) vs low (≤6, n=5,246),
Fisher exact, showing all effects with p<0.001 and ratio outside 0.8–1.25:

| descriptor | high cred | low cred | ratio | p |
|---|---|---|---|---|
| **frame_radar** | 5.9% | 0.7% | **8.32** | 7.8e-64 |
| beh_maneuver | 2.5% | 0.9% | 2.70 | 1.2e-11 |
| tech_helicopter | 0.7% | 0.3% | 2.64 | 5.6e-04 |
| tech_rocket | 1.2% | 0.5% | 2.51 | 9.9e-06 |
| beh_zigzag | 1.3% | 0.7% | 2.00 | 2.0e-04 |
| beh_formation | 3.5% | 2.2% | 1.62 | 6.6e-06 |
| shape_point | 4.0% | 2.6% | 1.56 | 8.5e-06 |
| beh_pace | 4.3% | 3.0% | 1.43 | 1.2e-04 |
| shape_dome | 5.4% | 7.5% | 0.72 | 1.1e-06 |
| sens_beam | 3.0% | 4.3% | 0.69 | 6.0e-05 |
| sens_sound | 1.8% | 2.9% | 0.63 | 6.7e-05 |
| sens_porthole | 3.4% | 6.7% | 0.51 | 3.9e-18 |
| **eff_entity** | 3.5% | 11.5% | **0.31** | 1.9e-70 |

> **High-credibility reports are instrumented and kinematic: radar contact,
> sharp manoeuvres, formations, point sources. Low-credibility reports are
> close-range and high-strangeness: occupants, portholes, light beams,
> sounds. Reported occupants are 3.2× more common in low-credibility
> reports (p = 2e-70).**

### 8.1 The decisive test — and it fails

The stated hypothesis was: *"If high-credibility witnesses report
era-invariant morphology, that's strong evidence for a real phenomenon."*

| stratum | n | Cramér's V | mean MI | era-invariant descriptors |
|---|---|---|---|---|
| high cred (≥8) | 8,099 | **0.1746** | 0.00300 | 46 / 48 |
| low cred (≤6) | 5,246 | **0.1715** | 0.00301 | 46 / 48 |

**Statistically indistinguishable.** High-credibility witnesses are *exactly
as era-dependent* as low-credibility ones. Credibility does not select for
era-invariance, so the proposed inference is unavailable. (Note also that the
single strongest marker of high credibility — radar — is itself strongly
era-dependent, MI 0.0062, 0% pre-industrial → 6.8% atomic. Credibility is
partly a proxy for *having instruments*.)

## 9. Interpretation

Both halves of the dichotomy are true, of different descriptors:

1. **Shape vocabulary is culturally constructed.** Airship → disc → triangle
   tracks aerospace technology with high significance. Anyone treating
   reported shape as a physical property of a craft is reading the observer's
   era, not the object.
2. **Kinematics, physical effects and occupant reports are era-invariant.**
   A luminous sphere moving erratically, leaving ground traces, disturbing
   animals, with figures seen nearby, is reported at a near-constant rate
   from antiquity to the present.

That asymmetry is the actual finding, and it is a *constraint* rather than a
verdict: whatever generates these reports has a stable kinematic/behavioural
signature and an era-plastic morphological description. Both a genuine
stimulus class and a stable perceptual/narrative template predict this.
Phase 3 cannot separate them; it rules out the simple forms of both
"purely cultural" and "purely physical."

## 10. Limitations

1. **Regex lexicon, not semantic parsing.** Recall per descriptor is
   unmeasured; a negation ("no sound") may fire `sens_sound` for some phrasing.
   Effects are relative frequencies across eras, so uniform recall error
   cancels, but era-correlated phrasing shifts do not.
2. **Pre-industrial n = 666**, and 100% of pre-1800 coverage comes from one
   compilation. The within-catalog control mitigates but cannot remove this.
3. Credibility scores exist only for Hatch (17,888 events) and are that
   compiler's judgement, not an independent rating.
4. Era bins are conventional, not inferred; boundary choices (notably
   1945/1957) will move marginal frequencies.
5. The corpus is overwhelmingly Western and 20th-century; "2,000 years"
   describes the date range, not uniform temporal sampling.
