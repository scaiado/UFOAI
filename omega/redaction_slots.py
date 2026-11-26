"""Redaction SLOT analysis -- what is withheld, not how much.  §5 item 2.

§1.7 counted 982 inline exemption substitutions and stopped at extent.  This
goes after content.  The route in is not grammar, as the handoff assumed, but
STRUCTURE: the DOW mission reports are MISREP forms, and a redaction sits in a
NAMED FIELD whose label states what was removed.

    • Major Command (MAJCOM): AFCENT
    • Combatant Command (COCOM): (b)(1)1.4a
    • Operations Center: (b)(1)1.4a
    • Full Name: (b)(3), 130b, (b)(6) 1.4a

No inference is needed for the class of the withheld token -- the form names it.
That makes four things measurable that a count of redactions cannot reach:

  1. PER-FIELD WITHHOLDING RATE.  24 documents share one schema, so each field
     has a rate: withheld in k of the n documents where it appears.  A field at
     24/24 is categorically protected; a field at 6/24 is protected by
     circumstance, which is a different claim about the policy.

  2. CALIBRATION.  The exemption code is an INDEPENDENT label attached by the
     releasing authority.  If field semantics and exemption code agree --
     (b)(6) privacy on name/email/phone, (b)(1)1.4(a) military plans on
     operations and weapons -- the slot reading is validated against the
     government's own classification, not against my guess.  Disagreement is
     equally informative and is reported.

  3. VALUE DOMAIN.  A field withheld in document X but RELEASED in document Y
     has its value space enumerated by Y.  The withholding is then inconsistent
     across documents, and the released instances bound what the withheld ones
     can say.

  4. CROSS-FIELD DETERMINATION.  Some withheld fields are fixed by a released
     neighbour.  `MAJCOM: AFCENT` is released while `COCOM` is withheld, but
     AFCENT is the air component of CENTCOM, so the withheld field is recovered
     from the released one.  Reported as candidate pairs with the rule, not as
     a claim about any single document.

Nothing here reconstructs a withheld VALUE from a classified source.  Every
statement rests on text the government released, read against itself.
"""
import os, re, sys, json, glob, collections

TXT_DIRS = [
    os.environ.get("OMEGA_PURSUE_TXT", ""),
    "data/raw/pursue_ocr/txt",
]
OUT = "evidence_vault/05_SCRUBBED_CONTENT"

# ---------------------------------------------------------------- markers
# A redaction marker, tolerant of this corpus's OCR.  Three families:
#   (b)(n)      FOIA exemption, brackets and letters frequently garbled
#               -- (b}(6), (bl(6l, fbl{6, (6)(7)(D), I 3 sc (b}l6)
#   1.4(a-h)    E.O. 13526 classification reason, often WITHOUT the (b)(1)
#               prefix: a bare "! 1.4a" in a field IS a withholding
#   3.5(c)      E.O. 13526 FOIA-review provision; 130b = 10 USC 130b
# Validated against hand-checked positives and negatives -- it must not fire
# on real released values (AFCENT, 1LT, 132 Wing, USCENTCOM, grid squares).
_BK = r"[\(\[\{\|fItl<]"          # an opening bracket, or what OCR made of one
_BKC = r"[\)\]\}\|lI1t>]"         # a closing bracket, likewise
MARK = re.compile(
    r"(?xi)"
    r"(?: " + _BK + r" \s* [bl6G] \s* " + _BKC + r" \s* " + _BK + r"? \s* [0-9lIOSG] )"
    r"| (?: FOIA \s* Exemption )"
    r"| (?: \b 1 \s* \.? \s* 4 \s* [a-h] \b )"
    r"| (?: \b 3 \s* \.? \s* [S5] \s* c \b )"
    r"| (?: \b 130 \s* b \b )"
)
# the normalisable exemption code, for the calibration step
CODE = re.compile(r"\(b\)\s*\(\s*(\d)\s*\)(?:\s*\(?\s*(1\.4\s*[a-h]|[A-H])\s*\)?)?", re.I)
EO_BARE = re.compile(r"\b1\s*\.?\s*4\s*([a-h])\b", re.I)
# A bare 1.4(x) directly after a classification banner is a PORTION MARKING
# declaring that paragraph's classification reason -- not a substitution for
# removed text.  Measured: 7 of 498 bare marks, all in narrative fields.
BANNER = re.compile(
    r"\(\s*(?:TS|S|C|U|SECRET|CONFIDENTIAL|UNCLASSIFIED)"
    r"(?:\s*/{1,2}\s*[A-Z0-9/ ,\.]{0,40})?\s*\)\s*[-\u2013:]?\s*$", re.I)

