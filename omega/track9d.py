"""TRACK 9 RED TEAM 2: is the 25 km effect a shared-centroid geocoding artifact?

The two arms are geocoded by DIFFERENT pipelines onto the SAME kind of target:
  historical: Nominatim place-name lookup -> settlement centroid
  modern:     Hatch arcminute DMS of a place name -> settlement centroid
If both land on the same town centroid, any historical and modern event naming
the same town becomes near-coincident by construction, inflating short-range
counts without any physical co-location.

Diagnostic: the distance distribution of historical -> nearest-modern pairs.
A centroid artifact produces a spike at very small distances (<2-5 km) far above
what the matched null produces. A genuine regional effect does not.
"""
from __future__ import annotations
import sys, json, collections
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, "/home/user/UFOAI/omega")
import corpus, phase2, track9

RNG = np.random.default_rng(314159)
cache = json.load(open(track9.GEO))
recs, _ = corpus.load_all()
CMAP = {"usa":"united states","us":"united states","great britain and ireland":"united kingdom",
        "england":"united kingdom","britain":"united kingdom","uk":"united kingdom",
        "scotland":"united kingdom","ussr":"russia"}
hist = []
for r in (x for x in recs if x.catalog == "WondersInTheSky"):
    g = cache.get(track9.clean(r.location))
    if g and r.year and r.year < 1880:
        c = track9.country_from_display(g["display"]); c = CMAP.get(c, c)
        hist.append(dict(lat=g["lat"], lon=g["lon"], c=c, loc=track9.clean(r.location)))
mc = json.load(open(track9.MC))
mod = []
for e in mc["events"]:
    if e["lat"] is None or not e["year"] or e["year"] < 1950: continue
    c = (e["country"] or "?").strip().lower(); c = CMAP.get(c, c)
    mod.append(dict(lat=e["lat"], lon=e["lon"], c=c, loc=e["location"] or ""))
hc = collections.Counter(h["c"] for h in hist); mcn = collections.Counter(m["c"] for m in mod)
both = {c for c in hc if hc[c] >= 3 and mcn.get(c, 0) >= 3}
H = [h for h in hist if h["c"] in both]; M = [m for m in mod if m["c"] in both]
hx = phase2.ecef(np.array([h["lat"] for h in H]), np.array([h["lon"] for h in H]))
mx = phase2.ecef(np.array([m["lat"] for m in M]), np.array([m["lon"] for m in M]))
mt = cKDTree(mx)
d, i = mt.query(hx, k=1)
gc = 2*phase2.R_E*np.arcsin(np.clip(d/(2*phase2.R_E), 0, 1))
print("=" * 86)
print(f"TRACK 9 RED TEAM 2   historical n={len(H)}  modern n={len(M)}")
print("\n  DISTANCE TO NEAREST MODERN EVENT (historical events)")
print(f"  {'band':>14}{'observed':>10}{'share':>9}")
bands = [(0,1),(1,2),(2,5),(5,10),(10,25),(25,50),(50,100),(100,1e9)]
for lo,hi in bands:
    n = int(((gc>=lo)&(gc<hi)).sum())
    print(f"  {lo:>5}-{hi if hi<1e8 else 'inf':>6} km{n:>10}{n/len(H)*100:>8.1f}%")
print(f"  median={np.median(gc):.1f} km   min={gc.min():.3f} km")
print("\n  SUB-2KM PAIRS (candidate shared-centroid artifacts):")
near = np.flatnonzero(gc < 2)
for k in near[:18]:
    print(f"    {gc[k]:>7.3f} km  HIST {H[k]['loc'][:34]:<35} <-> MOD {M[i[k]]['loc'][:34]}")
print(f"    ... {len(near)} pairs under 2 km ({len(near)/len(H)*100:.1f}% of historical events)")

# how many share a place-name token?
def toks(s):
    import re
    return {t for t in re.sub(r"[^a-z ]"," ",str(s).lower()).split() if len(t)>3}
shared = sum(1 for k in near if toks(H[k]['loc']) & toks(M[i[k]]['loc']))
print(f"    of those, {shared} share a place-name token with their matched modern event "
      f"({shared/max(1,len(near))*100:.0f}%)")

print("\n  EFFECT WITH SUB-5KM PAIRS EXCLUDED (removes centroid coincidences)")
keep = gc >= 5
print(f"    historical events retained: {int(keep.sum())}/{len(H)}")
Hk = [H[k] for k in range(len(H)) if keep[k]]
hxk = hx[keep]
Atree = cKDTree(mx)
for rad in (25, 50):
    obs = float(np.mean([len(b) for b in Atree.query_ball_point(hxk, r=phase2.chord(rad))]))
    # country+scale-matched null over the pooled set
    pool = Hk + M
    lab = np.array([1]*len(Hk)+[0]*len(M))
    xyz = np.vstack([hxk, mx])
    dens = np.array([len(Atree.query_ball_point(xyz[j], r=phase2.chord(rad))) for j in range(len(pool))])
    qs = np.unique(np.quantile(dens,[.2,.4,.6,.8])); ds = np.digitize(dens, qs)
    strat = np.array([f"{p['c']}|{x}" for p,x in zip(pool, ds)])
    idx_by = {s: np.flatnonzero(strat==s) for s in set(strat)}
    nh = {s:int(lab[v].sum()) for s,v in idx_by.items()}
    null = np.empty(2000)
    for t in range(2000):
        lp = np.zeros_like(lab)
        for s,v in idx_by.items():
            if nh[s]: lp[RNG.choice(v,size=min(nh[s],len(v)),replace=False)] = 1
        t2 = cKDTree(xyz[lp==0])
        null[t] = np.mean([len(b) for b in t2.query_ball_point(xyz[lp==1], r=phase2.chord(rad))])
    mu,sd = null.mean(), null.std(ddof=1)
    p = (1+int((null>=obs).sum()))/2001
    print(f"    {rad:>3}km  obs={obs:.2f}  null={mu:.2f}+/-{sd:.2f}  ratio={obs/mu:.3f}  "
          f"z={(obs-mu)/sd:+.2f}  p={p:.4f}  {'SURVIVES' if p<0.0125 else ('nominal' if p<0.05 else 'null')}")

print("\n  PER-COUNTRY BREAKDOWN at 25 km (is it all the UK?)")
for c in sorted(both):
    Hc = [k for k in range(len(H)) if H[k]['c']==c]
    if len(Hc) < 8: continue
    sub = gc[Hc]
    print(f"    {c:<18} nH={len(Hc):>4}  median dist={np.median(sub):>7.1f} km  "
          f"<25km={int((sub<25).sum())} ({(sub<25).mean()*100:.0f}%)")
