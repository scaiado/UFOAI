"""GEIPAN national case database: official-disposition replication of the Blue Book T3 control.

GEIPAN (CNES, France) is the only state UAP program that publishes its complete
case file with the official disposition attached to every case.  That gives this
project something the Blue Book corpus could not: a ground-truth denominator.

Classification scheme (GEIPAN, published):
  A  identified, certain
  B  probably identified
  C  unidentified for LACK of information
  D  unidentified DESPITE adequate information  (D1 / D2 in internal use)

Blue Book conflated C and D into "unidentified".  GEIPAN separates them, which
makes the decisive comparison possible: D vs C isolates "anomalous" from
"data-poor", holding the investigating agency, era, country and method fixed.
"""
import json, re, math, collections, statistics
import numpy as np

SRC = "data/raw/geipan/geipan_cases.json"

CLS = ("A", "B", "C", "D")

def load():
    recs = json.load(open(SRC, encoding="utf-8-sig"))
    out = []
    for r in recs:
        c = (r.get("Classification") or "").strip().upper()
        if c not in CLS:
            continue
        d = {
            "id": r["ID Etude de Cas"],
            "title": (r.get("Titre du Cas") or "").strip(),
            "cls": c,
            "year": r.get("Année") if isinstance(r.get("Année"), int) else None,
            "dept": str(r.get("Code département") or "").strip(),
            "region": (r.get("Region") or "").strip(),
            "lat": r.get("Latitude"), "lon": r.get("Longitude"),
            "details": (r.get("Détails") or "").strip(),
            "ident": (r.get("Identification") or "").strip(),
            "phen": (r.get("Phenomenon") or "").strip(),
            "ctype": (r.get("Type de cas") or "").strip(),
            "docs": (r.get("Cas contenant des documents") or "").strip() == "Oui",
            "docname": (r.get("Document pour cas") or "").strip(),
            "revisited": (r.get("Cas revisité") or "").strip() == "Oui",
        }
        od = str(r.get("Observation date") or "")
        m = re.match(r"^(\d{2}|--)/(\d{2}|--)/(\d{4})$", od.strip())
        d["day"] = int(m.group(1)) if m and m.group(1) != "--" else None
        d["month"] = int(m.group(2)) if m and m.group(2) != "--" else None
        if m: d["year"] = int(m.group(3))
        d["prec"] = "day" if d["day"] else ("month" if d["month"] else "year")
        out.append(d)
    return out

# ---------------------------------------------------------------- utilities
def ztest_prop(k1, n1, k2, n2):
    """Two-proportion z-test, pooled."""
    if n1 == 0 or n2 == 0: return (float("nan"),) * 3
    p1, p2 = k1 / n1, k2 / n2
    p = (k1 + k2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    if se == 0: return (p1 - p2, float("nan"), float("nan"))
    z = (p1 - p2) / se
    from math import erfc
    return (p1 - p2, z, erfc(abs(z) / math.sqrt(2)))

def perm_diff(a, b, stat, iters=20000, rng=None):
    """Two-sample permutation test on an arbitrary statistic of a 0/1 or float vector."""
    rng = rng or np.random.default_rng(20261126)
    a = np.asarray(a, float); b = np.asarray(b, float)
    obs = stat(a) - stat(b)
    pool = np.concatenate([a, b]); na = len(a)
    hits = 0
    for _ in range(iters):
        rng.shuffle(pool)
        if abs(stat(pool[:na]) - stat(pool[na:])) >= abs(obs) - 1e-12:
            hits += 1
    return obs, (hits + 1) / (iters + 1)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1; dl = math.radians(lon2 - lon1)
    h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(h))

# ------------------------------------------------- G1: analyst-prose contamination
_STOP = set("""le la les de du des un une et en au aux a à dans sur pour par avec ce cet cette
ces il elle ils elles que qui quoi dont ou où est sont etait etaient ete se sa son ses leur
leurs ne pas plus tres tres d l n s c j y m t qu lui on nous vous je tu me te si mais donc
or ni car comme tout tous toute toutes meme aussi bien deux trois""".split())
_TOK = re.compile(r"[a-zà-ÿ]{3,}")

