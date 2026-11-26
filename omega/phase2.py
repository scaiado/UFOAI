"""PROJECT OMEGA - Phase 2: the nuclear-proximity test.

Tests whether UAP reports cluster in SPACE AND TIME around nuclear
detonations, against a proper null.

Null model: space-time permutation (Kulldorff). Sighting DATES are permuted
across sightings, holding every location fixed. This automatically controls
all purely spatial confounding -- population, military presence, media
density, observer distribution -- because the spatial marginal is unchanged.
It also holds the temporal marginal fixed (the 1952 flap still exists), so
only the space-TIME association is tested.

Two nulls are run:
  GLOBAL      dates permuted across the whole corpus. Tests space-time
              association, but is confounded by era: Nevada testing and the
              1950s sighting flap coincide in time for unrelated reasons.
  CONDITIONAL dates permuted only WITHIN calendar years. Annual sighting
              totals are preserved exactly, so the "both peaked in the
              1950s" confound is removed. This is the decisive test.

Exact fast algorithm: under date permutation the geometry never changes.
Sightings are grouped by the exact set of detonations within radius r; for
each group the count of in-window detonations is precomputed for every date
in the pool, so one permutation costs a single gather-and-sum.
"""
from __future__ import annotations
import sys, json, math, collections
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, "/home/user/UFOAI/omega")
import corpus

R_E = 6371.0088
WINDOWS = [(50, 1), (50, 7), (50, 30),
           (100, 1), (100, 7), (100, 30),
           (500, 7), (500, 30), (500, 90),
           (1000, 30), (1000, 90), (1000, 180)]
NPERM = 10000
RNG = np.random.default_rng(20261125)

def ecef(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    return np.c_[np.cos(la)*np.cos(lo), np.cos(la)*np.sin(lo), np.sin(la)] * R_E

def chord(km):
    """Euclidean chord length matching a great-circle distance of km."""
    return 2 * R_E * math.sin(km / (2 * R_E))

def load(mode="inclusive"):
    suf = "" if mode == "strict" else f"_{mode}"
    mc = json.load(open(f"/home/user/UFOAI/data/processed/provenance/master_catalog{suf}.json"))
    S = [e for e in mc["events"]
         if e["lat"] is not None and e["date_precision"] == "day" and e["year"]]
    nk = [t for t in corpus.load_nuclear() if t["lat"] is not None and t["prec"] == "day"]
    return S, nk

def build(S, nk, radius_km):
    sxyz = ecef(np.array([e["lat"] for e in S]), np.array([e["lon"] for e in S]))
    txyz = ecef(np.array([t["lat"] for t in nk]), np.array([t["lon"] for t in nk]))
    tree = cKDTree(txyz)
    nbr = tree.query_ball_point(sxyz, r=chord(radius_km))
    tj = np.array([corpus.to_jdn(t["year"], t["month"], t["day"]) for t in nk], dtype=np.int64)
    groups, gid = {}, np.empty(len(S), dtype=np.int32)
    glist = []
    for i, nb in enumerate(nbr):
        key = tuple(sorted(nb))
        if key not in groups:
            groups[key] = len(glist)
            glist.append(np.sort(tj[list(key)]) if key else np.empty(0, dtype=np.int64))
        gid[i] = groups[key]
    return gid, glist

def fmatrix(glist, D, tol):
    """FM[g, j] = number of detonations in group g within tol days of date D[j]."""
    FM = np.zeros((len(glist), len(D)), dtype=np.int16)
    for g, Tg in enumerate(glist):
        if Tg.size == 0: continue
        hi = np.searchsorted(Tg, D + tol, side="right")
        lo = np.searchsorted(Tg, D - tol, side="left")
        FM[g] = (hi - lo).astype(np.int16)
    return FM

def perm_test(gid, FM, years, nperm=NPERM, conditional=False):
    n = len(gid)
    own = np.arange(n)
    observed = int(FM[gid, own].sum())
    null = np.empty(nperm, dtype=np.int64)
    if conditional:
        order = np.argsort(years, kind="stable")
        bounds = np.flatnonzero(np.r_[True, np.diff(years[order]) != 0])
        blocks = np.split(order, bounds[1:])
        blocks = [b for b in blocks if b.size > 1]
    for p in range(nperm):
        if conditional:
            pi = own.copy()
            for b in blocks:
                pi[b] = b[RNG.permutation(b.size)]
        else:
            pi = RNG.permutation(n)
        null[p] = FM[gid, pi].sum()
    # one-sided p: proportion of nulls >= observed (add-one correction)
    pval = (1 + int((null >= observed).sum())) / (nperm + 1)
    mu, sd = float(null.mean()), float(null.std(ddof=1))
    z = (observed - mu) / sd if sd > 0 else float("nan")
    # effect size: observed / expected ratio with bootstrap-free CI from null spread
    ratio = observed / mu if mu > 0 else float("nan")
    lo, hi = np.percentile(null, [2.5, 97.5])
    return dict(observed=observed, exp_mean=mu, exp_sd=sd, null_lo=float(lo),
                null_hi=float(hi), z=z, ratio=ratio, p=pval)

def main():
    S, nk = load("inclusive")
    print(f"[p2] sightings(geocoded,day-prec)={len(S)}  detonations={len(nk)}")
    D = np.array([corpus.to_jdn(e["year"], e["month"], e["day"]) for e in S], dtype=np.int64)
    years = np.array([e["year"] for e in S], dtype=np.int64)
    results = {}
    cache = {}
    for (r, tol) in WINDOWS:
        if r not in cache:
            cache[r] = build(S, nk, r)
        gid, glist = cache[r]
        FM = fmatrix(glist, D, tol)
        g = perm_test(gid, FM, years, conditional=False)
        c = perm_test(gid, FM, years, conditional=True)
        key = f"{r}km_{tol}d"
        results[key] = dict(radius_km=r, tol_days=tol, n_groups=len(glist),
                            global_null=g, conditional_null=c)
        print(f"  {key:<14} groups={len(glist):<5} obs={g['observed']:<7} "
              f"GLOBAL exp={g['exp_mean']:.1f} ratio={g['ratio']:.2f} z={g['z']:+.2f} p={g['p']:.5f} | "
              f"COND exp={c['exp_mean']:.1f} ratio={c['ratio']:.2f} z={c['z']:+.2f} p={c['p']:.5f}",
              flush=True)
    import os
    os.makedirs("/home/user/UFOAI/data/processed/nuclear_proximity", exist_ok=True)
    json.dump(dict(n_sightings=len(S), n_detonations=len(nk), n_perm=NPERM,
                   bonferroni_alpha=0.05/len(WINDOWS), windows=results),
              open("/home/user/UFOAI/data/processed/nuclear_proximity/permutation_tests.json", "w"),
              indent=1)
    print(f"\n[p2] Bonferroni alpha = 0.05/{len(WINDOWS)} = {0.05/len(WINDOWS):.5f}")
    return results

if __name__ == "__main__":
    main()