def portion_marks_only(v):
    """True if every marker in v is a banner-preceded portion marking."""
    hits = list(EO_BARE.finditer(v))
    if not hits or CODE.search(v):
        return False
    return all(BANNER.search(v[max(0, m.start() - 60):m.start()]) for m in hits)

BULLET = re.compile(r"[\u2022\u00b7]")

def legibility(v):
    """Share of characters that are alphanumeric or space."""
    if not v:
        return 0.0
    return sum(1 for c in v if c.isalnum() or c.isspace()) / len(v)

def classify_value(v):
    """WITHHELD / RELEASED / UNREADABLE / EMPTY for one field value.

    UNREADABLE exists so OCR damage is never silently counted as a RELEASE.
    Session 3's lesson -- a hit without context is noise -- applied to the
    complement: a non-hit in garbage is not evidence of disclosure.
    """
    s = v.strip()
    if not s or re.fullmatch(r"[\s\.\-_,;:/\\|()\[\]]*", s):
        return "EMPTY"
    if MARK.search(s):
        return "PORTION_MARK" if portion_marks_only(s) else "WITHHELD"
    if legibility(s) < 0.72 or not re.search(r"[A-Za-z0-9]{3}", s):
        return "UNREADABLE"
    return "RELEASED"


# ---------------------------------------------------------------- slot schema
# field label -> semantic slot class.  Ordered: first match wins.
SLOTS = [
    ("PERSONNEL",     r"full name|^name$|rank|e-?mail|phone|poc\b|operator|"
                      r"aircrew|pilot|wso\b|signature|prepared by|submitted by|"
                      r"jtac|released by|drafter"),
    ("CALLSIGN",      r"callsign|call sign|mode 3|iff|tail number|side number"),
    ("WEAPON_SENSOR", r"radar|rwr|mws\b|ircm|ecm\b|cmd name|chaff|flare|decoy|"
                      r"aam\b|gun|rounds|cartridge|designator|software load|"
                      r"mission data|munition|ordnance|weapon|pod\b|targeting|"
                      r"asset type|expend"),
    ("UNIT_ORG",      r"unit|wing|squadron|originator|service|detachment|"
                      r"group\b|command|cocom|majcom|operations center|"
                      r"task force|component|aoc\b"),
    ("GEO",           r"killbox|location|icao|country|airfield|base\b|"
                      r"coordinate|lat\b|lon\b|grid|area of|region|waypoint|"
                      r"airspace|start point|end point"),
    ("TIME",          r"time|dtg|date|duration|hour|shutdown|takeoff|land\b|"
                      r"on station|off station"),
    ("OPERATION",     r"operation|mission type|tasking|ato\b|jtar|sortie|"
                      r"objective|target|fragged|mission number|mission canceled"),
    ("CLASSIFICATION", r"classification|caveat|declassif|derived from|"
                      r"classified by|reason"),
    ("NARRATIVE",     r"gentext|narrative|remarks|comment|details|summary|"
                      r"weather|assessment"),
    ("COUNT_QTY",     r"^num|number of|quantity|^total\b|amount|accuracy"),
]
SLOTS = [(k, __import__("re").compile(v, __import__("re").I)) for k, v in SLOTS]

EO14 = {"a": "military plans/weapons/operations",
        "b": "foreign government information",
        "c": "intelligence activities/sources/methods",
        "d": "foreign relations", "e": "sci/tech/economic",
        "f": "nuclear safeguards", "g": "infrastructure vulnerabilities",
        "h": "weapons of mass destruction"}

# What the exemption code ITSELF asserts about the content class.  Used only to
# SCORE agreement with the slot reading -- never to assign a slot.
CODE_EXPECT = {
    "(b)(6)": {"PERSONNEL"},
    "(b)(7)": {"PERSONNEL"},
    "(b)(3)": {"PERSONNEL", "WEAPON_SENSOR"},      # 10 USC 130b = personnel
    "(b)(1)1.4a": {"OPERATION", "UNIT_ORG", "WEAPON_SENSOR", "CALLSIGN",
                   "GEO", "TIME", "COUNT_QTY"},
    "(b)(1)1.4c": {"WEAPON_SENSOR", "OPERATION"},
    "(b)(1)1.4g": {"WEAPON_SENSOR", "GEO", "UNIT_ORG"},
    "1.4a": {"OPERATION", "UNIT_ORG", "WEAPON_SENSOR", "CALLSIGN", "GEO",
             "TIME", "COUNT_QTY"},
    "1.4g": {"WEAPON_SENSOR", "GEO", "UNIT_ORG"},
    "1.4c": {"WEAPON_SENSOR", "OPERATION"},
    "1.4e": {"WEAPON_SENSOR"},
}

# A document counts as a MISREP form only if it carries the section spine.
SPINE = [r"\bCLASSIFICATION\b", r"\bMSGID\b", r"\bMSNID\b",
         r"\bOPERATION\b", r"\bAircraft\b|\bMission Type\b|\bGentext\b"]
