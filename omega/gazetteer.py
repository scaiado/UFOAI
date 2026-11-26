"""Bulk US/Canada place gazetteer from Wikidata, for NUFORC geocoding.

NUFORC ships no coordinates: 33,976 distinct city|state pairs, which at
Nominatim's 1 req/s is ~9.5 hours.  Wikidata's SPARQL endpoint is allowlisted
and serves the same information in bulk, one query per state/province, so the
whole gazetteer lands in minutes.  Queries are per-admin-unit because a single
nationwide query times out.
"""
import os, sys, json, time, subprocess, urllib.parse, collections

UA = "omega-research/1.0 (academic UAP data study; non-commercial)"
EP = "https://query.wikidata.org/sparql"
OUT = "data/raw/gazetteer"

# Q-ids: US states + DC, Canadian provinces/territories, keyed by NUFORC code
US = {
 "AL":"Q173","AK":"Q797","AZ":"Q816","AR":"Q1612","CA":"Q99","CO":"Q1261","CT":"Q779",
 "DE":"Q1393","DC":"Q61","FL":"Q812","GA":"Q1428","HI":"Q782","ID":"Q1221","IL":"Q1204",
 "IN":"Q1415","IA":"Q1546","KS":"Q1558","KY":"Q1603","LA":"Q1588","ME":"Q724","MD":"Q1391",
 "MA":"Q771","MI":"Q1166","MN":"Q1527","MS":"Q1494","MO":"Q1581","MT":"Q1212","NE":"Q1553",
 "NV":"Q1227","NH":"Q759","NJ":"Q1408","NM":"Q1522","NY":"Q1384","NC":"Q1454","ND":"Q1207",
 "OH":"Q1397","OK":"Q1649","OR":"Q824","PA":"Q1400","RI":"Q1387","SC":"Q1456","SD":"Q1211",
 "TN":"Q1509","TX":"Q1439","UT":"Q829","VT":"Q16551","VA":"Q1370","WA":"Q1223","WV":"Q1371",
 "WI":"Q1537","WY":"Q1214","PR":"Q1183","VI":"Q11703","GU":"Q16635",
}
CA = {
 "AB":"Q1951","BC":"Q1974","MB":"Q1948","NB":"Q1965","NL":"Q2003","NS":"Q1952",
 "NT":"Q2007","NU":"Q2023","ON":"Q1904","PE":"Q1979","QC":"Q176","SK":"Q1989","YT":"Q2009",
}

# human settlement (Q486972) or any subclass, inside the admin unit transitively
TMPL = """SELECT ?l ?lat ?lon ?pop WHERE {
  ?c wdt:P31/wdt:P279* wd:Q486972 ;
     wdt:P131+ wd:%s ;
     rdfs:label ?l ;
     p:P625/psv:P625 [ wikibase:geoLatitude ?lat ; wikibase:geoLongitude ?lon ] .
  OPTIONAL { ?c wdt:P1082 ?pop }
  FILTER(LANG(?l)="en")
}"""

def q(sparql, timeout=180):
    r = subprocess.run(
        ["curl", "-sS", "-A", UA, "-G", "--max-time", str(timeout),
         "--data-urlencode", f"query={sparql}",
         "-H", "Accept: application/sparql-results+json", EP],
        capture_output=True, text=True, errors="replace")
    try:
        # Wikidata labels can contain raw control characters; strict=False allows them
        return json.loads(r.stdout, strict=False)["results"]["bindings"]
    except Exception:
        return None

def main():
    os.makedirs(OUT, exist_ok=True)
    todo = [("US", k, v) for k, v in US.items()] + [("CA", k, v) for k, v in CA.items()]
    for cc, code, qid in todo:
        p = f"{OUT}/{cc}_{code}.json"
        if os.path.exists(p) and os.path.getsize(p) > 50:
            continue
        rows = q(TMPL % qid)
        if rows is None:
            print(f"  {cc}/{code} FAILED", flush=True); time.sleep(3); continue
        recs = []
        for b in rows:
            try:
                recs.append({"name": b["l"]["value"], "lat": float(b["lat"]["value"]),
                             "lon": float(b["lon"]["value"]),
                             "pop": int(float(b["pop"]["value"])) if "pop" in b else None})
            except Exception:
                pass
        json.dump(recs, open(p, "w"), ensure_ascii=False)
        print(f"  {cc}/{code} -> {len(recs)} places", flush=True)
        time.sleep(1.5)
    tot = 0
    for f in os.listdir(OUT):
        tot += len(json.load(open(f"{OUT}/{f}", encoding="utf-8")))
    print(f"\nDONE  gazetteer entries: {tot}  files: {len(os.listdir(OUT))}")

if __name__ == "__main__":
    main()
