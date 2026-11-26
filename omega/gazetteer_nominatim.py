"""Fallback geocoder for the NUFORC city|state pairs, via Nominatim.

WHY THIS EXISTS.  `omega/gazetteer.py` was supposed to bulk-load a place
gazetteer from the Wikidata SPARQL endpoint.  It never worked.  The recorded
diagnosis (HANDOFF section 2.2) was a JSON control-character error fixed with
`strict=False`; that diagnosis was WRONG.  The real failure is that the query
itself is too expensive and WDQS answers HTTP 504 "upstream request timeout"
after ~65 s, for every admin unit including the District of Columbia.  The
original `q()` swallowed that into `return None`, printing a generic "FAILED",
which is why the true cause stayed hidden.

IT RUNS ONLY ON THE RESIDUAL.  The Wikidata gazetteer resolves 85.8% of the
134,906 records (1,650,151 entries across 67 admin units, zero query failures).
The misses are not random and not truncation -- the result COUNT matches the
returned rows, so the sets are complete.  They are ENGLISH-LABEL GAPS in
Wikidata.  Measured on the 40 largest US cities, 3 are absent: San Antonio TX
(Q975 carries labels in Malayalam and Arabic but none in en/es/fr/de),
Washington DC and Tampa FL.  Those three alone account for ~600 NUFORC records.
Foreign cities (London, Sydney) are also absent because the gazetteer covers
only US states and Canadian provinces.

So this reads `ungeocoded_pairs.json` -- pairs that resolved in NO tier -- in
descending record-count order, at 1 req/s with an honest user agent and a
resumable per-pair cache.  It can be stopped at any point with a known
coverage figure.

Policy: 1 req/s, honest user agent, no retry storms.  Public endpoint only.
"""
import os, sys, json, time, subprocess, collections

UA = "omega-research/1.0 (academic UAP data study; non-commercial)"
EP = "https://nominatim.openstreetmap.org/search"
OUT = "data/raw/gazetteer_nominatim"
CACHE = f"{OUT}/cache.json"
PAIRS = "data/processed/nuforc/ungeocoded_pairs.json"
SLEEP = 1.1          # >1 s, per Nominatim usage policy

US_STATES = set("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD "
                "MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD "
                "TN TX UT VT VA WA WV WI WY PR VI GU".split())
CA_PROV = set("AB BC MB NB NL NS NT NU ON PE QC SK YT".split())


COUNTRY_CC = {
    "United States": "us", "Canada": "ca", "United Kingdom": "gb",
    "Australia": "au", "New Zealand": "nz", "Mexico": "mx", "India": "in",
    "Ireland": "ie", "Germany": "de", "France": "fr", "Japan": "jp",
    "Brazil": "br", "South Africa": "za", "Netherlands": "nl", "Spain": "es",
    "Italy": "it", "Philippines": "ph", "Puerto Rico": "pr",
}


