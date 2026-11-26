"""Tiered decontamination of GEIPAN analyst narratives, then re-run C-vs-D.

The raw narratives end in a verdict sentence that states the classification
outright ("Le GEIPAN classe ce cas en D : Phénomène étrange à très étrange /
de consistance moyenne à forte"), so any classifier trained on raw text is
reading the answer key.  This strips the leak in four tiers and reports the
accuracy gradient, so the result does not depend on one arbitrary cleaning rule.

L0  raw
L1  drop sentences naming GEIPAN or stating a classification
L2  L1 + drop the verdict lexicon (manque d'informations, non identifié,
    inexpliqué, étrange, consistance, PAN X)
L3  L2 + drop every sentence carrying an analyst-reasoning marker
    (hypothèse, méprise, conclut, explication, enquête, témoignage recueilli)
"""
import sys, re, json, math, collections, random
sys.path.insert(0, "/home/user/UFOAI")
import numpy as np
from omega.geipan import load, toks
from omega.geipan_t3 import balanced_cv_acc

_SENT = re.compile(r"(?<=[.!?])\s+")
_CLSSENT = re.compile(r"GEIPAN|class[ée]|classifi|\bPAN\s*[ABCD]\b", re.I)
_LEAK = re.compile(
    r"manque\s+d[\'e]\s*\w+|non[\s-]identifi\w*|inexpliqu\w*|non\s+expliqu\w*|"
    r"[ée]trang\w*|consistance|\bPAN\s*[ABCD]\b|identifi\w*|explicat\w*", re.I)
_REASON = re.compile(
    r"hypoth[èe]se|m[ée]prise|conclu\w*|enqu[êe]t\w*|t[ée]moignage\s+(?:recueilli|unique|a\s+[ée]t[ée])|"
    r"vraisembl\w*|probab\w*|compatib\w*|incompatib\w*|co[hî]ncid\w*|v[ée]rificat\w*", re.I)

def clean(txt, tier):
    if tier == 0: return txt
    sents = _SENT.split(txt)
    if tier >= 1: sents = [s for s in sents if not _CLSSENT.search(s)]
    if tier >= 3: sents = [s for s in sents if not _REASON.search(s)]
    out = " ".join(sents)
    if tier >= 2: out = _LEAK.sub(" ", out)
    return re.sub(r"\s+", " ", out).strip()

def run(arms, nperm=600, folds=5):
    recs = load()
    res = []
    for tier in (0, 1, 2, 3):
        data = []
        for r in recs:
            if r["cls"] not in arms: continue
            t = clean(r["details"], tier)
            if len(toks(t)) >= 5:
                data.append((dict(r, _txt=t), "D" if r["cls"] == "D" else "notD"))
        labs = ("D", "notD")
        obs, m = balanced_cv_acc(data, labs, folds=folds, seed=11)
        null = np.array([balanced_cv_acc(data, labs, folds=folds, seed=2000 + i,
                                         label_shuffle=True)[0] for i in range(nperm)])
        sd = null.std(ddof=1)
        p = (np.sum(null >= obs - 1e-12) + 1) / (nperm + 1)
        mdd = 1.645 * sd + 0.84 * sd
        # mean surviving token count, to show how much text each tier destroys
        tl = float(np.mean([len(toks(r["_txt"])) for r, _ in data]))
        res.append({"tier": tier, "n_each_arm": m, "n_total": len(data), "mean_tokens": tl,
                    "bal_acc": obs, "null_mean": float(null.mean()), "null_sd": float(sd),
                    "z": float((obs - null.mean()) / sd) if sd else float("nan"),
                    "p": float(p), "mdd_effect": float(mdd),
                    "effect": float(obs - 0.5),
                    "detectable": bool((obs - 0.5) > mdd)})
    return res

if __name__ == "__main__":
    out = {}
    for nm, arms in [("C_vs_D", ("C", "D")), ("AB_vs_D", ("A", "B", "D"))]:
        print(f"\n########## {nm}  (both arms officially unidentified)" if nm == "C_vs_D"
              else f"\n########## {nm}  (resolved vs anomalous)")
        print(f"{'tier':5s} {'n/arm':>6s} {'tok':>6s} {'bal.acc':>8s} {'null':>7s} {'sd':>6s} "
              f"{'z':>7s} {'p':>8s} {'effect':>8s} {'MDD':>7s} {'sig':>5s}")
        rs = run(arms)
        out[nm] = rs
        for r in rs:
            print(f"L{r['tier']:<4d} {r['n_each_arm']:6d} {r['mean_tokens']:6.0f} {r['bal_acc']:8.4f} "
                  f"{r['null_mean']:7.4f} {r['null_sd']:6.4f} {r['z']:+7.2f} {r['p']:8.4f} "
                  f"{r['effect']:+8.4f} {r['mdd_effect']:7.4f} {'YES' if r['detectable'] else 'no':>5s}")
    json.dump(out, open("data/processed/geipan/geipan_decontam.json", "w"), indent=1)
    print("\nwrote data/processed/geipan/geipan_decontam.json")
