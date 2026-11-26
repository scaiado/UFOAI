"""PROJECT OMEGA - Phase 4: the tests nobody has run.

4A  provenance-weighted signal test
4B  ancient/modern geographic hotspot persistence
4C  temporal spectral analysis + solar-cycle correlation (surrogate-tested)
4D  LIGHT CODE: information-theoretic test for structure in UAP light sequences
"""
from __future__ import annotations
import sys, re, json, math, collections, zlib
import numpy as np
from scipy import stats, signal
from scipy.spatial import cKDTree
sys.path.insert(0, "/home/user/UFOAI/omega")
import corpus, phase2, phase3

RNG = np.random.default_rng(271828)
MC = "/home/user/UFOAI/data/processed/provenance/master_catalog_inclusive.json"
OUT = "/home/user/UFOAI/data/processed/impossible_tests"

def events():
    return json.load(open(MC))["events"]

# ───────────────────────────────────────────────────────── 4A
def test_4a(ev):
    print("=" * 78)
    print("4A  PROVENANCE-WEIGHTED SIGNAL TEST")
    print("    Does the (decontaminated) nuclear-proximity signal differ between")
    print("    well-corroborated and single-sourced events?")
    import phase2c
    S = [e for e in ev if e["lat"] is not None and e["date_precision"] == "day" and e["year"]]
    clean, c1, c3 = phase2c.classify(S)
    nk = [t for t in corpus.load_nuclear() if t["lat"] is not None and t["prec"] == "day"]
    strata = {
        "single-sourced (1 catalog)": [e for e in clean if e["n_catalogs"] == 1],
        "corroborated (2-4 catalogs)": [e for e in clean if 2 <= e["n_catalogs"] <= 4],
        "well-corroborated (>=5)": [e for e in clean if e["n_catalogs"] >= 5],
        "deep provenance (depth>=10)": [e for e in clean if e["provenance_depth"] >= 10],
    }
    print(f"\n    {'stratum':<30}{'n':>7}{'obs':>7}{'exp':>9}{'ratio':>7}{'p':>9}")
    res = {}
    for label, sub in strata.items():
        if len(sub) < 200:
            print(f"    {label:<30}{len(sub):>7}   (too few)"); continue
        D = np.array([corpus.to_jdn(e["year"], e["month"], e["day"]) for e in sub])
        Y = np.array([e["year"] for e in sub])
        gid, gl = phase2.build(sub, nk, 500)
        FM = phase2.fmatrix(gl, D, 30)
        r = phase2.perm_test(gid, FM, Y, nperm=4000, conditional=True)
        res[label] = r
        print(f"    {label:<30}{len(sub):>7}{r['observed']:>7}{r['exp_mean']:>9.1f}"
              f"{r['ratio']:>7.3f}{r['p']:>9.4f}")
    print("\n    Interpretation: if nuclear clustering were an echo-chamber artifact it")
    print("    would concentrate in single-sourced events. If physical, it should")
    print("    strengthen with corroboration. Phase 2 found no signal at all, so this")
    print("    tests whether ANY stratum hides one.")
    return res

# ───────────────────────────────────────────────────────── 4B
def test_4b(ev):
    print("\n" + "=" * 78)
    print("4B  GEOGRAPHIC HOTSPOT PERSISTENCE (historical vs modern)")
    geo = [e for e in ev if e["lat"] is not None and e["year"]]
    out = {}
    for hist_cut, mod_cut, label in ((1800, 1950, "pre-1800 vs post-1950"),
                                     (1900, 1950, "pre-1900 vs post-1950")):
        H = [e for e in geo if e["year"] < hist_cut]
        M = [e for e in geo if e["year"] >= mod_cut]
        if len(H) < 20: 
            print(f"\n    {label}: only {len(H)} historical geocoded events - skipped")
            continue
        hx = phase2.ecef(np.array([e["lat"] for e in H]), np.array([e["lon"] for e in H]))
        mx = phase2.ecef(np.array([e["lat"] for e in M]), np.array([e["lon"] for e in M]))
        tree = cKDTree(mx)
        print(f"\n    {label}:  n_historical={len(H)}  n_modern={len(M)}")
        print(f"    {'radius':>8}{'observed':>10}{'exp_mean':>10}{'ratio':>8}{'z':>8}{'p':>9}")
        for rad in (50, 100, 250):
            obs = sum(1 for nb in tree.query_ball_point(hx, r=phase2.chord(rad)) if nb)
            # null: shuffle MODERN locations by resampling from the modern spatial
            # distribution is wrong (it is the same distribution). Correct null:
            # relabel which events are historical, drawing the same number of
            # "historical" points from the pooled set, preserving the pooled
            # spatial distribution. Tests whether HISTORICAL points sit closer to
            # modern density than randomly chosen points of the same corpus do.
            pooled = np.vstack([hx, mx])
            nh = len(hx)
            null = np.empty(2000)
            for i in range(2000):
                pick = RNG.choice(len(pooled), size=nh, replace=False)
                null[i] = sum(1 for nb in tree.query_ball_point(pooled[pick],
                                                                r=phase2.chord(rad)) if nb)
            mu, sd = null.mean(), null.std(ddof=1)
            z = (obs - mu) / sd if sd else float("nan")
            p = (1 + int((null >= obs).sum())) / 2001
            print(f"    {rad:>7}km{obs:>10}{mu:>10.1f}{obs/max(mu,1e-9):>8.3f}{z:>+8.2f}{p:>9.4f}")
            out[f"{label}_{rad}km"] = dict(obs=obs, exp=float(mu), z=float(z), p=p)
    # top persistent hotspots
    H = [e for e in geo if e["year"] < 1900]
    M = [e for e in geo if e["year"] >= 1950]
    if H and M:
        hx = phase2.ecef(np.array([e["lat"] for e in H]), np.array([e["lon"] for e in H]))
        mx = phase2.ecef(np.array([e["lat"] for e in M]), np.array([e["lon"] for e in M]))
        tree = cKDTree(mx)
        cnt = [(len(tree.query_ball_point(hx[i], r=phase2.chord(100))), H[i]) for i in range(len(H))]
        cnt.sort(key=lambda x: -x[0])
        print("\n    TOP 12 PERSISTENT LOCATIONS (pre-1900 event, modern events within 100km):")
        for n, e in cnt[:12]:
            print(f"      {n:>5} modern  {e['year']}  {(e['location'] or '?')[:42]:<42} {e['description'][:58]}")
    return out

