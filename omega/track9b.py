"""TRACK 9 RED TEAM: is the 25 km persistence effect just urbanisation?

The historical arm is dominated by English urban records (Oxford x4, London x3,
Uxbridge, Gunnersbury in the top 10). Pre-modern accounts survive from places
that had literate chroniclers, universities and observatories -- i.e. cities.
Modern reports also concentrate near population. A within-country permutation
draws controls from rural points, so an urban/rural contrast alone would
produce a short-range "persistence" signal.

NON-CIRCULAR CONTROL. Split the modern events at random into halves A and B.
Use half A ONLY to define local-density strata (independent of the outcome),
then permute era labels within country x density stratum and test persistence
against half B. Also restricts the historical arm to pre-1880, since Wonders in
the Sky is a pre-modern compilation.
"""
from __future__ import annotations
import sys, json, re, collections
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, "/home/user/UFOAI/omega")
import corpus, phase2, track9

RNG = np.random.default_rng(999333)
cache = json.load(open(track9.GEO))
recs, _ = corpus.load_all()
W = [r for r in recs if r.catalog == "WondersInTheSky"]
hist = []
for r in W:
    g = cache.get(track9.clean(r.location))
    if g and r.year and r.year < 1880:
        hist.append(dict(lat=g["lat"], lon=g["lon"], year=r.year,
                         c=track9.country_from_display(g["display"]),
                         loc=track9.clean(r.location)))
mc = json.load(open(track9.MC))
mod = [dict(lat=e["lat"], lon=e["lon"], year=e["year"],
            c=(e["country"] or "?").strip().lower())
       for e in mc["events"] if e["lat"] is not None and e["year"] and e["year"] >= 1950]
CMAP = {"usa":"united states","us":"united states","great britain and ireland":"united kingdom",
        "england":"united kingdom","britain":"united kingdom","uk":"united kingdom",
        "scotland":"united kingdom","ussr":"russia"}
for x in hist + mod: x["c"] = CMAP.get(x["c"], x["c"])
print(f"historical pre-1880 geocoded: {len(hist)}   modern post-1950: {len(mod)}")

# split modern into A (strata definition) and B (test target)
perm = RNG.permutation(len(mod))
A = [mod[i] for i in perm[: len(mod)//2]]
B = [mod[i] for i in perm[len(mod)//2:]]
Axyz = phase2.ecef(np.array([a["lat"] for a in A]), np.array([a["lon"] for a in A]))
Atree = cKDTree(Axyz)

def density(pts, rad=100):
    xyz = phase2.ecef(np.array([p["lat"] for p in pts]), np.array([p["lon"] for p in pts]))
    return np.array([len(Atree.query_ball_point(xyz[i], r=phase2.chord(rad)))
                     for i in range(len(pts))]), xyz

hd, hxyz = density(hist)
bd, bxyz = density(B)
print(f"local density (half-A events within 100km): historical median={np.median(hd):.0f}, "
      f"modern-B median={np.median(bd):.0f}")
print("  -> historical events sit in markedly denser reporting regions, which is the confound")

hc = collections.Counter(h["c"] for h in hist); bc = collections.Counter(b["c"] for b in B)
both = {c for c in hc if hc[c] >= 3 and bc.get(c, 0) >= 3}
H = [h for i, h in enumerate(hist) if h["c"] in both]
Hd = np.array([hd[i] for i, h in enumerate(hist) if h["c"] in both])
Bk = [b for i, b in enumerate(B) if b["c"] in both]
Bdk = np.array([bd[i] for i, b in enumerate(B) if b["c"] in both])
print(f"usable: historical={len(H)}  modern-B={len(Bk)}  countries={sorted(both)}")

pool = H + Bk
lab = np.array([1]*len(H) + [0]*len(Bk))
dens = np.concatenate([Hd, Bdk])
ctry = np.array([p["c"] for p in pool])
xyz = phase2.ecef(np.array([p["lat"] for p in pool]), np.array([p["lon"] for p in pool]))
# density quintiles computed on the POOLED set
qs = np.quantile(dens, [0.2, 0.4, 0.6, 0.8])
dstrat = np.digitize(dens, qs)
strat = np.array([f"{c}|{d}" for c, d in zip(ctry, dstrat)])
idx_by = {s: np.flatnonzero(strat == s) for s in set(strat)}
nh_by = {s: int(lab[v].sum()) for s, v in idx_by.items()}
usable = sum(n for s, n in nh_by.items() if n and len(idx_by[s]) > n)
print(f"strata (country x density quintile): {len(idx_by)}; historical events in "
      f"non-degenerate strata: {usable}/{len(H)}")

print(f"\n  {'radius':>8}{'obs':>10}{'null':>10}{'sd':>7}{'ratio':>8}{'z':>8}{'p':>9}  verdict")
out = {}
for rad in (25, 50, 100, 200):
    mt = cKDTree(xyz[lab == 0])
    obs = float(np.mean([len(b) for b in mt.query_ball_point(xyz[lab == 1], r=phase2.chord(rad))]))
    null = np.empty(3000)
    for i in range(3000):
        lp = np.zeros_like(lab)
        for s, v in idx_by.items():
            n = nh_by[s]
            if n: lp[RNG.choice(v, size=min(n, len(v)), replace=False)] = 1
        t2 = cKDTree(xyz[lp == 0])
        null[i] = np.mean([len(b) for b in t2.query_ball_point(xyz[lp == 1], r=phase2.chord(rad))])
    mu, sd = null.mean(), null.std(ddof=1)
    z = (obs-mu)/sd if sd else float("nan")
    p = (1+int((null >= obs).sum()))/3001
    v = "SURVIVES" if p < 0.0125 else ("nominal" if p < 0.05 else "null")
    print(f"  {rad:>7}km{obs:>10.2f}{mu:>10.2f}{sd:>7.2f}{obs/max(mu,1e-9):>8.3f}{z:>+8.2f}{p:>9.4f}  {v}")
    out[rad] = dict(obs=obs, null=float(mu), ratio=obs/max(mu,1e-9), z=float(z), p=p)
json.dump(out, open("/home/user/UFOAI/data/processed/persistence/track9b_density_controlled.json","w"), indent=1)
