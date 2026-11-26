"""PROJECT OMEGA - Phase 5: ICBM facility proximity test.

WHY THIS DESIGN. Individual silo coordinates could not be obtained
(overpass-api.de and its mirror both fail through this session's egress proxy:
ws_closed_mid_exchange on every attempt, including a backgrounded retry loop).
That turns out to matter less than it appears, because the SIGHTING coordinates
are the binding constraint: Hatch geocoded PLACE NAMES to arcminute DMS
(e.g. 'LatLongDMS: 45:45:00 N 04:52:00 E' -> 45.750002, 4.866667), so the
nominal 6-decimal precision is spurious and effective accuracy is ~2-20 km.
A 10 km window is below the resolution of the data. Windows start at 25 km.

The facility layer is therefore wing-field centroids (main-base coordinates,
public and verifiable to ~0.01 deg) with documented activation/deactivation
years. Three nulls, in increasing strength:

  T1 OPERATIONAL-PERIOD EXCESS. Space-time permutation, dates permuted within
     calendar year. Weak: operational windows are decades long, so a
     within-year permutation barely changes 'during', costing power.
  T2 ACTIVATION-EVENT EXCESS. Treats each wing's activation as a dated event
     and asks for excess within R km and +/-T days, exactly as Phase 2 treated
     detonations. Strong, directly comparable to Phase 2.
  T3 DIFFERENCE-IN-DIFFERENCES. Sighting rate near missile fields before vs
     after activation, differenced against the SAME contrast at non-missile
     SAC bomber bases. This is the decisive test: bomber bases are military,
     high-security and nuclear-armed but hold no silos, so the DiD estimand
     isolates 'missile field' from 'military base' and from era.
"""
from __future__ import annotations
import sys, re, json, math, collections
import numpy as np
from scipy import stats
sys.path.insert(0, "/home/user/UFOAI/omega")
import corpus, phase2, phase2c

RNG = np.random.default_rng(19620101)

# ── ICBM wings: (name, lat, lon, activation_year, deactivation_year, n_silos)
# Main-base coordinates; silo fields disperse ~30-120 km around each.
# Activation = first flight on alert; deactivation = last missile removed.
ICBM = [
    ("Malmstrom AFB MT (341st)",    47.505, -111.187, 1962, 2030, 200),
    ("Minot AFB ND (91st)",         48.416, -101.358, 1963, 2030, 150),
    ("Grand Forks AFB ND (321st)",  47.961,  -97.401, 1965, 1998, 150),
    ("Ellsworth AFB SD (44th)",     44.145, -103.104, 1963, 1994, 150),
    ("Whiteman AFB MO (351st)",     38.730,  -93.548, 1963, 1995, 150),
    ("F.E. Warren AFB WY (90th)",   41.133, -104.867, 1963, 2030, 200),
    ("Davis-Monthan AFB AZ (390th)",32.166, -110.883, 1963, 1984, 18),
    ("McConnell AFB KS (381st)",    37.622,  -97.267, 1963, 1986, 18),
    ("Little Rock AFB AR (308th)",  34.917,  -92.150, 1963, 1987, 18),
]
# ── Control: SAC bomber/tanker bases. Military, high-security, nuclear-armed,
# NO silo fields. Dates are the base's SAC bomber-era span.
CONTROL = [
    ("Barksdale AFB LA",   32.502,  -93.663, 1957, 2030),
    ("Dyess AFB TX",       32.421,  -99.855, 1957, 2030),
    ("Fairchild AFB WA",   47.615, -117.656, 1957, 1994),
    ("Castle AFB CA",      37.381, -120.568, 1957, 1995),
    ("Westover AFB MA",    42.198,  -72.535, 1957, 1974),
    ("Loring AFB ME",      46.950,  -67.886, 1957, 1994),
    ("Plattsburgh AFB NY", 44.651,  -73.468, 1957, 1995),
    ("Griffiss AFB NY",    43.234,  -75.407, 1957, 1995),
    ("Pease AFB NH",       43.078,  -70.823, 1957, 1991),
    ("Carswell AFB TX",    32.769,  -97.441, 1957, 1993),
    ("Offutt AFB NE",      41.118,  -95.913, 1957, 2030),
    ("Travis AFB CA",      38.263, -121.928, 1957, 2030),
]

