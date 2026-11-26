"""Codename / classification-marking extraction across every corpus on disk.

Every entry in CODENAMES carries an attestation tier, because mixing documented
programs with whistleblower claims and with known hoaxes is how a corpus of
"hits" becomes a corpus of noise.  Nothing is reported unless it is literally
present in the text.

Tiers
  OFFICIAL    named in government records (programs, panels, studies)
  CONTRACTOR  acknowledged industry/defence program
  ALLEGED     claim-only: named by claimants, no primary document
  FABRICATED  officially assessed as a hoax or forgery
"""
import os, re, json, collections, sys

# ---------------------------------------------------------------- the list
# tier, canonical name, notes.  Corrections to the working list are marked (!).
CODENAMES = {
    # ---- state UAP programs and studies
    "project sign":        ("OFFICIAL", "USAF UFO study, 1948-1949"),
    "project grudge":      ("OFFICIAL", "USAF UFO study, 1949-1952"),
    "project blue book":   ("OFFICIAL", "USAF UFO study, 1952-1969"),
    "blue book":           ("OFFICIAL", "Project Blue Book (short form)"),
    "project twinkle":     ("OFFICIAL", "USAF green-fireball instrumentation study, 1950-1951"),
    "project moon dust":   ("OFFICIAL", "USAF/State foreign-object recovery, 1953-1980s"),
    "moon dust":           ("OFFICIAL", "Project Moon Dust (short form)"),
    "project blue fly":    ("OFFICIAL", "USAF airlift of recovered foreign objects"),
    "project stork":       ("OFFICIAL", "Battelle statistical study for Blue Book (Special Report 14)"),
    "robertson panel":     ("OFFICIAL", "CIA scientific advisory panel, January 1953"),
    "condon committee":    ("OFFICIAL", "University of Colorado UFO Project, 1966-1968"),
    "condon report":       ("OFFICIAL", "Scientific Study of Unidentified Flying Objects, 1969"),
    "project condign":     ("OFFICIAL", "UK DIS study 1996-2000, report released 2006 (!) not 1950s"),
    "condign":             ("OFFICIAL", "UK Project Condign"),
    "aawsap":              ("OFFICIAL", "Advanced Aerospace Weapon System Applications Program, DIA 2008-2010"),
    "aatip":               ("OFFICIAL", "Advanced Aerospace Threat Identification Program"),
    "uaptf":               ("OFFICIAL", "Unidentified Aerial Phenomena Task Force, 2020-2022"),
    "aaro":                ("OFFICIAL", "All-domain Anomaly Resolution Office, 2022-"),
    "agency gepan":        ("OFFICIAL", "CNES Groupe d'Etudes des Phenomenes Aerospatiaux Non-identifies"),
    "gepan":               ("OFFICIAL", "CNES GEPAN, 1977-1988"),
    "sepra":               ("OFFICIAL", "CNES SEPRA, 1988-2004"),
    "geipan":              ("OFFICIAL", "CNES GEIPAN, 2005-"),
    "pursue":              ("OFFICIAL", "DoW UAP document release programme, 2026"),
    "baass":               ("CONTRACTOR", "Bigelow Aerospace Advanced Space Studies, AAWSAP prime"),
    "project 1794":        ("OFFICIAL", "USAF/Avro Canada disc-aircraft contract, 1956"),
    "silver bug":          ("OFFICIAL", "USAF Avro vertical-takeoff disc study, 1955"),
    "grill flame":         ("OFFICIAL", "US Army remote-viewing program, 1978-1982"),
    "center lane":         ("OFFICIAL", "successor to Grill Flame, 1983-1985"),
    "sun streak":          ("OFFICIAL", "DIA remote-viewing program, 1985-1990"),
    "star gate":           ("OFFICIAL", "DIA remote-viewing program, 1991-1995"),
    "stargate":            ("OFFICIAL", "Star Gate (compound form)"),
    # ---- aircraft / aerospace black programs
    "skunk works":         ("CONTRACTOR", "Lockheed Martin Advanced Development Programs"),
    "have blue":           ("CONTRACTOR", "Lockheed stealth demonstrator, 1977-1979"),
    "tacit blue":          ("CONTRACTOR", "Northrop stealth demonstrator, 1982-1985"),
    "senior crown":        ("OFFICIAL", "SR-71 operational program"),
    "senior year":         ("OFFICIAL", "U-2R program"),
    "senior prom":         ("OFFICIAL", "stealth cruise-missile demonstrator"),
    "senior span":         ("OFFICIAL", "U-2 SIGINT/datalink pod"),
    "senior ruby":         ("OFFICIAL", "U-2 ELINT system"),
    "senior trend":        ("OFFICIAL", "F-117A program"),
    "oxcart":              ("OFFICIAL", "CIA A-12 program"),
    "aquatone":            ("OFFICIAL", "CIA U-2 program"),
    "looking glass":       ("OFFICIAL", "SAC airborne command post, 1961-1990"),
    "aurora":              ("ALLEGED", "hypersonic aircraft; a single 1985 budget line, never confirmed"),
    "tr-3b":               ("ALLEGED", "triangular craft; no primary document"),
    "tr3b":                ("ALLEGED", "TR-3B variant spelling"),
    # ---- claim-only
    "project serpo":       ("ALLEGED", "alleged exchange program; anonymous 2005 emails"),
    "serpo":               ("ALLEGED", "Project SERPO"),
    "project pounce":      ("ALLEGED", "alleged recovery team; no primary document"),
    "glimmer glass":       ("ALLEGED", "named in 2023- whistleblower testimony; no primary document"),
    "immaculate constellation": ("ALLEGED", "named in 2024 congressional material; no released document"),
    "kona blue":           ("OFFICIAL", "proposed DHS successor to AAWSAP, never operational; AARO-acknowledged"),
    # ---- assessed fabricated
    "majestic 12":         ("FABRICATED", "FBI assessed the MJ-12 documents 'completely bogus', 1988"),
    "majestic-12":         ("FABRICATED", "MJ-12 (hyphenated)"),
    "mj-12":               ("FABRICATED", "MJ-12"),
    "operation majestic":  ("FABRICATED", "MJ-12 document series"),
    # ---- generic military usage, not a codename (kept to measure base rates)
    "bogey":               ("GENERIC", "aviation term for an unidentified contact; not a program"),
    "teaball":             ("GENERIC", "(!) USAF MiG-warning weapons control centre, Vietnam 1972 — SIGINT, not UAP"),
}

