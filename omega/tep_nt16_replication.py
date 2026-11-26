#!/usr/bin/env python3
"""Replication of GEPAN Note Technique No. 16 (CT/GEPAN-00013, Enquete 81/01,
1 March 1983) -- the Trans-en-Provence physical-trace analysis.

Every number in DATA below was transcribed by eye from the page image of
Note_techn16-R.pdf (GEIPAN case 1981-01-00849) and is cited by PDF page.
PDF page = printed page + 1 (PDF p.50 carries the printed folio "- 49 -").
Nothing here is estimated from figures; values only shown in figures
(Fig. 9, methyl-/proto-chlorophyllides) are NOT used.

Run:  python3 -I omega/tep_nt16_replication.py  > omega/reports/tep_nt16_replication_out.txt
Deterministic: exact permutation enumeration, Monte Carlo seeded.
"""
import itertools
import math
import json
import numpy as np
from scipy import stats

RNG = np.random.default_rng(19810108)

# ---------------------------------------------------------------- series 2
# NT16 PDF p.43 (sample list): E-1 d=0, E-2 d=1.5, E-3 d=2.1, E-4 d=3.5,
# E-5 d=10, E-6 d=10. Per-leaf fresh mass P (mg/leaf), same page.
D = np.array([0.0, 1.5, 2.1, 3.5, 10.0, 10.0])
P_LEAF = np.array([9.6, 9.88, 2.90, 2.82, 12.0, 4.87])
N_LEAVES = np.array([8, 8, 18, 16, 8, 15])

# NT16 PDF p.50, Tableau 2, checked cell by cell against the INRA handwritten
# original, Analyses2_INRA-R.pdf p.23 ("Tableau 8", units nmoles/mg). One cell differs.
T2 = {
    "ChlA":    [0.005, 0.010, 0.016, 0.017, 0.021, 0.0082],
    "ChlA'":   [0.353, 1.08, 1.14, 1.17, 1.25, 1.28],
    "ChlA''":  [0.0,   0.008, 0.0088, 0.0116, 0.0281, 0.0398],  # E-1 printed "trace" -> 0
    # NT16 p.50 prints E-1 ChlB = 0,930. The handwritten INRA original of the same table
    # (Analyses2_INRA-R.pdf p.23, "Tableau 8", nmoles/mg) reads 0,030. 0,930 is a
    # transcription error in NT16; we use the INRA original. See section 2b.
    "ChlB":    [0.030, 0.031, 0.030, 0.037, 0.049, 0.031],
    "ChlB'":   [0.13, 0.23, 0.22, 0.15, 0.18, 0.14],
    "PhA'":    [0.174, 0.21, 0.16, 0.12, 0.098, 0.026],
    "PhA":     [0.27, 0.50, 0.61, 0.58, 0.53, 0.50],
    "bCar":    [0.090, 0.106, 0.12, 0.158, 0.195, 0.251],
    "Lut":     [0.089, 0.087, 0.123, 0.140, 0.175, 0.287],
    "Vx+Nx+Chlide": [0.327, 0.538, 0.468, 0.746, 0.592, 0.655],
    "PChld4":  [0.061, 0.13, 0.12, 0.18, 0.13, 0.13],
    "PChld3":  [0.071, 0.23, 0.21, 0.20, 0.16, 0.16],
}
T2 = {k: np.array(v) for k, v in T2.items()}

# NT16 PDF p.58, Tableau 7 (co-factors, series 2). E-1 Tc carries "± 1,2".
T7 = {
    "VitA-deriv": [44, 0, 0, 0, 0, 0],
    "Tq":  [32, 21, 17, 10.6, 8.7, 6.6],
    "Tc":  [14.4, 4.8, 4.3, 1.8, 1.7, 0.8],
    "C-P": [71.5, 5.7, 3.7, 0.8, 0.6, 0.2],
    "Deriv5'": [14.9, 6, 33, 14, 6.7, 5.0],
}
T7 = {k: np.array(v, float) for k, v in T7.items()}

