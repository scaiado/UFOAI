"""OCCUPANT TAXONOMY MULTIMODALITY TEST.

If reported occupants were distinct biological populations, the categories
should behave like species: co-occurring LESS than chance, and segregating in
space and time into coherent ranges. If they are a single narrative space, they
should co-occur at chance and correlate with era and culture instead.

Hatch's six occupant categories:
  OID small alien / "Grey"      PSH pseudo-human / clone / organic robot
  GNT giant / tall              RBT possible robot, mechanical motions
  MON monster, fits no category FIG undefined or poorly seen figure

Four tests, each with an explicit null:
  A CO-OCCURRENCE   observed pair counts vs a null permuting category labels
                    within code-count strata (so verbosity is held fixed)
  B SPATIAL         mean within-category nearest-neighbour distance vs a null
                    permuting category labels among occupant events only
  C TEMPORAL        same statistic on dates
  D ERA DEPENDENCE  mutual information with era, the cultural-construction
                    prediction, measured the same way as Phase 3
"""
from __future__ import annotations
import sys, json, math, collections, itertools
import numpy as np
from scipy import stats
from scipy.spatial import cKDTree
sys.path.insert(0, "/home/user/UFOAI/omega")
import corpus, phase2, phase6

RNG = np.random.default_rng(606)
CATS = ["OID", "PSH", "GNT", "RBT", "MON", "FIG"]
NAMES = {"OID": "small alien/Grey", "PSH": "pseudo-human/clone", "GNT": "giant",
         "RBT": "robot/mechanical", "MON": "monster/no category",
         "FIG": "undefined figure"}
ERAS = [("pre-ind", -9999, 1800), ("industrial", 1800, 1945), ("atomic", 1945, 1957),
        ("space age", 1957, 1990), ("digital", 1990, 2030)]