# Memoised because the permutation nulls call it ~63,000 times on texts that
# never change -- only the LABELS are shuffled between draws.  On the witness
# corpus (4.3 MB over 142 cases) the uncached path re-tokenises every document
# on every fit, turning a minutes-long test into an hours-long one.  `toks` is
# a pure function of its argument, so the cache is semantically transparent.
# Python caches a str's hash on the object itself, and the records hold the
# same string objects across draws, so lookups cost a pointer-hash.
_TOKCACHE = {}
_TOKCACHE_MAX = 16384


def toks(s):
    v = _TOKCACHE.get(s)
    if v is None:
        v = [t for t in _TOK.findall(s.lower()) if t not in _STOP]
        if len(_TOKCACHE) >= _TOKCACHE_MAX:
            _TOKCACHE.clear()
        _TOKCACHE[s] = v
    return v

def nb_cv(recs, field, arms, folds=5, seed=7):
    """Stratified k-fold multinomial-NB accuracy on a text field. Measures how much
    of the official disposition is already written into the prose."""
    rng = np.random.default_rng(seed)
    data = [(r, r["cls"]) for r in recs if r["cls"] in arms and r[field]]
    by = collections.defaultdict(list)
    for r, y in data: by[y].append(r)
    folds_ix = [[] for _ in range(folds)]
    for y, rs in by.items():
        idx = rng.permutation(len(rs))
        for j, i in enumerate(idx):
            folds_ix[j % folds].append((rs[i], y))
    accs, base = [], []
    for k in range(folds):
        te = folds_ix[k]; tr = [x for j, f in enumerate(folds_ix) if j != k for x in f]
        cnt = {y: collections.Counter() for y in arms}
        tot = {y: 0 for y in arms}; pri = collections.Counter()
        vocab = set()
        for r, y in tr:
            ts = toks(r[field]); cnt[y].update(ts); tot[y] += len(ts)
            pri[y] += 1; vocab.update(ts)
        V = len(vocab) or 1
        maj = pri.most_common(1)[0][0]
        ok = 0; okb = 0
        for r, y in te:
            ts = [t for t in toks(r[field]) if t in vocab]
            best, bs = None, -1e18
            for yy in arms:
                lp = math.log(pri[yy] / len(tr)) if pri[yy] else -1e18
                for t in ts:
                    lp += math.log((cnt[yy][t] + 1) / (tot[yy] + V))
                if lp > bs: bs, best = lp, yy
            ok += (best == y); okb += (maj == y)
        accs.append(ok / len(te)); base.append(okb / len(te))
    return float(np.mean(accs)), float(np.mean(base)), len(data)