MARKINGS = {
    "banner_TS":    re.compile(r"\bTOP\s*SECRET\b"),
    "banner_S":     re.compile(r"(?<![A-Z])SECRET(?!\s*/\s*/?\s*NOFORN)(?![a-z])"),
    "banner_C":     re.compile(r"\bCONFIDENTIAL\b"),
    "banner_U":     re.compile(r"\bUNCLASSIFIED\b"),
    "portion_S":    re.compile(r"\(S\)|\(S//"),
    "portion_TS":   re.compile(r"\(TS\)|\(TS//"),
    "portion_C":    re.compile(r"\(C\)(?!\w)"),
    "portion_U":    re.compile(r"\(U\)(?!\w)"),
    "cav_NOFORN":   re.compile(r"\bNOFORN\b|\bNF\b"),
    "cav_ORCON":    re.compile(r"\bORCON\b"),
    "cav_PROPIN":   re.compile(r"\bPROPIN\b"),
    "cav_RELTO":    re.compile(r"\bREL\s+TO\b"),
    "cav_FVEY":     re.compile(r"\bFVEY\b"),
    "cav_LIMDIS":   re.compile(r"\bLIMDIS\b"),
    "cav_EXDIS":    re.compile(r"\bEXDIS\b"),
    "cav_NODIS":    re.compile(r"\bNODIS\b"),
    "cav_CUI":      re.compile(r"\bCUI\b"),
    "cav_FOUO":     re.compile(r"\bFOUO\b|FOR\s+OFFICIAL\s+USE\s+ONLY"),
    "cav_SCI":      re.compile(r"\bSI\s*/\s*TK\b|\bTALENT\s+KEYHOLE\b|\bHCS\b|\bCOMINT\b"),
    "decl_date":    re.compile(r"DECLASSIFIED\s+(?:ON|IN)|DECL\s*:|AUTO\s*DECL"),
    "redact_brkt":  re.compile(r"\[\s*(?:REDACTED|DELETED|WITHHELD|EXEMPT)[^\]]{0,40}\]", re.I),
    "redact_b":     re.compile(r"\(\s*b\s*\)\s*\(\s*[1-9]\s*\)"),   # FOIA exemption cites
    "redact_blk":   re.compile(r"[█▓▒░]{3,}"),  # block-glyph artifacts
}

# codename morphology for DISCOVERY: two capitalised words, adjective+noun shape
_CAND = re.compile(r"\b(?:PROJECT|OPERATION|PROGRAM|CODE\s*NAME|NICKNAME)\s+"
                   r"([A-Z][A-Za-z\-]{2,}(?:\s+[A-Z][A-Za-z\-]{2,})?)\b")

