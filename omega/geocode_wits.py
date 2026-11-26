"""Geocode Wonders in the Sky (Vallee & Aubeck) via Nominatim, 1 req/sec.
Unlocks the Track 9 / Phase 8 persistence test, which Phase 4B could not run
for want of geocoded pre-modern events (only 47 usable)."""
import sys, json, time, re, urllib.parse, subprocess, os
sys.path.insert(0, "/home/user/UFOAI/omega")
import corpus
OUT = "/tmp/claude-0/-home-user/f0aebeb3-1b62-5042-9067-46af83ba9a9d/scratchpad/omega/wits_geo.json"
recs, _ = corpus.load_all()
W = [r for r in recs if r.catalog == "WondersInTheSky"]
cache = json.load(open(OUT)) if os.path.exists(OUT) else {}
def clean(loc):
    s = re.sub(r"[\[\]'\"]", "", str(loc or "")).strip()
    s = re.sub(r"\s*\(.*?\)\s*", " ", s)
    return re.sub(r"\s+", " ", s).strip()
todo = []
for r in W:
    q = clean(r.location)
    if q and q not in cache: todo.append(q)
todo = list(dict.fromkeys(todo))
print(f"WondersInTheSky records={len(W)}  distinct location strings to geocode={len(todo)}", flush=True)
for i, q in enumerate(todo):
    u = ("https://nominatim.openstreetmap.org/search?format=json&limit=1&q="
         + urllib.parse.quote(q))
    p = subprocess.run(["curl","-sS","--max-time","30","-H","User-Agent: omega-research/1.0 (historical geocoding)",u],
                       capture_output=True, text=True)
    try:
        d = json.loads(p.stdout)
        cache[q] = {"lat": float(d[0]["lat"]), "lon": float(d[0]["lon"]),
                    "display": d[0].get("display_name","")[:160]} if d else None
    except Exception:
        cache[q] = None
    if (i+1) % 25 == 0:
        json.dump(cache, open(OUT,"w"))
        hit = sum(1 for v in cache.values() if v)
        print(f"  {i+1}/{len(todo)}  resolved={hit}", flush=True)
    time.sleep(1.1)
json.dump(cache, open(OUT,"w"))
hit = sum(1 for v in cache.values() if v)
print(f"DONE distinct={len(cache)} resolved={hit} ({hit*100//max(1,len(cache))}%)")
n = sum(1 for r in W if cache.get(clean(r.location)))
print(f"WondersInTheSky events now geocodable: {n} of {len(W)}")
