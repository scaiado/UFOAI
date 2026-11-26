"""Seed-average the §1.4 decontamination ladder.  Pays the debt §5 item 1 names.

WHY THIS EXISTS
---------------
§1.4 reported six tiers as a decay gradient:

  L0 +0.3494 / L1 +0.3019 / L2 +0.3113 / L3 +0.2643 / L4 +0.2176 / L5 +0.1795

and +0.1795 became "the project's upper bound on content", quoted in four
documents.  Every one of those numbers is a SINGLE DRAW.  There are two
independent seed dependencies, not one:

  (1) MATCHER seed.  `geipan_t3_final.length_matched(data, tol=0.12, seed=5)`
      pairs each D case to a random length-eligible C case.  seed=5 is a
      default nobody varied.  Affects L4, L5.

  (2) DOWNSAMPLE seed.  `balanced_cv_acc(..., seed=11)` shuffles each arm and
      keeps `m = min(arm sizes)` from each.  The C arm has 1020 cases and the D
      arm 106, so on every UNMATCHED tier this is a 106-of-1020 draw -- a 10:1
      subsample decided by one integer.  Affects L0, L1, L2, L3 (and rides on
      top of the matcher draw at L4/L5).

Session 3 measured matched witness tiers swinging +-0.1 across matcher seeds
(enquete W3's single draw hit +0.2607 against a 24-seed mean of +0.150).  So
the prior that these are stable point estimates is already falsified elsewhere
in this project.

WHAT IT MEASURES
----------------
Per tier, hold the text-cleaning fixed and vary one seed at a time:

  matcher sweep   (L4, L5)          24 matcher seeds, CV seed fixed at 11
  downsample sweep (L0..L5)         24 CV seeds, matcher seed fixed at 5

Reported per sweep: mean +- sd, median, min/max, range, n/arm range, and the
fraction of seeds reaching p<0.05.  The range is the number that matters: if it
is comparable to the tier-to-tier differences in §1.4, the ladder carries no
gradient information and must not be read as one.
"""
import sys, json, collections
sys.path.insert(0, "/home/user/UFOAI")
import numpy as np
from omega.geipan import load, toks
from omega.geipan_decontam import clean
from omega.geipan_t3 import balanced_cv_acc
from omega.geipan_t3_final import clean4, clean5, length_matched

SEEDS = 24
NPERM = 200          # spread is the target, not each individual p
ARMS = ("D", "notD")

# tier label -> (cleaning fn, whether the tier length-matches)
TIERS = {
    "L0": (lambda t: clean(t, 0), False),
    "L1": (lambda t: clean(t, 1), False),
    "L2": (lambda t: clean(t, 2), False),
    "L3": (lambda t: clean(t, 3), False),
    "L4": (clean4, True),
    "L5": (clean5, True),
}


def build(recs, cleanfn, min_tok):
    """Clean every C/D narrative and keep the ones with enough tokens left."""
    data = []
    for r in recs:
        if r["cls"] not in ("C", "D"):
            continue
        t = cleanfn(r["details"])
        if len(toks(t)) >= min_tok:
            data.append((dict(r, _txt=t), "D" if r["cls"] == "D" else "notD"))
    return data


def one_draw(data, matched, matcher_seed, cv_seed):
    """One (matcher, downsample) draw -> effect, n/arm, p, MDD."""
    d = length_matched(data, seed=matcher_seed) if matched else data
    arms = collections.Counter(y for _, y in d)
    if len(arms) < 2 or min(arms.values()) < 6:
        return None
    obs, m = balanced_cv_acc(d, ARMS, seed=cv_seed)
    null = np.array([balanced_cv_acc(d, ARMS, seed=90000 + 7 * cv_seed + i,
                                     label_shuffle=True)[0]
                     for i in range(NPERM)])
    sd = float(null.std(ddof=1))
    p = float((np.sum(null >= obs - 1e-12) + 1) / (NPERM + 1))
    return {"effect": float(obs - 0.5), "bal_acc": float(obs), "n_arm": int(m),
            "p": p, "null_sd": sd, "mdd": 2.485 * sd}


