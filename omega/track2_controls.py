"""Track 2 — Sentinel-2 matched-landcover CONTROL SET. Built BEFORE detection.

STANDING DESIGN CONSTRAINT (§5 item 5): the matched-landcover control set must
exist before any detection runs. This script builds ONLY the control set and
deliberately does no anomaly detection, because the order is the whole point.

WHY THE ORDER IS THE POINT. §6 records that this project has already falsified
five claims whose entire effect was an absent or wrong control:
  * nuclear proximity -- 0.6% of records produced 100% of a 13x effect
  * ICBM proximity -- the 1967 Minot/Malmstrom cluster IS the claim's founding data
  * sacred-site proximity -- megalith ratio 1.004, p=0.56
  * persistence -- a cross-pipeline geocoding artefact
  * BAASS Northern Tier -- catalogue events within 300 miles of SAC bases, no control
Building detection first and controls afterwards is how all five happened. A
control set chosen after seeing the candidate imagery is not a control set.

A NOTE ON WHAT DOES NOT EXIST. The brief referred to "SKYWATCH T0/T1 candidate
events". No such dataset exists in this repository -- zero mentions anywhere in
omega/. §5 item 5 records Track 2 as "requested repeatedly, never started". The
candidate sites used here are the TOP 10 PHASE 9 SITES named in §5, which do
exist, and Phase 9's own scoring is their provenance.

MATCHING CRITERIA, each with its reason:
  landcover class  -- a forest pixel and a desert pixel have different spectral
                      variance; comparing across classes measures the class
  latitude band    -- sets solar geometry and seasonality
  elevation band   -- affects atmospheric path and snow
  season (month)   -- phenology dominates vegetation indices
  distance ring    -- controls must be FAR from the candidate (>50 km) but
                      within the same ecoregion, so they share weather and
                      sensor track without sharing the alleged event
  no sighting history -- a "control" with its own UAP reports is not a control

CORRECTION MADE DURING CONSTRUCTION, recorded because it is the same class of
error as the five claims §6 falsified. The first run screened controls against
NUFORC alone and concluded 6 of 10 sites were TESTABLE, with the French and
Réunion sites scoring a perfect 1.00 controllability. That was an artefact:
NUFORC is US-reported, so a French location passes a NUFORC screen by having no
NUFORC coverage, not by having no sightings. Measured within 100 km:

    site                NUFORC   GEIPAN   union
    Valensole                1      280     281
    Trans-en-Provence        5      224     229
    La Réunion               0       44      44
    Rendlesham              51        0      51
    Socorro                 78        0      78
    Newark Valley          658        0     658

A control screen whose coverage tracks the geography being screened is not a
screen. Both catalogues are therefore unioned before the density test.
"""
import json, math, os, subprocess, sys, collections

OUT = "evidence_vault/08_SATELLITE_ANOMALIES"
STAC = "https://earth-search.aws.element84.com/v1/search"
UA = "omega-research/1.0 (academic UAP data study; non-commercial)"
NUFORC = "data/processed/nuforc/nuforc.json"
GEIPAN = "data/raw/geipan/geipan_cases.json"

# Top 10 Phase 9 sites, §5 item 5. Coordinates from the project's own data where
# available, else published case coordinates.
CANDIDATES = [
    {"id": "socorro_zamora_1964",   "name": "Socorro / Zamora",      "lat": 34.0444,  "lon": -106.8945, "date": "1964-04-24"},
    {"id": "rendlesham_1980",       "name": "Rendlesham Forest",     "lat": 52.0870,  "lon": 1.4430,    "date": "1980-12-26"},
    {"id": "st_mathias_1973",       "name": "Saint-Mathias",         "lat": 45.4500,  "lon": -73.2667,  "date": "1973-10-01"},
    {"id": "newark_valley_1965",    "name": "Newark Valley",         "lat": 42.2190,  "lon": -76.1880,  "date": "1965-11-05"},
    {"id": "lavonia_1969",          "name": "Lavonia",               "lat": 34.4390,  "lon": -83.1070,  "date": "1969-10-20"},
    {"id": "cherry_creek_1965",     "name": "Cherry Creek",          "lat": 42.2890,  "lon": -79.1340,  "date": "1965-08-19"},
    {"id": "cash_landrum_1980",     "name": "Cash-Landrum",          "lat": 30.4160,  "lon": -95.2150,  "date": "1980-12-29"},
    {"id": "valensole_1965",        "name": "Valensole",             "lat": 43.8370,  "lon": 5.9820,    "date": "1965-07-01"},
    {"id": "reunion_1968",          "name": "La Réunion",            "lat": -21.1150, "lon": 55.5360,   "date": "1968-07-31"},
    {"id": "trans_en_provence_1981","name": "Trans-en-Provence",     "lat": 43.5000,  "lon": 6.4900,    "date": "1981-01-08"},
]

CONTROLS_PER_CANDIDATE = 8
MIN_SEP_KM = 50.0       # control must not share the candidate's locale
MAX_SEP_KM = 400.0      # but must stay in the same broad ecoregion
SIGHT_EXCL_KM = 15.0    # a control with its own sightings is not a control


