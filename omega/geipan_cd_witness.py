"""GEIPAN C-vs-D on WITNESS-level text instead of analyst prose.

HANDOFF section 1.4 / failure mode #7: the test on `Détails` is unidentifiable.
That field is GEIPAN analyst prose written AFTER classification, and the leak
changes form at every decontamination tier -- verdict sentence, verdict
lexicon, conjugated verb (`manquons` 163/1017 C vs 0/106 D), cause noun,
measurement density, narrative length -- without the gradient plateauing.  The
residual +0.1795 at L5 is reported as an upper bound, not as content.

This script runs the same comparison on gendarmerie procès-verbaux and enquête
reports harvested from the dossiers.  Those are written by police, before and
independent of GEIPAN's verdict, so the analyst-verdict channel is structurally
absent rather than merely stripped.

PRE-REGISTERED PREDICTION (recorded before the first run):
  raw balanced accuracy 0.60-0.72, falling to 0.55-0.62 under length and
  numeral controls, NOT reaching null.  Reason: the C/D criterion is
  definitionally about information adequacy -- C is "unidentified for lack of
  information", D is "unidentified despite adequate information" -- so a D
  procès-verbal should be thicker (more witnesses, durations, bearings,
  instrument readings) because thickness IS the criterion.  The confound moves
  from the analyst's verdict to the file's thickness.  Expected to be
  irreducible in the same way A+B-vs-D was.
  Genuine content result only if phenomenon descriptors (shape, motion, colour,
  sound) discriminate AFTER information-quantity control.  Predicted: they will
  not.
  POWER WARNING: ~50 D cases carry documents, against 106 D total.  Section 1.4
  reached MDD 0.107 at 106 D vs 1017 C.  At n~50 vs ~100 expect MDD 0.15-0.22.
  A true effect of +0.10 would be invisible.  If MDD lands there the result is
  UNDERPOWERED (failure mode #2), not null, and is reported as such.
"""
import os, re, sys, json, random, collections
sys.path.insert(0, "/home/user/UFOAI")
import numpy as np
from omega.geipan import toks
from omega.geipan_t3 import balanced_cv_acc

PV = "data/processed/geipan_pv"
MIN_TOK = 40            # a usable witness document
NPERM = 600

# --- the analyst-verdict channel, for the ABSENCE CHECK ---------------------
# If these appear in witness text at the rates they do in `Détails`, the
# premise of this script is wrong and the test is not identified either.
VERDICT_RX = re.compile(
    r"\bmanquon\w*|\bgeipan\b|\bclass[ée]\w*\b|"
    r"ph[ée]nom[èe]ne\s+[ée]trange|consistance\b", re.I)
LEAK_LEX = re.compile(
    r"manquon\w*|informat\w*|renseignement\w*|r[ée]cent\w*|"
    r"analys\w*|correspond\w*|[ée]voqu\w*|compatib\w*|revisit\w*|geipan", re.I)
NUMERAL = re.compile(
    r"\d+|\bm[èe]tres?\b|\bkilom[èe]tres?\b|\bsecondes?\b|\bminutes?\b|"
    r"\bheures?\b|\benviron\b|\bdegr[ée]s?\b|\bkm\b|\bdizaines?\b|"
    r"\bcentaines?\b|\bmilliers?\b", re.I)

# phenomenon descriptors only: shape, motion, colour, sound
DESCRIPTOR = re.compile(
    r"\b(rond\w*|circulaire\w*|sph[ée]r\w*|disque\w*|ovale\w*|triangul\w*|"
    r"cigare\w*|allong[ée]\w*|cylindr\w*|boule\w*|point\w*|lumi[èe]re\w*|"
    r"lumineu\w*|brillant\w*|clignot\w*|rouge\w*|orange\w*|jaune\w*|vert\w*|"
    r"bleu\w*|blanc\w*|blanch\w*|sombre\w*|noir\w*|argent\w*|m[ée]tall\w*|"
    r"immobile\w*|stationnaire\w*|d[ée]plac\w*|vol\w*|mont\w*|descend\w*|"
    r"rapide\w*|lent\w*|zigzag\w*|oscill\w*|tourn\w*|silencieu\w*|bruit\w*|"
    r"sifflement\w*|bourdonnement\w*|sourd\w*|trainee\w*|tra[îi]n[ée]e\w*)\b",
    re.I)


