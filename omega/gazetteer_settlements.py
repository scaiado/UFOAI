"""High-precision settlement overlay for the NUFORC gazetteer.

STATUS: DOES NOT WORK AT ADMIN-UNIT SCALE.  NOT USED IN THE PIPELINE.
RETAINED AS A RECORDED NEGATIVE.

    `SERVICE wikibase:box` tolerates the P31/P279* class traversal only for
    SMALL boxes.  Measured: a Rhode Island-sized box returns in 8.3 s, but a
    province-sized bounding box (Alberta) answers `http_504: upstream request
    timeout` -- the same failure the P131+ form gives.  The Rhode Island test
    that motivated this script succeeded only because Rhode Island is tiny,
    and generalising from it was the error.

    It would be viable by tiling each admin unit into small boxes (~500-1000
    tiles at ~10 s each, i.e. 1.5-3 h), which is not worth the spend.
    Precision is instead carried by two things already in the pipeline: the
    population (P1082) tie-break in nuforc_ingest.load_gazetteer, and the
    per-record geocode tier in kv["GeocodeSource"] so downstream work can
    filter by provenance.

    A second latent bug, left visible rather than silently fixed: bbox()
    filters longitudes for the antimeridian case WITHOUT filtering the
    corresponding latitudes, so an Alaska-style box would be computed from
    mismatched lists.  It never ran far enough to matter.


WHY.  omega/gazetteer.py deliberately drops the settlement-class constraint,
because `wdt:P31/wdt:P279* wd:Q486972` is one of the two constructs that made
the query time out.  That buys recall (24k-76k coordinate-bearing entities per
state) at a cost in precision: only ~2-3% of those entities carry a population
(P1082), so for the rest there is no signal to prefer a town called Springfield
over a creek called Springfield in the same state.

That matters here specifically.  Section 6 records that the persistence result
was falsified as a CROSS-PIPELINE GEOCODING ARTEFACT -- Nominatim and Hatch DMS
agreeing on settlement centroids.  Geocoding precision has already cost this
project one result, so it gets a guard rather than a hope.

HOW.  The WDQS geospatial index (`SERVICE wikibase:box`) tolerates the class
traversal that the P131+ path does not: measured on a Rhode Island box,
box + P279* returns in 8.3 s where the P131+ form times out at 65 s.  So this
runs one box query per admin unit, bounded by the bounding box COMPUTED FROM
THE P131+ OUTPUT ALREADY ON DISK (free, and exact for that unit's extent), and
keeps only entities that are a human settlement or a subclass of one.

Output is written as `SET_<code>.json` beside the recall files.  Boxes bleed
across borders, which is harmless: the join is keyed on (state, name), so a
neighbouring state's town only ever competes under the state it was filed
under, and the NUFORC `state_provinces` field disambiguates.
"""
import os, sys, json, time, subprocess, collections

UA = "omega-research/1.0 (academic UAP data study; non-commercial)"
EP = "https://query.wikidata.org/sparql"
GAZ = "data/raw/gazetteer"
PAD = 0.25          # degrees of slack on the computed bbox

TMPL = """SELECT ?l ?lat ?lon ?pop WHERE {
  SERVICE wikibase:box {
    ?c wdt:P625 ?coord .
    bd:serviceParam wikibase:cornerSouthWest "Point(%(w).4f %(s).4f)"^^geo:wktLiteral .
    bd:serviceParam wikibase:cornerNorthEast "Point(%(e).4f %(n).4f)"^^geo:wktLiteral .
  }
  ?c wdt:P31/wdt:P279* wd:Q486972 ;
     rdfs:label ?l .
  FILTER(LANG(?l)="en")
  OPTIONAL { ?c wdt:P1082 ?pop }
  BIND(geof:latitude(?coord) AS ?lat)
  BIND(geof:longitude(?coord) AS ?lon)
}"""


def q(sparql, timeout=180):
    r = subprocess.run(
        ["curl", "-sS", "-A", UA, "-G", "--max-time", str(timeout),
         "--data-urlencode", f"query={sparql}", "-w", "\n__H__%{http_code}",
         "-H", "Accept: application/sparql-results+json", EP],
        capture_output=True, text=True, errors="replace")
    body, _, tail = r.stdout.rpartition("\n__H__")
    code = tail.strip() or f"curl_exit_{r.returncode}"
    if code != "200":
        return None, f"http_{code}: {body[:120].strip()!r}"
    try:
        return json.loads(body, strict=False)["results"]["bindings"], "ok"
    except Exception as e:
        return None, f"parse_{type(e).__name__}: {body[:120].strip()!r}"


def bbox(path):
    rows = json.load(open(path, encoding="utf-8"))
    if not rows:
        return None
    la = [r["lat"] for r in rows]
    lo = [r["lon"] for r in rows]
    # Alaska straddles the antimeridian; a single box cannot express that, so
    # clamp to the eastern (continental) lobe and accept the loss there.
    if max(lo) - min(lo) > 180:
        lo = [x for x in lo if x < 0]
        if not lo:
            return None
    return {"s": min(la) - PAD, "n": max(la) + PAD,
            "w": min(lo) - PAD, "e": max(lo) + PAD}


def main():
    src = sorted(f for f in os.listdir(GAZ)
                 if f.endswith(".json") and not f.startswith(("SET_", "NOM_")))
    print(f"{len(src)} recall files on disk", flush=True)
    done = fail = 0
    for fn in src:
        code = fn[:-5]
        out = f"{GAZ}/SET_{code}.json"
        if os.path.exists(out) and os.path.getsize(out) > 2:
            done += 1
            continue
        bb = bbox(f"{GAZ}/{fn}")
        if not bb:
            print(f"  {code} SKIP no bbox", flush=True)
            continue
        t0 = time.time()
        rows, why = q(TMPL % bb)
        if rows is None:
            print(f"  {code} FAILED  {why}", flush=True)
            fail += 1
            time.sleep(3)
            continue
        recs = []
        for b in rows:
            try:
                recs.append({"name": b["l"]["value"],
                             "lat": float(b["lat"]["value"]),
                             "lon": float(b["lon"]["value"]),
                             "pop": int(float(b["pop"]["value"])) if "pop" in b else None})
            except Exception:
                pass
        json.dump(recs, open(out, "w"), ensure_ascii=False)
        npop = sum(1 for x in recs if x["pop"])
        print(f"  {code} -> {len(recs)} settlements ({npop} with population) "
              f"in {time.time()-t0:.1f}s", flush=True)
        done += 1
        time.sleep(1.2)
    tot = 0
    for f in os.listdir(GAZ):
        if f.startswith("SET_"):
            tot += len(json.load(open(f"{GAZ}/{f}", encoding="utf-8")))
    print(f"\nDONE  settlement entries: {tot}  files: {done}  failed: {fail}")


if __name__ == "__main__":
    main()
