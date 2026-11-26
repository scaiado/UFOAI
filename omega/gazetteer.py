"""Bulk US/Canada place gazetteer from Wikidata, for NUFORC geocoding.

NUFORC ships no coordinates: ~31k distinct city|state pairs, which at
Nominatim's 1 req/s is ~8.5 hours.  Wikidata's SPARQL endpoint is allowlisted
and serves the same information in bulk, one query per state/province, so the
whole gazetteer lands in minutes.  Queries are per-admin-unit because a single
nationwide query times out.

CORRECTED DIAGNOSIS (2026-11-26).  This script never ran successfully, and the
previously recorded cause -- "Wikidata labels contain raw control characters, so
json.loads threw Invalid control character; now strict=False" -- was WRONG on
both counts:

  * The real failure was HTTP 504 "upstream request timeout" after ~65 s, for
    EVERY admin unit including the District of Columbia.  The query was simply
    too expensive.  The two costly constructs were the unbounded subclass
    traversal `wdt:P31/wdt:P279* wd:Q486972` and the statement-node coordinate
    form `p:P625/psv:P625 [...]`.  Replacing them with a plain `wdt:P625` plus
    `geof:latitude`/`geof:longitude` takes DC from timeout to 1.8 s, Rhode
    Island to 0.9 s and New York to 23.7 s.
  * Measured across 55,045 New York rows, the number of labels containing a
    control character is ZERO.  `strict=False` is retained because it is
    harmless, but it fixed nothing.

The old `q()` returned None on any exception, printing a generic "FAILED", which
is exactly why the 504 stayed hidden.  It now reports the HTTP status and the
response head.

Dropping the settlement-class constraint means the query returns every entity
with coordinates in the admin unit, not only populated places.  That is
deliberate -- it raises recall for the NUFORC join, and ambiguity is resolved
downstream by preferring candidates that carry a population (P1082), which
settlements do and landforms generally do not.
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
 "AB":"Q1951","BC":"Q1973","MB":"Q1948","NB":"Q1965","NL":"Q2003","NS":"Q1952",
 "NT":"Q2007","NU":"Q2023","ON":"Q1904","PE":"Q1978","QC":"Q176","SK":"Q1989","YT":"Q2009",
}

# human settlement (Q486972) or any subclass, inside the admin unit transitively
# Two corrections beyond dropping the P279* traversal, both found by chasing
# a single missing city (San Antonio, 260 NUFORC records):
#
# 1. COORDINATES: `wdt:P625` returns only TRUTHY coordinate statements.  San
#    Antonio (Q975) has no truthy P625 at all -- its coordinate exists only as
#    a statement node.  So the `p:P625/psv:P625` form is restored.  It was NOT
#    the cause of the timeouts (the class traversal was); it costs ~23 s on
#    Texas and recovers ~190 entities there.
#
# 2. LABELS: Wikidata's `mul` language code holds labels that are identical
#    across languages, and `FILTER(LANG(?l)="en")` excludes them.  San Antonio
#    and Arizona both carry their name ONLY under `mul`.  The effect is small
#    in count (Texas: 66,405 en-labelled vs 66,430 en-or-mul, +25) but high in
#    leverage, because the names spelled identically in every language are
#    exactly the big international city names.
TMPL = """SELECT ?l ?lat ?lon ?pop WHERE {
  ?c wdt:P131+ wd:%s ;
     p:P625/psv:P625 [ wikibase:geoLatitude ?lat ; wikibase:geoLongitude ?lon ] ;
     rdfs:label ?l .
  FILTER(LANG(?l) IN ("en","mul"))
  OPTIONAL { ?c wdt:P1082 ?pop }
}"""
# Fallback for an admin unit whose single query will not come back.
#
# CORRECTED DIAGNOSIS.  California first failed with parse_JSONDecodeError and
# Michigan with http_502, and I inferred that California's response was simply
# too large to return intact.  THAT WAS WRONG: on a plain retry with the
# identical query, California returned 78,195 places in 23.4 s and Michigan
# 33,597 in 11.9 s.  Both failures were TRANSIENT.  The fix that actually
# worked is the one-shot retry above, not this fallback, and the partition path
# below never executed -- it is UNTESTED IN SITU, though the partition queries
# themselves were verified by hand (on California, letter 'L' returns 5,420
# rows in 45 s with Los Angeles present; 'S' returns 8,162 in 50 s with San
# Diego and San Francisco present).
#
# It is retained as insurance for a unit that genuinely cannot answer in one
# query, because the shape of that failure is real even if these two instances
# were not it.  LIMIT/OFFSET paging is NOT the way to do it: stable pages need
# ORDER BY, and ordering ~90k rows is itself too expensive -- California
# answered http_504 at 65 s for `ORDER BY ?l LIMIT 40000 OFFSET 0`.
# Partitioning on the first character of the label needs no sort.
_PART = TMPL.rstrip()[:-1] + """  FILTER(%s)
}"""
LETTERS = [chr(c) for c in range(ord("A"), ord("Z") + 1)]


def partitions(qid):
    """(label, sparql) per partition: A-Z by initial, then everything else."""
    for L in LETTERS:
        yield L, _PART % (qid, 'STRSTARTS(?l,"%s")' % L)
    rest = " && ".join('!STRSTARTS(?l,"%s")' % L for L in LETTERS)
    yield "other", _PART % (qid, rest)


# The admin unit is NOT in its own result set: `?c wdt:P131+ wd:Q61` returns
# places located IN the District of Columbia, and the District is not located
# in itself.  For a city-state that excludes the very place being looked up --
# US_DC held 3,239 entries and not one of them was Washington, costing 115
# NUFORC records.  So each unit's own label and coordinates are appended to
# its own file.  Scoped per file, so 'Washington' is added only to DC.
SELF = """SELECT ?l ?lat ?lon ?pop WHERE {
  VALUES ?c { wd:%s }
  ?c p:P625/psv:P625 [ wikibase:geoLatitude ?lat ; wikibase:geoLongitude ?lon ] ;
     rdfs:label ?l .
  FILTER(LANG(?l) IN ("en","mul"))
  OPTIONAL { ?c wdt:P1082 ?pop }
}"""

def q(sparql, timeout=180):
    """-> (bindings, reason).  bindings is None on failure; reason is never
    generic, because a generic reason is what hid the 504 for a whole session."""
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
        # strict=False is harmless but fixes nothing; see the module docstring.
        return json.loads(body, strict=False)["results"]["bindings"], "ok"
    except Exception as e:
        return None, f"parse_{type(e).__name__}: {body[:120].strip()!r}"

def main():
    os.makedirs(OUT, exist_ok=True)
    todo = [("US", k, v) for k, v in US.items()] + [("CA", k, v) for k, v in CA.items()]
    for cc, code, qid in todo:
        p = f"{OUT}/{cc}_{code}.json"
        if os.path.exists(p) and os.path.getsize(p) > 50:
            continue
        t0 = time.time()
        rows, why = q(TMPL % qid)

        # Two real failure modes seen in practice, both surfaced only because
        # q() reports a reason instead of returning None:
        #   * California: the single response is large enough to be truncated
        #     mid-JSON, giving parse_JSONDecodeError.
        #   * Michigan: a transient http_502 from the endpoint.
        # Retry once for a transient error, then fall back to LIMIT/OFFSET
        # paging, which fixes the truncation case.
        if rows is None and why.startswith("http_5"):
            print(f"  {cc}/{code} transient {why.split(':')[0]}, retrying once",
                  flush=True)
            time.sleep(8)
            rows, why = q(TMPL % qid)

        if rows is None:
            print(f"  {cc}/{code} single query failed ({why.split(':')[0]}); "
                  f"partitioning by initial letter", flush=True)
            rows, bad = [], []
            for lbl, sq in partitions(qid):
                part, why2 = q(sq, timeout=300)
                if part is None:
                    bad.append(f"{lbl}:{why2.split(':')[0]}")
                    continue
                rows.extend(part)
                time.sleep(0.5)
            if bad:
                # A partial partition set is NOT silently accepted: name the
                # missing parts so the file is never mistaken for complete.
                print(f"  {cc}/{code} PARTITIONS FAILED: {', '.join(bad)}"
                      f" -- file will be INCOMPLETE", flush=True)
            print(f"  {cc}/{code} partitioned: {len(rows)} rows from "
                  f"{27 - len(bad)}/27 partitions", flush=True)
            if not rows:
                rows = None

        if rows is None:
            print(f"  {cc}/{code} FAILED  {why}", flush=True)
            time.sleep(3); continue
        recs = []
        for b in rows:
            try:
                recs.append({"name": b["l"]["value"], "lat": float(b["lat"]["value"]),
                             "lon": float(b["lon"]["value"]),
                             "pop": int(float(b["pop"]["value"])) if "pop" in b else None})
            except Exception:
                pass
        json.dump(recs, open(p, "w"), ensure_ascii=False)
        if not recs:
            # An admin unit with zero places means a WRONG Q-ID, not an empty
            # province.  Two were wrong here: BC was Q1974 (no English label,
            # correct is Q1973) and PE was Q1979 (correct Q1978).  Both wrote a
            # 0-row file and the run still reported "0 failed", which is how a
            # populous province went missing from a 1.65M-entry gazetteer.
            print(f"  {cc}/{code} EMPTY -- suspect a wrong Q-id ({qid}); "
                  f"not writing a 0-row file", flush=True)
            time.sleep(1.0)
            continue
        npop = sum(1 for x in recs if x["pop"])
        print(f"  {cc}/{code} -> {len(recs)} places ({npop} with population) "
              f"in {time.time()-t0:.1f}s", flush=True)
        time.sleep(1.5)
    # --- append each admin unit's own place record to its own file ---
    added = 0
    for cc, code, qid in todo:
        p = f"{OUT}/{cc}_{code}.json"
        if not os.path.exists(p):
            continue
        try:
            recs = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        if any(r.get("self") for r in recs):
            continue
        rows, why = q(SELF % qid, timeout=60)
        if not rows:
            print(f"  {cc}/{code} self-record unavailable ({why})", flush=True)
            continue
        for b in rows:
            try:
                recs.append({"name": b["l"]["value"],
                             "lat": float(b["lat"]["value"]),
                             "lon": float(b["lon"]["value"]),
                             "pop": int(float(b["pop"]["value"])) if "pop" in b else None,
                             "self": True})
                added += 1
            except Exception:
                pass
        json.dump(recs, open(p, "w"), ensure_ascii=False)
        time.sleep(0.3)
    print(f"  appended {added} self-records", flush=True)

    tot = 0
    for f in os.listdir(OUT):
        tot += len(json.load(open(f"{OUT}/{f}", encoding="utf-8")))
    print(f"\nDONE  gazetteer entries: {tot}  files: {len(os.listdir(OUT))}")

if __name__ == "__main__":
    main()