def main():
    recs, _ = corpus.load_all()
    H = [r for r in recs if r.catalog == "Hatch_UDB"]
    ev = [r for r in H if set(r.attrs) & set(CATS)]
    print("=" * 84)
    print("OCCUPANT TAXONOMY MULTIMODALITY TEST")
    print(f"  Hatch records: {len(H)}   with >=1 occupant category: {len(ev)}")
    cnt = {c: sum(1 for r in ev if c in r.attrs) for c in CATS}
    print(f"\n  {'code':<6}{'name':<24}{'n':>6}{'share of occupant events':>26}")
    for c in CATS:
        print(f"  {c:<6}{NAMES[c]:<24}{cnt[c]:>6}{cnt[c]/len(ev)*100:>24.1f}%")
    multi = sum(1 for r in ev if len(set(r.attrs) & set(CATS)) > 1)
    print(f"\n  events carrying >1 occupant category: {multi} ({multi/len(ev)*100:.1f}%)")

    # ---------------------------------------------------------------- A
    print("\n" + "=" * 84)
    print("A  CO-OCCURRENCE  (null: category labels permuted within code-count strata)")
    ncodes = np.array([len(r.attrs) for r in ev])
    q = np.quantile(ncodes, [.2, .4, .6, .8])
    strat = np.digitize(ncodes, q)
    M = np.array([[1 if c in r.attrs else 0 for c in CATS] for r in ev], dtype=np.int8)
    obs = {}
    for i, j in itertools.combinations(range(6), 2):
        obs[(i, j)] = int(((M[:, i] == 1) & (M[:, j] == 1)).sum())
    NP = 4000
    null = {k: np.empty(NP) for k in obs}
    idx_by = {s: np.flatnonzero(strat == s) for s in np.unique(strat)}
    for t in range(NP):
        Mp = M.copy()
        for col in range(6):
            for s, v in idx_by.items():
                Mp[v, col] = M[v, col][RNG.permutation(v.size)]
        for i, j in itertools.combinations(range(6), 2):
            null[(i, j)][t] = int(((Mp[:, i] == 1) & (Mp[:, j] == 1)).sum())
    print(f"  {'pair':<16}{'obs':>6}{'exp':>8}{'ratio':>8}{'p_less':>9}{'p_more':>9}")
    seg = 0
    for i, j in itertools.combinations(range(6), 2):
        o = obs[(i, j)]; n = null[(i, j)]
        mu = n.mean()
        pl = (1 + int((n <= o).sum())) / (NP + 1)
        pm = (1 + int((n >= o).sum())) / (NP + 1)
        flag = ""
        if pl < 0.05/15: flag = " <- fewer than chance"; seg += 1
        if pm < 0.05/15: flag = " <- MORE than chance"
        print(f"  {CATS[i]+'+'+CATS[j]:<16}{o:>6}{mu:>8.1f}{o/max(mu,1e-9):>8.2f}"
              f"{pl:>9.4f}{pm:>9.4f}{flag}")
    print(f"\n  pairs co-occurring significantly LESS than chance (Bonferroni 15): {seg}/15")
    print("  Distinct biological populations predict many such pairs. A single")
    print("  narrative space predicts none, or co-occurrence in EXCESS of chance.")

    # ---------------------------------------------------------------- B, C
    geo = [r for r in ev if r.lat is not None]
    print("\n" + "=" * 84)
    print(f"B  SPATIAL SEGREGATION  (geocoded occupant events: {len(geo)})")
    xyz = phase2.ecef(np.array([r.lat for r in geo]), np.array([r.lon for r in geo]))
    tree = cKDTree(xyz)
    lab = np.array([next((c for c in CATS if c in r.attrs), None) for r in geo])
    def within_nn(labels):
        tot, n = 0.0, 0
        for c in CATS:
            m = np.flatnonzero(labels == c)
            if m.size < 5: continue
            t = cKDTree(xyz[m])
            d, _ = t.query(xyz[m], k=2)
            gc = 2*phase2.R_E*np.arcsin(np.clip(d[:, 1]/(2*phase2.R_E), 0, 1))
            tot += gc.sum(); n += gc.size
        return tot/max(n, 1)
    o = within_nn(lab)
    nl = np.array([within_nn(lab[RNG.permutation(len(lab))]) for _ in range(2000)])
    p = (1 + int((nl <= o).sum())) / 2001
    print(f"  mean within-category nearest-neighbour distance: obs={o:.1f} km  "
          f"null={nl.mean():.1f}+/-{nl.std(ddof=1):.1f}  ratio={o/nl.mean():.3f}  p={p:.4f}")
    print("  (segregated populations => observed SMALLER than null)")

    print("\nC  TEMPORAL SEGREGATION")
    dt = [r for r in ev if r.year]
    jd = np.array([corpus.to_jdn(r.year, r.month, r.day) for r in dt], dtype=float)
    labt = np.array([next((c for c in CATS if c in r.attrs), None) for r in dt])
    def within_t(labels):
        tot, n = 0.0, 0
        for c in CATS:
            m = np.flatnonzero(labels == c)
            if m.size < 5: continue
            s = np.sort(jd[m])
            d = np.diff(s)
            tot += d.sum(); n += d.size
        return tot/max(n, 1)
    o2 = within_t(labt)
    nl2 = np.array([within_t(labt[RNG.permutation(len(labt))]) for _ in range(2000)])
    p2 = (1 + int((nl2 <= o2).sum())) / 2001
    print(f"  mean within-category consecutive gap: obs={o2:.1f} d  "
          f"null={nl2.mean():.1f}+/-{nl2.std(ddof=1):.1f}  ratio={o2/nl2.mean():.3f}  p={p2:.4f}")

    # ---------------------------------------------------------------- D
    print("\n" + "=" * 84)
    print("D  ERA DEPENDENCE  (the cultural-construction prediction)")
    def era_of(y):
        for nm, lo, hi in ERAS:
            if lo <= y < hi: return nm
        return None
    enames = [e[0] for e in ERAS]
    sub = [r for r in ev if r.year and era_of(r.year)]
    ei = np.array([enames.index(era_of(r.year)) for r in sub])
    print(f"  {'code':<6}" + "".join(f"{e[:9]:>11}" for e in enames) + f"{'MI(bits)':>11}{'chi2 p':>11}")
    tab = []
    for c in CATS:
        x = np.array([1 if c in r.attrs else 0 for r in sub])
        row = [int(((x == 1) & (ei == i)).sum()) for i in range(len(enames))]
        tab.append(row)
        fr = [row[i]/max(1, int((ei == i).sum())) for i in range(len(enames))]
        mi = phase6.mi_bits(x, ei) if hasattr(phase6, "mi_bits") else float("nan")
        # compute MI directly
        mi = 0.0
        for a in (0, 1):
            pa = (x == a).mean()
            for b in range(len(enames)):
                pb = (ei == b).mean(); pab = ((x == a) & (ei == b)).mean()
                if pab > 0 and pa > 0 and pb > 0: mi += pab*math.log2(pab/(pa*pb))
        t2 = np.array([[row[i], int((ei == i).sum())-row[i]] for i in range(len(enames))]).T
        t2 = t2[:, t2.sum(axis=0) > 0]
        try: _, pv, _, _ = stats.chi2_contingency(t2)
        except Exception: pv = float("nan")
        print(f"  {c:<6}" + "".join(f"{f*100:>10.1f}%" for f in fr) + f"{mi:>11.5f}{pv:>11.2e}")
    T = np.array(tab)
    chi2, pv, dof, _ = stats.chi2_contingency(T[:, T.sum(axis=0) > 0])
    v = math.sqrt(chi2/(T.sum()*(min(T.shape)-1)))
    print(f"\n  OMNIBUS category x era: chi2={chi2:.1f} dof={dof} p={pv:.3e} Cramer's V={v:.4f}")
    import os
    os.makedirs("/home/user/UFOAI/data/processed/occupants", exist_ok=True)
    json.dump(dict(n_occupant_events=len(ev), counts=cnt, multi_category=multi,
                   spatial=dict(obs=o, null=float(nl.mean()), p=p),
                   temporal=dict(obs=o2, null=float(nl2.mean()), p=p2),
                   era=dict(chi2=float(chi2), dof=int(dof), p=float(pv), cramers_v=float(v))),
              open("/home/user/UFOAI/data/processed/occupants/taxonomy_test.json", "w"), indent=1)

if __name__ == "__main__":
    main()
