import sys, re, json, math, collections
import numpy as np
from scipy import stats
sys.path.insert(0, "/home/user/UFOAI/omega")
import corpus, phase6, phase5
RNG = phase6.RNG
rows = phase6.load()
s = phase6.strata(rows)
N = len(rows)
def has(code): return np.array([1 if code in r["codes"] else 0 for r in rows], dtype=np.int8)
def hask(k):  return np.array([1 if k in r["kin"] else 0 for r in rows], dtype=np.int8)
PVALS = []

print("=" * 92)
print("TEST 1  BEHAVIOUR x OBSERVER TYPE")
print("  Null: observer-type label permuted WITHIN code-count strata (6 bins).")
obs_codes = ["MIL", "CIV", "AIR", "SEA", "RDR", "SCI", "HQO"]
beh_codes = list(phase6.BEHAV_OBS) + list(phase6.BEHAV_INT)
tab = np.array([[int(((has(o) == 1) & (has(b) == 1)).sum()) for b in beh_codes] for o in obs_codes])
v, chi2, p, dof = phase6.cramers_v(tab)
print(f"  OMNIBUS observer x behaviour: chi2={chi2:.1f} dof={dof} p={p:.3e} Cramer's V={v:.4f}")
PVALS.append(("T1 omnibus", p))
print(f"\n  {'observer':<10}{'behaviour':<34}{'n11':>6}{'odds':>8}{'MI(bits)':>10}{'p_strat':>9}")
t1rows = []
for o in obs_codes:
    xo = has(o)
    for b in beh_codes:
        xb = has(b)
        if ((xo == 1) & (xb == 1)).sum() < 25: continue
        r = phase6.perm_assoc(xo, xb, s, nperm=1500)
        t1rows.append((o, b, r))
for o, b, r in sorted(t1rows, key=lambda t: -abs(math.log(max(t[2]["odds"], 1e-9)))) [:16]:
    print(f"  {o:<10}{phase6.BEHAV_OBS.get(b, phase6.BEHAV_INT.get(b, b))[:33]:<34}"
          f"{r['a']:>6}{r['odds']:>8.2f}{r['mi']:>10.5f}{r['p']:>9.4f}")

print("\n" + "=" * 92)
print("TEST 2  OBSERVER-EFFECT TEST")
print("  H: if UAP respond to being observed, active observer action should predict")
print("     responsive behaviour. Null: action label permuted within code-count strata.")
print(f"\n  {'action':<22}{'outcome':<34}{'n11':>6}{'odds':>8}{'p_strat':>9}")
for a in ["OBS", "PHT"]:
    xa = has(a)
    for b in ["SIG", "PRB", "CMF", "LND", "EME", "VEH", "RAY", "SND", "TRC"]:
        xb = has(b)
        if ((xa == 1) & (xb == 1)).sum() < 15: continue
        r = phase6.perm_assoc(xa, xb, s, nperm=1500)
        tag = phase6.BEHAV_INT.get(b, phase6.BEHAV_OBS.get(b, b))
        print(f"  {phase6.ACTION[a]:<22}{tag[:33]:<34}{r['a']:>6}{r['odds']:>8.2f}{r['p']:>9.4f}")
        if a == "OBS" and b == "SIG": PVALS.append(("T2 chase->signal", r["p"]))
print("\n  CONTROL: does the same action predict a NON-responsive sensory attribute")
print("  (shape class) as strongly? If yes, the association is narrative, not responsive.")
for a in ["OBS", "PHT"]:
    xa = has(a)
    for b in ["SCR", "NLT", "CIG", "DLT"]:
        xb = has(b)
        r = phase6.perm_assoc(xa, xb, s, nperm=800)
        print(f"  {phase6.ACTION[a]:<22}{'shape: '+b:<34}{r['a']:>6}{r['odds']:>8.2f}{r['p']:>9.4f}")

print("\n" + "=" * 92)
print("TEST 3  ADAPTIVE / SEQUENCE STRUCTURE")
print("  Kinematic descriptor ORDER within a single report. Null: shuffle order")
print("  within report (identical machinery to the Phase 4D light-code test).")
seqs = []
for r in rows:
    hits = []
    for k, rx in phase6.KRX.items():
        m = rx.search(r["desc"] or "")
        if m: hits.append((m.start(), k))
    if len(hits) >= 2:
        hits.sort(); seqs.append([k for _, k in hits])
def ce(sq):
    bi = collections.Counter(); pre = collections.Counter()
    for q in sq:
        for x, y in zip(q, q[1:]): bi[(x, y)] += 1; pre[x] += 1
    Ntot = sum(bi.values()); H = 0.0
    for (x, y), c in bi.items(): H -= (c / Ntot) * math.log2(c / pre[x])
    return H
