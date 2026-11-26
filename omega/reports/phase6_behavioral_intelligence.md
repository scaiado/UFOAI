# PROJECT OMEGA — Phase 6: The Behavioural-Intelligence Hypothesis, Tested Seven Ways

**Status:** complete. **Verdict: not supported.**
**Code:** `omega/phase6.py`, `omega/phase6_tests.py`.
**Data:** 18,116 Hatch records (the only subset with a behaviour taxonomy and
credibility scores), 63 attribute codes, 10 text-derived kinematic descriptors.

---

## 0. Two design decisions made before testing

**0.1 The verbosity confound, checked and largely cleared.** A verbose report
should attract more codes, which would manufacture observer×behaviour
associations. Measured: mean description length by code-count bin is 94 → 95 →
97 → 101 characters for 3–5, 6–8, 9–11, 12–14 codes. Code count is **not**
driven by description length in Hatch's data (he coded from source material,
not from his own summary). All nulls are still permuted within six code-count
strata.

**0.2 Interpretive vs observational codes.** Hatch's taxonomy mixes
observations (`LND` landed, `SUB` submerged, `VEH` vehicle affected, `RDR`
radar, `TRC` traces) with **adjudications of intent**: `PRB` "Probe: possibly
remote controlled", `CMF` "Camouflage/disguise", `SIG` "Signals/responses",
`TLP` "Telepathy". The latter are one compiler's inferences. Tests built on
them measure his coding process, and are labelled `[INTERPRETIVE]` throughout.

## 1. Results

| test | statistic | p | Bonferroni (α=0.00714) |
|---|---|---|---|
| **T1** behaviour × observer type | χ²=2299.9, dof=108, **V=0.1075** | <1e-300 | **SURVIVES** |
| **T2** observer-effect (chase→signal) | odds 0.69 | 0.997 | null |
| **T3** kinematic sequence structure | +0.2504 bits (**8.19%** of entropy) | 0.0005 | **SURVIVES** |
| **T4** goal-directed targeting | 26.13% vs 24.80% within 45° | 0.127 | null |
| **T5** shape vs kinematic era-MI | 0.00774 vs 0.00323 (2.40×) | 0.118 | null |
| **T6** PRB × credibility | ratio 1.02 | 0.698 | null |
| **T7** temporal clustering of IB events | Fano 7.84 vs null 8.04 | 0.722 | null |

**Five of seven fail outright. Two survive, and neither supports the
hypothesis.** Details below.

### T1 — significant, but the content is where the observer is standing

Cramér's V = 0.1075 — a *small* effect. Every large association is an
observation-opportunity artifact:

| observer | behaviour | n | odds | p |
|---|---|---|---|---|
| at sea | submerged/emerged | 76 | **17.87** | 0.0008 |
| on aircraft | landed | 49 | **0.17** | 0.0008 |
| civilian | sampling | 344 | 4.88 | 0.0008 |
| civilian | animals affected | 618 | 4.09 | 0.0008 |
| civilian | plants affected | 747 | 3.40 | 0.0008 |
| on aircraft | physical trace | 29 | 0.30 | 0.014 |
| civilian | landed | 2,896 | 2.98 | 0.0008 |
| high-quality obs. | conversation [INT] | 46 | **0.22** | 0.0008 |
| high-quality obs. | missing time | 88 | 0.31 | 0.0008 |
| high-quality obs. | abduction | 105 | 0.38 | 0.004 |
| scientist | physical trace | 74 | 2.52 | 0.005 |

You only see something enter the water if you are at sea. Pilots do not see
landings or ground traces. Ground civilians are the ones near crops and
livestock. Scientists are called in *for* traces. And high-quality observers
report *fewer* conversations, abductions and missing-time episodes — the Phase 3
credibility pattern again. **Nothing here is UAP behaviour conditioning on
observer type; it is observer position determining what is observable.**

### T2 — the observer-effect test fails, and its control explains why

`OBS` (observation/chasing) → `SIG` (signal exchange): **p = 0.997**. No
responsiveness.

The control is the informative part. If observer action genuinely elicited
behaviour, it should not equally predict things that *cannot* respond:

| action | outcome | odds | p |
|---|---|---|---|
| photographed | **shape: saucer** | **1.52** | 0.0012 |
| chasing | **shape: saucer** | **1.16** | 0.0012 |
| photographed | beam emitted | **0.51** | 0.008 |
| photographed | vehicle affected | **0.55** | 0.030 |
| photographed | sound | **0.61** | 0.039 |

Observer action predicts *shape class* as strongly as anything else — and a
shape cannot respond to being watched. Meanwhile photographing predicts
**fewer** dramatic behaviours, because photographed events are distant lights,
not close encounters. These are selection effects on which events get reported
and how, not responses.

### T3 — the one substantive positive, and its limit

Kinematic descriptor **order** within a single report, against a
within-report shuffle (the Phase 4D machinery):

| quantity | value |
|---|---|
| reports with ≥2 kinematic descriptors | 4,285 (9,842 tokens) |
| H(unigram) | 3.0563 bits |
| H(k₂\|k₁) observed | **2.5273 bits** |
| within-report shuffled null | 2.7777 ± 0.0085 |
| structure above null | **+0.2504 bits = 8.19% of channel entropy** |
| p | **0.0005** |

This is **13× the relative effect of the light-code result** (0.6%). Top
transitions: `fast→ascend` 3.81× (n=479), `hover→vanish` 2.36×, `turn→fast`
2.28×, `pace→turn` 2.19×, `ascend→descend` 2.07×, `hover→fast` 1.79× (n=595).

