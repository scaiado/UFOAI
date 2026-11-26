# The undisclosed GEIPAN D cases are the re-examined ones

`omega/geipan_revisit_disclosure.py` · target list
`data/processed/geipan/cada_targets.json`

## Result

§1.3 established that D is the least documented arm — attachment share D
0.4528 vs A+B 0.9794, z=−25.83. That is a **marginal** statement about the
class. Crossing `Document pour cas` with `Cas revisité` **within class D**
localises it:

| | revisited | not revisited | total |
|---|---|---|---|
| has documents | 8 | 42 | **50** |
| **no documents** | **55** | **1** | **56** |

- revisit-rate among **undisclosed** D: **0.9821** (55/56)
- revisit-rate among **disclosed** D: **0.1600** (8/50)
- **z = +8.605**, risk ratio **6.14×**

**It is not an era artefact.** D cases skew old, and old files might simply be
less digitised — but the association holds *inside* every decade that has both
kinds of case:

| decade | n | undisclosed | revisit\|undisclosed | revisit\|disclosed |
|---|---|---|---|---|
| 1970s | 20 | 17 | 0.941 | 0.333 |
| 1980s | 19 | 12 | 1.000 | 0.571 |
| 1990s | 24 | 17 | 1.000 | 0.429 |
| 2000s | 9 | 7 | 1.000 | 0.000 |
| 2010s | 21 | 3 | 1.000 | 0.000 |

**Mantel-Haenszel odds ratio stratified by decade: 209.10.** An era artefact
would collapse this toward 1.0. It does the opposite — stratification
*strengthens* it, because the 1950s/60s/2020s strata that contribute no
undisclosed cases also contribute no counter-signal.

This is the fourth time in the project that a marginal result has been
stratified; §6 records one case where stratification collapsed the finding
(marginal-to-stratified collapse, failure mode #6). This one does not collapse.

## What it does NOT establish

**The direction of causation is undetermined.** Three readings fit the data
equally well, and nothing in the export distinguishes them:

1. **Re-examination withdraws documents.** A reopened dossier is pulled from
   publication while it is reprocessed.
2. **Missing documents cause re-examination.** You reopen the case you cannot
   resolve from the file you have.
3. **Both follow from a third thing** — e.g. the case was reopened under a
   procedure that re-scoped what may be disclosed.

Reading 2 is mundane and would make this an administrative artefact rather than
a disclosure finding. **It cannot be ruled out from the metadata.** Reading 1
and reading 3 are the ones that would matter, and separating them requires the
documents themselves — which is exactly what is unavailable.

Further caveats, stated plainly:

- **The semantics of `Cas revisité` are undocumented** in the export. The
  reading here is inferred from the French and from its distribution (flat
  ~5.0% across A/B/C, 59.4% in D — see the BAASS cross-check, §1).
- **n = 106.** One cell holds a single case. The z and the odds ratio are
  large, but the design is a cross-tabulation of two metadata fields, not an
  experiment.
- No claim is made about *why* any individual case is unpublished. Privacy
  redaction (CRPA L311-6) is a sufficient and entirely lawful explanation for
  any given file.

## How it connects to the rest

It supplies a mechanism that ties §1.3 to the BAASS result. BAASS counted
**205** D cases in mid-2009; the archive now holds **106**, with 2,104
post-2007 additions contributing only 31 D cases. GEIPAN reopened D cases,
reclassified roughly 99 of them out of D — and among those still in D, the
reopened ones are the ones whose dossiers are not published. Reclassification
and re-examination are plausibly one process observed through two fields.

It also **explains the power limit on the witness-level C-vs-D test.** Only 50
of 106 D cases carry any published document, so the test runs at 46 D vs 96 C
and will have a poor minimum detectable difference. The missing 56 are **not
missing at random** — they are the re-examined ones. The test is
power-limited by the very non-disclosure the project has now measured, and
that is itself the finding.

## CADA request

France's FOIA analogue. The 56 case IDs are enumerated in
`data/processed/geipan/cada_targets.json` with date, department, region,
coordinates and revisit flag. Draft letters:
`omega/reports/cada_request_draft.md`.

**Drafted, not filed** — per the standing constraints.
