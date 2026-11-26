"""Phase 2c: the DECONTAMINATED nuclear-proximity test.

Phase 2b established that the small-radius signal is driven by three
contamination mechanisms, none of which is "UAP activity near nuclear sites":

  C1 CIRCULARITY. The catalogs contain nuclear detonations themselves as
     timeline entries (Trinity, Hiroshima, Nagasaki, Castle Bravo). Testing
     the corpus against the detonation table partly tests it against itself.
  C2 OBSERVATION-OPPORTUNITY BIAS. Surviving reports come from observers
     stationed AT test sites during tests. Date permutation controls spatial
     confounding but cannot control this, because the observers' presence is
     *caused* by the test programme.
  C3 REPORT FRAMING. The descriptions explicitly reference the test, so the
     coincidence is part of why the record exists at all.

This script removes C1 and C3 explicitly, then re-runs the test. C2 is not
removable from catalogue data and is reported as a hard limitation.
"""
import sys, re, json, collections
import numpy as np
sys.path.insert(0, "/home/user/UFOAI/omega")
import corpus, phase2

NUKE_TEXT = re.compile(r"""atomic|nuclear|atom\s*bomb|a-?bomb|h-?bomb|hydrogen\s+bomb|
 detonat|mushroom\s+cloud|megaton|kiloton|\bkt\b|fission|thermonuclear|
 bikini\s+atoll|enewetak|eniwetok|test\s+site|nevada\s+test|yucca\s+flat|
 frenchman\s+flat|trinity\s+site|maralinga|semipalatinsk|novaya\s+zemlya|
 lop\s+nur|christmas\s+island|johnston\s+(atoll|island)|fallout|radioactive\s+cloud
""", re.I | re.X)

def classify(S):
    clean, c1, c3 = [], [], []
    for e in S:
        d = e["description"] or ""
        # C1: the record IS a detonation / weapons-programme milestone
        if re.search(r"(first|another)?\s*(atomic|nuclear)\s+(bomb|weapon|device|test)|"
                     r"is\s+detonated|detonation\s+of\s+a\s+nuclear|"
                     r"most\s+powerful\s+nuclear|nuclear\s+test:", d, re.I):
            c1.append(e); continue
        # C3: report framing references atomic testing
        if NUKE_TEXT.search(d):
            c3.append(e); continue
        clean.append(e)
    return clean, c1, c3

def main():
    S, nk = phase2.load("inclusive")
    clean, c1, c3 = classify(S)
    print(f"[p2c] sightings total={len(S)}")
    print(f"      C1 removed (record IS a detonation/milestone): {len(c1)}")
    print(f"      C3 removed (description references atomic testing): {len(c3)}")
    print(f"      CLEAN subset: {len(clean)}")
    print("\n  examples of C1 removals:")
    for e in c1[:5]: print(f"    {e['year']}-{e['month']:02d}-{e['day']:02d} {e['description'][:95]}")
    print("\n  examples of C3 removals:")
    for e in c3[:6]: print(f"    {e['year']}-{e['month']:02d}-{e['day']:02d} {e['description'][:95]}")

    D = np.array([corpus.to_jdn(e["year"], e["month"], e["day"]) for e in clean], dtype=np.int64)
    years = np.array([e["year"] for e in clean], dtype=np.int64)
    print(f"\n{'window':<14}{'obs':>6}{'exp':>9}{'ratio':>7}{'z':>8}{'p_cond':>9}  verdict")
    out = {}
    cache = {}
    for (r, tol) in phase2.WINDOWS:
        if r not in cache: cache[r] = phase2.build(clean, nk, r)
        gid, glist = cache[r]
        FM = phase2.fmatrix(glist, D, tol)
        c = phase2.perm_test(gid, FM, years, conditional=True)
        g = phase2.perm_test(gid, FM, years, conditional=False)
        alpha = 0.05 / len(phase2.WINDOWS)
        verdict = "SIGNIFICANT (Bonf)" if c["p"] < alpha else ("nominal" if c["p"] < 0.05 else "null")
        print(f"{r}km_{tol}d{'':<4}{c['observed']:>6}{c['exp_mean']:>9.1f}"
              f"{c['ratio']:>7.2f}{c['z']:>+8.2f}{c['p']:>9.5f}  {verdict}")
        out[f"{r}km_{tol}d"] = dict(radius_km=r, tol_days=tol,
                                    conditional_null=c, global_null=g)
    # ---- yield and type correlation on the clean subset, 500km/30d window
    print("\n### YIELD CORRELATION (clean subset, 500km / 30d)")
    bins = [(0, 10), (10, 100), (100, 1000), (1000, 1e9)]
    gid, glist = cache[500]
    for lo, hi in bins:
        sub = [t for t in nk if t["yield_kt"] is not None and lo <= t["yield_kt"] < hi]
        if len(sub) < 5: continue
        g2, gl2 = phase2.build(clean, sub, 500)
        FM = phase2.fmatrix(gl2, D, 30)
        c = phase2.perm_test(g2, FM, years, nperm=3000, conditional=True)
        print(f"  yield {lo:>5}-{hi if hi<1e8 else 'inf':>6} kt  n_tests={len(sub):<5} "
              f"obs={c['observed']:<6} exp={c['exp_mean']:>7.1f} ratio={c['ratio']:.3f} p={c['p']:.4f}")
    print("\n### TYPE CORRELATION (clean subset, 500km / 30d)")
    for code, label in (("A", "atmospheric/air"), ("U", "underground"), ("W", "underwater")):
        sub = [t for t in nk if len(t["ntype"]) > 1 and t["ntype"][1] == code]
        if len(sub) < 5: continue
        g2, gl2 = phase2.build(clean, sub, 500)
        FM = phase2.fmatrix(gl2, D, 30)
        c = phase2.perm_test(g2, FM, years, nperm=3000, conditional=True)
        print(f"  {label:<18} n_tests={len(sub):<5} obs={c['observed']:<6} "
              f"exp={c['exp_mean']:>7.1f} ratio={c['ratio']:.3f} p={c['p']:.4f}")
    import os
    os.makedirs("/home/user/UFOAI/data/processed/nuclear_proximity", exist_ok=True)
    json.dump(dict(n_total=len(S), n_c1_removed=len(c1), n_c3_removed=len(c3),
                   n_clean=len(clean), windows=out),
              open("/home/user/UFOAI/data/processed/nuclear_proximity/decontaminated.json", "w"), indent=1)

if __name__ == "__main__":
    main()