uni = collections.Counter(t for q in seqs for t in q); tot = sum(uni.values())
H_uni = -sum((v / tot) * math.log2(v / tot) for v in uni.values())
H_obs = ce(seqs)
null = np.array([ce([list(RNG.permutation(q)) for q in seqs]) for _ in range(2000)])
p3 = (1 + int((null <= H_obs).sum())) / 2001
print(f"\n  reports with >=2 kinematic descriptors: {len(seqs)}   tokens: {tot}")
print(f"  H(unigram)={H_uni:.4f}  H(k2|k1)={H_obs:.4f}  shuffled null={null.mean():.4f}"
      f"+/-{null.std(ddof=1):.4f}  p={p3:.4f}")
print(f"  structure above null = {null.mean()-H_obs:+.4f} bits "
      f"({(null.mean()-H_obs)/H_uni*100:+.2f}% of channel entropy)")
PVALS.append(("T3 sequence", p3))
bi = collections.Counter(); pre = collections.Counter()
for q in seqs:
    for x, y in zip(q, q[1:]): bi[(x, y)] += 1; pre[x] += 1
rr = [(c / (pre[x] * uni[y] / tot), c, x, y) for (x, y), c in bi.items() if c >= 40]
rr.sort(reverse=True)
print("  top transitions (obs/exp):")
for ratio, c, x, y in rr[:8]: print(f"     {ratio:>5.2f}  {c:>5}  {x} -> {y}")

print("\n" + "=" * 92)
print("TEST 4  GOAL-DIRECTED TARGETING")
print("  H: reported headings point toward military/missile facilities more than chance.")
COMPASS = {"north":0,"northeast":45,"east":90,"southeast":135,"south":180,
           "southwest":225,"west":270,"northwest":315,"nne":22,"ene":67,"ese":112,
           "sse":157,"ssw":202,"wsw":247,"wnw":292,"nnw":337}
CRX = re.compile(r"\b(" + "|".join(COMPASS) + r")\b", re.I)
FAC = [(f[0], f[1], f[2]) for f in phase5.ICBM] + [(f[0], f[1], f[2]) for f in phase5.CONTROL]
def bearing(la1, lo1, la2, lo2):
    p1, p2 = math.radians(la1), math.radians(la2); dl = math.radians(lo2 - lo1)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1)*math.sin(p2) - math.sin(p1)*math.cos(p2)*math.cos(dl)
    return (math.degrees(math.atan2(y, x)) + 360) % 360
pairs = []
for r in rows:
    if r["lat"] is None: continue
    m = list(CRX.finditer(r["desc"] or ""))
    if not m: continue
    hd = COMPASS[m[-1].group(1).lower()]
    best = min(FAC, key=lambda f: corpus.haversine(r["lat"], r["lon"], f[1], f[2]))
    d = corpus.haversine(r["lat"], r["lon"], best[1], best[2])
    if d > 400 or d < 5: continue
    pairs.append((hd, bearing(r["lat"], r["lon"], best[1], best[2])))
print(f"\n  usable (heading, facility-bearing) pairs within 5-400 km: {len(pairs)}")
if len(pairs) > 50:
    dev = np.array([min(abs(h - b), 360 - abs(h - b)) for h, b in pairs])
    obs = float((dev <= 45).mean())
    null = np.array([float((np.array([min(abs(h - b), 360 - abs(h - b))
             for h, b in zip(RNG.permutation([p[0] for p in pairs]),
                             [p[1] for p in pairs])]) <= 45).mean()) for _ in range(2000)])
    p4 = (1 + int((null >= obs).sum())) / 2001
    print(f"  fraction of headings within 45 deg of nearest facility: obs={obs:.4f}  "
          f"null={null.mean():.4f}+/-{null.std(ddof=1):.4f}  p={p4:.4f}")
    print(f"  mean angular deviation: obs={dev.mean():.1f} deg  (random expectation 90 deg)")
    PVALS.append(("T4 targeting", p4))

print("\n" + "=" * 92)
print("TEST 5  KINEMATICS-INVARIANCE vs SHAPE-INVARIANCE")
print("  H (from Phase 3): shape descriptors carry era information; kinematic ones do not.")
ERAS = [(-9999,1800),(1800,1945),(1945,1957),(1957,1990),(1990,2030)]
ei = np.array([next((i for i,(lo,hi) in enumerate(ERAS) if lo<=r["year"]<hi), -1)
               if r["year"] else -1 for r in rows])
ok = ei >= 0
def eramis(vecs):
    out = []
    for name, x in vecs:
        xx = x[ok]; e = ei[ok]; n = len(xx); mi = 0.0
        for a in (0,1):
            pa = (xx==a).mean()
            for b in range(5):
                pb = (e==b).mean(); pab = ((xx==a)&(e==b)).mean()
                if pab>0 and pa>0 and pb>0: mi += pab*math.log2(pab/(pa*pb))
        out.append((name, mi))
    return out
sh = eramis([(c, has(c)) for c in phase6.SHAPE])
ki = eramis([(k, hask(k)) for k in phase6.KRX])
print(f"\n  {'SHAPE code':<14}{'era MI':>10}     {'KINEMATIC':<14}{'era MI':>10}")
for i in range(max(len(sh), len(ki))):
    a = f"  {sh[i][0]:<14}{sh[i][1]:>10.5f}" if i < len(sh) else "  " + " "*24
    b = f"     {ki[i][0]:<14}{ki[i][1]:>10.5f}" if i < len(ki) else ""
    print(a + b)
