"""GEIPAN C-vs-D on WITNESS-level text instead of analyst prose.

HANDOFF section 1.4 / failure mode #7: the test on `Détails` is unidentifiable.
That field is GEIPAN analyst prose written AFTER classification, and the leak
changes form at every decontamination tier -- verdict sentence, verdict
lexicon, conjugated verb (`manquons` 163/1017 C vs 0/106 D), cause noun,
measurement density, narrative length -- without the gradient plateauing.  The
residual +0.1972 (seed-averaged; was +0.1795 as a single draw) at L5 is reported as an upper bound, not as content.

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

THIRD PREMISE RISK -- AND IT INVALIDATED THE ORIGINAL DOCUMENT SELECTION
  The harvest classifies dossier files as pv / enquete / questionnaire and the
  first version of this script treated all three as "witness-level".  MEASURED
  ON THE OCR'd CORPUS, that was wrong:

    class           n   GEIPAN/CNES header   gendarmerie   verdict language
    enquete        37           34 (92%)        18 (49%)        34 (92%)
    pv             38            9 (24%)        35 (92%)        23 (61%)
    questionnaire  25           24 (96%)         2 (8%)        24 (96%)

  A "Compte rendu d'enquête" is GEIPAN's OWN investigation report, on CNES
  letterhead, written after the investigation -- e.g. one in this corpus is
  dated 07/06/2024 for a 2018 observation.  "Questionnaire technique" is
  likewise a GEIPAN instrument.  Both are analyst documents, i.e. precisely the
  contaminated source this test exists to avoid.  Only the gendarmerie
  procès-verbal is authored outside GEIPAN and before its verdict.

  So the witness corpus is PV-ONLY, which costs most of the sample:
  106 D cases -> 50 with any published document (and section 1.10 shows the 56
  without are the re-examined ones) -> 46 with usable witness text -> 28 WITH A
  GENDARMERIE PV.  Against 51 C.  Balanced arm 28, approximate MDD 0.235, where
  section 1.4 achieved 0.107.  THE DETECTION FLOOR IS THEREFORE ABOVE SECTION
  1.4's FULLY-DECONTAMINATED RESIDUAL OF +0.1972 +- 0.0271 (seed-averaged):
  even if witness text carried
  that same signal, this test could not see it.

  Rather than report one underpowered null, the script now runs the SAME tiers
  on all three corpora and compares.  The contaminated arms have more cases and
  should separate well BECAUSE they contain the verdict; the clean arm should
  not.  That demonstrates where the signal lives instead of merely asserting
  it, and it makes the PV result interpretable as a contrast rather than as an
  isolated null.

SECOND PREMISE RISK, MEASURED AND GUARDED (2026-11-26)
  GEIPAN's dossier PDFs are mixed: 1951-1954 procès-verbaux carry NO embedded
  text layer, while a 1993 PV carries 12,548 characters of poor-quality
  embedded text ("CROQUIS DE L'ÉTAT DES LIEUX" -> "C R O Q U I S  D E
  L 'E'I'A'i'").  Text-layer availability therefore correlates with ERA, and D
  cases skew older.  A "pdftotext first, OCR if short" rule would run two text
  pipelines split along a line correlated with the label -- structurally the
  cross-pipeline defect that falsified the persistence result.  So every
  document is re-OCR'd through one pipeline (geipan_pv_extract.py), and OCR
  QUALITY IS CHECKED BETWEEN ARMS here before any effect is interpreted.  Tier
  W6 additionally matches the arms on quality.
  POWER WARNING: ~50 D cases carry documents, against 106 D total.  Section 1.4
  reached MDD 0.107 at 106 D vs 1017 C.  At n~50 vs ~100 expect MDD 0.15-0.22.
  A true effect of +0.10 would be invisible.  If MDD lands there the result is
  UNDERPOWERED (failure mode #2), not null, and is reported as such.
"""
import os, re, sys, json, math, random, collections
sys.path.insert(0, "/home/user/UFOAI")
import numpy as np
from omega.geipan import toks
from omega.geipan_t3 import balanced_cv_acc

PV = "data/processed/geipan_pv"
MIN_TOK = 40            # a usable witness document
NPERM = 600

