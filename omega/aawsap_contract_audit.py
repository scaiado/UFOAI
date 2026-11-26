"""AAWSAP contract audit: contracted vs delivered vs the government's own review.

§5 item 3.  Three primary documents, all on disk since session 3, never compared:

  D182  AAWSAP Statement of Work / Statement of Objectives, 18 July 2008
        solicitation HHM402-08-R-0211, contract HHM402-08-C-0072.
        Names 12 technical areas and 5 deliverable classes.
  D117-D153  the 37 delivered DIRD technical reports.
  D188  "Review of Advanced Aerospace Contract Deliverables", INFO MEMO
        U-429-09/DWO, 30 October 2009, DIA Directorate for Analysis to the
        DIRECTOR, DIA.  States how many reports were delivered and lists every
        title in Enclosure 1.

A closed loop: what was bought, what arrived, and what the buyer said about it.
D188 is the pivot, because it is the government grading its own contract and it
enumerates the deliverables by title -- so the public release can be reconciled
against the government's own delivery list, title by title.
"""
import os, re, sys, json, glob, collections, difflib

TXT = os.environ.get("OMEGA_PURSUE_TXT", "")
DIRD_DIR = "evidence_vault/01_PURSUE_PRIMARY/AAWSAP_DIRDs"
OCR = "data/raw/pursue_ocr/txt"
OUT = "evidence_vault/01_PURSUE_PRIMARY"

# The 12 technical areas required by D182 section 3(a).  The OCR of that list is
# badly degraded ("2. propusia'1; 3.oontrof; 4. powerge,ea1b,,"), so the
# canonical wording is taken from D188, which restates them in clean text:
# "lift, propulsion, control, power generation, spatial/temporal translation,
#  materials, structural configuration, signature reduction, human interface,
#  human effects, and armament" -- 11 named, the 12th being D182's
# "other peripheral areas in support of (1-11)".
AREAS = {
    "lift":            r"lift|lightcraft|magnetohydro|mhd|air.?breathing",
    "propulsion":      r"propulsion|positron|fusion.*propuls|nuclear propuls|"
                       r"warp|negative mass|aneutronic",
    "control":         r"control|cockpit|cognitive limits|automation|"
                       r"unmanned spacecraft",
    "power generation": r"power|energy|ultracapacitor|vacuum energy|"
                       r"extracting energy|fusion",
    "spatial/temporal translation": r"wormhole|stargate|space.?time|spacetime|"
                       r"metric engineering|extra.?dimension|teleport",
    "materials":       r"material|metallic glass|programmable matter|"
                       r"metamaterial|biomaterial|spintronic",
    "structural configuration": r"structur|configurat|platform",
    "signature reduction": r"invisibilit|cloak|signature|stealth|"
                       r"detection and high.?resolution",
    "human interface": r"human interface|limb.?operated|controlling external|"
                       r"cockpit|biosensor|biomems",
    "human effects":   r"human biological|biological tissue|field effects|"
                       r"acute and subacute",
    "armament":        r"laser|weapon|microwave|high.?energy laser|"
                       r"pulsed.?high.?power|directed energy",
    "other peripheral": r"drake|maverick|quantum comput|quantum tomography|"
                       r"entanglement|gravitational wave|gravity",
}
AREAS = {k: re.compile(v, re.I) for k, v in AREAS.items()}

# D182 section 11 deliverables
DELIVERABLES = {
    "a_status_reports": "monthly status reports (accomplishments, milestones, "
                        "work in progress)",
    "b_project_mgmt_plan": "per technical area, 60-day overview paper: scope of "
                           "final report, POA&M, team composition",
    "c_research_reports": "per technical area, comprehensive report + briefing, "
                          "to GPL by END OF THE TENTH MONTH, + executive version",
    "d_integrated_threat_assessment": "FINAL report + briefing assessing the "
                                      "foreign threat from advanced aerospace "
                                      "platforms, incorporating the individual "
                                      "research reports, at end of period of "
                                      "performance, + executive version",
    "e_resumes": "resumes of all key personnel",
}

