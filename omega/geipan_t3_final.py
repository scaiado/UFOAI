"""GEIPAN C-vs-D, tier L4: extended leak strip + length matching.

Token attribution on the L3 result showed the surviving separation was leakage,
not content:

  C side   "manquons" 163/1017 vs 0/106, "informations" 179 vs 3, "recent" 56 vs 0
           -- the C verdict phrase ("nous manquons d'informations"), conjugated,
           which the L2 lexicon missed.
  A/B side "lanternes" 254/2271 vs 0/106, "bolide" 87 vs 0, "iss" 72 vs 0,
           "venus" 121 vs 1 -- the NAMES OF THE EXPLANATIONS.  A resolved
           narrative states its cause; an unresolved one cannot.  The AB-vs-D
           comparison is therefore circular by construction and is withdrawn,
           not fixed: stripping every cause-noun would delete the content of the
           A/B arm itself.
  length   a single length threshold alone reaches 0.6321 balanced accuracy
           (D median 60 tokens vs C 44.5) -- and "longer narrative" is the
           operational meaning of "adequate information", i.e. the
           classification criterion, not a property of the event.

L4 keeps only C vs D, strips the conjugated verdict lexicon, and matches the two
arms on narrative length so length cannot carry the result.
"""
import sys, re, json, collections, random
sys.path.insert(0, "/home/user/UFOAI")
import numpy as np
from omega.geipan import load, toks
from omega.geipan_decontam import clean
from omega.geipan_t3 import balanced_cv_acc

# conjugated / inflected forms of the verdict language, plus the C boilerplate
_LEAK4 = re.compile(
    r"manquon\w*|manqu\w*|informat\w*|renseignement\w*|pr[ée]cis\w*|"
    r"r[ée]cent\w*|ancien\w*|d[ée]clar\w*|rapport\w*|donn[ée]e\w*|"
    r"analys\w*|correspond\w*|[ée]voqu\w*|compatib\w*|cons[ée]quen\w*|"
    r"revisit\w*|recueill\w*|t[ée]moi\w*|enqu[êe]t\w*|cas\b|geipan|"
    r"date\w*|heure\w*|jour\w*|mois\b", re.I)

def clean4(txt):
    t = clean(txt, 3)
    t = _LEAK4.sub(" ", t)
    return re.sub(r"\s+", " ", t).strip()

def length_matched(data, tol=0.12, seed=5):
    """Greedy 1:1 nearest-length matching of D cases to not-D cases."""
    rng = random.Random(seed)
    D = [(r, y) for r, y in data if y == "D"]
    N = [(r, y) for r, y in data if y == "notD"]
    pool = sorted(N, key=lambda x: len(toks(x[0]["_txt"])))
    plen = [len(toks(x[0]["_txt"])) for x in pool]
    used = set(); out = []
    for r, y in D:
        L = len(toks(r["_txt"]))
        cands = [i for i, pl in enumerate(plen)
                 if i not in used and abs(pl - L) <= max(3, tol * L)]
        if not cands: continue
        j = rng.choice(cands); used.add(j)
        out.append((r, y)); out.append(pool[j])
    return out

def run(nperm=600):
    recs = load()
    data = []
    for r in recs:
        if r["cls"] not in ("C", "D"): continue
        t = clean4(r["details"])
        if len(toks(t)) >= 5:
            data.append((dict(r, _txt=t), "D" if r["cls"] == "D" else "notD"))
    res = []
    for mode in ("unmatched", "length_matched"):
        d = data if mode == "unmatched" else length_matched(data)
        nD = sum(1 for _, y in d if y == "D")
        tD = [len(toks(r["_txt"])) for r, y in d if y == "D"]
        tN = [len(toks(r["_txt"])) for r, y in d if y == "notD"]
        obs, m = balanced_cv_acc(d, ("D", "notD"), seed=11)
        null = np.array([balanced_cv_acc(d, ("D", "notD"), seed=3000 + i,
                                         label_shuffle=True)[0] for i in range(nperm)])
        sd = null.std(ddof=1)
        p = float((np.sum(null >= obs - 1e-12) + 1) / (nperm + 1))
        mdd = float(1.645 * sd + 0.84 * sd)
        res.append({"mode": mode, "n_D": nD, "n_each_arm": m,
                    "median_tok_D": float(np.median(tD)), "median_tok_notD": float(np.median(tN)),
                    "bal_acc": obs, "null_mean": float(null.mean()), "null_sd": float(sd),
                    "z": float((obs - null.mean()) / sd), "p": p,
                    "effect": float(obs - 0.5), "mdd_effect": mdd,
                    "detectable": bool((obs - 0.5) > mdd)})
    return res

