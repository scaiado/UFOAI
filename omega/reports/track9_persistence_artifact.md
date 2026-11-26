# PROJECT OMEGA — Track 9: Ancient–Modern Persistence (and failure mode #5)

**Status:** tested with 7× the power of Phase 4B. **Verdict: artifact.**
**Code:** `omega/geocode_wits.py`, `track9.py`, `track9b.py`, `track9c.py`, `track9d.py`
**Outputs:** `data/processed/persistence/track9{,_final,b_density_controlled}.json`

---

## 1. The power problem, solved

Phase 4B could use **47** geocoded pre-1800 events, and the result inverted when
the window widened — a textbook underpowered artifact. *Wonders in the Sky*
(Vallée & Aubeck) was geocoded through Nominatim: 363 distinct location strings,
**229 resolved (63%)**, giving **335 geocoded pre-1880 events**, of which 140 sit
in countries with ≥3 events in both eras. A **7× increase** in the historical arm.

## 2. Three nulls, each better than the last

| null design | 25 km | 50 km | 100 km | 200 km |
|---|---|---|---|---|
| within-country only | 1.250 (p=0.0010) | 1.051 (0.187) | 0.998 (0.529) | 1.058 (0.034) |
| + density stratified **at 100 km** | 1.168 (0.0077) | 0.990 (0.624) | 0.977 (0.909) | 1.049 (0.0057) |
| + density stratified **at the test radius** | **1.188 (0.0003)** | **1.077 (0.0057)** | 1.013 (0.225) | 1.019 (0.043) |

The second design was self-refuting and is recorded as such: matching density at
100 km forces the 100 km result to ≈1.0 by construction, so the surviving
signals at 25 km and 200 km were simply the scales not matched. Matching at the
**test radius** fixed it — and produced the first properly monotonic decay in
this project: **1.188 → 1.077 → 1.013 → 1.019**, with two radii surviving
Bonferroni (α=0.0125).

Density strata were built from an **independent random half** of the modern
events, so the stratification is non-circular.

At that point this was the first result in Project Omega to survive a
well-constructed null, show coherent spatial decay, and not reduce to any of the
four previously identified failure modes. It then got the hardest red team yet.

## 3. The red team — shared-centroid geocoding convergence

The two arms are geocoded by **different pipelines onto the same kind of
target**:
- historical → Nominatim place-name lookup → settlement centroid
- modern → Hatch's arcminute DMS of a place name → settlement centroid

If both resolve the same town to the same point, any historical and modern event
naming that town becomes near-coincident **by construction**.

**Distance from each historical event to its nearest modern event:**

| band | n | share |
|---|---|---|
| 0–1 km | 17 | 12.1% |
| 1–2 km | 35 | 25.0% |
| 2–5 km | 31 | 22.1% |
| 5–10 km | 18 | 12.9% |
| 10–25 km | 24 | 17.1% |
| >25 km | 15 | 10.7% |

**Median 3.2 km. Minimum 0.092 km.** **52 pairs (37.1% of historical events) lie
within 2 km, and 90% of those share a place-name token with their match.**

The pairs are self-explanatory:

```
0.872 km  Reims, France            <->  REIMS, FR
1.580 km  Thann, Alsace, France    <->  THANN, HT RHIN, FR
1.129 km  London, England          <->  LONDON
1.423 km  Uxbridge, England        <->  UXBRIDGE, LONDON
1.168 km  Paris, France            <->  PARIS, FR
0.173 km  Nice, France             <->  NICE, FR
0.781 km  Metz, France             <->  METZ, FR
0.780 km  Besançon, France         <->  BESCANCON, FR
1.083 km  Boston, Massachusetts    <->  BOSTON, MA
0.486 km  Edinburgh, Scotland      <->  EDINBURGH, SCOTLAND
0.627 km  Goult, Vaucluse, France  <->  NEAR GOULT, FR
```

> **This is not geographic persistence of a phenomenon. It is place-name
> persistence.** Both corpora record events at notable, still-extant
> settlements — chroniclers and antiquarians wrote where literate institutions
> were; modern witnesses live where people live — and two independent geocoders
> agree on where those settlements are. The measured effect is the agreement of
> the geocoders.

Per-country medians confirm it: France 2.5 km (98% within 25 km), United Kingdom
2.8 km (94%), United States 2.9 km (75%). The top "persistent" locations are
Oxford ×4, London ×3, Uxbridge, Gunnersbury.

## 4. Why the obvious repair is also invalid

Excluding sub-5 km pairs leaves 25 km nominally alive (ratio 1.163, p=0.0030, on
57 events) while 50 km goes null (0.960, p=0.83) — the monotonic decay is gone.
More importantly, **that exclusion conditions on the outcome**: historical events
are selected by their distance to the nearest modern event, which is the
quantity under test. The repair is statistically inadmissible and its result
should not be cited, including by me.

**Conclusion: the catalog pair cannot separate phenomenon persistence from
place-name persistence.** Doing so requires historical events geocoded to
sub-settlement precision from primary sources — not place-name lookup.

## 5. Failure mode #5: cross-pipeline geocoding convergence

A new kind, distinct from the four before it:

| # | failure mode | first seen |
|---|---|---|
| 1 | contamination — the comparison table's rows inside the catalogs | Phase 2 (nuclear) |
| 2 | underpowered artifact — reverses as n grows | Phase 4B (persistence) |
| 3 | self-referential source events — the corpus holds the claim's founding cases | Phase 5 (ICBM/Mar 1967) |
| 4 | narrative convention — structure reproduces in acknowledged aircraft | Phase 6 T3 (kinematics) |
| 5 | **cross-pipeline geocoding convergence** — two geocoders agreeing on a centroid masquerades as spatial co-location | **Track 9** |

Plus three *nulls* withdrawn as invalid: global class-label permutation across
disjoint geographic footprints (Track 4), density matching at the wrong scale
(Track 9b), and outcome-conditioned subsetting (Track 9 §4).