# ---------------------------------------------------------------- series 1
# NT16 PDF p.46, Tableau 1. N-15 young control (20 m, collected 23.01.81 = J+15),
# N-8 young exposed (1.5 m, 09.01.81 = J+1), N-11 aged control (20 m, J+15),
# N-4 aged exposed (1.5 m, J+1). Dates: NT16 PDF p.42 and p.33.
T1 = {  # pigment: (N-15, N-8, N-11, N-4)
    "Chlorophylle A": (0.87, 0.58, 0.81, 0.54),
    "Chlorophylle B": (0.62, 0.45, 0.51, 0.37),
    "Chl (A+B)":      (1.49, 1.03, 1.32, 0.91),
    "Pheophytine A":  (0.73, 0.44, 0.29, 0.20),
    "beta-carotene":  (0.21, 0.09, 0.20, 0.10),
    "Luteine":        (0.32, 0.28, 0.34, 0.24),
    "Violaxanthine":  (0.15, 0.030, 0.17, 0.11),
    "Neoxanthine+chlorophyllides": (0.28, 0.30, 0.26, 0.25),
}
CV_SERIES1 = 0.22  # NT16 PDF p.45: "Les coefficients de variation atteignent C = 0,22 pour 3 mesures"

# NT16 PDF p.65 (printed 64): Arabidopsis gamma benchmark at 10^6 rad (Bounias 1973).
GAMMA_1E6 = {"Chlorophylle A": -30, "Chlorophylle B": -46, "Violaxanthine": -40,
             "Luteine": -30, "beta-carotene": -20}

# ---------------------------------------------------------------- reported stats
# What NT16 says it found, with page, so each can be checked.
REPORTED = [
    # (label, y-function, x-transform, N, reported r, reported P, page)
    ("SumChlA ~ d", "SumChlA", "d", 6, +0.6868, None, "p.50"),
    ("SumChlA/SumChlB ~ d", "ratioAB", "d", 6, +0.7509, 0.031, "p.51"),
    ("SumChlA/SumChlB ~ 1/(d+1)", "ratioAB", "inv", 6, -0.891, 0.0039, "p.51"),
    ("SumPhA/SumChlA ~ 1/(d+1)", "PhA_tot/ChlA", "inv", 6, +0.990, None, "p.51"),
    ("PhA'/SumChlA ~ 1/(d+1)", "PhA'/ChlA", "inv", 6, +0.993, None, "p.51"),
    ("ln(PhA'/SumChlA) ~ ln(d+1)", "lnPhA'/ChlA", "ln", 5, 0.916, 0.28e-3, "p.52"),
    ("beta-carotene ~ d", "bCar", "d", 6, 0.945, 0.0022, "p.52 Tab.3"),
    ("Luteine ~ d", "Lut", "d", 6, 0.871, 0.012, "p.52 Tab.3"),
    ("ln Tq ~ ln(d+1)", "lnTq", "ln", 6, -0.973, 0.00054, "p.60 Tab.8"),
    ("ln Tc ~ ln(d+1)", "lnTc", "ln", 6, -0.951, 0.0018, "p.60 Tab.8"),
    ("ln C-P ~ ln(d+1)", "lnC-P", "ln", 6, -0.961, 0.0011, "p.60 Tab.8"),
]


def derived(t2, t7):
    sA = t2["ChlA"] + t2["ChlA'"] + t2["ChlA''"]
    sB = t2["ChlB"] + t2["ChlB'"]
    sPh = t2["PhA"] + t2["PhA'"]
    return {
        "SumChlA": sA, "SumChlB": sB, "SumChl": sA + sB,
        "ratioAB": sA / sB,
        "PhA_tot/ChlA": sPh / sA,
        "PhA'/ChlA": t2["PhA'"] / sA,
        "lnPhA'/ChlA": np.log(t2["PhA'"] / sA),
        "bCar": t2["bCar"], "Lut": t2["Lut"],
        "Vx+Nx+Chlide": t2["Vx+Nx+Chlide"],
        "PhA": t2["PhA"], "PhA'": t2["PhA'"],
        "PChld3": t2["PChld3"], "PChld4": t2["PChld4"],
        "lnTq": np.log(t7["Tq"]), "lnTc": np.log(t7["Tc"]), "lnC-P": np.log(t7["C-P"]),
    }


def xform(d, kind):
    return {"d": d, "inv": 1.0 / (d + 1.0), "ln": np.log(d + 1.0)}[kind]


