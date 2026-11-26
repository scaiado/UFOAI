"""PROJECT OMEGA Phase 1 - candidate generation & near-duplicate matching.

Strategy: block on date, score candidates with THREE independent lexical
signals (IDF-weighted word cosine, character 4-gram Jaccard, rare-token
overlap), veto on geographic/locational incompatibility, then union-find.

Lexical (not semantic) similarity is deliberate: recopied catalog entries
share surface wording, whereas sentence embeddings rate any two
"bright light over farmland" reports as near-identical and would merge
genuinely distinct events.
"""
from __future__ import annotations
import sys, re, math, json, collections, itertools
import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
sys.path.insert(0, "/home/user/UFOAI/omega")
import corpus

# ---------------------------------------------------------------- utilities
class DSU:
    def __init__(s, n): s.p = list(range(n)); s.r = [0]*n
    def find(s, x):
        while s.p[x] != x: s.p[x] = s.p[s.p[x]]; x = s.p[x]
        return x
    def union(s, a, b):
        ra, rb = s.find(a), s.find(b)
        if ra == rb: return False
        if s.r[ra] < s.r[rb]: ra, rb = rb, ra
        s.p[rb] = ra
        if s.r[ra] == s.r[rb]: s.r[ra] += 1
        return True

def shingles(s, k=4):
    s = re.sub(r"\s+", " ", s)
    return {s[i:i+k] for i in range(max(0, len(s)-k+1))} if len(s) >= k else {s}

def jacc(a, b):
    if not a or not b: return 0.0
    i = len(a & b)
    return i / (len(a) + len(b) - i)

LOC_STOP = set("""the of and near city town county state province region area north south
east west central upper lower new saint st mt mount fort ft air force base afb
usa us united states america""".split())

# Tokens too coarse to establish identity on their own: countries, large
# regions, US states. A shared token from this set is weak evidence; a shared
# token outside it (a settlement, installation or landmark) is strong.
COARSE = set("""usa us united states america american canada canadian mexico mexican brazil
brazilian argentina argentine chile chilean peru peruvian venezuela colombia uruguay
england english britain british scotland wales ireland irish france french germany german
italy italian spain spanish portugal portuguese belgium belgian netherlands holland dutch
denmark danish norway norwegian sweden swedish finland finnish poland polish russia russian
ussr soviet ukraine austria austrian switzerland swiss greece greek turkey turkish
china chinese japan japanese korea korean india indian australia australian zealand
africa african egypt egyptian israel israeli iran iranian iraq morocco algeria tunisia
yugoslavia serbia croatia romania romanian hungary hungarian bulgaria czech slovakia
alabama alaska arizona arkansas california colorado connecticut delaware florida georgia
hawaii idaho illinois indiana iowa kansas kentucky louisiana maine maryland massachusetts
michigan minnesota mississippi missouri montana nebraska nevada hampshire jersey mexico
york carolina dakota ohio oklahoma oregon pennsylvania island tennessee texas utah
vermont virginia washington wisconsin wyoming ontario quebec alberta columbia manitoba
saskatchewan scotia brunswick newfoundland
atlantic pacific ocean sea gulf coast europe asia continent antarctica antarctic
county state province region district department prefecture provincia
afb nas base airport air force field army navy station
rsa uk usaf
beach lake river valley hill hills mountain mountains bay port harbor harbour point
springs creek park range proving grounds sands desert forest wood woods island islands
north south east west central north-east northeast northwest southeast southwest
city town village hamlet airport airfield aerodrome""".split())

def specific_tokens(t):
    return {x for x in t if x not in COARSE}
def loc_tokens(s, extra=()):
    s = " ".join([str(s)] + [str(e) for e in extra])
    s = re.sub(r"[^a-z ]+", " ", s.lower())
    return {t for t in s.split() if len(t) > 2 and t not in LOC_STOP}

# date tolerance in days, by the coarser of the two precisions
def date_ok(a, b):
    if a.year is None or b.year is None: return False
    pa, pb = a.prec, b.prec
    coarse = "year" if "year" in (pa, pb) else ("month" if "month" in (pa, pb) else "day")
    pre1900 = (a.year < 1900) or (b.year < 1900)
    # tolerance follows the DATE PRECISION. Era widens only coarse precisions
    # (old sources disagree on month/year); a day-precise pre-1900 date gets
    # only +-2d slack for calendar/source discrepancies, not +-1 year, which
    # otherwise merges distinct events inside the 1897 airship wave.
    if coarse == "day":
        tol = 2 if pre1900 else 1
    elif coarse == "month":
        tol = 62 if pre1900 else 31
    else:
        tol = 366 if pre1900 else 183
    ja, jb = corpus.to_jdn(a.year, a.month, a.day), corpus.to_jdn(b.year, b.month, b.day)
    if coarse == "year":
        return abs(a.year - b.year) <= (1 if pre1900 else 0)
    return abs(ja - jb) <= tol