**Red Team — the MID control.** Hatch flagged 986 events `MID: Likely
mis-identification` (aircraft, balloons, meteors, stars). If the grammar is
narrative, it must appear there too:

| subset | n seq | structure | % of entropy | p |
|---|---|---|---|---|
| all | 4,285 | +0.2504 | 8.19% | 0.0008 |
| **MID (acknowledged misidentifications)** | 178 | **+0.1372** | **4.48%** | **0.0075** |
| not MID/HOX | 4,079 | +0.2528 | 8.27% | 0.0008 |
| high credibility (≥8) | 1,997 | +0.2453 | 8.05% | 0.0008 |
| low credibility (≤6) | 1,157 | +0.2643 | 8.78% | 0.0008 |

**The structure is present in objects Hatch himself identified as planes and
balloons**, at roughly half strength. It is also **credibility-independent**
(8.05% vs 8.78%), which is what a narrative convention looks like and not what
observational quality looks like.

At matched sample size (n=178), MID = 0.1342 bits vs non-MID 0.2463 ± 0.0705,
**p ≈ 0.050** — the residual difference sits exactly on the nominal threshold
and does **not** survive correction for this phase's seven tests.

The transitions name the mechanism: `hover → fast → ascend → vanish` is the
**grammar of departure** — the narrative and physical arc of any aerial object
leaving an observer's field of view, aircraft included.

### T4 — no targeting

1,389 usable (reported heading, nearest-facility bearing) pairs at 5–400 km.
Headings within 45° of the nearest military/missile facility: **26.13%
observed vs 24.80% null, p = 0.127**. Mean angular deviation **89.6°** against
a random expectation of 90.0°. The "UAP surveil our infrastructure" hypothesis
leaves no trace in reported headings.

### T5 — direction right, power insufficient

Shape codes mean era-MI 0.00774; kinematic descriptors 0.00323 — a **2.40×**
ratio in the direction Phase 3 predicted (top era-carriers: `DLT` triangle
0.0330, `SCR` saucer 0.0240). But group-label permutation gives **p = 0.118**
with only 10 descriptors per group, and one kinematic descriptor (`k_fast`,
MI 0.0194) breaks the clean separation. **Phase 3's shape/kinematics asymmetry
does not reach significance when tested formally.** I previously described it
as a finding; it is a direction, not a result.

### T6 — PRB flat; communication claims track credibility hard

`PRB` "possibly remote controlled": high 13.43% vs low 13.20%, ratio 1.02,
p = 0.698 — Hatch's own intelligence attribution is credibility-independent.
But:

| code | high cred | low cred | ratio | p |
|---|---|---|---|---|
| `RDR` radar | 6.32% | 0.53% | **11.99** | 7.4e-80 |
| `PHT` photographed | 5.58% | 3.20% | 1.74 | 5.5e-11 |
| `CVS` conversation [INT] | 0.39% | 3.84% | **0.10** | 1.3e-51 |
| `TLP` telepathy [INT] | 0.51% | 2.88% | **0.18** | 3.5e-29 |
| `ABD` abduction | 1.30% | 3.82% | 0.34 | 5.5e-21 |
| `LND` landed | 13.18% | 22.38% | 0.59 | 1.8e-43 |

**Claims of actual communication with the phenomenon are concentrated 5.6–10×
in low-credibility reports; instrumented detection is concentrated 12× in
high-credibility ones.** If intelligence were being observed, the observers
best placed to assess it report it least.

### T7 — no coordinated waves

Intelligence-attributed events (PRB/CMF/SIG/CVS/TLP, n = 4,225) have Fano
factor 7.84 in 30-day bins; all other events 41.73. Within-year label
permutation null: 8.039 ± 0.330, **p = 0.722**. Intelligence-attributed events
are **less** temporally clustered than ordinary ones, and their own clustering
is exactly at chance.

## 2. Verdict

> **The behavioural-intelligence hypothesis was tested seven ways and failed
> all seven.** Five tests returned outright nulls: no responsiveness to
> observation (p=0.997), no targeting of infrastructure (p=0.127, mean
> deviation 89.6° against 90° random), no era-separation of kinematics from
> shape (p=0.118), no credibility gradient in intelligence attribution
> (p=0.698), and no temporal coordination (p=0.722). The two significant
> results have identified content that is not behaviour: T1 is observer
> position determining what is observable (V=0.108; sea observers see
> submersions, pilots never see landings), and T3 is a departure grammar that
> reproduces in acknowledged aircraft and balloons at half strength and is
> independent of witness credibility.

## 3. The one thing worth pursuing

T3's residual — MID 0.1342 vs size-matched non-MID 0.2463 ± 0.0705, p ≈ 0.050 —
is the only quantity in Phase 6 that is both unexplained and in the
hypothesis-favouring direction. It fails correction at n=178. **The decisive
experiment is a larger acknowledged-misidentification control**: Project Blue
Book's identified cases (~11,500 of 12,618 were resolved) would give a control
set 60× larger than Hatch's MID flag and settle whether unexplained events
carry more kinematic structure than identified aircraft. That is a concrete,
public-records target.

## 4. Limitations

1. Hatch-only (18,116 of 36,129 events); the single-compiler coding is both
   the enabling feature and a single point of failure.
2. The kinematic descriptors are regex over telegraphic prose; recall is
   unmeasured, and "going quickly" is Hatch's own stock phrase, which may
   itself impose sequence regularity.
3. T4 takes the last compass term as the heading; Hatch's "south going quickly
   north" convention means some headings are origins, which adds noise and
   biases toward the null.
4. T5 has 10 descriptors per group — badly underpowered for a group-mean test.
5. `MID` is Hatch's judgement, not an independent identification.