def pearson(x, y):
    return float(np.corrcoef(x, y)[0, 1])


def exact_perm(x, y, stat=pearson):
    """Two-sided exact permutation p over all n! label orderings."""
    obs = abs(stat(x, y))
    n = len(x)
    hits = tot = 0
    for perm in itertools.permutations(range(n)):
        tot += 1
        if abs(stat(x[list(perm)], y)) >= obs - 1e-12:
            hits += 1
    return hits / tot


# ---------------------------------------------------------------- soil, LDP
# Analyse_LDP-R.pdf, spark-source mass spectrometry, letter dated 23 Oct 1981 (p.2).
# Four result sheets read by eye from the page images: PDF p.5 "Echantillon terre"
# plaque 4571; p.8 "Depot sur terre" plaque 4571; p.11 "Depot sur terre" plaque 4574;
# p.14 "Echantillon terre" plaque 4574. ppm unless %; '%' converted x1e4.
# The lab states (p.4, p.7, p.10, p.13): semi-quantitative, "a un facteur trois pres",
# no sensitivity correction, alkalis over- and heavy metals under-estimated.
# Interpretation that 4571/4574 are two plates of the same two samples is INFERRED from
# the identical sample names on both plates and the letter's "deux echantillons" (p.2).
# Excluded: values given as L (below detection) or < (upper bound only); Na on the
# p.8 sheet (written "913%", physically impossible, UNREADABLE).
LDP = {  # element: (soil_4571, deposit_4571, deposit_4574, soil_4574)
    "C": (2e4, 6.1e4, 20e4, 61e4), "Mg": (4400, 3000, 1.5e4, 2e4), "Si": (3.3e4, 3.4e4, 5.6e4, 25e4),
    "P": (57, 580, 3800, 880), "S": (1400, 430, 1400, 6460), "Cl": (172, 88, 290, 1330),
    "K": (3.1e4, 3.2e4, 0.7e4, 4.8e4), "Ca": (10.7e4, 24e4, 36e4, 36e4), "Sc": (8.3, 170, 560, 1275),
    "Ti": (480, 1600, 3500, 1.6e4), "V": (9.4, 95, 94, 430), "Cr": (10.2, 310, 110, 527),
    "Mn": (100, 670, 680, 1560), "Fe": (2240, 3400, 10e4, 14.4e4), "Co": (2.2, 2.2, 11, 50),
    "Ni": (3.2, 1.1, 11, 74), "Cu": (3.4, 1.7, 37, 170), "Ga": (12, 43, 71, 212), "As": (1.4, 4.2, 4.6, 21),
    "Rb": (65, 66, 93, 3340), "Sr": (106, 50, 160, 2520), "I": (2.3, 24, 2.3, 10.8), "Ba": (3.5, 36, 77, 540),
    "La": (2.5, 1.7, 8.6, 118),
}
LDP_CENSORED = {"Zn": "4571: soil 8.6, deposit 88; 4574: deposit <140, soil <665 (upper bounds only)",
                "Pb": "4571: soil L7.4, deposit 15; 4574: deposit 49, soil 112",
                "Na": "4571: soil 840, deposit UNREADABLE ('913%'); 4574: deposit 1400, soil 1955"}