# Document classes, by provenance (measured -- see the docstring).
CORPORA = {
    "pv":            {"pv"},             # gendarmerie, pre-verdict: THE witness corpus
    "enquete":       {"enquete"},        # GEIPAN analyst report: contaminated control
    "questionnaire": {"questionnaire"},  # GEIPAN instrument: contaminated control
}
CLEAN = "pv"

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


def load_witness(keep):
    """One record per case: documents of the given classes, concatenated."""
    idx = json.load(open(f"{PV}/index.json", encoding="utf-8"))
    by = collections.defaultdict(lambda: {"txt": [], "arm": None, "year": None,
                                          "files": [], "methods": [], "q": []})
    for r in idx:
        if r.get("cls") not in keep:
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
        e["q"].append((r.get("q") or {}).get("score", 0.0))
    out = []
    for cid, e in by.items():
        out.append({"cid": cid, "arm": e["arm"], "year": e["year"],
                    "files": e["files"], "methods": e["methods"],
                    "qual": (sum(e["q"]) / len(e["q"])) if e["q"] else 0.0,
                    "raw": norm("\n".join(e["txt"]))})
    return out


def _matched(data, keyfn, tol, floor, seed=5):
    """Greedy 1:1 nearest matching of D cases to C cases on keyfn."""
    rng = random.Random(seed)
    D = [(r, y) for r, y in data if y == "D"]
    N = [(r, y) for r, y in data if y == "C"]
    pk = [keyfn(x[0]) for x in N]
    used, out = set(), []
    for r, y in D:
        L = keyfn(r)
        c = [i for i, v in enumerate(pk)
             if i not in used and abs(v - L) <= max(floor, tol * abs(L))]
        if not c:
            continue
        j = rng.choice(c)
        used.add(j)
        out += [(r, y), N[j]]
    return out


def length_matched(data, tol=0.20, seed=5):
    return _matched(data, lambda r: len(toks(r["_txt"])), tol, 10, seed)


def quality_matched(data, tol=0.25, seed=7):
    """Match on OCR quality AND then on length, so neither can carry it."""
    q = _matched(data, lambda r: r.get("qual", 0.0), tol, 0.03, seed)
    return _matched(q, lambda r: len(toks(r["_txt"])), 0.25, 12, seed + 1)


def tier(recs, name, fn, matched=False):
    """matched: False | "length" | "quality" """
    data = []
    for r in recs:
        t = fn(r["raw"])
        if len(toks(t)) >= 10:
            data.append((dict(r, _txt=t), r["arm"]))
    if matched == "length":
        data = length_matched(data)
    elif matched == "quality":
        data = quality_matched(data)
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
    qD = [r.get("qual", 0.0) for r, y in data if y == "D"]
    qC = [r.get("qual", 0.0) for r, y in data if y == "C"]
    # Three-way disposition. MDD = 1.645*sd + 0.84*sd = 2.485*sd is the effect
    # detectable with 80% POWER at one-sided alpha=0.05; the SIGNIFICANCE
    # threshold is only ~1.645*sd. So an effect can beat the permutation null
    # (p < 0.05) and still sit below the MDD: detected here, but a replication
    # would have under 80% chance of detecting it again. Conflating "below MDD"
    # with "not distinguishable from null" is wrong, and an earlier version of
    # this script did exactly that.
    sig = p < 0.05
    above = (obs - 0.5) > (1.645 * sd + 0.84 * sd)
    disp = ("detected at adequate power" if (sig and above)
            else "SIGNIFICANT BUT UNDERPOWERED for this size" if sig
            else "not distinguishable from null")
    return {"tier": name, "status": "ok", "n_D": arms["D"], "n_C": arms["C"],
            "significant": bool(sig), "above_mdd": bool(above),
            "disposition": disp,
            "median_qual_D": round(float(np.median(qD)), 4) if qD else None,
            "median_qual_C": round(float(np.median(qC)), 4) if qC else None,
            "n_each_arm": m, "bal_acc": round(obs, 4),
            "effect": round(obs - 0.5, 4), "null_mean": round(float(null.mean()), 4),
            "null_sd": round(sd, 4), "p": round(p, 5),
            "mdd": round(1.645 * sd + 0.84 * sd, 4),
            "median_tok_D": float(np.median(tD)), "median_tok_C": float(np.median(tC))}


