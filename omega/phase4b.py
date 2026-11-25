"""Phase 4 corrections.

4B-fix: the first null was degenerate. Drawing pseudo-historical points from the
POOLED set draws ~99% modern points, and a modern point always has a modern
neighbour, so E[count] saturated at n_historical and every z was hugely
negative. It measured nothing. Correct null: permute the ERA LABEL within
country, which holds the continental coverage shift (pre-1800 Europe vs
post-1950 US) fixed and asks whether historical events sit near modern ones
more than same-country chance.

4D-check: identify which colour bigrams drive the entropy deficit. If they are
English collocations and aircraft navigation-light conventions (red/green
port/starboard, red/white/blue), the 'light code' signal is linguistic.
"""
import sys, re, json, math, collections
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, "/home/user/UFOAI/omega")
import corpus, phase2, phase4

RNG = np.random.default_rng(161803)
ev = phase4.events()

# ─────────────────────────────────────────── 4B corrected
print("=" * 78)
print("4B-CORRECTED  hotspot persistence, era label permuted WITHIN COUNTRY")

def country_of(e):
    c = (e.get("country") or "").strip().lower()
    if c: return c
    loc = (e.get("location") or "").lower()
    for k in ("england","scotland","wales","britain","uk","france","belgium","germany",
              "italy","spain","usa","united states","canada","brazil","argentina",
              "australia","japan","china","russia","ussr","mexico","india"):
        if k in loc: return k
    m = re.search(r",\s*([a-z][a-z\s]{2,20})$", loc)
    return m.group(1).strip() if m else "?"

geo = [e for e in ev if e["lat"] is not None and e["year"]]
for hist_cut, label in ((1800, "pre-1800"), (1900, "pre-1900")):
    H = [e for e in geo if e["year"] < hist_cut]
    M = [e for e in geo if e["year"] >= 1950]
    pool = H + M
    lab = np.array([1]*len(H) + [0]*len(M))
    ctry = np.array([country_of(e) for e in pool])
    xyz = phase2.ecef(np.array([e["lat"] for e in pool]),
                      np.array([e["lon"] for e in pool]))
    # restrict to countries that contain BOTH eras -- otherwise the label
    # permutation is uninformative there.
    byc = collections.defaultdict(lambda: [0, 0])
    for i, c in enumerate(ctry): byc[c][lab[i]] += 1
    keep = {c for c, (nm, nh) in byc.items() if nh >= 3 and nm >= 3}
    sel = np.array([c in keep for c in ctry])
    print(f"\n  {label}: n_hist={len(H)} n_mod={len(M)}; countries with both eras="
          f"{len(keep)}; usable points={int(sel.sum())} "
          f"(hist={int(lab[sel].sum())})")
    if lab[sel].sum() < 15:
        print("    too few historical events in dual-era countries - UNDERPOWERED, skipped")
        continue
    X, L, C = xyz[sel], lab[sel], ctry[sel]
    modtree = cKDTree(X[L == 0])
    for rad in (50, 100, 250):
        nb = modtree.query_ball_point(X[L == 1], r=phase2.chord(rad))
        obs = float(np.mean([len(b) for b in nb]))   # mean modern neighbours per hist event
        null = np.empty(2000)
        idx_by_c = {c: np.flatnonzero(C == c) for c in set(C)}
        nh_by_c = {c: int(L[idx_by_c[c]].sum()) for c in idx_by_c}
        for it in range(2000):
            Lp = np.zeros_like(L)
            for c, idx in idx_by_c.items():
                if nh_by_c[c]:
                    Lp[RNG.choice(idx, size=nh_by_c[c], replace=False)] = 1
            t2 = cKDTree(X[Lp == 0])
            nb2 = t2.query_ball_point(X[Lp == 1], r=phase2.chord(rad))
            null[it] = np.mean([len(b) for b in nb2])
        mu, sd = null.mean(), null.std(ddof=1)
        z = (obs - mu) / sd if sd else float("nan")
        p = (1 + int((null >= obs).sum())) / 2001
        print(f"    {rad:>4}km  obs={obs:>8.2f}  exp={mu:>8.2f}+/-{sd:<6.2f} "
              f"ratio={obs/max(mu,1e-9):.3f}  z={z:+.2f}  p={p:.4f}")

# ─────────────────────────────────────────── 4D bigram audit
print("\n" + "=" * 78)
print("4D-CHECK  which colour bigrams drive the entropy deficit?")
seqs = []
for e in ev:
    c = [m.group(1).lower() for m in phase4.CRX.finditer(e["description"] or "")]
    if len(c) >= 2: seqs.append(c)
bi = collections.Counter()
pre = collections.Counter()
for s in seqs:
    for a, b in zip(s, s[1:]):
        bi[(a, b)] += 1; pre[a] += 1
uni = collections.Counter(t for s in seqs for t in s)
tot = sum(uni.values())
rows = []
for (a, b), c in bi.items():
    if c < 25: continue
    expected = pre[a] * (uni[b] / tot)
    rows.append((c / expected, c, expected, a, b))
rows.sort(reverse=True)
print(f"\n  {'obs/exp':>8}{'obs':>7}{'exp':>9}  bigram")
for r, c, e2, a, b in rows[:14]:
    print(f"  {r:>8.2f}{c:>7}{e2:>9.1f}  {a} -> {b}")
print(f"\n  {'(most suppressed)':>8}")
for r, c, e2, a, b in rows[-6:]:
    print(f"  {r:>8.2f}{c:>7}{e2:>9.1f}  {a} -> {b}")

# are the top bigrams symmetric pairs (collocations) rather than directed code?
print("\n  SYMMETRY TEST (an encoding has direction; a collocation does not):")
seen = set()
for r, c, e2, a, b in rows[:12]:
    if (b, a) in seen or (a, b) in seen: continue
    seen.add((a, b))
    rev = bi.get((b, a), 0)
    exp_rev = pre[b] * (uni[a] / tot) if pre[b] else float("nan")
    print(f"    {a:>7} -> {b:<7} obs={c:<5} | {b:>7} -> {a:<7} obs={rev:<5} "
          f"| fwd/rev={c/max(rev,1):.2f}")
print("\n  CONTROL: same test on a NON-UAP word class (direction/compass terms),")
print("  which cannot plausibly be an NHI code, to see if the effect is generic.")
DIRS = ["north","south","east","west","northeast","northwest","southeast","southwest"]
DRX = re.compile(r"\b(" + "|".join(DIRS) + r")\b", re.I)
dseq = []
for e in ev:
    c = [m.group(1).lower() for m in DRX.finditer(e["description"] or "")]
    if len(c) >= 2: dseq.append(c)
def ce(sequences):
    b2 = collections.Counter(); p2 = collections.Counter()
    for s in sequences:
        for a, b in zip(s, s[1:]): b2[(a, b)] += 1; p2[a] += 1
    N = sum(b2.values()); H = 0.0
    for (a, b), c in b2.items(): H -= (c/N) * math.log2(c/p2[a])
    return H
H_obs_d = ce(dseq)
nd = np.array([ce([list(RNG.permutation(s)) for s in dseq]) for _ in range(500)])
pd_ = (1 + int((nd <= H_obs_d).sum())) / 501
print(f"    direction words: n_reports={len(dseq)} H_obs={H_obs_d:.4f} "
      f"null={nd.mean():.4f}+/-{nd.std(ddof=1):.4f} p={pd_:.4f}")