def geo_veto(a, b, km_modern=150.0, km_ancient=400.0):
    """True => definitely different places."""
    if a.lat is None or b.lat is None: return False
    lim = km_ancient if (a.year or 2000) < 1900 or (b.year or 2000) < 1900 else km_modern
    return corpus.haversine(a.lat, a.lon, b.lat, b.lon) > lim

def loc_veto(a, b):
    ta, tb = a._lt, b._lt
    if len(ta) >= 1 and len(tb) >= 1 and not (ta & tb):
        # both name places and share no token at all
        return True
    return False

# ---------------------------------------------------------------- main
def build(recs, cos_floor=0.28, verbose=True):
    n = len(recs)
    for r in recs:
        r._lt = loc_tokens(r.location, getattr(r, "places", ()) or ())
    docs = [r.norm if r.norm else "zzz" for r in recs]
    if verbose: print(f"[tfidf] fitting on {n} docs ...", flush=True)
    vec = TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=2,
                          sublinear_tf=True, max_features=600000, dtype=np.float32)
    X = vec.fit_transform(docs)
    X = sparse.csr_matrix(X)
    if verbose: print(f"[tfidf] matrix {X.shape}, nnz={X.nnz}", flush=True)

    # ---- blocking: year buckets; low-precision & pre-1900 recs also go in neighbours
    buckets = collections.defaultdict(list)
    for i, r in enumerate(recs):
        if r.year is None: continue
        buckets[r.year].append(i)
        if r.prec == "year" or r.year < 1900:
            buckets[r.year - 1].append(i); buckets[r.year + 1].append(i)

    cand = []           # (i, j, cos)
    for yr in sorted(buckets):
        idx = sorted(set(buckets[yr]))
        if len(idx) < 2: continue
        Xi = X[idx]
        S = (Xi @ Xi.T).tocoo()
        for a, b, v in zip(S.row, S.col, S.data):
            if a >= b or v < cos_floor: continue
            cand.append((idx[a], idx[b], float(v)))
        if verbose and yr % 10 == 0:
            print(f"[block] {yr}: n={len(idx)} cum_cand={len(cand)}", flush=True)
    # dedupe candidate pairs (records in overlapping year buckets)
    seen = {}
    for i, j, v in cand:
        k = (i, j) if i < j else (j, i)
        if k not in seen or v > seen[k]: seen[k] = v
    cand = [(i, j, v) for (i, j), v in seen.items()]
    if verbose: print(f"[cand] {len(cand)} unique candidate pairs >= cos {cos_floor}", flush=True)
    return X, vec, cand

def place_date_candidates(recs, X, max_group=60):
    """Second candidate generator: block on exact date + shared specific place
    token, independent of wording. Required because the two styles present in
    the corpus (telegraphic vs prose) can share almost no vocabulary for the
    same event, so a text-similarity floor alone loses real duplicates."""
    import collections as _c
    idx = _c.defaultdict(list)
    for i, r in enumerate(recs):
        if r.prec != "day" or r.year is None: continue
        for t in specific_tokens(r._lt):
            idx[(r.year, r.month, r.day, t)].append(i)
    Xn = X
    out = {}
    for key, members in idx.items():
        if len(members) < 2 or len(members) > max_group: continue
        for a in range(len(members)):
            for b in range(a + 1, len(members)):
                i, j = members[a], members[b]
                if i == j: continue
                k = (i, j) if i < j else (j, i)
                if k in out: continue
                v = float((Xn[k[0]] @ Xn[k[1]].T).toarray()[0, 0])
                out[k] = v
    return [(i, j, v) for (i, j), v in out.items()]

def score_pairs(recs, cand, shing_cache=None):
    """Attach date/geo/jaccard/rare-token features to each candidate pair."""
    sh = shing_cache if shing_cache is not None else {}
    out = []
    for i, j, cos in cand:
        a, b = recs[i], recs[j]
        if not date_ok(a, b): continue
        if geo_veto(a, b): continue
        for k in (i, j):
            if k not in sh: sh[k] = shingles(recs[k].norm)
        jc = jacc(sh[i], sh[j])
        ta, tb = set(a.norm.split()), set(b.norm.split())
        inter = ta & tb
        rare = {t for t in inter if len(t) > 5}
        out.append(dict(i=i, j=j, cos=cos, jac=jc,
                        ntok=min(len(ta), len(tb)), ninter=len(inter), nrare=len(rare),
                        same_cat=a.catalog == b.catalog,
                        geo_both=(a.lat is not None and b.lat is not None),
                        locveto=loc_veto(a, b)))
    return out, sh