TIERS = [
    ("W0 raw text",               lambda t: t,                          False),
    ("W1 verdict phrasing out",   lambda t: norm(VERDICT_RX.sub(" ", t)), False),
    ("W2 + leak lexicon out",     lambda t: norm(LEAK_LEX.sub(" ", VERDICT_RX.sub(" ", t))), False),
    ("W3 + length matched",       lambda t: norm(LEAK_LEX.sub(" ", VERDICT_RX.sub(" ", t))), "length"),
    ("W4 + numerals out",         lambda t: norm(NUMERAL.sub(" ", LEAK_LEX.sub(" ", VERDICT_RX.sub(" ", t)))), "length"),
    ("W5 descriptors only",       lambda t: norm(" ".join(DESCRIPTOR.findall(t))), "length"),
    ("W6 quality+length matched", lambda t: norm(NUMERAL.sub(" ", LEAK_LEX.sub(" ", VERDICT_RX.sub(" ", t)))), "quality"),
]


def provenance(recs, arms, label):
    """Premise checks. Printed BEFORE any tier, for every corpus."""
    print(f"\n  --- premise 1: analyst-verdict channel present? ---")
    for w in ("geipan", "cnes", "manquons", "class", "gendarmerie", "brigade"):
        d = sum(1 for r in recs if r["arm"] == "D" and re.search(w, r["raw"], re.I))
        c = sum(1 for r in recs if r["arm"] == "C" and re.search(w, r["raw"], re.I))
        print(f"    {w:<12} D {d:>3}/{arms['D']:<4} ({d/max(1,arms['D']):>5.0%})"
              f"   C {c:>3}/{arms['C']:<4} ({c/max(1,arms['C']):>5.0%})")
    print(f"  --- premise 2: does OCR quality or length track the label? ---")
    qD = np.array([r["qual"] for r in recs if r["arm"] == "D"])
    qC = np.array([r["qual"] for r in recs if r["arm"] == "C"])
    tD = np.array([len(toks(r["raw"])) for r in recs if r["arm"] == "D"])
    tC = np.array([len(toks(r["raw"])) for r in recs if r["arm"] == "C"])
    for lbl, a, b in (("quality", qD, qC), ("tokens", tD, tC)):
        if len(a) > 1 and len(b) > 1:
            sp = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
            z = (a.mean() - b.mean()) / sp if sp else float("nan")
            print(f"    {lbl:<10} D med={np.median(a):>8.2f}  C med={np.median(b):>8.2f}"
                  f"   z={z:+.3f}")


def run_corpus(name, keep):
    recs = load_witness(keep)
    arms = collections.Counter(r["arm"] for r in recs)
    print(f"\n{'='*74}")
    print(f"CORPUS '{name}'  ({'CLEAN -- gendarmerie, pre-verdict' if name == CLEAN else 'CONTAMINATED CONTROL -- GEIPAN-authored'})")
    print(f"{'='*74}")
    print(f"  cases: {len(recs)}  by arm: {dict(arms)}")
    if len(recs) < 16 or arms["D"] < 8 or arms["C"] < 8:
        print("  INSUFFICIENT -- reported as such, not as null.")
        return {"corpus": name, "status": "insufficient", "arms": dict(arms)}
    provenance(recs, arms, name)
    out = []
    print(f"\n  --- tiers (permutation null, {NPERM} draws) ---")
    print(f"  {'tier':<28}{'n/arm':>6}{'bal.acc':>9}{'effect':>9}{'p':>8}{'MDD':>8}"
          f"{'medD':>7}{'medC':>7}")
    for tname, fn, m in TIERS:
        r = tier(recs, tname, fn, m)
        out.append(r)
        if r["status"] != "ok":
            print(f"  {tname:<28}  INSUFFICIENT {r.get('arms')}")
            continue
        flag = {"detected at adequate power": "",
                "SIGNIFICANT BUT UNDERPOWERED for this size": "  <-- sig, under-powered",
                "not distinguishable from null": "  <-- null"}[r["disposition"]]
        print(f"  {tname:<28}{r['n_each_arm']:>6}{r['bal_acc']:>9.4f}"
              f"{r['effect']:>+9.4f}{r['p']:>8.4f}{r['mdd']:>8.4f}"
              f"{r['median_tok_D']:>7.0f}{r['median_tok_C']:>7.0f}{flag}")
    return {"corpus": name, "status": "ok", "arms": dict(arms),
            "n_cases": len(recs), "tiers": out}


