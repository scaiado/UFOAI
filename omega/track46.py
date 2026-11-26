"""TRACK 4 + TRACK 6: facility-class proximity with a class-specificity null.

THE NULL PROBLEM. UAP reports and human infrastructure both concentrate where
people are. A naive test ("are sightings closer to bases than to random
points?") is guaranteed to return a huge spurious effect. Relocating facilities
to random country points has the same flaw.

THE FIX. Hold the POOLED set of all facility coordinates fixed and permute the
CLASS labels among them. The null then asks the only interesting question:
given that reports cluster near human infrastructure in general, is there
anything specific about military bases, nuclear facilities or megalithic sites?
Megaliths double as a non-military infrastructure control.
"""
from __future__ import annotations
import sys, json, glob, os, math, collections
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, "/home/user/UFOAI/omega")
import corpus, phase2

WD = "/tmp/claude-0/-home-user/f0aebeb3-1b62-5042-9067-46af83ba9a9d/scratchpad/omega/wd"
MC = "/home/user/UFOAI/data/processed/provenance/master_catalog_inclusive.json"
RNG = np.random.default_rng(4646)
NPERM = 2000

def load_wd():
    cls = {}
    for f in sorted(glob.glob(f"{WD}/*.json")):
        name = os.path.basename(f)[:-5]
        try: d = json.load(open(f))
        except Exception: continue
        b = d.get("results", {}).get("bindings", [])
        pts = []
        for r in b:
            c = r.get("coord", {}).get("value", "")
            m = c.replace("Point(", "").replace(")", "").split()
            if len(m) != 2: continue
            try: lon, lat = float(m[0]), float(m[1])
            except Exception: continue
            if abs(lat) > 90 or abs(lon) > 180: continue
            pts.append((lat, lon, r.get("itemLabel", {}).get("value", "")[:70]))
        if pts: cls[name] = pts
    # merge megalith subclasses
    meg = []
    for k in list(cls):
        if k.startswith("megalith"): meg += cls.pop(k)
    if meg: cls["megalithic_site"] = meg
    return cls