def geocode(city, state, country=""):
    cc = ("us" if state in US_STATES else "ca" if state in CA_PROV
          else COUNTRY_CC.get(country, ""))
    args = ["curl", "-sS", "-A", UA, "-G", "--max-time", "45",
            "--data-urlencode", f"city={city}",
            "--data-urlencode", "format=jsonv2",
            "--data-urlencode", "limit=1"]
    if state:
        args += ["--data-urlencode", f"state={state}"]
    elif country and not cc:
        # No state and no recognised country code: hand Nominatim the country
        # name as a free-text component. NUFORC leaves `state_provinces` blank
        # for non-US/CA sightings, so for those rows country is the ONLY
        # disambiguator available -- without it "London" and "Perth" resolve by
        # Nominatim's own popularity ordering rather than by the data.
        args += ["--data-urlencode", f"country={country}"]
    if cc:
        args += ["--data-urlencode", f"countrycodes={cc}"]
    args += ["-w", "\n__H__%{http_code}", EP]
    r = subprocess.run(args, capture_output=True, text=True, errors="replace")
    body, _, tail = r.stdout.rpartition("\n__H__")
    if tail.strip() != "200":
        return None, tail.strip() or f"curl{r.returncode}"
    try:
        j = json.loads(body, strict=False)
    except Exception as e:
        return None, f"parse:{type(e).__name__}"
    if not j:
        return None, "no_match"
    h = j[0]
    try:
        return {"lat": float(h["lat"]), "lon": float(h["lon"]),
                "display": h.get("display_name", "")[:160],
                "type": h.get("type", "")}, "ok"
    except Exception:
        return None, "bad_fields"


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
    os.makedirs(OUT, exist_ok=True)
    cache = {}
    if os.path.exists(CACHE):
        try:
            cache = json.load(open(CACHE, encoding="utf-8"))
        except Exception:
            cache = {}
    # NOTE: `cache` is persistent across runs and across worklists, so its keys
    # are a SUPERSET of the current worklist's -- a pair the Wikidata gazetteer
    # later resolves drops out of ungeocoded_pairs.json but stays in the cache.
    # Coverage must therefore look pairs up defensively.
    pairs = json.load(open(PAIRS, encoding="utf-8"))
    ordered = sorted(pairs.items(), key=lambda kv: -kv[1])[:limit]
    total_recs = sum(pairs.values())
    print(f"{len(pairs)} distinct pairs, {total_recs} records; "
          f"geocoding top {len(ordered)}; cached {len(cache)}", flush=True)

    stats = collections.Counter()
    t0 = time.time()
    for i, (key, n) in enumerate(ordered, 1):
        if key in cache:
            stats["cached"] += 1
            continue
        # The first run cached under the 2-field key "city|state"; the worklist
        # now carries "city|state|country". Reuse those entries rather than
        # re-querying ~1,200 resolved pairs.
        legacy = "|".join(key.split("|")[:2])
        if legacy in cache:
            cache[key] = cache[legacy]
            stats["cached_legacy"] += 1
            continue
        # Salvage the first run's MALFORMED keys. Its worklist was built with
        # rpartition(", ") on the display string, so a stateless location put
        # the city in both fields -- "London|London". Those queries went out
        # with state="London", which Nominatim ignored, so the coordinates are
        # usable even though the key was not. 851 of that run's 1,252 resolved
        # pairs (68%) are in this form; re-querying them would waste ~16 min of
        # requests against a free public endpoint for no gain.
        st_now = key.split("|")[1] if len(key.split("|")) > 1 else ""
        if not st_now:
            city_now = key.split("|")[0]
            salv = cache.get(f"{city_now}|{city_now}")
            if salv:
                cache[key] = salv
                stats["cached_salvaged"] += 1
                continue
        parts = key.split("|")
        city, state = parts[0], parts[1] if len(parts) > 1 else ""
        country = parts[2] if len(parts) > 2 else ""
        if not city.strip():
            cache[key] = None
            stats["empty_city"] += 1
            continue
        res, why = geocode(city.strip(), state.strip(), country.strip())
        cache[key] = res
        stats[why] += 1
        time.sleep(SLEEP)
        if i % 100 == 0:
            hit = sum(1 for v in cache.values() if v)
            cov = sum(pairs.get(k, 0) for k, v in cache.items() if v) / total_recs
            el = time.time() - t0
            print(f"  [{i}/{len(ordered)}] hits={hit} coverage={cov:.1%} "
                  f"elapsed={el/60:.1f}m {dict(stats)}", flush=True)
            json.dump(cache, open(CACHE, "w"), ensure_ascii=False)

    json.dump(cache, open(CACHE, "w"), ensure_ascii=False)

    # Emit in the per-state file format omega/nuforc_ingest.load_gazetteer reads.
    bystate = collections.defaultdict(list)
    for key, v in cache.items():
        if not v:
            continue
        parts = key.split("|")
        city, state = parts[0], parts[1] if len(parts) > 1 else ""
        # Skip the first run's malformed self-referential keys ("London|London"):
        # their state field is really a city name and would create a bogus file.
        if state and city and state == city:
            continue
        bystate[state.strip() or "XX"].append(
            {"name": city.strip(), "lat": v["lat"], "lon": v["lon"], "pop": None})
    os.makedirs("data/raw/gazetteer", exist_ok=True)
    for st, rows in bystate.items():
        json.dump(rows, open(f"data/raw/gazetteer/NOM_{st}.json", "w"),
                  ensure_ascii=False)

    hit = sum(1 for v in cache.values() if v)
    cov = sum(pairs.get(k, 0) for k, v in cache.items() if v) / total_recs
    print(f"\nDONE  pairs resolved {hit}/{len(cache)}  "
          f"record coverage {cov:.2%}  state files {len(bystate)}")
    print(f"  {dict(stats)}")


if __name__ == "__main__":
    main()
