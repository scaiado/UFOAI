"""How much of the witness test's tier-to-tier disagreement is sampling noise?

The PV corpus tiers do not decay monotonically:

  W0 raw            n/arm 28  +0.1621  p=0.0017
  W2 lexicon out    n/arm 28  +0.1439  p=0.0083
  W3 length matched n/arm 22  -0.0444  p=0.4975
  W4 + numerals out n/arm 21  +0.1111  p=0.0416
  W5 descriptors    n/arm 24  +0.1667  p=0.0117
  W6 qual+len match n/arm 14  +0.0733  p=0.1081

Those rows are NOT nested samples.  The greedy matcher runs separately per tier
on different text, so each draws a different subset and n/arm swings 14-28.
Reading the sequence as a decay gradient -- as section 1.4's five tiers could
legitimately be read -- is therefore invalid here.

This script measures the instability instead of inferring it: hold the tier
fixed and vary ONLY the matcher seed.  The spread of the effect across seeds is
the sampling noise attributable to which cases the matcher happens to pair.  If
that spread covers the tier-to-tier differences, the "gradient" is noise.
"""
import os, re, sys, json, math, random, collections
sys.path.insert(0, "/home/user/UFOAI")
import numpy as np
from omega.geipan import toks
from omega.geipan_t3 import balanced_cv_acc
import omega.geipan_cd_witness as W

SEEDS = 24
NPERM = 200          # lower than the main run: we want the SPREAD, not each p


def effect_for_seed(recs, textfn, seed, mode):
    data = []
    for r in recs:
        t = textfn(r["raw"])
        if len(toks(t)) >= 10:
            data.append((dict(r, _txt=t), r["arm"]))
    if mode == "length":
        data = W._matched(data, lambda r: len(toks(r["_txt"])), 0.20, 10, seed)
    else:
        q = W._matched(data, lambda r: r.get("qual", 0.0), 0.25, 0.03, seed)
        data = W._matched(q, lambda r: len(toks(r["_txt"])), 0.25, 12, seed + 1)
    arms = collections.Counter(y for _, y in data)
    if len(arms) < 2 or min(arms.values()) < 6:
        return None
    obs, m = balanced_cv_acc(data, ("D", "C"), seed=11)
    null = np.array([balanced_cv_acc(data, ("D", "C"), seed=5000 + i,
                                     label_shuffle=True)[0] for i in range(NPERM)])
    p = float((np.sum(null >= obs - 1e-12) + 1) / (NPERM + 1))
    return {"seed": seed, "n_arm": m, "effect": obs - 0.5, "p": p,
            "null_sd": float(null.std(ddof=1))}


def main():
    # Which corpus to probe. The enquete corpus matters as much as pv: its W3
    # row is the only "detected at adequate power" result in the main run
    # (+0.2607, p=0.0017, MDD 0.2316) and it rose FIVEFOLD from +0.0500 when
    # length was matched. Either that is matcher noise, or length is a
    # SUPPRESSOR there -- D enquete reports run 2,526 tokens against C's 1,291,
    # so controlling length can unmask signal rather than remove it. If it
    # survives seed variation the enquete corpus becomes a POSITIVE CONTROL,
    # which is what makes the pv null interpretable instead of merely
    # underpowered.
    which = sys.argv[1] if len(sys.argv) > 1 else "pv"
    recs = W.load_witness({which})
    print(f"{which} corpus: {len(recs)} cases, "
          f"{dict(collections.Counter(r['arm'] for r in recs))}\n")

    strip = lambda t: W.norm(W.NUMERAL.sub(" ", W.LEAK_LEX.sub(
        " ", W.VERDICT_RX.sub(" ", t))))

    for label, textfn, mode in (
            ("W3 length-matched", lambda t: W.norm(W.LEAK_LEX.sub(
                " ", W.VERDICT_RX.sub(" ", t))), "length"),
            ("W6 quality+length matched", strip, "quality")):
        rows = [r for s in range(SEEDS)
                if (r := effect_for_seed(recs, textfn, s, mode))]
        if not rows:
            print(f"{label}: no usable seeds")
            continue
        eff = np.array([r["effect"] for r in rows])
        ns = np.array([r["n_arm"] for r in rows])
        sig = sum(1 for r in rows if r["p"] < 0.05)
        print(f"=== {label} ===")
        print(f"  seeds usable      : {len(rows)}/{SEEDS}")
        print(f"  n/arm             : {ns.min()}-{ns.max()} (median {int(np.median(ns))})")
        print(f"  effect min / max  : {eff.min():+.4f} / {eff.max():+.4f}")
        print(f"  effect mean +- sd : {eff.mean():+.4f} +- {eff.std(ddof=1):.4f}")
        print(f"  effect median     : {np.median(eff):+.4f}")
        print(f"  seeds with p<0.05 : {sig}/{len(rows)} ({sig/len(rows):.0%})")
        print(f"  RANGE             : {eff.max()-eff.min():.4f}")
        print(f"  sign flips        : "
              f"{'YES' if (eff.min() < 0 < eff.max()) else 'no'}")
        print()

    print("Interpretation: if the across-seed RANGE is comparable to the")
    print("tier-to-tier differences in the main run, then the tier sequence")
    print("carries no gradient information and must not be read as one.")


if __name__ == "__main__":
    main()