def soil(out):
    section("7. Soil: LDP spark-source mass spec (Analyse_LDP-R.pdf pp.5,8,11,14)")
    el = list(LDP)
    a = np.log10(np.array([LDP[e] for e in el], float))
    s1, d1, d2, s2 = a.T
    rep_soil = s2 - s1            # same soil sample, plate 4574 vs 4571
    rep_dep = d2 - d1             # same deposit sample, plate 4574 vs 4571
    lr1 = d1 - s1                 # deposit/soil on plate 4571
    lr2 = d2 - s2                 # deposit/soil on plate 4574
    print("Replicate agreement (same sample, two plates), |log10 ratio|:")
    print(f"  soil   : median {np.median(np.abs(rep_soil)):.2f} dex (x{10**np.median(np.abs(rep_soil)):.1f}), "
          f"max {np.max(np.abs(rep_soil)):.2f} dex (x{10**np.max(np.abs(rep_soil)):.0f}, {el[int(np.argmax(np.abs(rep_soil)))]})")
    print(f"  deposit: median {np.median(np.abs(rep_dep)):.2f} dex (x{10**np.median(np.abs(rep_dep)):.1f}), "
          f"max {np.max(np.abs(rep_dep)):.2f} dex (x{10**np.max(np.abs(rep_dep)):.0f}, {el[int(np.argmax(np.abs(rep_dep)))]})")
    n3 = int(np.sum(np.abs(rep_soil) > math.log10(3)))
    print(f"  soil replicates outside the lab's own factor-3 tolerance: {n3}/{len(el)}")
    print("Deposit/soil contrast, |log10 ratio|:")
    print(f"  plate 4571 median {np.median(np.abs(lr1)):.2f} dex; plate 4574 median {np.median(np.abs(lr2)):.2f} dex")
    print(f"  plate-wide offset (median log ratio): 4571 {np.median(lr1):+.2f}, 4574 {np.median(lr2):+.2f}")
    c1 = lr1 - np.median(lr1); c2 = lr2 - np.median(lr2)
    print(f"  agreement of the two plates on WHICH elements are enriched: Spearman rho(c1,c2) = "
          f"{stats.spearmanr(c1, c2)[0]:+.3f} (P={stats.spearmanr(c1, c2)[1]:.3g})")
    thr = math.log10(3)
    both = [e for e, x, y in zip(el, c1, c2) if x > thr and y > thr]
    print(f"  elements enriched in deposit beyond x3 (after plate-median centring) on BOTH plates: {both}")
    for e in ("P", "Fe", "Cr", "Mn", "Ca", "C"):
        i = el.index(e)
        print(f"    {e:3s} deposit/soil 4571 x{10**lr1[i]:.2f}, 4574 x{10**lr2[i]:.2f}; centred x{10**c1[i]:.2f}, x{10**c2[i]:.2f}")
    # null: shuffle plate-2 element labels, count elements enriched on both
    rng = np.random.default_rng(4571)
    nb = np.array([np.sum((c1 > thr) & (rng.permutation(c2) > thr)) for _ in range(20000)])
    print(f"  null (shuffle element labels on one plate, 20k): mean {nb.mean():.2f} elements enriched on both; "
          f"P(>= {len(both)}) = {(nb >= len(both)).mean():.3f}")
    for k, v in LDP_CENSORED.items():
        print(f"  censored/unreadable {k}: {v}")
    out["soil"] = dict(rep_soil_median_dex=float(np.median(np.abs(rep_soil))),
                       rep_soil_outside_x3=n3, n_elements=len(el), both_enriched=both,
                       p_both=float((nb >= len(both)).mean()))


def section(t):
    print("\n" + "=" * 78 + "\n" + t + "\n" + "=" * 78)


