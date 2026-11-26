# 08 — SATELLITE ANOMALIES / Track 2

**Status: CONTROL SET BUILT. DETECTION NOT RUN — by design.**

## Why the order is the whole point

§5 item 5 states the standing design constraint: the matched-landcover control
set must exist *before* detection. §6 records five claims this project falsified
whose entire effect was an absent or wrong control:

- nuclear proximity — 0.6% of records produced 100% of a 13× effect
- ICBM proximity — the 1967 Minot/Malmstrom cluster **is** the claim's founding data
- sacred-site proximity — megalith ratio 1.004, p=0.56
- persistence — a cross-pipeline geocoding artefact
- BAASS Northern Tier — catalogue events within 300 miles of SAC bases, no control at all

Detection-first-controls-later is how all five happened. **A control set chosen
after seeing the candidate imagery is not a control set.**

## What does not exist

The brief referred to "SKYWATCH T0/T1 candidate events". **No such dataset
exists in this repository** — zero mentions anywhere in `omega/`. §5 item 5
records Track 2 as *"requested repeatedly, never started"*. The candidates used
are the **top 10 Phase 9 sites** named in §5, which do exist.

## A correction made during construction

The first run screened controls against **NUFORC alone** and concluded 6 of 10
sites testable, with the French and Réunion sites at a perfect 1.00. That was an
artefact. NUFORC is US-reported, so a French location passes a NUFORC screen by
having **no NUFORC coverage**, not by having no sightings. Measured within 100 km:

| site | NUFORC | GEIPAN | union |
|---|---|---|---|
| Valensole | 1 | **280** | 281 |
| Trans-en-Provence | 5 | **224** | 229 |
| La Réunion | 0 | 44 | 44 |
| Rendlesham | 51 | 0 | 51 |
| Socorro | 78 | 0 | 78 |
| Newark Valley | 658 | 0 | 658 |

**A control screen whose coverage tracks the geography being screened is not a
screen.** Both catalogues are now unioned: 127,175 points (NUFORC 123,771 +
GEIPAN 3,404). Rejections rose 68 → 83.

## The control set

All **10 of 10** candidates have Sentinel-2 L2A coverage at <20% cloud, same
calendar month, 2019–2024. **59 control points accepted, 83 rejected** for
having their own sighting history within 15 km.

Matched on: landcover proxy (spectral), latitude band, calendar month, cloud
cover <20%, separation 50–400 km (far enough not to share the locale, near
enough to share ecoregion and sensor track), and no sighting history.

| site | eligible | rejected | ring | frac | verdict |
|---|---|---|---|---|---|
| La Réunion | 8 | 0 | 8 | 1.00 | **TESTABLE** |
| Rendlesham Forest | 8 | 3 | 11 | 0.73 | **TESTABLE** |
| Socorro / Zamora | 8 | 5 | 13 | 0.62 | **TESTABLE** |
| Trans-en-Provence | 8 | 6 | 14 | 0.57 | **TESTABLE** |
| Saint-Mathias | 8 | 8 | 16 | 0.50 | **TESTABLE** |
| Valensole | 8 | 8 | 16 | 0.50 | **TESTABLE** |
| Cherry Creek | 4 | 13 | 17 | 0.24 | NOT CONTROLLABLE |
| Cash-Landrum | 3 | 12 | 15 | 0.20 | NOT CONTROLLABLE |
| Lavonia | 2 | 13 | 15 | 0.13 | NOT CONTROLLABLE |
| Newark Valley | 2 | 15 | 17 | 0.12 | NOT CONTROLLABLE |

## The structural finding

**Controllability is inversely proportional to local sighting density, and four
of ten sites cannot be controlled at all.** Newark Valley has 658 sightings
within 100 km and yields 2 clean controls from 17 candidates; Cash-Landrum has
887 and yields 3 from 15.

This is the mechanism behind §6's falsified proximity claims, made measurable.
Those claims were US-centric, and **in the US sighting field a candidate's
neighbourhood already has reports** — so there is no comparison ground. The
claim "UAP cluster near X" is close to unfalsifiable by this route in populated
US regions, not because analysts were careless but because the reporting field
saturates the control space.

**The corollary is actionable:** run Track 2 detection on the six testable sites
first, and report the four others as *not controllable* rather than as null.
Trans-en-Provence is among the testable six, which is convenient — it is also
the only physical-trace class-D case with full laboratory analysis.

## Honest limits

- `eligible` counts clean points on a 50–400 km ring with a **15 km** exclusion
  radius. A site can yield clean ring points while its own 100 km
  neighbourhood is dense; the two measures answer different questions and both
  are reported.
- Landcover matching is currently a **spectral proxy** via Sentinel-2 scene
  availability, not a classified landcover product. A true match needs a
  landcover raster (e.g. ESA WorldCover), which is not on the allowlist.
- No detection has been run. `track2_control_set.json` carries
  `"detection_run": false`.