SPINE = [__import__("re").compile(s, __import__("re").I) for s in SPINE]
MIN_SPINE = 3


def slot_of(label):
    for k, rx in SLOTS:
        if rx.search(label):
            return k
    return "UNCLASSIFIED_SLOT"


def codes_in(value):
    """Normalised exemption codes present in a withheld value."""
    out = []
    for m in CODE.finditer(value):
        b, sub = m.group(1), (m.group(2) or "").replace(" ", "").lower()
        out.append(f"(b)({b}){sub}" if sub.startswith("1.4") else f"(b)({b})")
    if not out:
        for m in EO_BARE.finditer(value):
            out.append("1.4" + m.group(1).lower())
    return out or ["UNSPECIFIED"]


def iter_texts():
    for d in TXT_DIRS:
        if d and os.path.isdir(d):
            for f in sorted(glob.glob(os.path.join(d, "*.txt"))):
                yield f, open(f, encoding="utf-8", errors="replace").read()


def is_misrep(text):
    return sum(1 for rx in SPINE if rx.search(text)) >= MIN_SPINE


def parse_fields(text):
    out = []
    for chunk in BULLET.split(text)[1:]:
        if ":" not in chunk:
            continue
        lab, _, val = chunk.partition(":")
        lab = re.sub(r"\s+", " ", lab).strip()
        if not (2 <= len(lab) <= 70) or not re.match(r"[A-Za-z]", lab):
            continue
        if legibility(lab) < 0.80:
            continue
        out.append((lab, re.sub(r"\s+", " ", val).strip()))
    return out


def canonical_labels(parsed, min_docs=3):
    """Labels that recur across documents are schema; singletons are OCR noise."""
    seen = collections.Counter()
    for _, fs in parsed:
        for lab in {l for l, _ in fs}:
            seen[lab] += 1
    return {l for l, n in seen.items() if n >= min_docs}