def main():
    results = [run_corpus(n, k) for n, k in CORPORA.items()]

    print(f"\n{'='*74}")
    print("CONTRAST -- where does the signal live?")
    print(f"{'='*74}")
    print(f"  {'corpus':<16}{'n_D':>5}{'n_C':>5}{'W0 raw':>10}{'W6 cleaned':>12}{'W6 MDD':>9}  disposition")
    for r in results:
        if r["status"] != "ok":
            print(f"  {r['corpus']:<16}{r['arms'].get('D',0):>5}{r['arms'].get('C',0):>5}"
                  f"{'--':>10}{'--':>12}{'--':>9}  insufficient corpus")
            continue
        ok = [t for t in r["tiers"] if t["status"] == "ok"]
        w0 = next((t for t in ok if t["tier"].startswith("W0")), None)
        w6 = next((t for t in ok if t["tier"].startswith("W6")), None)
        if not (w0 and w6):
            continue
        disp = ("effect survives cleaning" if w6["effect"] > w6["mdd"]
                else "below detection floor -- UNDERPOWERED, not null")
        print(f"  {r['corpus']:<16}{r['arms']['D']:>5}{r['arms']['C']:>5}"
              f"{w0['effect']:>+10.4f}{w6['effect']:>+12.4f}{w6['mdd']:>9.4f}  {disp}")

    print()
    clean = next((r for r in results if r["corpus"] == CLEAN), None)
    dirty = [r for r in results if r["corpus"] != CLEAN and r["status"] == "ok"]
    if clean and clean["status"] == "ok":
        ok = [t for t in clean["tiers"] if t["status"] == "ok"]
        w6 = next((t for t in ok if t["tier"].startswith("W6")), None)
        if w6:
            if not w6["significant"]:
                print(f"  The CLEAN (gendarmerie PV) corpus gives effect "
                      f"{w6['effect']:+.4f}, p={w6['p']:.4f}, MDD {w6['mdd']:.4f}.")
                print("  => NOT DISTINGUISHABLE FROM NULL.")
                print("     This is UNDERPOWERED, NOT a demonstrated null: the MDD")
                print(f"     ({w6['mdd']:.3f}) sits ABOVE section 1.4's fully-decontaminated")
                print("     residual of +0.1972 +- 0.0271 (seed-averaged), so the effect of interest is")
                print("     below this test's detection floor by construction.")
                print("     Cause is measured, not speculative: only 28 of 106 D cases")
                print("     have a published gendarmerie PV, and section 1.10 shows the")
                print("     56 D cases with no published dossier are the RE-EXAMINED ones.")
                print("     The test is power-limited by the non-disclosure the project")
                print("     has already measured. That is the finding.")
            elif not w6["above_mdd"]:
                print(f"  The CLEAN corpus effect {w6['effect']:+.4f} BEATS the"
                      f" permutation null (p={w6['p']:.4f}) but sits BELOW its"
                      f" MDD of {w6['mdd']:.4f}.")
                print("  => SIGNIFICANT BUT UNDERPOWERED. These are not the same")
                print("     thing: the effect is real at alpha=0.05 on this sample,")
                print("     but the design had under 80% power for an effect that")
                print("     size, so a replication could easily miss it. Report the")
                print("     effect WITH its power, never as a clean positive.")
            else:
                print(f"  The CLEAN corpus effect {w6['effect']:+.4f} exceeds its MDD "
                      f"{w6['mdd']:.4f} (p={w6['p']:.4f}).")
                print("     Treat as a candidate, not a result, until replicated on an")
                print("     independent arm: n is small and the tiers may not have"
                      " plateaued.")
    if dirty:
        print()
        print("  The CONTAMINATED controls are the interpretive anchor: if they")
        print("  separate well while the clean corpus does not, the signal in the")
        print("  earlier analyst-prose test was the verdict, as section 1.4 argued.")

    json.dump({"corpora": results},
              open("data/processed/geipan_pv/cd_witness_result.json", "w"),
              indent=1, ensure_ascii=False)
    print("\n  wrote data/processed/geipan_pv/cd_witness_result.json")


if __name__ == "__main__":
    main()