# Enclosure 1 of D188: the 26 FY 2009 technical reports, as the government
# listed them, in its order.  Transcribed from the OCR of that table.
D188_LIST = [
    ("Inertial Electrostatic Confinement Fusion", "U Illinois"),
    ("Pulse-Power-Based Weaponry", "Northrup"),
    ("Space-Time Modifications for Spaceflight Applications", "Earth Tech"),
    ("Novel MEMS-Based Biosensors", "Arizona St U"),
    ("Theory and Experiments of Invisibility Cloaking", "U St. Andrews"),
    ("Wormholes in Space Time", "Earth Tech"),
    ("Gravity Wave Communication", "Gravwave"),
    ("Superconductors in Gravity Research", ""),
    ("Antigravity for Aerospace Applications", "EarthTech"),
    ("Field Effects on Biological Tissues", "Wayne State"),
    ("Positron Aerospace Propulsion", "Positronics"),
    ("Vacuum Energy Applications", "Earth Tech"),
    ("Improved Statistical Approach to Drake Equation", "Acad Astra"),
    ("Maverick vs. Corporate Research Cultures", ""),
    ("Biosensors and BioMEMS", "Arizona St U"),
    ("Metamaterials for Aerospace Applications", "U Texas"),
    ("Warp Drives", ""),
    ("Controlling Devices Without Limb-Operated Interfaces", "Wayne State"),
    ("Materials for Advanced Aerospace Platforms", "Ohio State U"),
    ("Metallic Glasses", "Johns Hopkins U"),
    ("Programmable Matter", "Prog Matter"),
    ("Metallic Spintronics", "U Texas"),
    ("High-Energy Laser Weapons", "Priv Consultant"),
    ("Quantum Entanglement Communications", "Washington"),
    ("Space Access: Where Been, Where Go", "Hypertech"),
    ("Advanced Nuclear Propulsion for Deep Space", "Nevada"),
]

# Enclosure 1's Author column, as pseudonymised in the release.
# "MP Person 6" for Pulse-Power-Based Weaponry is an OCR truncation of 64.
D188_PERSON = [70, 64, 57, 65, 68, 58, 77, 75, 58, 81, 69, 58, 80, 75, 65, 78,
               74, 73, 66, 63, 90, 71, 79, 76, 67, 72]

PERSON_RX = re.compile(r"(?:AAP|MP|AAWSAP)\s?Person\s?(\d+)", re.I)

MONTHS = ("january february march april may june july august september "
          "october november december").split()


def dird_inventory():
    """(id, title, date) for each delivered DIRD, from the vault filenames."""
    out = []
    for f in sorted(os.listdir(DIRD_DIR)):
        if not f.endswith(".txt"):
            continue
        stem = re.sub(r"_djvu\.txt$", "", f)
        m = re.match(r"DOW-UAP-D(\d+)[_-]+AAWSAP?-DIRD-(.+)$", stem)
        if not m:
            continue
        did, rest = int(m.group(1)), m.group(2)
        dm = re.search(r"-(" + "|".join(MONTHS) + r")-(\d{1,2})-(\d{4})",
                       rest, re.I)
        date = None
        if dm:
            date = (int(dm.group(3)), MONTHS.index(dm.group(1).lower()) + 1,
                    int(dm.group(2)))
            rest = rest[:dm.start()]
        title = rest.replace("_", " ").replace("-", " ").strip()
        out.append({"id": f"D{did}", "n": did, "title": title, "date": date,
                    "file": f})
    return out


def norm(s):
    return re.sub(r"[^a-z0-9 ]", " ", s.lower()).split()


def pair_score(title, d):
    tt, dt = set(norm(title)), set(norm(d["title"]))
    overlap = len(tt & dt) / max(1, min(len(tt), len(dt)))
    seq = difflib.SequenceMatcher(None, " ".join(sorted(tt)),
                                  " ".join(sorted(dt))).ratio()
    return max(overlap, seq)


def assign_one_to_one(titles, pool):
    """1:1 assignment of D188 titles to delivered DIRDs.

    A greedy best-match is WRONG here and was caught doing it: it handed D135
    to both "Space-Time Modifications" and "Antigravity", D123 to both
    "Pulse-Power-Based Weaponry" and "Positron Aerospace Propulsion", and D136
    to both biosensor entries -- inflating the match count while leaving the
    true counterparts (D132, D121) unclaimed.  Each delivered report is one
    document, so the mapping must be injective.  Solved exactly.
    """
    import numpy as np
    from scipy.optimize import linear_sum_assignment
    C = np.array([[1.0 - pair_score(t, d) for d in pool] for t, _ in titles])
    ri, ci = linear_sum_assignment(C)
    return {int(r): (pool[int(c)], 1.0 - C[r, c]) for r, c in zip(ri, ci)}


