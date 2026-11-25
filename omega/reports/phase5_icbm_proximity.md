# PROJECT OMEGA — Phase 5: ICBM / Launch-Facility Proximity Test

**Status:** complete — **the claim does not survive the placebo test.**
**Code:** `omega/phase5.py`, `omega/phase5b.py` (red team).
**Output:** `data/processed/icbm_proximity/phase5.json`

---

## 1. Two constraints discovered before testing

**1.1 Individual silo coordinates are unobtainable here.** `overpass-api.de`
and `overpass.kumi.systems` both fail through this session's egress proxy
(`ws_closed_mid_exchange` on every attempt, including a backgrounded retry
loop across nine per-wing bounding boxes). Host access was granted; the
transport fails.

**1.2 It matters less than it appears, because the *sighting* coordinates are
the binding constraint.** The catalog's coordinates carry 6 decimal places
(17,058 of 17,823), which is spurious: the paired field reads
`LatLongDMS: 45:45:00 N 04:52:00 E` → `45.750002, 4.866667`. Hatch geocoded
**place names** to arcminute DMS and converted. Effective accuracy is
~2–20 km depending on how the place was specified ("TUCSON, AZ" vs
"NNW / NELLIS AIR FORCE BASE"). **The requested 10 km window is below the
resolution of the data**, independent of silo coordinates. Windows run
25–500 km; a 10 km ring is reported in the radius profile for completeness
only.

Facility layer: 9 ICBM wings by main-base coordinates (public, ~0.01°) with
documented activation/deactivation years — Malmstrom, Minot, Grand Forks,
Ellsworth, Whiteman, F.E. Warren (Minuteman/Peacekeeper), Davis-Monthan,
McConnell, Little Rock (Titan II).

**Control group: 12 SAC bomber/tanker bases** (Barksdale, Dyess, Fairchild,
Castle, Westover, Loring, Plattsburgh, Griffiss, Pease, Carswell, Offutt,
Travis). Military, high-security, nuclear-armed, **no silo fields**. This
isolates "missile field" from "military base," the confound that would
otherwise consume the entire result.

Decontamination as in Phase 2: 186 events removed whose text references
missile/silo/ICBM/SAC/nuclear. Clean n = 16,532.

## 2. Three tests of increasing strength

| test | null | result |
|---|---|---|
| **T1** operational-period excess | year labels permuted, locations fixed | **null** |
| **T2** activation-event excess | within-year conditional date permutation (Phase 2 design) | **null** |
| **T3** difference-in-differences | missile fields vs SAC bases, pre/post 1963 | **nominally positive** |

### T1 — operational-period excess (decontaminated)

| radius | obs | exp | ratio | p |
|---|---|---|---|---|
| 25 km | 39 | 47.6 | 0.820 | 0.973 |
| 50 km | 62 | 65.1 | 0.952 | 0.739 |
| 100 km | 116 | 120.6 | 0.962 | 0.754 |
| 200 km | 273 | 312.2 | 0.874 | 0.999 |
| 500 km | 933 | 1047.3 | 0.891 | 1.000 |

No excess during operational periods at any radius. Ratios ≤ 1.

### T2 — activation-event excess (decontaminated, 15 windows)

Every window null. Largest ratio 1.38 (50 km/90 d, obs = 1). Counts at
25–100 km and ±30–90 d are **zero**. No burst around activation.

### T3 — difference-in-differences (decontaminated)

| radius | M_pre | M_post | C_pre | C_post | DiD | 95% CI | p |
|---|---|---|---|---|---|---|---|
| 25 km | 13 | 23 | 29 | 30 | 1.710 | [0.72, 4.35] | 0.287 |
| **50 km** | 15 | 37 | 67 | 64 | **2.582** | **[1.29, 5.42]** | **0.0081** |
| 100 km | 38 | 63 | 157 | 203 | 1.282 | [0.82, 2.03] | 0.306 |
| 200 km | 91 | 133 | 298 | 332 | 1.312 | [0.97, 1.80] | 0.087 |

(All-events stratum, 50 km: DiD = 3.09 [1.61, 6.69], p = 0.0009 — survives
Bonferroni α = 0.00208.) The radius profile decays properly:
3.04 (10 km) → 2.73 (40) → 2.58 (50) → 1.68 (75) → 1.28 (100) → 1.26 (300 km).
Restricting both groups to the US interior *strengthens* it
(100 km DiD = 3.98, p = 0.0004).

**On its face this is a positive result for the facility claim.** It is not.

## 3. Red Team — three attacks, one fatal

### 3.1 Placebo activation years — FATAL

The identical DiD, re-run with counterfactual "activation" years:

