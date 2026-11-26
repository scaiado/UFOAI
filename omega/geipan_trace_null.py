#!/usr/bin/env python3
"""Database-level null model for the physical-trace evidence class in GEIPAN.

Question: in the GEIPAN case export, are cases whose official narrative
reports a ground trace more often classified D (unidentified despite adequate
information) than cases that do not, once the era trend in D-rates (HANDOFF
section 1.3: D-rate fell 3.78x) is controlled?

Three narrative classes, because "aucune trace au sol" is the commonest hit
(habit 2 in HANDOVER_PROMPT: a keyword hit without context is noise):
  POSITIVE  - a trace is reported as found
  NEGATED   - the narrative says no trace was found
  NONE      - traces not mentioned
POSITIVE hits are all printed so they can be read, not just counted.

Caveat carried into the report: a physical trace is part of what makes
information "adequate", so trace -> D is partly definitional (failure mode #7,
HANDOFF section 1.4). The test bounds the association; it cannot show the
trace caused the D.

Run: python3 -I omega/geipan_trace_null.py > omega/reports/geipan_trace_null_out.txt
"""
import json
import re
import collections
import numpy as np
from scipy import stats

CASES = "data/raw/geipan/geipan_cases.json"
TRACE = re.compile(
    r"(traces?|empreintes?|marques?)\s+(\w+\s+){0,4}?"
    r"(au sol|sur le sol|dans (l'|le |la )?(herbe|champ|sol|terre)|de brûl|circulaire)",
    re.I)
NEG = re.compile(r"(aucune?|pas de|ni |sans |n'a révélé|ne révèle|ne sera|n'est|n'ont|n'a été|absence)", re.I)
# Narratives that mention a trace only to say it is unrelated / prosaic are still POSITIVE
# for "a trace was reported"; we keep them and flag them on read-through.

# Manual adjudication after reading every POSITIVE and every NEGATED hit (2026-11-26).
OVERRIDE = {
    # "trace au sol" = ground track of a satellite / aircraft, not a physical trace
    "2002-12-01601": ("NONE", "ISS ground track"),
    "2011-06-02771": ("NONE", "ISS ground track"),
    "2015-08-09278": ("NONE", "aircraft ground track"),
    "2025-10-51703": ("NONE", "re-entry ground track"),
    "2025-10-51737": ("NONE", "re-entry ground track"),
    # generic methodological sentence, no trace in the case
    "1998-06-01503": ("NONE", "generic: 'il aurait fallu ... trace au sol'"),
    "2001-09-01573": ("NONE", "generic: 'les traces au sol sont ... precieuses'"),
    # negation regex fired on an unrelated clause; a trace WAS found
    "2016-03-09454": ("POSITIVE", "'le temoin a trouve le lendemain une trace ronde dans le sol'"),
    "1979-06-00635": ("POSITIVE", "hot ashes found; 'aucune AUTRE trace'"),
}


def classify(text):
    pos = neg = False
    for m in TRACE.finditer(text or ""):
        window = text[max(0, m.start() - 45):m.end() + 25]
        if NEG.search(window):
            neg = True
        else:
            pos = True
    return "POSITIVE" if pos else ("NEGATED" if neg else "NONE")


def era(y):
    return "1937-1988" if y <= 1988 else ("1989-2006" if y <= 2006 else "2007+")