def scan_text(txt):
    low = txt.lower()
    hits = {}
    for cn in CODENAMES:
        n = low.count(cn)
        if n: hits[cn] = n
    marks = {k: len(rx.findall(txt)) for k, rx in MARKINGS.items() if rx.search(txt)}
    cands = collections.Counter(m.group(1).strip() for m in _CAND.finditer(txt))
    return hits, marks, cands

def ctx(txt, needle, w=110):
    low = txt.lower(); i = low.find(needle)
    if i < 0: return ""
    return re.sub(r"\s+", " ", txt[max(0, i - w): i + len(needle) + w]).strip()

def main():
    SP = "/tmp/claude-0/-home-user/f0aebeb3-1b62-5042-9067-46af83ba9a9d/scratchpad"
    corpora = [("pursue", f"{SP}/omega/pursue/txt", ".txt"),
               ("geipan_tep", "/home/user/UFOAI/data/raw/geipan/docs/1981-01-00849/txt", ".txt")]
    index = {"codename_hits": collections.defaultdict(lambda: {"docs": 0, "count": 0, "examples": []}),
             "markings": collections.defaultdict(lambda: {"docs": 0, "count": 0}),
             "discovered": collections.Counter(),
             "per_doc": {}, "corpora": {}}
    for cname, root, ext in corpora:
        if not os.path.isdir(root): continue
        files = sorted(f for f in os.listdir(root) if f.endswith(ext))
        index["corpora"][cname] = {"n_docs": len(files), "root": root}
        for f in files:
            p = os.path.join(root, f)
            try: txt = open(p, encoding="utf-8", errors="replace").read()
            except Exception: continue
            hits, marks, cands = scan_text(txt)
            if hits or marks:
                index["per_doc"][f"{cname}/{f}"] = {"codenames": hits, "markings": marks,
                                                   "chars": len(txt)}
            for cn, n in hits.items():
                e = index["codename_hits"][cn]
                e["docs"] += 1; e["count"] += n
                if len(e["examples"]) < 4:
                    e["examples"].append({"doc": f"{cname}/{f}", "context": ctx(txt, cn)})
            for k, n in marks.items():
                index["markings"][k]["docs"] += 1; index["markings"][k]["count"] += n
            index["discovered"].update(cands)
    # fold tiers in
    out = {"corpora": index["corpora"], "codenames": {}, "markings": dict(index["markings"]),
           "discovered_unknown": {}, "per_doc": index["per_doc"]}
    for cn, e in index["codename_hits"].items():
        tier, note = CODENAMES[cn]
        out["codenames"][cn] = {"tier": tier, "note": note, **e}
    known = set()
    for cn in CODENAMES: known.update(cn.upper().split())
    for nm, n in index["discovered"].most_common():
        if n < 2: continue
        if any(w in known for w in nm.upper().split()): continue
        out["discovered_unknown"][nm] = n
    os.makedirs("data/processed/codenames", exist_ok=True)
    json.dump(out, open("data/processed/codenames/codename_index.json", "w"), indent=1)

    # ------------------------------------------------------------ report
    print(f"corpora: " + ", ".join(f"{k}={v['n_docs']} docs" for k, v in out["corpora"].items()))
    print(f"\n=== CODENAMES PRESENT ({len(out['codenames'])} of {len(CODENAMES)} searched) ===")
    print(f"{'tier':11s} {'codename':28s} {'docs':>5s} {'hits':>6s}")
    for cn, e in sorted(out["codenames"].items(), key=lambda x: (-x[1]["docs"], x[0])):
        print(f"{e['tier']:11s} {cn:28s} {e['docs']:5d} {e['count']:6d}")
    absent = [c for c in CODENAMES if c not in out["codenames"]]
    print(f"\n=== ABSENT ({len(absent)}) — searched, zero occurrences, reported as zero ===")
    for c in sorted(absent): print(f"   {CODENAMES[c][0]:11s} {c}")
    print(f"\n=== CLASSIFICATION MARKINGS ===")
    for k, v in sorted(out["markings"].items(), key=lambda x: -x[1]["docs"]):
        print(f"  {k:14s} docs={v['docs']:4d}  occurrences={v['count']:7d}")
    print(f"\n=== DISCOVERED (PROJECT/OPERATION X, >=2 occurrences, not in known list) ===")
    for nm, n in list(out["discovered_unknown"].items())[:40]:
        print(f"  {n:5d}  {nm}")
    print("\nwrote data/processed/codenames/codename_index.json")

if __name__ == "__main__":
    main()