| cut year | 50 km | 100 km | 200 km |
|---|---|---|---|
| 1951 | 0.93 (p=0.86) | 0.85 (0.52) | 0.54 (0.0002) |
| 1955 | 0.47 (0.043) | 0.82 (0.47) | 0.85 (0.32) |
| 1959 | 1.08 (0.79) | 1.08 (0.70) | 1.23 (0.14) |
| **1963 (TRUE)** | **2.58 (0.0081)** | 1.28 (0.31) | 1.31 (0.087) |
| **1967 (placebo)** | **2.38 (0.0136)** | **2.10 (0.0013)** | **1.69 (0.0009)** |
| 1971 | 0.77 (0.49) | 0.72 (0.20) | 0.82 (0.24) |
| 1975 | 0.72 (0.39) | 0.67 (0.14) | 0.72 (0.049) |
| 1979 | 0.40 (0.13) | 0.46 (0.069) | 0.58 (0.022) |

**A placebo cut at 1967 — when nothing was activated — produces an effect as
strong as, and at 100/200 km stronger than, the true 1963 activation.** The
statistic is not responding to activation.

### 3.2 What it is responding to

Annual counts within 100 km, decontaminated:

| year | 1963 | 1964 | 1965 | 1966 | **1967** | 1968 | 1969 |
|---|---|---|---|---|---|---|---|
| near ICBM | 0 | 0 | 8 | 9 | **37** | 3 | 3 |
| near SAC | 8 | 18 | 39 | 47 | 46 | 17 | 6 |

The control bases show an ordinary 1965–67 flap. The ICBM region shows a
**1967 spike 4× its 1966 value**, and **March 1967 alone contributes 13 of
the 37 events.**

### 3.3 Excluding 1967 annihilates the effect

| radius | DiD with 1967 | DiD excluding 1967 | p |
|---|---|---|---|
| 50 km | 2.582 | **1.726** | 0.224 |
| 100 km | 1.282 | **0.684** | 0.217 |
| 200 km | 1.312 | **0.906** | 0.594 |

## 4. Conclusion — and the second circularity

> **The ICBM-facility proximity signal is entirely the March 1967
> Minot/Malmstrom cluster.** Operational-period and activation-event tests are
> flat null. The difference-in-differences result is nominally significant but
> fails a placebo test (a fake 1967 activation performs as well or better) and
> disappears when a single year is removed.

March 1967 is precisely the Echo Flight / Oscar Flight period from which the
missile-facility claim originates. **A hypothesis cannot be confirmed by the
observations that generated it.** The 13 March-1967 records are the claim's
source, not independent corroboration of it — and 22 of the 37 contributing
events are single-sourced Hatch records.

This is a *different* circularity from Phase 2. There, the comparison table's
own rows had been copied into the UAP catalogs. Here the catalog contains the
hypothesis's founding events and nothing else that bears on it. Both times the
corpus contained the hypothesis rather than evidence for it.

**What this does NOT establish.** It does not refute the Malmstrom incidents.
Those are a documentary question about specific March 1967 events, and this
catalog holds only thin single-sourced traces of them. The correct statement is
narrower and more useful: **the catalog cannot test the facility claim,
because the only events producing a signal are the ones the claim is made of.**

## 5. What would actually test it

The facility claim requires records the catalog does not contain:

1. **Project Blue Book case files, March 1967**, Minot and Great Falls (Malmstrom) — NARA RG 341, microfilm rolls covering Jan–Jun 1967.
2. **341st Strategic Missile Wing and 91st SMW unit histories, 1966–68** — AFHRA, Maxwell AFB. Unit histories are routinely declassified and are the primary record of Echo/Oscar Flight.
3. **Missile-maintenance and Unsatisfactory Report logs** for the affected flights — these would show whether guidance-system dropouts occurred and what was recorded as the cause.
4. **An ICBM launch-facility coordinate set** (START treaty data exchange, or OSM via a working transport) to permit a silo-level rather than wing-level test — though note §1.2: sighting-location accuracy caps the achievable resolution at ~20 km regardless.

## 6. Limitations

1. Facility coordinates are main-base locations, not silo fields; silo fields
   disperse 30–120 km around each base, so the 25 km ring is partly an
   artifact of base-centroid placement.
2. Activation/deactivation years are encoded to year precision from published
   wing histories, not from primary documents.
3. Control bases were selected by the analyst as nuclear-armed non-silo SAC
   installations; a different control set would move the DiD.
4. Cell counts in the decisive 50 km DiD are small (15 / 37 / 67 / 64).
5. The test is US-only. Soviet, French, Chinese and British missile fields are
   not represented, and the corpus's non-US geocoding is sparse.
