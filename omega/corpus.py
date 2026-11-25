"""PROJECT OMEGA - corpus loader & normalizer for the ufo_data catalogs.

Normalizes 30 heterogeneous UAP catalogs into one record schema with
parsed dates (with explicit precision), coordinates, and provenance refs.
"""
from __future__ import annotations
import json, os, re, math, unicodedata, hashlib
from dataclasses import dataclass, field, asdict

BIN = "/home/user/ufo_data/bin"

# Publication year of the underlying compilation, used to order citation
# lineages (earliest-source attribution). Sourced from ufo_data/README.md.
CATALOG_META = {
    "ancient.json":            ("WondersInTheSky", 2009, "catalog"),
    "anon_pdf.json":           ("AnonPDF2023",     2023, "catalog"),
    "bb_unknowns.json":        ("BlueBookUnknowns",1969, "military"),
    "dolan.json":              ("Dolan",           2009, "catalog"),
    "eberhart.json":           ("EberhartUFOI",    2022, "catalog"),
    "hatch_udb.json":          ("Hatch_UDB",       2002, "catalog"),
    "hostile.json":            ("HostileFawcett",  1961, "catalog"),
    "johnson.json":            ("Johnson",         2012, "catalog"),
    "magonia.json":            ("Magonia",         1969, "catalog"),
    "maj2.json":               ("Majestic",        2023, "catalog"),
    "mut.json":                ("MysteryHeliAdams",1991, "catalog"),
    "nicap_db.json":           ("NICAP",           1980, "organization"),
    "nuclear_tests.json":      ("NuclearTests",    1996, "reference"),
    "overmeire.json":          ("Overmeire",       2001, "catalog"),
    "rr0.json":                ("rr0",             2023, "catalog"),
    "scully.json":             ("Scully",          1950, "catalog"),
    "trace.json":              ("Trace",           1990, "catalog"),
    "ufo_evidence_hall.json":  ("UFOEvidenceHall", 2003, "catalog"),
}
for i in range(1, 10):
    CATALOG_META[f"pre_roswell_chap{i}.json"] = (f"Rife_ch{i}", 2000, "catalog")

NER_FILES = {"eberhart_openai.json", "openai_results.json"}

@dataclass
class Rec:
    uid: str
    catalog: str          # source catalog file stem
    source: str           # self-reported source tag
    source_id: str
    date_raw: str
    year: int | None = None
    month: int | None = None
    day: int | None = None
    prec: str = "none"    # day|month|year|none
    date_uncertain: bool = False
    lat: float | None = None
    lon: float | None = None
    location: str = ""
    country: str = ""
    desc: str = ""
    norm: str = ""        # normalized description text
    refs: list = field(default_factory=list)
    etype: str = ""
    attrs: list = field(default_factory=list)
    credibility: float | None = None
    duration: str = ""
    kv: dict = field(default_factory=dict)
    summary: bool = False
    places: list = field(default_factory=list)

_YEAR_OK = lambda y: y is not None and -600 <= y <= 2030

def parse_date(s, catalog):
    """Return (year, month, day, precision, uncertain).

    Handles the formats actually present in the corpus:
      '7/16/1945'  m/d/yyyy        '5/21/70'  m/d/yy (Hatch, 1900s)
      '1/840?'     m/yyyy, fuzzy   '4/34'     m/yyyy (ancient, AD 34)
      '812'        yyyy            '1/-1/840' m/d/yyyy with -1 = unknown
      '1954-05'    iso-ish
    """
    if s is None: return (None, None, None, "none", False)
    t = str(s).strip()
    if not t: return (None, None, None, "none", False)
    unc = ("?" in t) or ("c." in t.lower()) or ("ca." in t.lower())
    t = t.replace("?", "").strip()
    t = re.sub(r"\s*\(.*?\)\s*", "", t)
    t = t.replace("-", "/") if re.match(r"^\d{4}/\d{1,2}", t.replace("-", "/")) and t.count("-") and len(t.split("-")[0]) == 4 else t
    parts = [p for p in re.split(r"[/\.\s]+", t) if p not in ("",)]
    nums = []
    for p in parts:
        p2 = p.lstrip("+")
        if re.fullmatch(r"-?\d+", p2): nums.append(int(p2))
    if not nums: return (None, None, None, "none", unc)
    # negative sentinels (-1) mean "unknown component"
    nums = [None if (n is not None and n < 0) else n for n in nums]

    y = m = d = None
    if len(nums) >= 3:
        m, d, y = nums[0], nums[1], nums[2]
        if y is not None and 0 <= y <= 99:
            # 2-digit year: Hatch/NICAP style, 20th century
            y = 1900 + y if y >= 30 else 2000 + y
    elif len(nums) == 2:
        a, b = nums
        if b is not None and b > 31:        # m/yyyy
            m, y = a, b
        elif a is not None and a > 31:      # yyyy/m
            y, m = a, b
        elif b is not None and 0 <= b <= 99 and a is not None and a <= 12:
            m, y = a, (1900 + b if b >= 30 else 2000 + b)
        else:
            y = b
    else:
        y = nums[0]
        if y is not None and 0 <= y <= 99: y = 1900 + y

    if m is not None and not (1 <= m <= 12): m = None
    if d is not None and not (1 <= d <= 31): d = None
    if not _YEAR_OK(y): return (None, None, None, "none", unc)
    prec = "day" if (m and d) else ("month" if m else "year")
    return (y, m, d, prec, unc)