MISSILE_TEXT = re.compile(r"""missile|silo|\bicbm\b|minuteman|titan|peacekeeper|
 \bsac\b|strategic\s+air\s+command|launch\s+(facility|control)|\blcf\b|\blcc\b|
 warhead|nuclear|atomic|atlas\s+missile|nike""", re.I | re.X)

def load_sightings():
    mc = json.load(open("/home/user/UFOAI/data/processed/provenance/master_catalog_inclusive.json"))
    S = [e for e in mc["events"]
         if e["lat"] is not None and e["date_precision"] == "day" and e["year"]]
    clean = [e for e in S if not MISSILE_TEXT.search(e["description"] or "")]
    removed = len(S) - len(clean)
    return S, clean, removed

def dists(S, fac):
    """(n_sight x n_fac) great-circle distance matrix in km."""
    sx = phase2.ecef(np.array([e["lat"] for e in S]), np.array([e["lon"] for e in S]))
    fx = phase2.ecef(np.array([f[1] for f in fac]), np.array([f[2] for f in fac]))
    # chord -> great circle
    d = np.linalg.norm(sx[:, None, :] - fx[None, :, :], axis=2)
    return 2 * phase2.R_E * np.arcsin(np.clip(d / (2 * phase2.R_E), 0, 1))

# ─────────────────────────────────────────────── T1
def t1_operational(S, label):
    print(f"\n  T1  OPERATIONAL-PERIOD EXCESS  [{label}]")
    D = dists(S, ICBM)
    yrs = np.array([e["year"] for e in S])
    act = np.array([f[3] for f in ICBM]); dea = np.array([f[4] for f in ICBM])
    print(f"      {'radius':>8}{'obs':>8}{'exp':>9}{'ratio':>8}{'p':>9}")
    out = {}
    for R in (25, 50, 100, 200, 500):
        near = D <= R
        obs = int(((yrs[:, None] >= act[None, :]) & (yrs[:, None] <= dea[None, :]) & near).any(axis=1).sum())
        null = np.empty(2000, dtype=int)
        for i in range(2000):
            yp = yrs.copy()
            # permute years WITHIN year-block is degenerate here, so permute the
            # year labels globally among sightings (locations fixed).
            RNG.shuffle(yp)
            null[i] = int(((yp[:, None] >= act[None, :]) & (yp[:, None] <= dea[None, :]) & near).any(axis=1).sum())
        mu, sd = null.mean(), null.std(ddof=1)
        p = (1 + int((null >= obs).sum())) / 2001
        print(f"      {R:>7}km{obs:>8}{mu:>9.1f}{obs/max(mu,1e-9):>8.3f}{p:>9.4f}")
        out[R] = dict(obs=obs, exp=float(mu), ratio=obs/max(mu,1e-9), p=p)
    return out

# ─────────────────────────────────────────────── T2
def t2_activation(S, label):
    print(f"\n  T2  ACTIVATION-EVENT EXCESS  [{label}]  (Phase-2 style space-time perm)")
    jd = np.array([corpus.to_jdn(e["year"], e["month"], e["day"]) for e in S])
    yrs = np.array([e["year"] for e in S])
    D = dists(S, ICBM)
    aj = np.array([corpus.to_jdn(f[3], 7, 1) for f in ICBM])
    print(f"      {'window':>16}{'obs':>7}{'exp':>9}{'ratio':>8}{'z':>8}{'p':>9}")
    out = {}
    for R in (25, 50, 100, 200, 500):
        near = D <= R
        for T in (30, 90, 365):
            obs = int((near & (np.abs(jd[:, None] - aj[None, :]) <= T)).sum())
            null = np.empty(2000, dtype=int)
            # conditional (within-year) date permutation, as in Phase 2
            order = np.argsort(yrs, kind="stable")
            bnd = np.flatnonzero(np.r_[True, np.diff(yrs[order]) != 0])
            blocks = [b for b in np.split(order, bnd[1:]) if b.size > 1]
            for i in range(2000):
                pi = np.arange(len(jd))
                for b in blocks: pi[b] = b[RNG.permutation(b.size)]
                null[i] = int((near & (np.abs(jd[pi][:, None] - aj[None, :]) <= T)).sum())
            mu, sd = null.mean(), null.std(ddof=1)
            z = (obs - mu) / sd if sd else float("nan")
            p = (1 + int((null >= obs).sum())) / 2001
            print(f"      {R:>5}km/{T:>4}d{obs:>7}{mu:>9.1f}{obs/max(mu,1e-9):>8.3f}{z:>+8.2f}{p:>9.4f}")
            out[f"{R}km_{T}d"] = dict(obs=obs, exp=float(mu), ratio=obs/max(mu,1e-9),
                                      z=float(z), p=p)
    return out

