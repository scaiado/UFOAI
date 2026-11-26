"""TRACK 9 / Phase 8 redo: ancient-modern geographic persistence, now powered.

Phase 4B could use only 47 geocoded pre-1800 events and the result inverted
when the window widened -- a textbook underpowered artifact. Nominatim
geocoding of Wonders in the Sky (Vallee & Aubeck) raises the historical arm to
337 events spanning antiquity to 1879, a 7x increase.

Null: era label permuted WITHIN COUNTRY, which holds the continental coverage
shift fixed (pre-modern coverage is Eurasian; post-1950 is US-dominated).
"""
from __future__ import annotations
import sys, json, re, collections
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, "/home/user/UFOAI/omega")
import corpus, phase2

RNG = np.random.default_rng(90909)
GEO = "/tmp/claude-0/-home-user/f0aebeb3-1b62-5042-9067-46af83ba9a9d/scratchpad/omega/wits_geo.json"
MC = "/home/user/UFOAI/data/processed/provenance/master_catalog_inclusive.json"

def clean(loc):
    s = re.sub(r"[\[\]'\"]", "", str(loc or "")).strip()
    s = re.sub(r"\s*\(.*?\)\s*", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def country_from_display(d):
    parts = [p.strip() for p in str(d or "").split(",")]
    return parts[-1].lower() if parts else "?"

def main():
    cache = json.load(open(GEO))
    recs, _ = corpus.load_all()
    W = [r for r in recs if r.catalog == "WondersInTheSky"]
    hist = []
    for r in W:
        g = cache.get(clean(r.location))
        if g: hist.append(dict(lat=g["lat"], lon=g["lon"], year=r.year,
                               country=country_from_display(g["display"]),
                               loc=r.location, desc=r.desc[:90]))
    mc = json.load(open(MC))
    mod = [dict(lat=e["lat"], lon=e["lon"], year=e["year"],
                country=(e["country"] or "").strip().lower() or "?")
           for e in mc["events"] if e["lat"] is not None and e["year"] and e["year"] >= 1950]
    print("=" * 84)
    print("TRACK 9  ANCIENT-MODERN GEOGRAPHIC PERSISTENCE (powered)")
    print(f"  historical (Wonders in the Sky, geocoded): {len(hist)}   "
          f"year range {min(h['year'] for h in hist)}-{max(h['year'] for h in hist)}")
    print(f"  modern (post-1950, geocoded): {len(mod)}")

    # harmonise country names: use reverse-geocoded country for historical, and
    # map Hatch's country strings onto the same vocabulary where possible.
    CMAP = {"usa":"united states","us":"united states","united states":"united states",
            "great britain and ireland":"united kingdom","england":"united kingdom",
            "britain":"united kingdom","uk":"united kingdom","scotland":"united kingdom",
            "france":"france","germany":"germany","italy":"italy","spain":"spain",
            "china":"china","japan":"japan","russia":"russia","ussr":"russia",
            "brazil":"brazil","canada":"canada","australia":"australia","india":"india",
            "belgium":"belgium","netherlands":"netherlands","switzerland":"switzerland",
            "austria":"austria","turkey":"türkiye","greece":"greece","egypt":"egypt",
            "mexico":"mexico","argentina":"argentina","poland":"poland","sweden":"sweden",
            "norway":"norway","denmark":"denmark","portugal":"portugal","ireland":"ireland"}
    def norm(c):
        c = (c or "?").lower()
        return CMAP.get(c, c)
    for h in hist: h["c"] = norm(h["country"])
    for m in mod: m["c"] = norm(m["country"])
    hc = collections.Counter(h["c"] for h in hist)
    mc2 = collections.Counter(m["c"] for m in mod)
    both = {c for c in hc if hc[c] >= 3 and mc2.get(c, 0) >= 3}
    print(f"  countries with >=3 events in BOTH eras: {len(both)} -> "
          f"{sorted(both)[:12]}{' ...' if len(both)>12 else ''}")
    H = [h for h in hist if h["c"] in both]
    M = [m for m in mod if m["c"] in both]
    print(f"  usable: historical={len(H)}  modern={len(M)}")
    if len(H) < 30:
        print("  STILL UNDERPOWERED"); return

    pool = H + M
    lab = np.array([1]*len(H) + [0]*len(M))
    ctry = np.array([p["c"] for p in pool])
    xyz = phase2.ecef(np.array([p["lat"] for p in pool]), np.array([p["lon"] for p in pool]))
    idx_by_c = {c: np.flatnonzero(ctry == c) for c in set(ctry)}
    nh_by_c = {c: int(lab[v].sum()) for c, v in idx_by_c.items()}
    print(f"\n  {'radius':>8}{'obs mean':>11}{'null mean':>11}{'sd':>8}{'ratio':>8}{'z':>8}{'p':>9}")
    out = {}
    for rad in (25, 50, 100, 200):
        mt = cKDTree(xyz[lab == 0])
        nb = mt.query_ball_point(xyz[lab == 1], r=phase2.chord(rad))
        obs = float(np.mean([len(b) for b in nb]))
        null = np.empty(3000)
        for i in range(3000):
            lp = np.zeros_like(lab)
            for c, v in idx_by_c.items():
                n = nh_by_c[c]
                if n: lp[RNG.choice(v, size=n, replace=False)] = 1
            t2 = cKDTree(xyz[lp == 0])
            nb2 = t2.query_ball_point(xyz[lp == 1], r=phase2.chord(rad))
            null[i] = np.mean([len(b) for b in nb2])
        mu, sd = null.mean(), null.std(ddof=1)
        z = (obs - mu) / sd if sd else float("nan")
        p = (1 + int((null >= obs).sum())) / 3001
        print(f"  {rad:>7}km{obs:>11.2f}{mu:>11.2f}{sd:>8.2f}"
              f"{obs/max(mu,1e-9):>8.3f}{z:>+8.2f}{p:>9.4f}")
        out[rad] = dict(obs=obs, null=float(mu), sd=float(sd),
                        ratio=obs/max(mu,1e-9), z=float(z), p=p)
    print(f"\n  Bonferroni alpha = 0.05/4 = {0.05/4:.4f}")
    import os
    os.makedirs("/home/user/UFOAI/data/processed/persistence", exist_ok=True)
    json.dump(dict(n_hist=len(H), n_mod=len(M), countries=sorted(both), results=out),
              open("/home/user/UFOAI/data/processed/persistence/track9.json", "w"), indent=1)
    # top persistent historical locations, for the record
    mt = cKDTree(xyz[lab == 0])
    cnt = [(len(mt.query_ball_point(xyz[i], r=phase2.chord(100))), H[i]) for i in range(len(H))]
    cnt.sort(key=lambda x: -x[0])
    print("\n  TOP 10 historical events with most modern events within 100 km")
    print("  (note: this is a map of modern reporting density, NOT a test)")
    for n, h in cnt[:10]:
        print(f"    {n:>5}  {h['year']:>5}  {clean(h['loc'])[:34]:<35} {h['desc'][:46]}")

if __name__ == "__main__":
    main()