def norm(t):
    return re.sub(r"\s+", " ", t).strip()


def load_witness():
    """One record per case: all witness-class documents concatenated."""
    idx = json.load(open(f"{PV}/index.json", encoding="utf-8"))
    by = collections.defaultdict(lambda: {"txt": [], "arm": None, "year": None,
                                          "files": [], "methods": []})
    for r in idx:
        if not r["witness"]:
            continue
        p = os.path.join(PV, f"{r['cid']}__{r['file']}.txt")
        if not os.path.exists(p):
            continue
        t = open(p, encoding="utf-8", errors="replace").read()
        if len(toks(t)) < MIN_TOK:
            continue
        e = by[r["cid"]]
        e["txt"].append(t)
        e["arm"] = r["arm"]
        e["year"] = r["year"]
        e["files"].append(r["file"])
        e["methods"].append(r["method"])
    out = []
    for cid, e in by.items():
        out.append({"cid": cid, "arm": e["arm"], "year": e["year"],
                    "files": e["files"], "methods": e["methods"],
                    "raw": norm("\n".join(e["txt"]))})
    return out


def length_matched(data, tol=0.20, seed=5):
    rng = random.Random(seed)
    D = [(r, y) for r, y in data if y == "D"]
    N = [(r, y) for r, y in data if y == "C"]
    plen = [len(toks(x[0]["_txt"])) for x in N]
    used, out = set(), []
    for r, y in D:
        L = len(toks(r["_txt"]))
        c = [i for i, pl in enumerate(plen)
             if i not in used and abs(pl - L) <= max(10, tol * L)]
        if not c:
            continue
        j = rng.choice(c)
        used.add(j)
        out += [(r, y), N[j]]
    return out


def tier(recs, name, fn, matched=False):
    data = []
    for r in recs:
        t = fn(r["raw"])
        if len(toks(t)) >= 10:
            data.append((dict(r, _txt=t), r["arm"]))
    if matched:
        data = length_matched(data)
    arms = collections.Counter(y for _, y in data)
    if len(arms) < 2 or min(arms.values()) < 8:
        return {"tier": name, "status": "insufficient", "arms": dict(arms)}
    obs, m = balanced_cv_acc(data, ("D", "C"), seed=11)
    null = np.array([balanced_cv_acc(data, ("D", "C"), seed=3000 + i,
                                     label_shuffle=True)[0] for i in range(NPERM)])
    sd = float(null.std(ddof=1))
    p = float((np.sum(null >= obs - 1e-12) + 1) / (NPERM + 1))
    tD = [len(toks(r["_txt"])) for r, y in data if y == "D"]
    tC = [len(toks(r["_txt"])) for r, y in data if y == "C"]
    return {"tier": name, "status": "ok", "n_D": arms["D"], "n_C": arms["C"],
            "n_each_arm": m, "bal_acc": round(obs, 4),
            "effect": round(obs - 0.5, 4), "null_mean": round(float(null.mean()), 4),
            "null_sd": round(sd, 4), "p": round(p, 5),
            "mdd": round(1.645 * sd + 0.84 * sd, 4),
            "median_tok_D": float(np.median(tD)), "median_tok_C": float(np.median(tC))}