# ─────────────────────────────────────────────── T3
def t3_did(S, label):
    print(f"\n  T3  DIFFERENCE-IN-DIFFERENCES  [{label}]")
    print("      missile fields vs SAC bomber bases, pre- vs post-activation")
    Di = dists(S, ICBM); Dc = dists(S, CONTROL)
    yrs = np.array([e["year"] for e in S])
    print(f"      {'radius':>8}{'M_pre':>7}{'M_post':>7}{'C_pre':>7}{'C_post':>7}"
          f"{'DiD':>8}{'95% CI':>18}{'p':>9}")
    out = {}
    for R in (25, 50, 100, 200):
        mi = (Di <= R).any(axis=1); ci = (Dc <= R).any(axis=1) & ~mi
        # window: 10 yrs either side of 1963 (median ICBM activation)
        pre = (yrs >= 1953) & (yrs <= 1962)
        post = (yrs >= 1963) & (yrs <= 1972)
        mpre, mpost = int((mi & pre).sum()), int((mi & post).sum())
        cpre, cpost = int((ci & pre).sum()), int((ci & post).sum())
        if min(mpre, mpost, cpre, cpost) < 5:
            print(f"      {R:>7}km{mpre:>7}{mpost:>7}{cpre:>7}{cpost:>7}   (cells too small)")
            continue
        did = (mpost / mpre) / (cpost / cpre)
        # bootstrap CI over sightings
        bs = []
        idx = np.arange(len(S))
        for _ in range(4000):
            b = RNG.choice(idx, size=len(idx), replace=True)
            a1 = int((mi[b] & pre[b]).sum()); a2 = int((mi[b] & post[b]).sum())
            c1 = int((ci[b] & pre[b]).sum()); c2 = int((ci[b] & post[b]).sum())
            if min(a1, a2, c1, c2) > 0: bs.append((a2/a1)/(c2/c1))
        lo, hi = np.percentile(bs, [2.5, 97.5])
        # Fisher exact on the 2x2x2 collapsed to the interaction
        tab = np.array([[mpost, mpre], [cpost, cpre]])
        _, pf = stats.fisher_exact(tab)
        print(f"      {R:>7}km{mpre:>7}{mpost:>7}{cpre:>7}{cpost:>7}{did:>8.3f}"
              f"   [{lo:.3f}, {hi:.3f}]{pf:>9.4f}")
        out[R] = dict(m_pre=mpre, m_post=mpost, c_pre=cpre, c_post=cpost,
                      did=float(did), ci=[float(lo), float(hi)], p_fisher=float(pf))
    return out

def main():
    S, clean, removed = load_sightings()
    print("=" * 84)
    print("PHASE 5  ICBM / LAUNCH-FACILITY PROXIMITY TEST")
    print(f"  sightings (geocoded, day-precision): {len(S)}")
    print(f"  removed as text-contaminated (mention missile/silo/SAC/nuclear): {removed}")
    print(f"  clean subset: {len(clean)}")
    print(f"  ICBM wings: {len(ICBM)}   control SAC bomber bases: {len(CONTROL)}")
    res = {}
    for label, SS in (("ALL", S), ("DECONTAMINATED", clean)):
        print("\n" + "-" * 84)
        print(f"  == {label} (n={len(SS)}) ==")
        res[label] = dict(t1=t1_operational(SS, label), t2=t2_activation(SS, label),
                          t3=t3_did(SS, label))
    ntests = 5 + 15 + 4
    print(f"\n  Bonferroni across {ntests} tests per stratum: alpha = {0.05/ntests:.5f}")
    import os
    os.makedirs("/home/user/UFOAI/data/processed/icbm_proximity", exist_ok=True)
    json.dump(dict(n_all=len(S), n_clean=len(clean), n_removed=removed,
                   n_tests=ntests, bonferroni_alpha=0.05/ntests,
                   icbm=ICBM, control=CONTROL, results=res),
              open("/home/user/UFOAI/data/processed/icbm_proximity/phase5.json", "w"),
              indent=1, default=str)

if __name__ == "__main__":
    main()