_WS = re.compile(r"\s+")
_MDLINK = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")
_NONWORD = re.compile(r"[^a-z0-9 ]+")
STOP = set("""the a an and or of to in on at from by with for as is was were be been being
that this these those it its he she they them his her their there here then than
over near about into onto up down out off very many some one two three said also
report reported reports sighting sighting s seen saw observed observer observers
case object objects ufo ufos light lights sky am pm""".split())

# catalog-template boilerplate: identical across unrelated entries, so it
# inflates lexical similarity and must be removed before scoring.
BOILER = [
    r"\(\s*nicap\s*:[^)]*\)", r"\(\s*bb\s*:[^)]*\)", r"code\s*:\s*\w+",
    r"rating\s*:\s*\d+", r"\(\s*translated from french\s*\)",
    r"\bnicap\s+ufo\s*e(vidence)?\b", r"\(\s*fufor index\s*\)",
    r"\(\s*mcdonald list[^)]*\)", r"\(\s*nara\s*\)", r"\(\s*nc\s*\)",
    r"\bsection\s+[ivxl]+\b", r"no further details",
    r"\b\d+\s*-\s*(distant|close) encounters\b",
    r"\b(distant|close) encounters\b", r"\beme cases\b", r"\bradar cases\b",
    r"\baviation cases\b", r"\bphotographic cases\b", r"\bentity cases\b",
    r"electro-?magnetic effects", r"malfunctions due to eme",
]
_BOILER_RE = [re.compile(b, re.I) for b in BOILER]