def main():
    d = json.load(open(CASES, encoding="utf-8"))
    rows = []
    for c in d:
        cls = classify(c.get("Détails", ""))
        if c["ID Etude de Cas"] in OVERRIDE:
            cls = OVERRIDE[c["ID Etude de Cas"]][0]
        rows.append(dict(id=c["ID Etude de Cas"], k=c["Classification"], y=int(c["Année"]),
                         t=cls, title=c["Titre du Cas"], txt=c.get("Détails", "")))
    print(f"cases: {len(rows)}")
    tab = collections.Counter((r["t"], r["k"]) for r in rows)
    for t in ("POSITIVE", "NEGATED", "NONE"):
        n = sum(tab[(t, k)] for k in "ABCD")
        print(f"  {t:9s} n={n:5d}  " + "  ".join(f"{k}={tab[(t,k)]}" for k in "ABCD")
              + f"   D-rate={tab[(t,'D')]/n:.4f}" if n else "")

    print("\nPOSITIVE narratives (read every one):")
    for r in sorted((r for r in rows if r["t"] == "POSITIVE"), key=lambda r: r["id"]):
        m = next(iter(TRACE.finditer(r["txt"])))
        s = max(0, m.start() - 90)
        print(f"  {r['id']} {r['k']} | {r['title'][:38]:38s} | ...{r['txt'][s:m.end()+70].replace(chr(10),' ')}...")

    # ---- 2x2 positive vs everything else, D vs not-D, overall and by era
    def two_by_two(sub):
        a = sum(1 for r in sub if r["t"] == "POSITIVE" and r["k"] == "D")
        b = sum(1 for r in sub if r["t"] == "POSITIVE" and r["k"] != "D")
        c = sum(1 for r in sub if r["t"] != "POSITIVE" and r["k"] == "D")
        e = sum(1 for r in sub if r["t"] != "POSITIVE" and r["k"] != "D")
        return np.array([[a, b], [c, e]])

    print("\nTrace-POSITIVE vs rest, D vs not-D")
    t = two_by_two(rows)
    orr, p = stats.fisher_exact(t)
    print(f"  overall table {t.tolist()}  OR={orr:.2f}  Fisher P={p:.3g}")
    pr = t[0, 0] / t[0].sum()
    ci = stats.binomtest(int(t[0, 0]), int(t[0].sum())).proportion_ci(method="exact")
    print(f"  D-rate among trace-positive: {pr:.3f} [exact 95% {ci.low:.3f},{ci.high:.3f}]  vs rest {t[1,0]/t[1].sum():.4f}")

    tables = []
    for e in ("1937-1988", "1989-2006", "2007+"):
        sub = [r for r in rows if era(r["y"]) == e]
        te = two_by_two(sub)
        tables.append(te)
        o, pe = stats.fisher_exact(te) if te[0].sum() and te[1].sum() else (float("nan"), float("nan"))
        print(f"  {e:10s} {te.tolist()}  OR={o:.2f}  P={pe:.3g}")
    # Mantel-Haenszel pooled OR and CMH test
    num = sum(tb[0, 0] * tb[1, 1] / tb.sum() for tb in tables if tb.sum())
    den = sum(tb[0, 1] * tb[1, 0] / tb.sum() for tb in tables if tb.sum())
    or_mh = num / den if den else float("inf")
    # CMH chi-square (no continuity correction)
    A = sum(tb[0, 0] for tb in tables)
    EA = sum(tb[0].sum() * tb[:, 0].sum() / tb.sum() for tb in tables)
    VA = sum(tb[0].sum() * tb[1].sum() * tb[:, 0].sum() * tb[:, 1].sum() / (tb.sum() ** 2 * (tb.sum() - 1)) for tb in tables)
    chi = (A - EA) ** 2 / VA
    print(f"  Mantel-Haenszel OR={or_mh:.2f}  CMH chi2={chi:.2f}  P={stats.chi2.sf(chi,1):.3g}  (observed D {A}, expected {EA:.2f})")

    # ---- permutation null within era: shuffle the D labels within era
    rng = np.random.default_rng(1981)
    pos_idx = np.array([r["t"] == "POSITIVE" for r in rows])
    isD = np.array([r["k"] == "D" for r in rows])
    eras = np.array([era(r["y"]) for r in rows])
    obs = int((pos_idx & isD).sum())
    null = np.empty(20000, int)
    for i in range(null.size):
        lab = isD.copy()
        for e in np.unique(eras):
            m = eras == e
            lab[m] = rng.permutation(lab[m])
        null[i] = (pos_idx & lab).sum()
    print(f"  within-era label permutation (20k): observed D among trace-positive={obs}, "
          f"null mean={null.mean():.2f}, P(null>=obs)={(null >= obs).mean():.4f}")

    # ---- found vs searched-and-not-found, and searched vs not mentioned
    print("\nDoes it matter whether a trace was FOUND, or only whether someone LOOKED?")
    for lab, g1, g2 in (("POSITIVE vs NEGATED", {"POSITIVE"}, {"NEGATED"}),
                        ("SEARCHED (POS+NEG) vs NONE", {"POSITIVE", "NEGATED"}, {"NONE"})):
        tabs = []
        for e in ("1937-1988", "1989-2006", "2007+"):
            sub = [r for r in rows if era(r["y"]) == e]
            a = sum(1 for r in sub if r["t"] in g1 and r["k"] == "D"); b = sum(1 for r in sub if r["t"] in g1 and r["k"] != "D")
            c = sum(1 for r in sub if r["t"] in g2 and r["k"] == "D"); f = sum(1 for r in sub if r["t"] in g2 and r["k"] != "D")
            tabs.append(np.array([[a, b], [c, f]]))
        tot = sum(tabs)
        o, pf = stats.fisher_exact(tot)
        num = sum(tb[0, 0] * tb[1, 1] / tb.sum() for tb in tabs if tb.sum())
        den = sum(tb[0, 1] * tb[1, 0] / tb.sum() for tb in tabs if tb.sum())
        A = sum(tb[0, 0] for tb in tabs)
        EA = sum(tb[0].sum() * tb[:, 0].sum() / tb.sum() for tb in tabs if tb.sum() > 1)
        VA = sum(tb[0].sum() * tb[1].sum() * tb[:, 0].sum() * tb[:, 1].sum() / (tb.sum() ** 2 * (tb.sum() - 1)) for tb in tabs if tb.sum() > 1)
        chi = (A - EA) ** 2 / VA
        print(f"  {lab:28s} pooled {tot.tolist()}  crude OR={o:.2f} (Fisher P={pf:.3g})  "
              f"MH OR={num/den:.2f}  CMH P={stats.chi2.sf(chi,1):.3g}")
        for e, tb in zip(("1937-1988", "1989-2006", "2007+"), tabs):
            r1 = tb[0, 0] / tb[0].sum() if tb[0].sum() else float("nan")
            r2 = tb[1, 0] / tb[1].sum() if tb[1].sum() else float("nan")
            print(f"      {e:10s} D-rate {r1:.3f} (n={tb[0].sum()}) vs {r2:.4f} (n={tb[1].sum()})")

    # ---- where Trans-en-Provence sits
    tep = next(r for r in rows if r["id"] == "1981-01-00849")
    print("\nNB: recall of the narrative regex is not measured. Cases describing a trace in other")
    print("words (brulure, herbe couchee, cercle) are in NONE. The test is about the trace as GEIPAN's")
    print("own summary reports it, not about every trace case in the archive.")
    print(f"\nTrans-en-Provence classified as: {tep['t']} / {tep['k']}")


if __name__ == "__main__":
    main()