if __name__ == "__main__":
    rs = run()
    print("GEIPAN  C vs D  (both arms officially unidentified; L4 decontamination)")
    print(f"{'mode':15s} {'n/arm':>6s} {'tokD':>6s} {'tokC':>6s} {'bal.acc':>8s} {'null':>7s} "
          f"{'sd':>6s} {'z':>7s} {'p':>8s} {'effect':>8s} {'MDD':>7s} {'sig':>4s}")
    for r in rs:
        print(f"{r['mode']:15s} {r['n_each_arm']:6d} {r['median_tok_D']:6.1f} {r['median_tok_notD']:6.1f} "
              f"{r['bal_acc']:8.4f} {r['null_mean']:7.4f} {r['null_sd']:6.4f} {r['z']:+7.2f} "
              f"{r['p']:8.4f} {r['effect']:+8.4f} {r['mdd_effect']:7.4f} "
              f"{'YES' if r['detectable'] else 'no':>4s}")
    json.dump(rs, open("data/processed/geipan/geipan_t3_final.json", "w"), indent=1)
    print("\nwrote data/processed/geipan/geipan_t3_final.json")

# ---------------------------------------------------------------- tier L5
# L4 attribution showed the surviving separation is MEASUREMENT DENSITY:
#   toward D  estimee 12/106 vs 2, metres 26 vs 12, secondes 42 vs 20,
#             environ 36 vs 16, masse, disparaitre, sombre
#   toward C  angulaire 2 vs 9, faible 9 vs 26, courte, rien, peut, ans
# i.e. D narratives contain quantities and C narratives contain hedges.  But
# "the narrative contains quantities" IS the operational meaning of "adequate
# information", which is the criterion separating D from C.  L5 removes every
# numeral and quantity word.  If the effect dies, measurement density was the
# whole effect and the test is unidentifiable on analyst prose.
_QTY = re.compile(
    r"\d+|\b(?:m[èe]tres?|kilom[èe]tres?|km|secondes?|minutes?|heures?|"
    r"environ|estim\w*|approximat\w*|diam[èe]tres?|angulaires?|altitudes?|"
    r"distances?|vitesses?|tailles?|dimensions?|longueurs?|largeurs?|"
    r"hauteurs?|masses?|degr[ée]s?|dur[ée]\w*|faibl\w*|fort\w*|grand\w*|"
    r"petit\w*|court\w*|long\w*|lent\w*|rapid\w*)\b", re.I)

def clean5(txt):
    return re.sub(r"\s+", " ", _QTY.sub(" ", clean4(txt))).strip()

def run_l5(nperm=600):
    recs = load()
    data = []
    for r in recs:
        if r["cls"] not in ("C", "D"): continue
        t = clean5(r["details"])
        if len(toks(t)) >= 5:
            data.append((dict(r, _txt=t), "D" if r["cls"] == "D" else "notD"))
    out = []
    for mode in ("unmatched", "length_matched"):
        d = data if mode == "unmatched" else length_matched(data)
        tD = [len(toks(r["_txt"])) for r, y in d if y == "D"]
        tN = [len(toks(r["_txt"])) for r, y in d if y == "notD"]
        obs, m = balanced_cv_acc(d, ("D", "notD"), seed=11)
        null = np.array([balanced_cv_acc(d, ("D", "notD"), seed=4000 + i,
                                         label_shuffle=True)[0] for i in range(nperm)])
        sd = null.std(ddof=1)
        out.append({"tier": "L5", "mode": mode, "n_each_arm": m,
                    "median_tok_D": float(np.median(tD)), "median_tok_notD": float(np.median(tN)),
                    "bal_acc": obs, "null_mean": float(null.mean()), "null_sd": float(sd),
                    "z": float((obs - null.mean()) / sd),
                    "p": float((np.sum(null >= obs - 1e-12) + 1) / (nperm + 1)),
                    "effect": float(obs - 0.5), "mdd_effect": float(2.485 * sd),
                    "detectable": bool((obs - 0.5) > 2.485 * sd)})
    return out
