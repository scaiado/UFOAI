"""GEIPAN C-vs-D: independent replication of the Blue Book T3 control, with power.

Blue Book T3 asked whether the kinematic/descriptor structure of UNIDENTIFIED
reports differs from RESOLVED reports, and returned null at adequate power
(p=0.2727, MDD 0.1169 against a 0.112 target).

GEIPAN permits the sharper version.  Both C and D are officially unidentified;
C is unidentified for lack of information, D despite adequate information.  If
"strangeness" is a real property of a subset of reports, D is where it lives,
and D should be separable from C.  Agency, era, country, language, investigator
and write-up convention are all held fixed.
"""
import sys, json, math, collections, random
sys.path.insert(0, "/home/user/UFOAI")
import numpy as np
from omega.geipan import load, toks

RNG = np.random.default_rng(20261126)

def nb_fit(train, arms):
    cnt = {y: collections.Counter() for y in arms}; tot = {y: 0 for y in arms}
    pri = collections.Counter(); vocab = set()
    for r, y in train:
        ts = toks(r["_txt"]); cnt[y].update(ts); tot[y] += len(ts)
        pri[y] += 1; vocab.update(ts)
    return cnt, tot, pri, vocab, len(train)

def nb_pred(r, arms, cnt, tot, pri, vocab, n):
    V = len(vocab) or 1
    ts = [t for t in toks(r["_txt"]) if t in vocab]
    best, bs = None, -1e18
    for y in arms:
        if not pri[y]: continue
        lp = math.log(pri[y] / n)
        for t in ts: lp += math.log((cnt[y][t] + 1) / (tot[y] + V))
        if lp > bs: bs, best = lp, y
    return best

def balanced_cv_acc(data, arms, folds=5, seed=0, label_shuffle=False):
    """Balanced (size-matched) k-fold accuracy so the majority baseline is 0.5."""
    rng = random.Random(seed)
    by = collections.defaultdict(list)
    for r, y in data: by[y].append(r)
    m = min(len(v) for v in by.values())
    bal = []
    for y, rs in by.items():
        rs = rs[:]; rng.shuffle(rs)
        bal += [(r, y) for r in rs[:m]]
    if label_shuffle:
        ys = [y for _, y in bal]; rng.shuffle(ys)
        bal = [(r, y) for (r, _), y in zip(bal, ys)]
    rng.shuffle(bal)
    fs = [bal[i::folds] for i in range(folds)]
    accs = []
    for k in range(folds):
        te = fs[k]; tr = [x for j, f in enumerate(fs) if j != k for x in f]
        mdl = nb_fit(tr, arms)
        ok = sum(nb_pred(r, arms, *mdl) == y for r, y in te)
        accs.append(ok / len(te))
    return float(np.mean(accs)), m

def run(field, arms, name, nperm=400):
    recs = load()
    data = [(dict(r, _txt=r[field]), ("D" if r["cls"] == "D" else "notD"))
            for r in recs if r["cls"] in arms and r[field]]
    labs = ("D", "notD")
    obs, m = balanced_cv_acc(data, labs, seed=11)
    # permutation null: shuffle labels, same balanced design
    null = [balanced_cv_acc(data, labs, seed=1000 + i, label_shuffle=True)[0] for i in range(nperm)]
    null = np.array(null)
    p = (np.sum(null >= obs - 1e-12) + 1) / (nperm + 1)
    # power: MDD at alpha .05, 80% power, for a balanced-accuracy statistic
    sd = null.std(ddof=1)
    mdd = 0.5 + 1.645 * sd + 0.84 * sd          # one-sided alpha .05, power .80
    return {"name": name, "field": field, "arm_n_each": m, "obs_bal_acc": obs,
            "null_mean": float(null.mean()), "null_sd": float(sd), "p": float(p),
            "z": float((obs - null.mean()) / sd) if sd else float("nan"),
            "mdd_bal_acc": float(mdd), "mdd_effect": float(mdd - 0.5), "nperm": nperm}

if __name__ == "__main__":
    out = []
    for fld in ("details", "ident"):
        out.append(run(fld, ("C", "D"), "C_vs_D (both officially unidentified)"))
        out.append(run(fld, ("A", "B", "D"), "AB_vs_D (resolved vs anomalous)"))
    print(f"{'test':42s} {'field':8s} {'n/arm':>6s} {'bal.acc':>8s} {'null':>7s} {'z':>7s} {'p':>8s} {'MDD':>7s}")
    for r in out:
        print(f"{r['name']:42s} {r['field']:8s} {r['arm_n_each']:6d} {r['obs_bal_acc']:8.4f} "
              f"{r['null_mean']:7.4f} {r['z']:+7.2f} {r['p']:8.4f} {r['mdd_effect']:+7.4f}")
    json.dump(out, open("data/processed/geipan/geipan_t3.json", "w"), indent=1)
    print("\nwrote data/processed/geipan/geipan_t3.json")