# ───────────────────────────────────────────────────────── 4C
def test_4c(ev):
    print("\n" + "=" * 78)
    print("4C  TEMPORAL SPECTRAL ANALYSIS + SOLAR CYCLE")
    E = [e for e in ev if e["year"] and e["month"] and 1900 <= e["year"] <= 2000]
    cnt = collections.Counter((e["year"], e["month"]) for e in E)
    t0, t1 = 1900, 2001
    months = [(y, m) for y in range(t0, t1) for m in range(1, 13)]
    y = np.array([cnt.get(k, 0) for k in months], dtype=float)
    tt = np.arange(len(y)) / 12.0 + t0
    print(f"    monthly series: n={len(y)} months, total events={int(y.sum())}, "
          f"mean={y.mean():.1f}, max={y.max():.0f} ({months[int(y.argmax())]})")
    # detrend: the series is dominated by reporting-effort changes, so remove a
    # 25-month moving average before spectral analysis.
    k = 25
    trend = np.convolve(y, np.ones(k)/k, mode="same")
    r = y - trend
    f, P = signal.periodogram(r, fs=12.0, detrend="linear", scaling="spectrum")
    ok = (f > 1/40) & (f < 6)
    idx = np.argsort(P[ok])[::-1][:8]
    print(f"\n    top periodogram peaks (detrended residual):")
    print(f"    {'period(yr)':>12}{'power':>12}{'power/median':>14}")
    med = np.median(P[ok])
    for i in idx:
        per = 1.0 / f[ok][i]
        print(f"    {per:>12.2f}{P[ok][i]:>12.1f}{P[ok][i]/med:>14.1f}")
    # annual cycle
    bym = collections.Counter(e["month"] for e in E)
    tot = sum(bym.values())
    expm = tot / 12
    chi2 = sum((bym[m] - expm) ** 2 / expm for m in range(1, 13))
    pm = 1 - stats.chi2.cdf(chi2, 11)
    print(f"\n    ANNUAL CYCLE: chi2={chi2:.1f} dof=11 p={pm:.3e}")
    print("      " + "  ".join(f"{m}:{bym[m]*100/tot:.1f}%" for m in range(1, 13)))
    # solar cycle
    sun = {}
    for line in open("/tmp/claude-0/-home-user/f0aebeb3-1b62-5042-9067-46af83ba9a9d/scratchpad/omega/sunspots.csv"):
        p = line.strip().split(";")
        if len(p) < 4: continue
        try: sun[(int(p[0]), int(p[1]))] = float(p[3])
        except Exception: continue
    s = np.array([sun.get(kk, np.nan) for kk in months])
    m = ~np.isnan(s)
    ys, ss = y[m], s[m]
    # naive correlation (WRONG - both series autocorrelated) then surrogate test
    rp = stats.pearsonr(ys, ss)
    rs = stats.spearmanr(ys, ss)
    print(f"\n    SOLAR: naive Pearson r={rp[0]:+.4f} p={rp[1]:.3e} | "
          f"Spearman rho={rs[0]:+.4f} p={rs[1]:.3e}")
    # phase-randomised surrogates preserve the power spectrum (hence the
    # autocorrelation) of the sighting series while destroying its phase
    # relationship to the solar series. This is the correct null.
    def surrogate(x):
        F = np.fft.rfft(x - x.mean())
        ph = RNG.uniform(0, 2*np.pi, len(F)); ph[0] = 0
        return np.fft.irfft(np.abs(F) * np.exp(1j*ph), n=len(x)) + x.mean()
    null = np.array([stats.pearsonr(surrogate(ys), ss)[0] for _ in range(2000)])
    p_sur = (1 + int((np.abs(null) >= abs(rp[0])).sum())) / 2001
    print(f"    SOLAR: phase-randomised surrogate p={p_sur:.4f}  "
          f"(null |r| 95th pct = {np.percentile(np.abs(null),95):.4f})")
    # detrended residual vs sunspot
    rr = stats.pearsonr(r[m], ss)
    print(f"    SOLAR (detrended residual): r={rr[0]:+.4f} p={rr[1]:.3e}")
    return dict(annual_chi2=float(chi2), annual_p=float(pm),
                solar_pearson=float(rp[0]), solar_p_naive=float(rp[1]),
                solar_p_surrogate=float(p_sur),
                solar_detrended_r=float(rr[0]), solar_detrended_p=float(rr[1]))

