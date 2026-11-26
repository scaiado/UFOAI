"""Phase 2b: identify the specific sighting/detonation pairs driving the
small-radius signal, and check the obvious alternative explanation --
that the 'UAP sighting' IS the detonation, seen and reported."""
import sys, json, numpy as np
sys.path.insert(0, "/home/user/UFOAI/omega")
import corpus, phase2

S, nk = phase2.load("inclusive")
tj = np.array([corpus.to_jdn(t["year"], t["month"], t["day"]) for t in nk])
sj = np.array([corpus.to_jdn(e["year"], e["month"], e["day"]) for e in S])

for radius, tol in ((50, 30), (100, 7)):
    print("=" * 100)
    print(f"### CONTRIBUTING PAIRS: within {radius} km and {tol} days")
    rows = []
    for i, e in enumerate(S):
        for t_i, t in enumerate(nk):
            if abs(sj[i] - tj[t_i]) > tol: continue
            d = corpus.haversine(e["lat"], e["lon"], t["lat"], t["lon"])
            if d > radius: continue
            rows.append((d, sj[i] - tj[t_i], e, t))
    rows.sort(key=lambda r: (abs(r[1]), r[0]))
    for d, dt, e, t in rows:
        print(f"  {d:6.1f}km {dt:+4d}d  {e['year']}-{e['month']:02d}-{e['day']:02d}  "
              f"[{','.join(e['catalogs'])}] ncat={e['n_catalogs']}")
        print(f"      TEST: {t['name']} ({t['country']}, {t['ntype']}, "
              f"{t['yield_kt']}kt, depth {t['depth_km']}km) {t['year']}-{t['month']:02d}-{t['day']:02d}")
        print(f"      SIGHT: {(e['location'] or '?')[:60]} | {e['description'][:170]}")
    print(f"  --- {len(rows)} pairs ---\n")