def summarise(label, rows, single_value):
    eff = np.array([r["effect"] for r in rows])
    ns = np.array([r["n_arm"] for r in rows])
    sig = sum(1 for r in rows if r["p"] < 0.05)
    s = {"sweep": label, "seeds_usable": len(rows),
         "n_arm_min": int(ns.min()), "n_arm_max": int(ns.max()),
         "n_arm_median": int(np.median(ns)),
         "effect_mean": float(eff.mean()), "effect_sd": float(eff.std(ddof=1)),
         "effect_median": float(np.median(eff)),
         "effect_min": float(eff.min()), "effect_max": float(eff.max()),
         "effect_range": float(eff.max() - eff.min()),
         "frac_p05": sig / len(rows), "n_p05": sig,
         "sign_flips": bool(eff.min() < 0 < eff.max()),
         "published_single_draw": single_value,
         "published_percentile": float((eff < single_value).mean()),
         "mean_mdd": float(np.mean([r["mdd"] for r in rows]))}
    return s


# the §1.4 published single-draw effects, for the percentile column
PUBLISHED = {"L0": 0.3494, "L1": 0.3019, "L2": 0.3113,
             "L3": 0.2643, "L4": 0.2176, "L5": 0.1795}


def main():
    which = sys.argv[1:] or list(TIERS)
    recs = load()
    print(f"GEIPAN C-vs-D tier seed stability  |  {SEEDS} seeds/sweep, "
          f"{NPERM} perms/draw")
    print(f"corpus: {len(recs)} cases, "
          f"{dict(collections.Counter(r['cls'] for r in recs))}\n")
    out = {}

    hdr = (f"{'tier':5s} {'sweep':11s} {'n/arm':>9s} {'mean+-sd':>17s} "
           f"{'median':>8s} {'min':>8s} {'max':>8s} {'range':>7s} "
           f"{'p<.05':>7s} {'1.4 draw':>9s} {'pctile':>7s}")
    print(hdr)
    print("-" * len(hdr))

    for tier in which:
        cleanfn, matched = TIERS[tier]
        min_tok = 10 if matched else 5
        data = build(recs, cleanfn, min_tok)
        out[tier] = {"n_cases": len(data), "matched": matched, "sweeps": []}

        sweeps = [("downsample", [(5, s) for s in range(SEEDS)])]
        if matched:
            sweeps.insert(0, ("matcher", [(s, 11) for s in range(SEEDS)]))
            # The two marginal sweeps hold the OTHER seed at its published
            # value, and the published value is a low draw on both axes -- so
            # neither marginal mean is the estimate.  Vary both together.
            sweeps.append(("joint", [(s, 11 + 3 * s) for s in range(SEEDS)]))

        for name, pairs in sweeps:
            rows = [r for ms, cs in pairs
                    if (r := one_draw(data, matched, ms, cs))]
            if not rows:
                print(f"{tier:5s} {name:11s} no usable seeds")
                continue
            s = summarise(name, rows, PUBLISHED[tier])
            s["draws"] = rows
            out[tier]["sweeps"].append(s)
            print(f"{tier:5s} {name:11s} "
                  f"{s['n_arm_min']:4d}-{s['n_arm_max']:<4d} "
                  f"{s['effect_mean']:+.4f} +- {s['effect_sd']:.4f} "
                  f"{s['effect_median']:+8.4f} {s['effect_min']:+8.4f} "
                  f"{s['effect_max']:+8.4f} {s['effect_range']:7.4f} "
                  f"{s['n_p05']:3d}/{s['seeds_usable']:<3d} "
                  f"{PUBLISHED[tier]:+9.4f} {s['published_percentile']:7.2f}")

    json.dump(out, open("data/processed/geipan/geipan_tier_seed_stability.json",
                        "w"), indent=1)
    print("\nwrote data/processed/geipan/geipan_tier_seed_stability.json")


if __name__ == "__main__":
    main()