def main():
    recs = load_witness()
    arms = collections.Counter(r["arm"] for r in recs)
    print(f"cases with usable witness text: {len(recs)}  by arm: {dict(arms)}")
    meth = collections.Counter(m for r in recs for m in r["methods"])
    print(f"extraction methods: {dict(meth)}")
    if len(recs) < 20 or arms["D"] < 8 or arms["C"] < 8:
        print("\nINSUFFICIENT WITNESS CORPUS -- reporting as such, not as null.")
        json.dump({"status": "insufficient_corpus", "n": len(recs),
                   "arms": dict(arms)},
                  open("data/processed/geipan_pv/cd_witness_result.json", "w"),
                  indent=1)
        return

    # --- premise check: is the analyst-verdict channel actually absent? -----
    print("\n=== PREMISE CHECK: analyst-verdict channel in witness text ===")
    vD = sum(1 for r in recs if r["arm"] == "D" and VERDICT_RX.search(r["raw"]))
    vC = sum(1 for r in recs if r["arm"] == "C" and VERDICT_RX.search(r["raw"]))
    print(f"  docs containing verdict phrasing:  D {vD}/{arms['D']}   C {vC}/{arms['C']}")
    for w in ("manquons", "geipan", "classé", "étrange"):
        d = sum(1 for r in recs if r["arm"] == "D" and re.search(w, r["raw"], re.I))
        c = sum(1 for r in recs if r["arm"] == "C" and re.search(w, r["raw"], re.I))
        print(f"    {w:<12} D {d:>4}/{arms['D']:<5} C {c:>4}/{arms['C']}")
    print("  (in `Détails`, `manquons` was 163/1017 C vs 0/106 D -- "
          "if that asymmetry reappears here the premise fails)")

    TIERS = [
        ("W0 raw witness text",        lambda t: t,                          False),
        ("W1 verdict phrasing out",    lambda t: norm(VERDICT_RX.sub(" ", t)), False),
        ("W2 + leak lexicon out",      lambda t: norm(LEAK_LEX.sub(" ", VERDICT_RX.sub(" ", t))), False),
        ("W3 + length matched",        lambda t: norm(LEAK_LEX.sub(" ", VERDICT_RX.sub(" ", t))), True),
        ("W4 + numerals out",          lambda t: norm(NUMERAL.sub(" ", LEAK_LEX.sub(" ", VERDICT_RX.sub(" ", t)))), True),
        ("W5 descriptors only",        lambda t: norm(" ".join(DESCRIPTOR.findall(t))), True),
    ]
    out = []
    print(f"\n=== TIERS (permutation null, {NPERM} draws) ===")
    print(f"  {'tier':<26}{'n_arm':>7}{'bal.acc':>9}{'effect':>9}{'p':>9}{'MDD':>8}"
          f"{'medD':>7}{'medC':>7}")
    for name, fn, m in TIERS:
        r = tier(recs, name, fn, m)
        out.append(r)
        if r["status"] != "ok":
            print(f"  {name:<26}  INSUFFICIENT {r['arms']}")
            continue
        print(f"  {name:<26}{r['n_each_arm']:>7}{r['bal_acc']:>9.4f}"
              f"{r['effect']:>+9.4f}{r['p']:>9.4f}{r['mdd']:>8.4f}"
              f"{r['median_tok_D']:>7.0f}{r['median_tok_C']:>7.0f}")

    ok = [r for r in out if r["status"] == "ok"]
    if ok:
        print("\n=== VERDICT ===")
        last = ok[-1]
        if last["effect"] <= last["mdd"]:
            print(f"  Final tier effect {last['effect']:+.4f} <= MDD {last['mdd']:.4f}")
            print("  -> NOT DISTINGUISHABLE FROM NULL AT THIS POWER.")
            print("     This is UNDERPOWERED, not a demonstrated null, unless MDD")
            print("     is below the effect size of interest.")
        else:
            print(f"  Final tier effect {last['effect']:+.4f} > MDD {last['mdd']:.4f}, "
                  f"p={last['p']:.4f}")
            eff = [r["effect"] for r in ok]
            print(f"  gradient across tiers: "
                  f"{' -> '.join(f'{e:+.3f}' for e in eff)}")
            if len(eff) >= 3 and abs(eff[-1] - eff[-2]) > 0.02:
                print("  Gradient has NOT plateaued -> residual is an UPPER BOUND,")
                print("  not content. Same disposition as section 1.4.")
            else:
                print("  Gradient appears to have plateaued -> residual is a")
                print("  candidate content effect; needs an independent replication arm.")

    json.dump({"n_cases": len(recs), "arms": dict(arms), "tiers": out},
              open("data/processed/geipan_pv/cd_witness_result.json", "w"),
              indent=1, ensure_ascii=False)
    print("\nwrote data/processed/geipan_pv/cd_witness_result.json")


if __name__ == "__main__":
    main()
