"""TRACK 9 FINAL: scale-matched density control.

track9b matched local density at 100 km and then tested at 25/50/100/200 km.
That is not a fair test: matching at 100 km forces the 100 km result to ~1.0 by
construction, so any surviving signal at other radii is simply the scale that
was not matched. The correct design matches the density proxy AT THE SAME
RADIUS as the test. Density is still computed from an independent half of the
modern data, so the stratification is non-circular.
"""
from __future__ import annotations
import sys, json, collections
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, "/home/user/UFOAI/omega")
import corpus, phase2, track9

RNG = np.random.default_rng(555777)
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
        hist.append(dict(lat=g["lat"], lon=g["lon"], c=c))
mc = json.load(open(track9.MC))
mod = []
for e in mc["events"]:
    if e["lat"] is None or not e["year"] or e["year"] < 1950: continue
    c = (e["country"] or "?").strip().lower(); c = CMAP.get(c, c)
    mod.append(dict(lat=e["lat"], lon=e["lon"], c=c))
perm = RNG.permutation(len(mod))
A = [mod[i] for i in perm[:len(mod)//2]]; B = [mod[i] for i in perm[len(mod)//2:]]
Atree = cKDTree(phase2.ecef(np.array([a["lat"] for a in A]), np.array([a["lon"] for a in A])))

print("=" * 86)
print("TRACK 9 FINAL  scale-matched density-controlled persistence test")
print(f"  historical (pre-1880, geocoded)={len(hist)}  modern-A(strata)={len(A)}  modern-B(target)={len(B)}")
print(f"\n  {'radius':>8}{'nH':>5}{'obs':>9}{'null':>9}{'sd':>7}{'ratio':>8}{'z':>8}{'p':>9}  verdict")
out = {}
for rad in (25, 50, 100, 200):
    hc = collections.Counter(h["c"] for h in hist); bc = collections.Counter(b["c"] for b in B)
    both = {c for c in hc if hc[c] >= 3 and bc.get(c, 0) >= 3}
    H = [h for h in hist if h["c"] in both]; Bk = [b for b in B if b["c"] in both]
    pool = H + Bk
    lab = np.array([1]*len(H) + [0]*len(Bk))
    xyz = phase2.ecef(np.array([p["lat"] for p in pool]), np.array([p["lon"] for p in pool]))
    # density measured at THE TEST RADIUS, from the independent half A
    dens = np.array([len(Atree.query_ball_point(xyz[i], r=phase2.chord(rad)))
                     for i in range(len(pool))])
    qs = np.unique(np.quantile(dens, [0.2, 0.4, 0.6, 0.8]))
    dstrat = np.digitize(dens, qs)
    strat = np.array([f"{p['c']}|{d}" for p, d in zip(pool, dstrat)])
    idx_by = {s: np.flatnonzero(strat == s) for s in set(strat)}
    nh_by = {s: int(lab[v].sum()) for s, v in idx_by.items()}
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
    print(f"  {rad:>7}km{len(H):>5}{obs:>9.2f}{mu:>9.2f}{sd:>7.2f}{obs/max(mu,1e-9):>8.3f}{z:>+8.2f}{p:>9.4f}  {v}")
    out[rad] = dict(n_hist=len(H), obs=obs, null=float(mu), sd=float(sd),
                    ratio=obs/max(mu,1e-9), z=float(z), p=p, n_strata=len(idx_by))
print(f"\n  Bonferroni alpha = 0.05/4 = 0.0125")
json.dump(out, open("/home/user/UFOAI/data/processed/persistence/track9_final.json","w"), indent=1)