def main():
    out = {}
    V = derived(T2, T7)

    # ---------------------------------------------------- 1. series 1 effects
    section("1. Series 1 (Tableau 1, NT16 p.46): exposed vs 20 m control, n=1 pooled sample per cell")
    print("Percent change with 95% interval from analytical CV=0.22 (p.45), Monte Carlo 200k.")
    print("NB: this interval covers ANALYTICAL noise only. There is no biological replicate,")
    print("so between-plant / between-microsite variance is unestimated and the true interval is wider.")
    res1 = {}
    for pig, (c_y, e_y, c_o, e_o) in T1.items():
        row = {}
        for age, c, e in (("young", c_y, e_y), ("aged", c_o, e_o)):
            pt = 100 * (e / c - 1)
            sim_c = c * (1 + CV_SERIES1 * RNG.standard_normal(200_000))
            sim_e = e * (1 + CV_SERIES1 * RNG.standard_normal(200_000))
            ok = (sim_c > 0) & (sim_e > 0)
            r = 100 * (sim_e[ok] / sim_c[ok] - 1)
            lo, hi = np.percentile(r, [2.5, 97.5])
            # one-sided prob that a NULL (true ratio 1) gives a drop at least this large
            null_c = c * (1 + CV_SERIES1 * RNG.standard_normal(200_000))
            null_e = c * (1 + CV_SERIES1 * RNG.standard_normal(200_000))
            okn = (null_c > 0) & (null_e > 0)
            nr = 100 * (null_e[okn] / null_c[okn] - 1)
            p_null = float(np.mean(nr <= pt)) if pt < 0 else float(np.mean(nr >= pt))
            row[age] = dict(pct=round(pt, 1), lo=round(lo, 1), hi=round(hi, 1), p_null_analytical=round(p_null, 4))
        g = GAMMA_1E6.get(pig)
        res1[pig] = row
        print(f"  {pig:30s} young {row['young']['pct']:+6.1f}% [{row['young']['lo']:+6.1f},{row['young']['hi']:+6.1f}] p0={row['young']['p_null_analytical']:.4f}"
              f" | aged {row['aged']['pct']:+6.1f}% [{row['aged']['lo']:+6.1f},{row['aged']['hi']:+6.1f}] p0={row['aged']['p_null_analytical']:.4f}"
              + (f" | gamma 1e6 rad {g:+d}%" if g is not None else ""))
    out["series1"] = res1

    # inactive-form check: does pheophytin (inactive) rise as the text claims?
    ph = T1["Pheophytine A"]; ca = T1["Chlorophylle A"]
    print("\n  Pheophytin A / Chlorophyll A ratio (the 'inactive form' index):")
    for age, i, j in (("young", 0, 1), ("aged", 2, 3)):
        rc, re_ = ph[i] / ca[i], ph[j] / ca[j]
        print(f"    {age}: control {rc:.3f} -> exposed {re_:.3f}  ({100*(re_/rc-1):+.1f}%)")

    # ---------------------------------------------------- 2. reproduce reported stats
    section("2. Reproducing NT16's reported correlations from its own Tableaux 2/7")
    rep = []
    for label, yk, xk, n, r_rep, p_rep, page in REPORTED:
        y = V[yk]; x = xform(D, xk)
        if n == 5:
            # p.52 says N=5 for the bilog PhA' regression without naming the dropped
            # point. We try every single-point deletion and report which matches.
            best = None
            for drop in range(6):
                m = np.ones(6, bool); m[drop] = False
                r = pearson(x[m], y[m])
                if best is None or abs(abs(r) - abs(r_rep)) < abs(abs(best[1]) - abs(r_rep)):
                    best = (drop, r)
            r_ours = best[1]; note = f"best match drops E-{best[0]+1}"
            p_par = stats.pearsonr(x[np.arange(6) != best[0]], y[np.arange(6) != best[0]])[1]
        else:
            r_ours = pearson(x, y); note = ""
            p_par = stats.pearsonr(x, y)[1]
        match = "MATCH" if abs(r_ours - r_rep) < 0.01 else ("SIGN/ABS" if abs(abs(r_ours) - abs(r_rep)) < 0.01 else "DIFF")
        rep.append(dict(label=label, page=page, r_reported=r_rep, r_ours=round(r_ours, 4),
                        p_reported=p_rep, p_param_2s=float(f"{p_par:.3g}"), p_param_1s=float(f"{p_par/2:.3g}"),
                        status=match, note=note))
        print(f"  {label:32s} {page:11s} r_rep={r_rep:+.4f} r_ours={r_ours:+.4f} {match:8s}"
              f" P_rep={p_rep} P_ours 2s={p_par:.3g} 1s={p_par/2:.3g} {note}")
    print("  Floor: with N=6 and the d=10 tie, the smallest attainable two-sided permutation p is 2/720 = 0.0028.")
    out["reproduction"] = rep

    # ---------------------------------------------------- 2b. the E-1 ChlB value
    section("2b. NT16 Tableau 2 E-1 Chlorophylle B: printed 0,930 (NT16 p.50) vs 0,030 (INRA original, Analyses2_INRA-R p.23)")
    for alt in (0.930, 0.030):
        t2a = dict(T2); t2a["ChlB"] = T2["ChlB"].copy(); t2a["ChlB"][0] = alt
        Va = derived(t2a, T7)
        r1 = pearson(D, Va["ratioAB"]); r2 = pearson(1 / (D + 1), Va["ratioAB"])
        rB = pearson(D, Va["SumChlB"])
        print(f"  E-1 ChlB={alt:.3f}: ratio~d r={r1:+.4f} (rep +0.7509); ratio~1/(d+1) r={r2:+.4f} (rep -0.891);"
              f" SumChlB~d r={rB:+.4f} (text: 'pas de correlation significative')")

    # ---------------------------------------------------- 3. null models
    section("3. Null model A: exact permutation of distance labels (720 orderings, ties kept)")
    print("Each p is the share of the 720 relabelings whose |r| >= observed.")
    perm_rows = []
    for label, yk, xk, n, r_rep, p_rep, page in REPORTED:
        if n != 6:
            continue
        y = V[yk]; x = xform(D, xk)
        p = exact_perm(x, y)
        r = pearson(x, y)
        z = math.atanh(r); se = 1 / math.sqrt(len(x) - 3)
        lo, hi = math.tanh(z - 1.96 * se), math.tanh(z + 1.96 * se)
        perm_rows.append(dict(label=label, r=round(r, 3), r_ci95=[round(lo, 3), round(hi, 3)], p_perm=round(p, 4)))
        print(f"  {label:32s} r={r:+.3f} [Fisher-z 95% {lo:+.3f},{hi:+.3f}]  p_perm={p:.4f}  (parametric P reported {p_rep})")
    out["perm"] = perm_rows

    section("3b. Null model B: forking paths -- best of 3 distance transforms per variable")
    print("NT16 fits d, 1/(d+1) and ln(d+1) and reports whichever straightens the curve.")
    print("Null: permute labels, take max |r| over the three transforms; compare observed max.")
    fork = []
    xs = [xform(D, k) for k in ("d", "inv", "ln")]
    keys = ["SumChlA", "SumChlB", "SumChl", "ratioAB", "PhA_tot/ChlA", "PhA'/ChlA", "bCar", "Lut",
            "Vx+Nx+Chlide", "PhA", "PhA'", "PChld3", "PChld4", "lnTq", "lnTc", "lnC-P"]
    perms = list(itertools.permutations(range(6)))
    for k in keys:
        y = V[k]
        obs = max(abs(pearson(x, y)) for x in xs)
        null = np.array([max(abs(pearson(x[list(pm)], y)) for x in xs) for pm in perms])
        p = float(np.mean(null >= obs - 1e-12))
        fork.append(dict(var=k, max_abs_r=round(obs, 4), p_fork=round(p, 4)))
        print(f"  {k:16s} max|r|={obs:.3f}  p_fork={p:.4f}")
    out["fork"] = fork

    section("3c. Null model C: joint relabeling -- how many of 16 variables reach p_fork<0.05 by chance?")
    print("Permutes distance labels once for ALL variables together, preserving their")
    print("shared-sample correlation. 720 relabelings; count variables with max|r| >= 0.811")
    print("(the 2-sided 5% critical r for N=6).")
    rcrit = 0.811
    obs_count = sum(1 for k in keys if max(abs(pearson(x, V[k])) for x in xs) >= rcrit)
    counts = []
    for pm in perms:
        c = 0
        for k in keys:
            if max(abs(pearson(x[list(pm)], V[k])) for x in xs) >= rcrit:
                c += 1
        counts.append(c)
    counts = np.array(counts)
    p_joint = float(np.mean(counts >= obs_count))
    print(f"  observed: {obs_count}/16 variables with max|r|>={rcrit}")
    print(f"  null: mean {counts.mean():.2f}, median {np.median(counts):.0f}, 95th pct {np.percentile(counts,95):.0f}; P(count>=obs)={p_joint:.4f}")
    out["joint"] = dict(obs=obs_count, null_mean=float(counts.mean()), p=p_joint)

    # ---------------------------------------------------- 4. leverage
    section("4. Leverage: is the 'gradient' a gradient, or E-1 versus the rest?")
    print("Drop E-1 (d=0, the centre) and recompute on the 5 remaining points.")
    lev = []
    m = np.arange(6) != 0
    for label, yk, xk, n, r_rep, p_rep, page in REPORTED:
        if n != 6:
            continue
        y = V[yk]; x = xform(D, xk)
        r_all = pearson(x, y); r_wo = pearson(x[m], y[m])
        p_wo = stats.pearsonr(x[m], y[m])[1]
        lev.append(dict(label=label, r_all=round(r_all, 3), r_without_E1=round(r_wo, 3), p_without_E1=float(f"{p_wo:.3g}")))
        print(f"  {label:32s} r_all={r_all:+.3f}  r_without_E1={r_wo:+.3f}  P2s={p_wo:.3g}")
    out["leverage"] = lev
    # Spearman too (rank-based, d ties)
    print("\n  Spearman rho on all six (robust to the d=0 lever):")
    for k in ["SumChlA", "ratioAB", "PhA'/ChlA", "bCar", "Lut", "lnTq", "lnTc", "lnC-P"]:
        rho, p = stats.spearmanr(D, V[k])
        print(f"    {k:14s} rho={rho:+.3f}  P2s={p:.3g}")

    # ---------------------------------------------------- 5. leaf-size confound
    section("5. Confound: leaf development (fresh mass per leaf, NT16 p.43)")
    print("INRA itself flags E-3/E-4 as possibly less developed (p.43-44). Is mass per leaf")
    print("related to distance, and does controlling for it change the pigment gradient?")
    rPD = pearson(D, P_LEAF)
    print(f"  r(d, mass/leaf) = {rPD:+.3f}")
    conf = []
    for k in ["SumChlA", "bCar", "Lut", "lnTq", "lnTc", "lnC-P", "PhA'/ChlA"]:
        y = V[k]
        rYP = pearson(P_LEAF, y); rYD = pearson(D, y)
        part = (rYD - rYP * rPD) / math.sqrt((1 - rYP**2) * (1 - rPD**2))
        conf.append(dict(var=k, r_d=round(rYD, 3), r_mass=round(rYP, 3), partial_r_d_given_mass=round(part, 3)))
        print(f"  {k:12s} r(d)={rYD:+.3f}  r(mass)={rYP:+.3f}  partial r(d|mass)={part:+.3f}")
    out["confound"] = conf

    # ---------------------------------------------------- 6. carotenoid/chlorophyll pattern
    section("6. The pattern argument (NT16 p.64-65): carotenoids hit harder than chlorophylls")
    for age, ci, ei in (("young", 0, 1), ("aged", 2, 3)):
        car = T1["beta-carotene"][ei] / T1["beta-carotene"][ci]
        chl = T1["Chlorophylle A"][ei] / T1["Chlorophylle A"][ci]
        ratio = car / chl
        # analytical-noise CI on the double ratio (4 independent values, CV .22 each)
        sims = []
        vals = [T1["beta-carotene"][ei], T1["beta-carotene"][ci], T1["Chlorophylle A"][ei], T1["Chlorophylle A"][ci]]
        s = [v * (1 + CV_SERIES1 * RNG.standard_normal(200_000)) for v in vals]
        ok = np.all(np.array(s) > 0, axis=0)
        dr = (s[0][ok] / s[1][ok]) / (s[2][ok] / s[3][ok])
        lo, hi = np.percentile(dr, [2.5, 97.5])
        p_le1 = float(np.mean(dr >= 1.0))
        print(f"  {age}: (bCar exp/ctl)/(ChlA exp/ctl) = {ratio:.3f}  95% analytical [{lo:.3f},{hi:.3f}]  P(sim>=1)={p_le1:.3f}")
    # series 2: bCar/SumChlA vs d
    r = pearson(D, V["bCar"] / V["SumChlA"])
    print(f"  series 2: r(d, bCar/SumChlA) = {r:+.3f}  (E-1 bCar/SumChlA = {V['bCar'][0]/V['SumChlA'][0]:.3f}, "
          f"E-5/E-6 mean = {np.mean(V['bCar'][4:]/V['SumChlA'][4:]):.3f})")
    print("  per-sample bCar/SumChlA (series 2): " + ", ".join(
        f"E-{i+1}(d={D[i]:g})={V['bCar'][i]/V['SumChlA'][i]:.3f}" for i in range(6)))
    m = np.arange(6) != 0
    print(f"  r(d, bCar/SumChlA) without E-1 = {pearson(D[m], (V['bCar']/V['SumChlA'])[m]):+.3f}")
    print("  So: from 1.5 m outward carotene/chlorophyll rises with distance (carotenoids depleted more")
    print("  near the trace, as series 1 says), but at the centre E-1 chlorophyll is the more depleted.")

    soil(out)

    with open("omega/reports/tep_nt16_replication.json", "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