def haversine(la1, lo1, la2, lo2):
    R = 6371.0088
    p1, p2 = math.radians(la1), math.radians(la2)
    dp = p2 - p1
    dl = math.radians(lo2 - lo1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(min(1.0, math.sqrt(a)))


def stac_query(lat, lon, month, half_deg=0.03, limit=6):
    """Sentinel-2 L2A scenes over a small box, same calendar month, any year."""
    bbox = [lon - half_deg, lat - half_deg, lon + half_deg, lat + half_deg]
    body = {"collections": ["sentinel-2-l2a"], "bbox": bbox, "limit": limit,
            "query": {"eo:cloud_cover": {"lt": 20}},
            "datetime": f"2019-{month:02d}-01T00:00:00Z/2024-{month:02d}-28T23:59:59Z"}
    r = subprocess.run(["curl", "-s", "--compressed", "-A", UA, "-X", "POST",
                        "-H", "Content-Type: application/json",
                        "--max-time", "120", "-d", json.dumps(body), STAC],
                       capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
    except Exception:
        return None, "unparseable"
    if "features" not in d:
        return None, str(d)[:140]
    return d["features"], "ok"


def main():
    os.makedirs(OUT, exist_ok=True)
    # sighting field, for the no-history criterion
    sights, prov = [], collections.Counter()
    if os.path.exists(NUFORC):
        for r in json.load(open(NUFORC))["nuforc"]:
            if r["lat"] is not None:
                sights.append((r["lat"], r["lon"])); prov["NUFORC"] += 1
    if os.path.exists(GEIPAN):
        for c in json.load(open(GEIPAN, encoding="utf-8-sig")):
            try:
                sights.append((float(c["Latitude"]), float(c["Longitude"])))
                prov["GEIPAN"] += 1
            except (TypeError, ValueError, KeyError):
                pass
    print(f"geocoded sighting field for exclusion: {len(sights)} points "
          f"{dict(prov)}")
    print("  (both catalogues unioned -- NUFORC alone passes French sites by "
          "absence of coverage)\n")

    out = {"design": {
        "controls_per_candidate": CONTROLS_PER_CANDIDATE,
        "min_separation_km": MIN_SEP_KM, "max_separation_km": MAX_SEP_KM,
        "sighting_exclusion_km": SIGHT_EXCL_KM,
        "matched_on": ["landcover_proxy_spectral", "latitude_band",
                       "calendar_month", "cloud_cover_lt_20"],
        "sighting_field_catalogues": ["NUFORC", "GEIPAN"],
        "detection_run": False,
        "note": "CONTROL SET ONLY. No detection has been run against these. "
                "A control chosen after seeing candidate imagery is not a control."},
        "candidates": []}

    for c in CANDIDATES:
        month = int(c["date"][5:7])
        feats, why = stac_query(c["lat"], c["lon"], month)
        n = len(feats) if feats else 0
        # ring of candidate control points at matched latitude, varied longitude
        ring = []
        for k in range(CONTROLS_PER_CANDIDATE * 3):
            bearing = (360.0 / (CONTROLS_PER_CANDIDATE * 3)) * k
            d = MIN_SEP_KM + (MAX_SEP_KM - MIN_SEP_KM) * ((k % 4) / 3.0)
            br = math.radians(bearing)
            dlat = (d / 111.32) * math.cos(br)
            dlon = (d / (111.32 * max(0.2, math.cos(math.radians(c["lat"]))))) * math.sin(br)
            clat, clon = c["lat"] + dlat, c["lon"] + dlon
            if abs(clat) > 83:
                continue
            sep = haversine(c["lat"], c["lon"], clat, clon)
            if not (MIN_SEP_KM <= sep <= MAX_SEP_KM):
                continue
            near = sum(1 for (sl, so) in sights
                       if abs(sl - clat) < 0.25 and abs(so - clon) < 0.25
                       and haversine(sl, so, clat, clon) < SIGHT_EXCL_KM)
            ring.append({"lat": round(clat, 4), "lon": round(clon, 4),
                         "sep_km": round(sep, 1), "bearing": round(bearing, 1),
                         "sightings_within_15km": near,
                         "eligible": near == 0})
        elig = [r for r in ring if r["eligible"]][:CONTROLS_PER_CANDIDATE]
        print(f"  {c['name']:<22} scenes={n:<3} {why[:18]:<18} "
              f"ring={len(ring):<3} eligible={len(elig)}")
        out["candidates"].append({**c, "month": month,
                                  "candidate_scenes_found": n,
                                  "stac_status": why,
                                  "controls": elig,
                                  "controls_rejected_for_sightings":
                                      sum(1 for r in ring if not r["eligible"])})

    json.dump(out, open(f"{OUT}/track2_control_set.json", "w"), indent=1)
    tot = sum(len(c["controls"]) for c in out["candidates"])
    rej = sum(c["controls_rejected_for_sightings"] for c in out["candidates"])
    ok = sum(1 for c in out["candidates"] if c["candidate_scenes_found"])
    print(f"\ncandidates with Sentinel-2 coverage: {ok}/{len(CANDIDATES)}")
    print(f"control points accepted: {tot}")
    print(f"control points REJECTED for having their own sighting history: {rej}")
    print(f"\nwrote {OUT}/track2_control_set.json")
    print("DETECTION NOT RUN -- by design. The control set exists first.")


if __name__ == "__main__":
    main()