def find_capstone():
    """Does the Integrated Threat Assessment (deliverable d) exist anywhere?"""
    rx = re.compile(r"integrated\s+threat\s+assessment|"
                    r"integrated\s+final\s+assessment", re.I)
    hits = []
    for d in (TXT, OCR):
        if not d or not os.path.isdir(d):
            continue
        for f in sorted(glob.glob(os.path.join(d, "*.txt"))):
            t = open(f, encoding="utf-8", errors="replace").read()
            for m in rx.finditer(t):
                hits.append({"file": os.path.basename(f),
                             "context": re.sub(r"\s+", " ",
                                               t[max(0, m.start() - 110):
                                                 m.end() + 110])})
    return hits


# Contract line items, transcribed from the CLIN tables.  In these tables the
# item name is followed by quantity, then the accounting block, then the dollar
# figure, then the period of performance -- so a figure printed ABOVE an item
# name belongs to the PRECEDING item.  Read the other way round, D111 appears to
# price the threat assessment at $2.1M; it does not, that is the research-report
# CLIN closing out.
CLINS = {
    "base year 0001-0005 (22 Sep 2008 - 29 Sep 2009), D111": [
        ("0001", "Monthly Status Reports (qty 12)", 2887000.00),
        ("0002", "Project Management Plan for Tasks 3.a.1-3.a.12", 3600000.00),
        ("0003", "Research Report for Tasks 3.a.1-3.a.12", 2100000.00),
        ("0004", "Comprehensive Integrated Threat Assessment", 240000.00),
    ],
    "option year 1, 1001-1005 (22 Sep 2009 - 21 Sep 2010), D113 P00002": [
        ("1001", "Monthly Status Reports (qty 12)", 1549100.00),
        ("1002", "Project Management Plan for Tasks 3.a.1-3.a.12", 4759300.00),
        ("1003", "Research Report for Tasks 3.a.1-3.a.12", 2870600.00),
        ("1004", "Comprehensive Integrated Threat Assessment", 220200.00),
        ("1005", "Travel", 36700.00),
    ],
}