def norm_text(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = _MDLINK.sub(r"\1", s)
    for rx in _BOILER_RE: s = rx.sub(" ", s)
    s = s.lower()
    s = _NONWORD.sub(" ", s)
    toks = [t for t in s.split() if t not in STOP and len(t) > 1]
    return " ".join(toks)

def _refs(r):
    raw = r.get("ref")
    out = []
    if isinstance(raw, str): raw = [raw]
    if isinstance(raw, list):
        for x in raw:
            x = str(x)
            names = _MDLINK.findall(x)
            if names:
                for n, u in names: out.append({"text": _WS.sub(" ", n).strip()[:300], "url": u[:300]})
            else:
                out.append({"text": _WS.sub(" ", x).strip()[:300], "url": ""})
    return out

def _coords(r):
    kv = r.get("key_vals") or {}
    ll = kv.get("LatLong")
    if not ll:
        loc = str(r.get("location") or "")
        if re.fullmatch(r"\s*-?\d+(\.\d+)?\s+-?\d+(\.\d+)?\s*", loc): ll = loc
    if not ll: return (None, None)
    try:
        a, b = str(ll).split()[:2]
        la, lo = float(a), float(b)
        if -90 <= la <= 90 and -180 <= lo <= 180 and not (la == 0 and lo == 0):
            return (la, lo)
    except Exception:
        pass
    return (None, None)

def load_all(bindir=BIN, include_nuclear=False):
    recs, ner = [], {}
    for fn in sorted(os.listdir(bindir)):
        if not fn.endswith(".json"): continue
        path = os.path.join(bindir, fn)
        try:
            data = json.load(open(path, encoding="utf-8-sig"))
        except Exception:
            continue
        if fn in NER_FILES:
            arr = data.get("results", [])
            for r in arr:
                ner[(r.get("event_source"), r.get("event_source_id"))] = {
                    "locations": r.get("locations") or [], "names": r.get("names") or [],
                    "index": r.get("index") or [],
                }
            continue
        if fn not in CATALOG_META: continue
        if fn == "nuclear_tests.json" and not include_nuclear: continue
        cat, _py, _k = CATALOG_META[fn]
        if not (isinstance(data, dict) and len(data) == 1): continue
        arr = list(data.values())[0]
        if not isinstance(arr, list): continue
        for i, r in enumerate(arr):
            if not isinstance(r, dict): continue
            kv = r.get("key_vals") or {}
            y, m, d, prec, unc = parse_date(r.get("date") or r.get("basic_date") or r.get("alt_basic_date"), cat)
            la, lo = _coords(r)
            desc = _WS.sub(" ", str(r.get("desc") or "")).strip()
            sid = str(r.get("source_id") or f"{cat}_{i}")
            cred = kv.get("Credibility")
            try: cred = float(cred) if cred not in (None, "") else None
            except Exception: cred = None
            recs.append(Rec(
                uid=f"{cat}#{i}", catalog=cat, source=str(r.get("source") or cat),
                source_id=sid, date_raw=str(r.get("date") or ""),
                year=y, month=m, day=d, prec=prec, date_uncertain=unc,
                lat=la, lon=lo, location=str(r.get("location") or "")[:200],
                country=str(kv.get("Country") or "")[:60],
                desc=desc[:4000], norm=norm_text(desc),
                refs=_refs(r), etype=str(r.get("type") or ""),
                attrs=[a.split(":")[0] for a in (r.get("attributes") or []) if isinstance(a, str)],
                credibility=cred, duration=str(kv.get("Duration") or ""),
                summary=is_summary(desc),
                places=(places_from_desc(desc) if not str(r.get("location") or "").strip() else []),
                kv={k: v for k, v in kv.items() if k in (
                    "Country","Credibility","Duration","Locale","LatLong","HatchDesc",
                    "NukeY","NukeType","NukeName","NukeCountry","NukeDepth")},
            ))
    return recs, ner

def load_nuclear(bindir=BIN):
    data = json.load(open(os.path.join(bindir, "nuclear_tests.json"), encoding="utf-8-sig"))
    arr = list(data.values())[0]
    out = []
    for i, r in enumerate(arr):
        kv = r.get("key_vals") or {}
        y, m, d, prec, _ = parse_date(r.get("date") or r.get("basic_date"), "NuclearTests")
        la, lo = _coords(r)
        try: yld = float(kv.get("NukeY")) if kv.get("NukeY") not in (None, "") else None
        except Exception: yld = None
        try: depth = float(kv.get("NukeDepth")) if kv.get("NukeDepth") not in (None, "") else None
        except Exception: depth = None
        out.append(dict(uid=f"NUKE#{i}", year=y, month=m, day=d, prec=prec,
                        lat=la, lon=lo, yield_kt=yld, depth_km=depth,
                        ntype=str(kv.get("NukeType") or ""), name=str(kv.get("NukeName") or ""),
                        country=str(kv.get("NukeCountry") or ""), desc=str(r.get("desc") or "")[:300]))
    return out

def to_jdn(y, m, d):
    """Julian day number; tolerates missing m/d by substituting mid-values."""
    if y is None: return None
    mm = m or 7; dd = d or 1
    a = (14 - mm) // 12; yy = y + 4800 - a; mo = mm + 12 * a - 3
    return dd + (153 * mo + 2) // 5 + 365 * yy + yy // 4 - yy // 100 + yy // 400 - 32045

# Aggregate/meta rows ("Sweden recorded over 1,000 ghost rocket sightings")
# describe a class of events, not one event; they must not merge with specifics.
_SUMMARY = re.compile(r"""(recorded\s+(over|more\s+than)|\bover\s+[\d,]{3,}\s|
  a\s+(large\s+)?number\s+of\s+(reports|sightings)|many\s+(reports|sightings)|
  \bwave\s+of\b|\bflap\b|hundreds\s+of|thousands\s+of|
  \b\d{2,3}%\s+of\s+these|total\s+of\s+[\d,]+\s+(reports|sightings|cases))""",
  re.I | re.X)
def is_summary(desc):
    return bool(_SUMMARY.search(str(desc or "")))

# crude but effective place extraction for rows with an empty location field:
# catalog prose almost always names the place in "in X, Y" / "at X, Y" form.
_PLACE = re.compile(r"\b(?:in|at|near|over|from)\s+((?:[A-Z][\w'\-\.]+(?:\s+[A-Z][\w'\-\.]+){0,3})"
                    r"(?:,\s*[A-Z][\w'\-\.]+(?:\s+[A-Z][\w'\-\.]+){0,2}){0,2})")
_PLACE_BAD = set("""The A An On In At And Or But He She They It This That There Then When While
Mr Mrs Ms Dr Capt Lt Col Gen Sgt Maj Rev Prof USAF US USA UFO UFOs Air Force Navy Army
According Later Soon After Before During Both One Two Three Four Five Six Seven Eight Nine Ten
January February March April May June July August September October November December
French English German Spanish Italian Russian Translated Source Note Ref See Image
Monday Tuesday Wednesday Thursday Friday Saturday Sunday Project Operation""".split())
def places_from_desc(desc, limit=3):
    out = []
    txt = str(desc or "")
    for rx in _BOILER_RE: txt = rx.sub(" ", txt)   # strip "(Translated from French)" etc
    for m in _PLACE.finditer(txt[:600]):
        cand = m.group(1).strip(" .,;")
        head = cand.split(",")[0].split()[0]
        if head in _PLACE_BAD: continue
        if len(cand) < 3: continue
        out.append(cand)
        if len(out) >= limit: break
    return out

R_EARTH = 6371.0088
def haversine(la1, lo1, la2, lo2):
    p = math.pi / 180.0
    dla = (la2 - la1) * p; dlo = (lo2 - lo1) * p
    h = math.sin(dla / 2) ** 2 + math.cos(la1 * p) * math.cos(la2 * p) * math.sin(dlo / 2) ** 2
    return 2 * R_EARTH * math.asin(math.sqrt(min(1.0, h)))