# ------------------------------------------------------------------- main
def main():
    recs = load()
    R = {"n": len(recs)}
    print(f"GEIPAN cases loaded: {len(recs)}")
    dist = collections.Counter(r["cls"] for r in recs)
    R["class_dist"] = dict(dist)
    print("class dist:", dict(sorted(dist.items())))

    AB = [r for r in recs if r["cls"] in ("A", "B")]
    C  = [r for r in recs if r["cls"] == "C"]
    D  = [r for r in recs if r["cls"] == "D"]
    print(f"resolved A+B={len(AB)}  data-poor C={len(C)}  anomalous D={len(D)}")

    # ---- G1 analyst prose
    print("\n=== G1  analyst-prose contamination (how much disposition is in the text) ===")
    g1 = {}
    for name, arms in [("AB_vs_D", ("A","B","D")), ("C_vs_D", ("C","D")), ("AB_vs_C", ("A","B","C"))]:
        for fld in ("details", "ident"):
            acc, bl, n = nb_cv(recs, fld, arms)
            g1[f"{name}|{fld}"] = {"acc": acc, "majority_baseline": bl, "n": n, "gain": acc - bl}
            print(f"  {name:10s} {fld:8s} n={n:5d}  acc={acc:.4f}  majority={bl:.4f}  gain={acc-bl:+.4f}")
    R["G1_prose"] = g1

    # ---- G2 pre-classification facts
    print("\n=== G2  pre-classification facts: do they predict D? ===")
    g2 = {}
    # (a) documents attached (physical evidence present)
    for label, arm in [("D_vs_AB", (D, AB)), ("D_vs_C", (D, C))]:
        a, b = arm
        k1 = sum(r["docs"] for r in a); k2 = sum(r["docs"] for r in b)
        dp, z, p = ztest_prop(k1, len(a), k2, len(b))
        g2[f"docs|{label}"] = {"rate_a": k1/len(a), "rate_b": k2/len(b), "diff": dp, "z": z, "p": p,
                               "n_a": len(a), "n_b": len(b)}
        print(f"  docs attached   {label:9s} {k1/len(a):.4f} vs {k2/len(b):.4f}  diff={dp:+.4f} z={z:+.2f} p={p:.4g}")
    # (b) date precision (a proxy for information quality)
    for label, arm in [("D_vs_AB", (D, AB)), ("D_vs_C", (D, C))]:
        a, b = arm
        k1 = sum(r["prec"] == "day" for r in a); k2 = sum(r["prec"] == "day" for r in b)
        dp, z, p = ztest_prop(k1, len(a), k2, len(b))
        g2[f"dayprec|{label}"] = {"rate_a": k1/len(a), "rate_b": k2/len(b), "diff": dp, "z": z, "p": p}
        print(f"  day-precision   {label:9s} {k1/len(a):.4f} vs {k2/len(b):.4f}  diff={dp:+.4f} z={z:+.2f} p={p:.4g}")
    # (c) case type
    print("  case type distribution:")
    for arm, nm in ((AB, "A+B"), (C, "C"), (D, "D")):
        cc = collections.Counter(r["ctype"] for r in arm)
        tot = sum(cc.values())
        g2[f"ctype|{nm}"] = {k: v/tot for k, v in cc.items()}
        print(f"    {nm:4s} " + "  ".join(f"{k[:22]}={v/tot:.3f}" for k, v in cc.most_common(4)))
    R["G2_facts"] = g2

    # ---- G3 temporal: D-rate over time vs agency capacity
    print("\n=== G3  D-rate over time (is 'anomalous' a phenomenon or an agency artifact?) ===")
    by_yr = collections.defaultdict(lambda: collections.Counter())
    for r in recs:
        if r["year"]: by_yr[r["year"]][r["cls"]] += 1
    rows = []
    for y in sorted(by_yr):
        c = by_yr[y]; n = sum(c.values())
        if n >= 10:
            rows.append({"year": y, "n": n, "D": c["D"], "D_rate": c["D"]/n,
                         "C_rate": c["C"]/n, "AB_rate": (c["A"]+c["B"])/n})
    R["G3_by_year"] = rows
    for rr in rows:
        print(f"  {rr['year']}  n={rr['n']:4d}  D={rr['D']:3d} ({rr['D_rate']:.3f})  C={rr['C_rate']:.3f}  A+B={rr['AB_rate']:.3f}")
    # correlation of D-rate with caseload (investigative capacity dilution test)
    if len(rows) >= 6:
        ns = np.array([r["n"] for r in rows], float)
        ds = np.array([r["D_rate"] for r in rows], float)
        from scipy import stats as st
        rho, prho = st.spearmanr(ns, ds)
        R["G3_caseload_vs_Drate"] = {"spearman_rho": float(rho), "p": float(prho), "n_years": len(rows)}
        print(f"  Spearman(caseload, D-rate) rho={rho:+.4f} p={prho:.4g} over {len(rows)} years")

    json.dump(R, open("data/processed/geipan/geipan_analysis.json", "w"), indent=1, default=str)
    print("\nwrote data/processed/geipan/geipan_analysis.json")
    return R

if __name__ == "__main__":
    main()