msh = np.mean([x[1] for x in sh]); mki = np.mean([x[1] for x in ki])
allv = [x[1] for x in sh] + [x[1] for x in ki]
lab = np.array([1]*len(sh) + [0]*len(ki))
diff = msh - mki
nullg = np.empty(20000)
for i in range(20000):
    lp = RNG.permutation(lab)
    nullg[i] = np.mean(np.array(allv)[lp==1]) - np.mean(np.array(allv)[lp==0])
p5 = (1 + int((nullg >= diff).sum())) / 20001
print(f"\n  mean era-MI  shape={msh:.5f}  kinematic={mki:.5f}  difference={diff:+.5f} bits")
print(f"  group-label permutation p={p5:.5f}  (ratio shape/kinematic = {msh/max(mki,1e-9):.2f}x)")
PVALS.append(("T5 shape>kinematic era-MI", p5))

print("\n" + "=" * 92)
print("TEST 6  CREDIBILITY GRADIENT FOR INTELLIGENCE-ATTRIBUTION CODES")
cred = np.array([r["cred"] if r["cred"] is not None else np.nan for r in rows])
hi = cred >= 8; lo = (cred <= 6) & ~np.isnan(cred)
print(f"  n_high={int(hi.sum())} n_low={int(lo.sum())}")
print(f"\n  {'code':<40}{'high':>9}{'low':>9}{'ratio':>8}{'p':>11}")
for c in ["PRB","CMF","SIG","TLP","CVS","ABD","OPR","LND","SUB","EME","VEH","RDR","TRC","PHT","OBS"]:
    x = has(c); a, b = int(x[hi].sum()), int(x[lo].sum())
    if a + b < 20: continue
    _, pf = stats.fisher_exact(np.array([[a, int(hi.sum())-a], [b, int(lo.sum())-b]]))
    ra = (a/hi.sum())/max(1e-9, b/lo.sum())
    nm = phase6.BEHAV_INT.get(c, phase6.BEHAV_OBS.get(c, phase6.ACTION.get(c, c)))
    print(f"  {nm[:39]:<40}{a/hi.sum()*100:>8.2f}%{b/lo.sum()*100:>8.2f}%{ra:>8.2f}{pf:>11.2e}")
    if c == "PRB": PVALS.append(("T6 PRB credibility", pf))

print("\n" + "=" * 92)
print("TEST 7  TEMPORAL CLUSTERING OF INTELLIGENCE-ATTRIBUTION EVENTS")
print("  H: goal-directed activity should arrive in coordinated waves.")
IB = ((has("PRB") | has("CMF") | has("SIG") | has("CVS") | has("TLP")) == 1)
jd = np.array([corpus.to_jdn(r["year"], r["month"], r["day"]) if r["year"] else -1 for r in rows])
yr = np.array([r["year"] if r["year"] else -1 for r in rows])
good = (jd > 0) & (yr >= 1947) & (yr <= 1995)
def fano(j):
    if len(j) < 30: return np.nan
    b = np.arange(j.min(), j.max() + 31, 30)
    h, _ = np.histogram(j, bins=b)
    return h.var(ddof=1) / max(h.mean(), 1e-9)
ib = good & IB; nb = good & ~IB
f_ib, f_nb = fano(jd[ib]), fano(jd[nb])
print(f"\n  n(intelligence-attributed)={int(ib.sum())}  n(other)={int(nb.sum())}")
print(f"  Fano factor (30-day bins): IB={f_ib:.3f}   non-IB={f_nb:.3f}")
nullf = np.empty(2000)
lab2 = IB[good].astype(int)
jg, yg = jd[good], yr[good]
for i in range(2000):
    lp = lab2.copy()
    for y in np.unique(yg):
        idx = np.flatnonzero(yg == y)
        lp[idx] = lab2[idx][RNG.permutation(idx.size)]
    nullf[i] = fano(jg[lp == 1])
p7 = (1 + int((nullf >= f_ib).sum())) / 2001
print(f"  null (labels permuted within year): {nullf.mean():.3f}+/-{nullf.std(ddof=1):.3f}  p={p7:.4f}")
PVALS.append(("T7 temporal clustering", p7))

print("\n" + "=" * 92)
print(f"MULTIPLE-TESTING SUMMARY  ({len(PVALS)} primary tests)")
alpha = 0.05 / len(PVALS)
print(f"  Bonferroni alpha = 0.05/{len(PVALS)} = {alpha:.5f}")
for nm, p in PVALS:
    print(f"  {nm:<34}p={p:<10.5f}{'SURVIVES' if p < alpha else ('nominal' if p < 0.05 else 'null')}")
json.dump([(a, float(b)) for a, b in PVALS],
          open("/home/user/UFOAI/data/processed/impossible_tests/phase6_pvals.json", "w"), indent=1)