# ───────────────────────────────────────────────────────── 4D  LIGHT CODE
COLORS = ["red","orange","yellow","green","blue","white","amber","purple",
          "violet","pink","silver","gold","black"]
CRX = re.compile(r"\b(" + "|".join(COLORS) + r")\b", re.I)

def test_4d(ev):
    print("\n" + "=" * 78)
    print("4D  LIGHT CODE: information-theoretic test for structure in colour sequences")
    print("    H0: colour mentions are an unordered bag drawn from report-specific")
    print("        composition. Encoded information would make the ORDER predictable,")
    print("        lowering the bigram conditional entropy below the shuffled null.")
    seqs = []
    for e in ev:
        c = [m.group(1).lower() for m in CRX.finditer(e["description"] or "")]
        if len(c) >= 2: seqs.append(c)
    n = len(seqs); tot = sum(len(s) for s in seqs)
    print(f"\n    reports with >=2 colour mentions: {n}   total colour tokens: {tot}")
    uni = collections.Counter(t for s in seqs for t in s)
    print("    colour frequencies: " + ", ".join(f"{k}:{v}" for k, v in uni.most_common()))

    def cond_entropy(sequences):
        bi = collections.Counter(); pre = collections.Counter()
        for s in sequences:
            for a, b in zip(s, s[1:]):
                bi[(a, b)] += 1; pre[a] += 1
        H = 0.0; N = sum(bi.values())
        if N == 0: return float("nan")
        for (a, b), c in bi.items():
            H -= (c / N) * math.log2(c / pre[a])
        return H

    H_obs = cond_entropy(seqs)
    H_uni = -sum((v/tot) * math.log2(v/tot) for v in uni.values())
    print(f"\n    unigram entropy H(colour)            = {H_uni:.4f} bits")
    print(f"    observed conditional entropy H(c2|c1) = {H_obs:.4f} bits")
    null = []
    for _ in range(2000):
        sh = [list(RNG.permutation(s)) for s in seqs]      # within-report shuffle
        null.append(cond_entropy(sh))
    null = np.array(null)
    p = (1 + int((null <= H_obs).sum())) / 2001
    print(f"    within-report shuffled null           = {null.mean():.4f} "
          f"+/- {null.std(ddof=1):.4f} bits")
    print(f"    one-sided p (observed lower than null) = {p:.4f}")
    print(f"    information gain over unigram          = {H_uni - H_obs:+.4f} bits "
          f"({(H_uni-H_obs)/H_uni*100:+.1f}%)")
    # compressibility check: does the corpus of colour strings compress better
    # than a composition-matched shuffle?
    joined = "\n".join(" ".join(s) for s in seqs).encode()
    c_obs = len(zlib.compress(joined, 9))
    cn = []
    for _ in range(200):
        sh = "\n".join(" ".join(RNG.permutation(s)) for s in seqs).encode()
        cn.append(len(zlib.compress(sh, 9)))
    cn = np.array(cn)
    print(f"\n    zlib size observed={c_obs}  shuffled={cn.mean():.0f}+/-{cn.std(ddof=1):.0f}"
          f"  p={(1+int((cn<=c_obs).sum()))/201:.4f}")
    return dict(n_reports=n, n_tokens=tot, H_unigram=float(H_uni),
                H_conditional=float(H_obs), null_mean=float(null.mean()),
                null_sd=float(null.std(ddof=1)), p=float(p),
                zlib_obs=int(c_obs), zlib_null=float(cn.mean()))

if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    ev = events()
    r = {}
    r["4A"] = {k: {kk: float(vv) if isinstance(vv, (int, float)) else vv
                   for kk, vv in v.items()} for k, v in test_4a(ev).items()}
    r["4B"] = test_4b(ev)
    r["4C"] = test_4c(ev)
    r["4D"] = test_4d(ev)
    json.dump(r, open(f"{OUT}/phase4.json", "w"), indent=1, default=str)
    print(f"\n[p4] wrote {OUT}/phase4.json")
