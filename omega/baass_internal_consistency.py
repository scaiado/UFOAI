"""Internal arithmetic consistency of DOW-UAP-D172 (BAASS Ten Month Report).

Closed numeric sets stated in the document are re-added here.  This measures
the care taken in the deliverable, which is the prior to hold before trusting
any of its unverifiable content.
"""
CHECKS = []


def chk(name, parts, stated, note=""):
    got = sum(parts)
    CHECKS.append((name, got, stated, got == stated, note))


# --- MUFON CMS, p239: Vallee/Hynek classification x level -------------------
AN = [844, 97, 65, 34, 13]
FB = [3330, 83, 48, 55, 6]
MA = [1806, 73, 21, 32, 13]
CE = [1761, 139, 165, 157, 11]
classified = sum(AN + FB + MA + CE)
chk("MUFON CMS classified records", AN + FB + MA + CE, classified, "derived")

# p239 pie chart: "Close Encounter (CE) 25.5%", "Anomaly (AN) 12.1%"
print("=" * 74)
print("MUFON CMS (p238-239) -- stated total records: 17,281 (as of 30 Jun 2009)")
print("=" * 74)
print(f"  AN={sum(AN):>5} FB={sum(FB):>5} MA={sum(MA):>5} CE={sum(CE):>5}")
print(f"  classified subtotal        : {classified}")
print(f"  stated database total      : 17281")
print(f"  classified share of total  : {classified/17281:.4f}")
print()
print("  pie-chart percentages reproduce on WHICH denominator?")
for lbl, v, stated in (("CE", sum(CE), 25.5), ("AN", sum(AN), 12.1)):
    print(f"    {lbl}: on classified({classified}) = {100*v/classified:5.2f}%  "
          f"on total(17281) = {100*v/17281:5.2f}%   stated {stated}%")

# --- MUFON CMS outcome tallies, p238 ---------------------------------------
print()
print("  outcome tallies (same page, '~' approximate in source):")
out = {"Hoax": 831, "Identified natural": 446, "Identified man-made": 690,
       "Identified (other)": 867, "Insufficient data": 3040}
for k, v in out.items():
    print(f"    {k:<22}{v:>6}")
print(f"    {'sum':<22}{sum(out.values()):>6}   of 17281 = {sum(out.values())/17281:.4f}")
print(f"    {'Entity Events':<22}{3988:>6}   of 17281 = {3988/17281:.4f}")
print(f"    {'within 500ft of witness':<22}{4041:>6}")
print(f"    {'within 20ft of witness':<22}{845:>6}")
print(f"    CE total ({sum(CE)}) vs 'Entity Events' (3988): "
      f"{'CONSISTENT' if sum(CE) >= 3988 else 'INCONSISTENT -- entity > close-encounter'}")

# --- Canadian government release, p260 -------------------------------------
print()
print("=" * 74)
print("CANADIAN RELEASE (p260, as of 30 Jun 2009)")
print("=" * 74)
chk("CAPELLA + spreadsheet", [264, 353], 618, "stated 618 cases recorded")
chk("618 - 586 discrepancy", [32], 618 - 586, "stated 'discrepancy of 32 cases'")
print(f"  4127 pages reviewed; 618 cases recorded for additional review")
print(f"  264 in CAPELLA + 353 in spreadsheet = {264+353}  vs stated 618  "
      f"-> {'OK' if 264+353 == 618 else 'OFF BY ' + str(618-264-353)}")
print(f"  618 - 586 used for statistics = {618-586}  vs stated 32  -> "
      f"{'OK' if 618-586 == 32 else 'MISMATCH'}")
print(f"  stated '5%': {32/618:.4f} -> {'OK (rounds to 5%)' if abs(32/618-0.05) < 0.005 else 'MISMATCH'}")

# --- UK MoD, p296 ----------------------------------------------------------
print()
print("=" * 74)
print("UK MoD FILES (p296, Tables VII & VIII)")
print("=" * 74)
mod = [3, 71, 74, 48, 146, 1, 76, 13, 22, 9, 3, 87, 61]
tod = {"Dawn": 8, "Daylight": 112, "Dusk": 36, "Night": 407}
print(f"  Table VII  13 file series, case counts sum = {sum(mod)}")
print(f"  Table VIII time-of-day sum               = {sum(tod.values())}")
print(f"  difference                               = {sum(mod)-sum(tod.values())}"
      f"  ({(sum(mod)-sum(tod.values()))/sum(mod):.1%} of cases lack a time-of-day)")
print(f"  'In progress' rows (AIR 2/19086=87, DEFE 24/1939=61) = {87+61}")
print(f"  completed-only sum                       = {sum(mod)-87-61}")
print(f"  completed-only vs time-of-day            = "
      f"{sum(mod)-87-61-sum(tod.values())}")
print(f"  207 multiple-witness reports of {sum(mod)} = {207/sum(mod):.1%}")

# --- GEIPAN translation throughput, p283 -----------------------------------
print()
print("=" * 74)
print("GEIPAN TRANSLATION THROUGHPUT (p283, paras 50-51)")
print("=" * 74)
print(f"  68 D cases ~ 672 pages -> {672/68:.2f} pp/case; stated typical ~9 pp")
print(f"  stated rate: 4 cases/translator/week")
print(f"  late Mar 2009 -> 30 Jun 2009 is ~14 weeks -> "
      f"{68/14:.2f} cases/week achieved = {68/14/4:.2f} translator-equivalents")
print(f"  68 of 205 stated D cases = {68/205:.1%} complete")

# --- Blue Book, p190 -------------------------------------------------------
print()
print("=" * 74)
print("BLUE BOOK FRAMING (p190)")
print("=" * 74)
print(f"  USAF factsheet as cited: 12,618 sightings, 701 unidentified "
      f"= {701/12618:.4f}")
print(f"  relayed claim 'as many as possibly 4,000' -> {4000/12618:.4f}")
print(f"  relayed claim '30-40% of 12,000' -> 3,600-4,800")
print(f"  ratio of relayed claim to official: {4000/701:.1f}x")

print()
print("=" * 74)
print("SUMMARY")
print("=" * 74)
for name, got, stated, ok, note in CHECKS:
    print(f"  [{'PASS' if ok else 'FAIL'}] {name:<34} got={got:<7} stated={stated}")