def main():
    raw = [(os.path.basename(p), t) for p, t in iter_texts()]
    forms = [(b, t) for b, t in raw if is_misrep(t)]
    parsed = [(b, parse_fields(t)) for b, t in forms]
    parsed = [(b, fs) for b, fs in parsed if len(fs) >= 10]
    canon = canonical_labels(parsed)

    fields = collections.defaultdict(
        lambda: {"WITHHELD": 0, "RELEASED": 0, "UNREADABLE": 0, "EMPTY": 0,
                 "PORTION_MARK": 0,
                 "codes": collections.Counter(), "released_vals": [],
                 "docs": set()})
    rows = []
    for base, fs in parsed:
        for lab, val in fs:
            if lab not in canon:
                continue
            k = classify_value(val)
            rec = fields[lab]
            rec[k] += 1
            rec["docs"].add(base)
            if k == "WITHHELD":
                cs = codes_in(val)
                rec["codes"].update(cs)
                rows.append({"doc": base, "label": lab, "slot": slot_of(lab),
                             "codes": cs})
            elif k == "RELEASED" and len(val) <= 60:
                rec["released_vals"].append(val)

    tot = {k: sum(f[k] for f in fields.values())
           for k in ("WITHHELD", "RELEASED", "UNREADABLE", "EMPTY",
                     "PORTION_MARK")}
    print(f"texts read              : {len(raw)}")
    print(f"MISREP forms (spine>={MIN_SPINE})  : {len(forms)}  "
          f"-> parsed with >=10 fields: {len(parsed)}")
    print(f"canonical field labels (>=3 docs) : {len(canon)}")
    print(f"field instances         : withheld {tot['WITHHELD']}, "
          f"released {tot['RELEASED']}, unreadable {tot['UNREADABLE']}, "
          f"empty {tot['EMPTY']}, portion-marks excluded "
          f"{tot['PORTION_MARK']}")
    den = tot["WITHHELD"] + tot["RELEASED"]
    print(f"withholding rate over decidable instances: "
          f"{tot['WITHHELD']}/{den} = {tot['WITHHELD']/den:.3f}")

    # ---- 1. what is withheld, by slot
    print("\n=== 1. WHAT IS WITHHELD, by slot class ===")
    print("    rate = withheld / (withheld + released); unreadable excluded")
    print(f"{'slot':18s} {'wh':>5s} {'rel':>6s} {'unrd':>5s} {'rate':>6s}  "
          f"dominant exemptions")
    agg = collections.defaultdict(
        lambda: {"w": 0, "r": 0, "u": 0, "codes": collections.Counter()})
    for lab, f in fields.items():
        a = agg[slot_of(lab)]
        a["w"] += f["WITHHELD"]; a["r"] += f["RELEASED"]
        a["u"] += f["UNREADABLE"]; a["codes"].update(f["codes"])
    for k, a in sorted(agg.items(), key=lambda x: -x[1]["w"]):
        d = a["w"] + a["r"]
        rate = f"{a['w']/d:6.2f}" if d else "    --"
        tops = ", ".join(f"{c} {n}" for c, n in a["codes"].most_common(2)) or "-"
        print(f"{k:18s} {a['w']:5d} {a['r']:6d} {a['u']:5d} {rate}  {tops}")

    # ---- 2. calibration against the releasing authority's own code
    print("\n=== 2. CALIBRATION against the releasing authority's own code ===")
    print("    NARRATIVE and UNCLASSIFIED_SLOT are CONTAINERS, not content")
    print("    classes -- a redaction inside free prose has no inferable slot,")
    print("    so they are excluded from scoring rather than scored as wrong.")
    ag = dis = un = skip = 0
    conf = collections.Counter()
    for r in rows:
        if r["slot"] in ("NARRATIVE", "UNCLASSIFIED_SLOT"):
            skip += len(r["codes"])
            continue
        for c in r["codes"]:
            exp = CODE_EXPECT.get(c)
            if exp is None:
                un += 1
                continue
            if r["slot"] in exp:
                ag += 1
            else:
                dis += 1
                conf[(c, r["slot"])] += 1
    sc = ag + dis
    if sc:
        print(f"  scored tokens : {sc}   (unscored code: {un}, "
              f"container slot: {skip})")
        print(f"  slot CONSISTENT with the cited exemption : {ag} ({ag/sc:.1%})")
        print(f"  inconsistent                             : {dis} ({dis/sc:.1%})")
        for (c, s), n in conf.most_common(6):
            print(f"    {c:12s} on {s:18s} {n:4d}")

    # ---- 3. inconsistent fields
    print("\n=== 3. INCONSISTENTLY WITHHELD -- withheld in some docs, "
          "released in others ===")
    print("    the released instances bound the value domain of the withheld ones")
    inc = [(l, f) for l, f in fields.items()
           if f["WITHHELD"] >= 2 and f["RELEASED"] >= 2]
    inc.sort(key=lambda x: -min(x[1]["WITHHELD"], x[1]["RELEASED"]))
    print(f"  {'wh':>3} {'rel':>4}  {'slot':15s} {'label':32s} released values")
    for lab, f in inc[:24]:
        vals = sorted(set(f["released_vals"]))[:4]
        print(f"  {f['WITHHELD']:>3} {f['RELEASED']:>4}  {slot_of(lab):15s} "
              f"{lab[:32]:32s} {'; '.join(v[:22] for v in vals)[:58]}")
    print(f"\n  inconsistently withheld fields: {len(inc)} of {len(fields)}")

    # ---- 4. categorically protected
    print("\n=== 4. CATEGORICALLY PROTECTED -- never once released ===")
    cat = [(l, f) for l, f in fields.items()
           if f["RELEASED"] == 0 and f["WITHHELD"] >= 3]
    cat.sort(key=lambda x: -x[1]["WITHHELD"])
    print(f"  {'wh':>3} {'unrd':>5}  {'slot':15s} label")
    for lab, f in cat[:24]:
        print(f"  {f['WITHHELD']:>3} {f['UNREADABLE']:>5}  {slot_of(lab):15s} "
              f"{lab[:46]}")
    print(f"\n  categorically protected fields (>=3 withheld, 0 released): "
          f"{len(cat)}")

    os.makedirs(OUT, exist_ok=True)
    json.dump({"n_texts": len(raw), "n_forms": len(forms),
               "n_parsed": len(parsed), "n_canonical_labels": len(canon),
               "totals": tot,
               "slots": {k: {"withheld": a["w"], "released": a["r"],
                             "unreadable": a["u"], "codes": dict(a["codes"])}
                         for k, a in agg.items()},
               "calibration": {"agree": ag, "disagree": dis, "unscored": un,
                               "container_skipped": skip,
                               "disagreements": {f"{c}|{s}": n
                                                 for (c, s), n in conf.items()}},
               "fields": {l: {"withheld": f["WITHHELD"],
                              "released": f["RELEASED"],
                              "unreadable": f["UNREADABLE"],
                              "empty": f["EMPTY"],
                              "portion_marks": f["PORTION_MARK"],
                              "slot": slot_of(l),
                              "n_docs": len(f["docs"]),
                              "codes": dict(f["codes"]),
                              "released_vals":
                                  sorted(set(f["released_vals"]))[:12]}
                          for l, f in fields.items()},
               "instances": rows},
              open(f"{OUT}/redaction_slots.json", "w"), indent=1)
    print(f"\nwrote {OUT}/redaction_slots.json")


if __name__ == "__main__":
    main()
