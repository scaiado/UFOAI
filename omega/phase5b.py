"""Phase 5b: RED TEAM the 50 km difference-in-differences result.

Three attacks:
  A PLACEBO ACTIVATION YEARS. Re-run the identical DiD with counterfactual
    'activation' years. If the effect appears for years when nothing was
    activated, it is not about activation.
  B RADIUS MONOTONICITY. A real spatial proximity effect should decay with
    distance, not peak at one ring.
  C EVENT AUDIT. Read the actual post-activation events near missile fields,
    as was done in Phase 2 where it exposed the contamination.
"""
import sys, json, collections
import numpy as np
from scipy import stats
sys.path.insert(0, "/home/user/UFOAI/omega")
import corpus, phase2, phase5

RNG = np.random.default_rng(777001)
S, clean, removed = phase5.load_sightings()

def did_at(SS, R, cut, half=10):
    Di = phase5.dists(SS, phase5.ICBM); Dc = phase5.dists(SS, phase5.CONTROL)
    yrs = np.array([e["year"] for e in SS])
    mi = (Di <= R).any(axis=1); ci = (Dc <= R).any(axis=1) & ~mi
    pre = (yrs >= cut - half) & (yrs < cut)
    post = (yrs >= cut) & (yrs < cut + half)
    a1, a2 = int((mi & pre).sum()), int((mi & post).sum())
    c1, c2 = int((ci & pre).sum()), int((ci & post).sum())
    if min(a1, a2, c1, c2) < 5: return None
    did = (a2 / a1) / (c2 / c1)
    _, p = stats.fisher_exact(np.array([[a2, a1], [c2, c1]]))
    return dict(did=did, p=p, m_pre=a1, m_post=a2, c_pre=c1, c_post=c2)

print("=" * 86)
print("A  PLACEBO ACTIVATION YEARS  (true ICBM activation = 1963)")
print(f"   {'cut year':>10}{'R=25km':>22}{'R=50km':>22}{'R=100km':>22}")
for cut in (1951, 1955, 1959, 1963, 1967, 1971, 1975, 1979, 1983):
    row = f"   {cut:>10}"
    for R in (25, 50, 100):
        r = did_at(clean, R, cut)
        row += f"   DiD={r['did']:>5.2f} p={r['p']:<7.4f}" if r else "            (small)   "
    print(row + ("   <-- TRUE" if cut == 1963 else ""))

print("\n" + "=" * 86)
print("B  RADIUS PROFILE at the true cut (decontaminated)")
print(f"   {'R(km)':>7}{'M_pre':>7}{'M_post':>7}{'C_pre':>7}{'C_post':>7}{'DiD':>8}{'p':>9}")
for R in (10, 25, 40, 50, 60, 75, 100, 150, 200, 300):
    r = did_at(clean, R, 1963)
    if r: print(f"   {R:>7}{r['m_pre']:>7}{r['m_post']:>7}{r['c_pre']:>7}"
                f"{r['c_post']:>7}{r['did']:>8.3f}{r['p']:>9.4f}")
    else: print(f"   {R:>7}   (cells too small)")

print("\n" + "=" * 86)
print("C  EVENT AUDIT: post-1963 events within 50 km of an ICBM wing (decontaminated)")
Di = phase5.dists(clean, phase5.ICBM)
yrs = np.array([e["year"] for e in clean])
sel = np.flatnonzero(((Di <= 50).any(axis=1)) & (yrs >= 1963) & (yrs < 1973))
wing = np.argmin(Di, axis=1)
byw = collections.Counter(phase5.ICBM[wing[i]][0] for i in sel)
print("   by nearest wing:")
for k, v in byw.most_common(): print(f"     {v:>3}  {k}")
print(f"\n   {len(sel)} events; listing all:")
for i in sel:
    e = clean[i]
    print(f"     {e['year']}-{e['month']:02d}-{e['day']:02d} {Di[i].min():>5.1f}km "
          f"{phase5.ICBM[wing[i]][0][:26]:<26} ncat={e['n_catalogs']} "
          f"{(e['location'] or '?')[:26]:<26} {e['description'][:88]}")

print("\n" + "=" * 86)
print("D  CONTROL-SET SENSITIVITY: is the DiD an artifact of control geography?")
print("   The control bases are coastal/eastern; missile fields are Plains/Midwest.")
print("   Re-run restricting BOTH groups to the US interior (lon -105..-90).")
inner = [e for e in clean if -105 <= e["lon"] <= -90 and 30 <= e["lat"] <= 50]
print(f"   interior subset n={len(inner)}")
for R in (25, 50, 100, 200):
    r = did_at(inner, R, 1963)
    print(f"     R={R:>4}km  " + (f"DiD={r['did']:.3f} p={r['p']:.4f} "
          f"(M {r['m_pre']}->{r['m_post']}, C {r['c_pre']}->{r['c_post']})" if r else "(cells too small)"))