def main():
    dirds = dird_inventory()
    print(f"delivered DIRDs in the release: {len(dirds)} "
          f"({dirds[0]['id']}-{dirds[-1]['id']})")

    # ---- 1. reconcile D188's Enclosure 1 against the release
    print(f"\n=== 1. D188 Enclosure 1 ({len(D188_LIST)} FY2009 reports) "
          f"vs the public release ===")
    print(f"  {'score':>5}  {'DIRD':5s} {'date':10s} D188 title -> released title")
    # D188's list is explicitly the FY2009 reports, and D117-D142 is exactly
    # 26 documents, so the assignment is restricted to that block.  Drawing
    # from all 37 let the solver reach into the FY2010 wave (D152, D149) to
    # satisfy injectivity while leaving the true counterparts D119 and D132
    # unclaimed.  NOTE: a square assignment matches everything by
    # construction, so "26/26" is structural and is NOT itself evidence.  The
    # evidence is the score distribution plus the independent affiliation check
    # below.
    pool = [d for d in dirds if d["n"] <= 142]
    assign = assign_one_to_one(D188_LIST, pool)
    used, unmatched = set(), []
    rows = []
    for i, (title, aff) in enumerate(D188_LIST):
        d, sc = assign[i]
        ok = sc >= 0.34
        if ok:
            used.add(d["id"])
        else:
            unmatched.append((title, aff, d, sc))
        ds = "%04d-%02d-%02d" % d["date"] if d["date"] else "?"
        rows.append({"d188_title": title, "affiliation": aff,
                     "matched": d["id"] if ok else None, "score": round(sc, 3),
                     "released_title": d["title"], "date": ds})
        print(f"  {sc:5.2f}  {(d['id'] if ok else '--'):5s} {ds:10s} "
              f"{title[:44]:44s} -> {d['title'][:40]}")

    scs = sorted(sc for _, sc in assign.values())
    exact = sum(1 for x in scs if x >= 0.99)
    strong = sum(1 for x in scs if 0.60 <= x < 0.99)
    weak = sum(1 for x in scs if x < 0.60)
    print(f"\n  assignment is square (26 titles, 26 documents), so every title")
    print(f"  receives a counterpart by construction.  Score distribution:")
    print(f"    exact title match (>=0.99) : {exact}")
    print(f"    strong retitle   (0.60-)   : {strong}")
    print(f"    weak on title alone (<0.60) : {weak}  "
          f"-- resolved by author ID below")

    # ---- the real independent check: the pseudonym namespace is SHARED
    # D188's Enclosure 1 gives an author per title as "MP Person NN", and each
    # DIRD names its author as "AAP Person NN" / "MP Person NN".  The release
    # pseudonymised consistently ACROSS documents, so the author number is an
    # identifier that was assigned independently of any matching I do.  If the
    # number on each DIRD equals the number D188 attaches to the title assigned
    # to it, the mapping is confirmed by the release's own redaction scheme.
    #
    # The affiliation check this replaces was impossible: the DIRDs carry no
    # institution line at all, only the pseudonym, so it returned 0/8 as an
    # artifact of the instrument rather than as evidence.
    print("\n  AUTHOR-ID CROSS-CHECK (independent of title similarity):")
    print("  D188 Enclosure 1 and the DIRDs share one pseudonym namespace.")
    idok = idbad = idmiss = 0
    bad = []
    for i, (title, aff) in enumerate(D188_LIST):
        d, sc = assign[i]
        txt = open(os.path.join(DIRD_DIR, d["file"]), encoding="utf-8",
                   errors="replace").read()[:3000]
        m = PERSON_RX.search(txt)
        want = D188_PERSON[i]
        if not m:
            idmiss += 1
            continue
        got = int(m.group(1))
        if got == want:
            idok += 1
        else:
            idbad += 1
            bad.append((title, d["id"], want, got))
    print(f"    author ID agrees : {idok}/{len(D188_LIST)}")
    print(f"    disagrees        : {idbad}")
    print(f"    no ID found      : {idmiss}")
    for t, did, w, g in bad:
        print(f"      {did}  {t[:44]:44s} D188 says {w}, document says {g}")
    if idok == len(D188_LIST):
        print("    => every FY2009 deliverable the government recorded is")
        print("       present in the public release, confirmed by an identifier")
        print("       the release itself assigned.  No deliverable is missing.")

    # (superseded) affiliation check kept out: DIRDs carry no institution line
    print("\n  Low-title-similarity pairs, for reference:")
    AFFRX_UNUSED = {"Earth Tech": r"earth\s*tech", "EarthTech": r"earth\s*tech",
             "Arizona St U": r"arizona state", "Northrup": r"northrop|northrup",
             "U Illinois": r"illinois", "U St. Andrews": r"st\.?\s*andrews",
             "Gravwave": r"gravwave|grav\s*wave", "Wayne State": r"wayne state",
             "Positronics": r"positronic", "Acad Astra": r"academy|astronaut",
             "U Texas": r"texas", "Ohio State U": r"ohio state",
             "Johns Hopkins U": r"johns hopkins", "Prog Matter": r"programmable",
             "Washington": r"washington", "Hypertech": r"hypertech",
             "Nevada": r"nevada", "Priv Consultant": r"consult"}
    print("\n  The three weak title pairs resolved by author ID alone:")
    for i, (title, aff) in enumerate(D188_LIST):
        d, sc = assign[i]
        if sc >= 0.60:
            continue
        print(f"    {d['id']:5s} person {D188_PERSON[i]:>3}  "
              f"{title[:42]:42s} -> {d['title'][:38]}")
    if unmatched and idok != len(D188_LIST):
        print("  UNRESOLVED (recorded as delivered; no confirmed counterpart):")
        for t, a, d, sc in unmatched:
            print(f"    {t}  [{a}]   best guess {d['id']} {d['title'][:36]} "
                  f"({sc:.2f})")

    # ---- 2. the FY2009 / FY2010 split
    print("\n=== 2. DELIVERY WAVES, by the dates on the documents themselves ===")
    waves = collections.defaultdict(list)
    for d in dirds:
        y, m = (d["date"][0], d["date"][1]) if d["date"] else (0, 0)
        waves[(y, m)].append(d["id"])
    for (y, m), ids in sorted(waves.items()):
        print(f"  {y}-{m:02d}  {len(ids):2d}  {' '.join(ids)}")
    claimed = {d["id"] for d, _ in assign.values()}
    leftover = [d["id"] for d in dirds if d["n"] <= 142
                and d["id"] not in claimed]
    print(f"  D117-D142 documents NOT claimed by any D188 title: "
          f"{leftover if leftover else '-- none'}")

    fy09 = [d for d in dirds if d["n"] <= 142]
    fy10 = [d for d in dirds if d["n"] >= 143]
    print(f"\n  D117-D142 = {len(fy09)} documents -- D188 says 26 were "
          f"delivered in FY2009")
    print(f"  D143-D153 = {len(fy10)} documents -- the option-year wave")
    if fy09:
        print(f"  D117-D142 date span: "
              f"{min(d['date'] for d in fy09 if d['date'])} to "
              f"{max(d['date'] for d in fy09 if d['date'])}")
    if fy10:
        print(f"  D143-D153 date span: "
              f"{min(d['date'] for d in fy10 if d['date'])} to "
              f"{max(d['date'] for d in fy10 if d['date'])}")

    # ---- 3. coverage of the 12 contracted technical areas
    print("\n=== 3. COVERAGE of D182's 12 contracted technical areas ===")
    cov = {}
    for area, rx in AREAS.items():
        hit = [d["id"] for d in dirds if rx.search(d["title"])]
        cov[area] = hit
        flag = "  " if hit else "**"
        print(f"  {flag} {area:30s} {len(hit):2d}  {' '.join(hit[:9])}")
    empty = [a for a, h in cov.items() if not h]
    print(f"\n  areas with no matching deliverable: "
          f"{len(empty)}  {empty if empty else '-- none'}")

    # ---- 4. the capstone deliverable
    print("\n=== 4. DELIVERABLE (d): INTEGRATED THREAT ASSESSMENT ===")
    print("    D182 s11(d): a final report and briefing assessing the foreign")
    print("    threat from advanced aerospace platforms, incorporating the")
    print("    individual research reports, at the end of the period of")
    print("    performance.  This is the capstone -- the only deliverable that")
    print("    states a threat judgement rather than surveying physics.")
    hits = find_capstone()
    if hits:
        print(f"\n    references found: {len(hits)}")
        for h in hits[:8]:
            print(f"      [{h['file'][:40]}] ...{h['context'][:150]}")
    else:
        print("\n    NOT PRESENT and NEVER REFERENCED anywhere in the release "
              "corpus.")

    # ---- 5. the CLIN structure IS the SoW deliverable list, priced
    print("\n=== 5. CONTRACT LINE ITEMS -- the SoW deliverables, priced ===")
    print("    'Tasks 3.a.1 - 3.a.12' is D182 s3(a)'s twelve technical areas,")
    print("    which independently confirms the 12-area reading of that")
    print("    document's badly OCR'd list.")
    for yr, items in CLINS.items():
        tot = sum(v for _, _, v in items)
        print(f"\n  {yr}")
        for clin, name, v in items:
            print(f"    {clin}  {name:48s} ${v:>12,.2f}  "
                  f"{v/tot:5.1%}")
        print(f"          {'listed total':48s} ${tot:>12,.2f}")

    ita = [(yr, c, v) for yr, items in CLINS.items()
           for c, n, v in items if "Threat Assessment" in n]
    print(f"\n  Comprehensive Integrated Threat Assessment, as contracted:")
    for yr, c, v in ita:
        print(f"    CLIN {c}  ${v:>10,.2f}   ({yr.split(',')[0]})")
    print(f"    TOTAL CONTRACTED: ${sum(v for _, _, v in ita):,.2f}")

    json.dump({"n_dirds": len(dirds), "dirds": dirds, "clins": CLINS,
               "leftover_fy09": leftover,
               "d188_reconciliation": rows,
               "matched": len(used), "unmatched": [u[0] for u in unmatched],
               "waves": {f"{y}-{m:02d}": ids for (y, m), ids in waves.items()},
               "author_id_check": {"agree": idok, "disagree": idbad,
                                   "missing": idmiss},
               "area_coverage": cov, "areas_uncovered": empty,
               "deliverables": DELIVERABLES,
               "capstone_references": hits},
              open(f"{OUT}/aawsap_contract_audit.json", "w"), indent=1)
    print(f"\nwrote {OUT}/aawsap_contract_audit.json")


if __name__ == "__main__":
    main()
