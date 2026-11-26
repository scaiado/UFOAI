"""BAASS Ten Month Report (July 2009) vs the GEIPAN 2026 export.

DOW-UAP-D172 p283 para 50 states the then-current public GEIPAN disposition
breakdown outright:

    "D cases: 205 cases for 23 regions.  C cases: 323 cases for 23 regions."

and p219 confirms BAASS used GEIPAN's own definition of D ("the cases that
remain unexplained after thorough investigations").  The release BAASS was
reading is described on p219 as "approximately 100,000 pages documenting over
1,650 investigations of UFO cases from 1977 through 2007".

This is an independent, contemporaneous, third-party count of the same
population our 2026 export measures.  HANDOFF section 1.3 established that the
D-rate fell 3.78x; that is a RATE result and so is open to a denominator
objection.  An absolute decrease in the D COUNT cannot be produced by adding
cases to the archive -- only by moving specific cases out of D.  This script
tests for that.
"""
import json, collections, math

BAASS_D, BAASS_C = 205, 323
BAASS_LO, BAASS_HI = 1977, 2007
BAASS_INVESTIGATIONS = 1650

cases = json.load(open("data/raw/geipan/geipan_cases.json"))
K_CLS, K_YR, K_REV = "Classification", "Année", "Cas revisité"


def year(c):
    try:
        return int(str(c[K_YR])[:4])
    except (ValueError, TypeError):
        return None


print(f"GEIPAN 2026 export: {len(cases)} cases\n")

print("=" * 72)
print("1. FULL-ARCHIVE DISPOSITION (2026)")
print("=" * 72)
tot = collections.Counter(c[K_CLS] for c in cases)
for k in "ABCD":
    print(f"  {k}: {tot[k]:>5}   {tot[k]/len(cases):.4f}")
print(f"  total: {sum(tot.values())}")

win = [c for c in cases if (y := year(c)) is not None and BAASS_LO <= y <= BAASS_HI]
wc = collections.Counter(c[K_CLS] for c in win)

print()
print("=" * 72)
print(f"2. THE WINDOW BAASS READ ({BAASS_LO}-{BAASS_HI})")
print("=" * 72)
print(f"  cases in window, 2026 export : {len(win)}")
print(f"  BAASS 2009, 'over N investigations': {BAASS_INVESTIGATIONS}")
print(f"  ratio                         : {len(win)/BAASS_INVESTIGATIONS:.3f}x")
print()
for k in "ABCD":
    print(f"  {k}: {wc[k]:>5}   {wc[k]/len(win):.4f}")

print()
print("=" * 72)
print("3. THE TEST: BAASS 2009 COUNT vs 2026 COUNT, SAME WINDOW")
print("=" * 72)
print(f"  {'':<22}{'BAASS 2009':>12}{'2026 window':>14}{'2026 full':>12}{'change':>12}")
for k, b in (("C", BAASS_C), ("D", BAASS_D)):
    ch = wc[k] / b
    print(f"  {'class '+k:<22}{b:>12}{wc[k]:>14}{tot[k]:>12}{ch:>11.2f}x")

d_short = BAASS_D - wc["D"]
print()
print(f"  D shortfall in window : {BAASS_D} - {wc['D']} = {d_short}")
print(f"  C surplus in window   : {wc['C']} - {BAASS_C} = {wc['C'] - BAASS_C}")
print(f"  D shortfall vs FULL archive D: {BAASS_D} - {tot['D']} = {BAASS_D - tot['D']}")

print()
print("=" * 72)
print("4. WHERE THE SURVIVING D CASES ARE (decade)")
print("=" * 72)
dec = collections.Counter()
dec_all = collections.Counter()
for c in cases:
    y = year(c)
    if y is None:
        continue
    d = (y // 10) * 10
    dec_all[d] += 1
    if c[K_CLS] == "D":
        dec[d] += 1
for d in sorted(dec_all):
    inwin = "  <-- BAASS window" if BAASS_LO - 10 < d <= BAASS_HI else ""
    r = dec[d] / dec_all[d] if dec_all[d] else 0
    print(f"  {d}s: D={dec[d]:>4} / {dec_all[d]:>5}  D-rate={r:.4f}{inwin}")

print()
print("=" * 72)
print("5. 'CAS REVISITE' -- GEIPAN's own record of re-examination")
print("=" * 72)
rev = collections.Counter((c[K_CLS], c.get(K_REV)) for c in cases)
vals = sorted({v for _, v in rev})
print(f"  {'':<8}" + "".join(f"{str(v):>10}" for v in vals) + f"{'rev-rate':>12}")
for k in "ABCD":
    row = [rev[(k, v)] for v in vals]
    n = sum(row)
    oui = rev[(k, "Oui")]
    print(f"  {k:<8}" + "".join(f"{x:>10}" for x in row) + f"{(oui/n if n else 0):>12.4f}")

# Is revisit-flagging independent of surviving class?  2x2 on D vs A+B+C.
d_oui, d_tot = rev[("D", "Oui")], sum(rev[("D", v)] for v in vals)
o_oui = sum(rev[(k, "Oui")] for k in "ABC")
o_tot = sum(rev[(k, v)] for k in "ABC" for v in vals)
p1, p2 = d_oui / d_tot, o_oui / o_tot
pp = (d_oui + o_oui) / (d_tot + o_tot)
se = math.sqrt(pp * (1 - pp) * (1 / d_tot + 1 / o_tot))
z = (p1 - p2) / se if se else float("nan")
print()
print(f"  D revisit-rate   {p1:.4f}  (n={d_tot})")
print(f"  A+B+C revisit-rate {p2:.4f}  (n={o_tot})")
print(f"  z = {z:+.3f}")

print()
print("=" * 72)
print("6. BAASS TRANSLATION CLAIM (p283 para 51)")
print("=" * 72)
print("  'completed work on 68 GEIPAN category D cases (roughly 672 pages)'")
print(f"  implied pages/case: {672/68:.2f}   stated typical: ~9")
print("  'all the D-class reports in Regions 1 through 6, and some of Region 7'")
reg = collections.Counter(c["Region"] for c in cases if c[K_CLS] == "D")
print(f"  distinct regions holding a surviving D case, 2026: {len(reg)}")
for r, n in reg.most_common(10):
    print(f"    {n:>4}  {r}")