def main():
    cls = load_wd()
    print("=" * 88)
    print("FACILITY LAYERS (Wikidata, coordinates present)")
    for k, v in sorted(cls.items(), key=lambda x: -len(x[1])):
        print(f"  {k:<24}{len(v):>7}")
    mc = json.load(open(MC))
    S = [e for e in mc["events"] if e["lat"] is not None]
    sx = phase2.ecef(np.array([e["lat"] for e in S]), np.array([e["lon"] for e in S]))
    print(f"  geocoded UAP events: {len(S)}")

    names = sorted(cls, key=lambda k: -len(cls[k]))
    pooled = [(la, lo, k) for k in names for (la, lo, _n) in cls[k]]
    plat = np.array([p[0] for p in pooled]); plon = np.array([p[1] for p in pooled])
    plab = np.array([p[2] for p in pooled])
    pxyz = phase2.ecef(plat, plon)
    counts = {k: int((plab == k).sum()) for k in names}
    print(f"  pooled facility points: {len(pooled)}")

    def median_nn(sel_mask):
        t = cKDTree(pxyz[sel_mask])
        d, _ = t.query(sx, k=1)
        gc = 2 * phase2.R_E * np.arcsin(np.clip(d / (2 * phase2.R_E), 0, 1))
        return float(np.median(gc)), gc

    # ---- spatial strata: 5-degree grid cells. Permuting class labels GLOBALLY
    # is invalid here because the classes have disjoint geographic footprints
    # (US-only military layers vs Europe-only megaliths): a mixed random subset
    # covers more of the event distribution than any single class, so every
    # class spuriously looks "farther than chance". Permuting WITHIN grid cells
    # preserves each class's footprint and tests only class identity.
    gcell = (np.floor(plat / 5).astype(int) * 1000 + np.floor(plon / 5).astype(int))
    cells = {}
    for i, c in enumerate(gcell): cells.setdefault(c, []).append(i)
    cellarr = {c: np.array(v) for c, v in cells.items()}
    print(f"  spatial strata (5-degree cells containing facilities): {len(cellarr)}")

    print("\n" + "=" * 88)
    print("CLASS-SPECIFICITY TEST  (coords fixed, class labels permuted WITHIN 5-deg cells)")
    print(f"  {'class':<22}{'n':>6}{'obs med km':>12}{'null med km':>13}{'ratio':>8}"
          f"{'z':>8}{'p':>9}")
    out = {}
    for k in names:
        mask = plab == k
        obs, gcobs = median_nn(mask)
        # per-cell count of this class, so the null preserves the footprint
        percell = {c: int(mask[v].sum()) for c, v in cellarr.items()}
        percell = {c: n for c, n in percell.items() if n > 0}
        null = np.empty(NPERM)
        for i in range(NPERM):
            pick = []
            for c, n in percell.items():
                v = cellarr[c]
                pick.append(RNG.choice(v, size=min(n, len(v)), replace=False))
            pick = np.concatenate(pick)
            m2 = np.zeros(len(pooled), dtype=bool); m2[pick] = True
            t = cKDTree(pxyz[m2]); d, _ = t.query(sx, k=1)
            null[i] = np.median(2 * phase2.R_E * np.arcsin(np.clip(d/(2*phase2.R_E), 0, 1)))
        mu, sd = null.mean(), null.std(ddof=1)
        z = (obs - mu) / sd if sd else float("nan")
        # one-sided: sightings CLOSER than null => smaller distance
        p = (1 + int((null <= obs).sum())) / (NPERM + 1)
        print(f"  {k:<22}{counts[k]:>6}{obs:>12.1f}{mu:>13.1f}{obs/max(mu,1e-9):>8.3f}"
              f"{z:>+8.2f}{p:>9.4f}")
        out[k] = dict(n=counts[k], obs_median_km=obs, null_median_km=float(mu),
                      null_sd=float(sd), ratio=obs/max(mu,1e-9), z=float(z), p=p,
                      frac_within_10km=float((gcobs <= 10).mean()),
                      frac_within_50km=float((gcobs <= 50).mean()))
    alpha = 0.05 / len(names)
    print(f"\n  Bonferroni alpha = 0.05/{len(names)} = {alpha:.5f}")
    print(f"\n  {'class':<22}{'% events <=10km':>17}{'% <=50km':>11}")
    for k in names:
        print(f"  {k:<22}{out[k]['frac_within_10km']*100:>16.2f}%{out[k]['frac_within_50km']*100:>10.1f}%")

    # ---- TRACK 6: are UAP hotspots near facilities at all, in absolute terms?
    print("\n" + "=" * 88)
    print("TRACK 6  ABSOLUTE PROXIMITY (not class-specific): nearest ANY facility")
    t = cKDTree(pxyz); d, _ = t.query(sx, k=1)
    gc = 2 * phase2.R_E * np.arcsin(np.clip(d/(2*phase2.R_E), 0, 1))
    for q in (5, 10, 25, 50, 100, 250):
        print(f"    within {q:>4} km of any catalogued facility: "
              f"{(gc<=q).mean()*100:>5.2f}%  ({int((gc<=q).sum())} events)")
    print(f"    median distance to nearest facility: {np.median(gc):.1f} km")
    os.makedirs("/home/user/UFOAI/data/processed/convergence", exist_ok=True)
    json.dump(dict(layers={k: len(v) for k, v in cls.items()}, n_events=len(S),
                   class_specificity=out, bonferroni_alpha=alpha),
              open("/home/user/UFOAI/data/processed/convergence/track46.json", "w"), indent=1)
    print("\n  wrote data/processed/convergence/track46.json")

if __name__ == "__main__":
    main()
