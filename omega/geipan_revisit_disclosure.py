"""Which GEIPAN D cases are undisclosed, and what predicts it.

HANDOFF section 1.3 established that D is the least documented arm:
document-attachment share D 0.4528 vs A+B 0.9794, z=-25.83, surviving
within-era stratification.  That is a MARGINAL result about the class.

This localises it.  The export carries a `Cas revisité` ("case revisited")
flag, and section 1 of the BAASS cross-check showed D is the class under active
re-examination (59.4% vs a flat ~5.0% for A, B and C; z=+22.065).  Crossing the
two fields asks a sharper question: among D cases specifically, does
re-examination predict non-disclosure?

Output is the named case list for a CADA request (France's FOIA analogue).
"""
import json, math, collections

cases = json.load(open("data/raw/geipan/geipan_cases.json", encoding="utf-8-sig"))


def has_doc(r):
    d = str(r.get("Document pour cas") or "").strip()
    return bool(d) and d != "/" and "." in d


def cls(r):
    return (r.get("Classification") or "").strip().upper()


def rev(r):
    return (r.get("Cas revisité") or "").strip() == "Oui"


def year(r):
    s = str(r.get("Année") or "")[:4]
    return int(s) if s.isdigit() else None


def ztest(a_hit, a_n, b_hit, b_n):
    if not a_n or not b_n:
        return float("nan")
    p1, p2 = a_hit / a_n, b_hit / b_n
    pp = (a_hit + b_hit) / (a_n + b_n)
    se = math.sqrt(pp * (1 - pp) * (1 / a_n + 1 / b_n))
    return (p1 - p2) / se if se else float("nan")


D = [r for r in cases if cls(r) == "D"]
print(f"D cases: {len(D)}\n")

print("=" * 70)
print("1. DISCLOSURE x RE-EXAMINATION, WITHIN CLASS D")
print("=" * 70)
cell = collections.Counter((has_doc(r), rev(r)) for r in D)
print(f"  {'':<18}{'revisited':>12}{'not revisited':>16}{'total':>8}")
for hd, lbl in ((True, "documents"), (False, "NO documents")):
    a, b = cell[(hd, True)], cell[(hd, False)]
    print(f"  {lbl:<18}{a:>12}{b:>16}{a+b:>8}")
nod_n = cell[(False, True)] + cell[(False, False)]
doc_n = cell[(True, True)] + cell[(True, False)]
r_nod = cell[(False, True)] / nod_n if nod_n else 0
r_doc = cell[(True, True)] / doc_n if doc_n else 0
z = ztest(cell[(False, True)], nod_n, cell[(True, True)], doc_n)
print()
print(f"  revisit-rate, undisclosed D : {r_nod:.4f}  ({cell[(False,True)]}/{nod_n})")
print(f"  revisit-rate, disclosed D   : {r_doc:.4f}  ({cell[(True,True)]}/{doc_n})")
print(f"  z = {z:+.3f}")
if r_doc > 0:
    print(f"  risk ratio = {r_nod/r_doc:.2f}x")

print()
print("=" * 70)
print("2. IS IT JUST ERA?  (D cases skew older; older files may be less digitised)")
print("=" * 70)
print(f"  {'decade':<10}{'n':>5}{'undisclosed':>13}{'rev|undisc':>12}{'rev|disc':>10}")
for d in sorted({(year(r) // 10) * 10 for r in D if year(r)}):
    sub = [r for r in D if year(r) and (year(r) // 10) * 10 == d]
    nod = [r for r in sub if not has_doc(r)]
    doc = [r for r in sub if has_doc(r)]
    rn = sum(1 for r in nod if rev(r)) / len(nod) if nod else float("nan")
    rd = sum(1 for r in doc if rev(r)) / len(doc) if doc else float("nan")
    print(f"  {d}s{'':<5}{len(sub):>5}{len(nod):>13}{rn:>12.3f}{rd:>10.3f}")

# Mantel-Haenszel-style check: pool the within-decade 2x2s.
num = den = 0.0
for d in sorted({(year(r) // 10) * 10 for r in D if year(r)}):
    sub = [r for r in D if year(r) and (year(r) // 10) * 10 == d]
    a = sum(1 for r in sub if not has_doc(r) and rev(r))
    b = sum(1 for r in sub if not has_doc(r) and not rev(r))
    c = sum(1 for r in sub if has_doc(r) and rev(r))
    e = sum(1 for r in sub if has_doc(r) and not rev(r))
    n = a + b + c + e
    if n and (a + b) and (c + e):
        num += (a * e) / n
        den += (b * c) / n
print()
print(f"  Mantel-Haenszel odds ratio, stratified by decade: "
      f"{(num/den if den else float('inf')):.2f}")
print("  (if the marginal association were an era artefact this would collapse"
      " toward 1.0)")

print()
print("=" * 70)
print("3. CADA REQUEST TARGET LIST")
print("=" * 70)
targets = sorted((r for r in D if not has_doc(r)),
                 key=lambda r: str(r.get("ID Etude de Cas")))
print(f"  {len(targets)} D cases with no published document")
print(f"  of which revisited: {sum(1 for r in targets if rev(r))}")
json.dump([{"id": r["ID Etude de Cas"], "title": r.get("Titre du Cas"),
            "date": r.get("Observation date"), "year": year(r),
            "department": r.get("Department"), "region": r.get("Region"),
            "revisited": rev(r), "phenomenon": r.get("Phenomenon"),
            "lat": r.get("Latitude"), "lon": r.get("Longitude")}
           for r in targets],
          open("data/processed/geipan/cada_targets.json", "w"),
          indent=1, ensure_ascii=False)
print("  wrote data/processed/geipan/cada_targets.json")
