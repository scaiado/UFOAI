"""PROJECT OMEGA - Phase 1: the provenance collapse.

Matching rule (calibrated, see omega/reports/phase1_calibration.md):
  REQUIRED: date compatible (tol by precision; +/-1d modern day-prec,
            +/-31d month-prec, +/-1y pre-1900 or year-prec)
  VETO:     both geocoded and > GEO_KM apart
  EVIDENCE  (any one sufficient):
    T1 both geocoded within GEO_KM                       (geo identity)
    T2 place-name token overlap AND any text support      (place identity)
    T3 one side has no place info AND text support >= mid (text identity)
    T4 place names conflict AND text support >= high      (text overrides)
Transitive closure is guarded: components are split if not geo/date cohesive.
"""
from __future__ import annotations
import sys, os, re, json, math, collections, random
import numpy as np
sys.path.insert(0, "/home/user/UFOAI/omega")
import corpus, dedupe

GEO_KM_MODERN = 150.0
GEO_KM_ANCIENT = 400.0

def text_support(p):
    """Graded text-evidence level: 0 none, 1 weak, 2 mid, 3 high."""
    cos, jac, nrare, ninter = p["cos"], p["jac"], p["nrare"], p["ninter"]
    if cos >= 0.45 or jac >= 0.35 or nrare >= 8: return 3
    if cos >= 0.20 or jac >= 0.15 or nrare >= 4: return 2
    if cos >= 0.09 or jac >= 0.05 or nrare >= 2 or ninter >= 4: return 1
    return 0

MODE = "strict"   # "strict" | "inclusive"

def decide(recs, p):
    """Calibrated on an 80-pair adjudicated development sample.

    Cross-catalog pairs achieved 42/45 = 93% precision under the tiered rule;
    SAME-catalog pairs achieved only 4/35 = 11%, because a catalog compiler has
    already deduplicated their own list -- two entries in one catalog are
    presumptively two distinct reports. Duplication is a cross-catalog
    phenomenon, so intra-catalog merging requires near-identical text.
    """
    a, b = recs[p["i"]], recs[p["j"]]
    ts = text_support(p)
    # aggregate row vs specific event: only vetoed when the date is coarse.
    # (A mass sighting is often written up as an aggregate by one compiler and
    # as a specific report by another -- Lubbock Lights, New Delhi 1951.)
    if a.summary != b.summary and not (a.prec == "day" and b.prec == "day"):
        return (False, "summary_mismatch", ts)
    if a.catalog == b.catalog:
        # strict intra-catalog rule: same section-duplicate style entries only
        if p["cos"] >= 0.60 and p["jac"] >= 0.40 and (a._lt & b._lt):
            return (True, "T0_intra_strict", ts)
        return (False, "intra_reject", ts)
    both_geo = a.lat is not None and b.lat is not None
    if both_geo:
        lim = GEO_KM_ANCIENT if (a.year or 2000) < 1900 or (b.year or 2000) < 1900 else GEO_KM_MODERN
        dkm = corpus.haversine(a.lat, a.lon, b.lat, b.lon)
        if dkm > lim: return (False, "geo_veto", ts)
        return (True, "T1_geo", ts)
    ta, tb = a._lt, b._lt
    if ta and tb:
        shared = ta & tb
        if shared:
            spec = dedupe.specific_tokens(shared)
            if spec and a.prec == "day" and b.prec == "day":
                # same calendar day + a shared settlement/installation name.
                # Measured base rate: such a collision occurs in 2.31% of
                # WITHIN-catalog same-day pairs but 12.15% of CROSS-catalog
                # ones (5.3x), so ~81% of these pairs are duplications.
                if MODE == "inclusive":
                    return (True, "T2a_place_specific", ts)
                return ((ts >= 1), "T2a_place_specific", ts)
            return ((ts >= 1), "T2b_place_coarse", ts)
        return ((ts >= 3), "T4_textoverride", ts)
    return ((ts >= 2), "T3_text", ts)

def cohesive(recs, members):
    """Cluster-level sanity: geo spread and date spread within limits."""
    pts = [(recs[m].lat, recs[m].lon) for m in members if recs[m].lat is not None]
    if len(pts) >= 2:
        lim = GEO_KM_ANCIENT if any((recs[m].year or 2000) < 1900 for m in members) else GEO_KM_MODERN
        for x in range(len(pts)):
            for y in range(x + 1, len(pts)):
                if corpus.haversine(pts[x][0], pts[x][1], pts[y][0], pts[y][1]) > lim * 1.5:
                    return False
    js = [corpus.to_jdn(recs[m].year, recs[m].month, recs[m].day) for m in members if recs[m].year]
    if js and (max(js) - min(js)) > 400: return False
    return True

def split_component(recs, members, pairset):
    """Complete-linkage style split of a non-cohesive component."""
    out = []
    pool = list(members)
    while pool:
        seed = pool.pop(0); grp = [seed]
        changed = True
        while changed:
            changed = False
            for m in list(pool):
                if all(((min(m, g), max(m, g)) in pairset) for g in grp) and cohesive(recs, grp + [m]):
                    grp.append(m); pool.remove(m); changed = True
        out.append(grp)
    return out

# ----------------------------------------------------- reference normalization
_REFNORM = [
    (r"project\s*blue\s*book|bluebook|\bbbu?\b|\bbb\b", "PROJECT_BLUEBOOK"),
    (r"\bnicap\b", "NICAP"), (r"\bapro\b", "APRO"), (r"\bmufon\b", "MUFON"),
    (r"\bcufos\b|center for ufo studies", "CUFOS"), (r"\bnuforc\b", "NUFORC"),
    (r"\bcondon\b", "CONDON"), (r"\bvall[eé]e\b|magonia|wonders in the sky", "VALLEE"),
    (r"hynek", "HYNEK"), (r"keyhoe", "KEYHOE"), (r"\brr0\b", "RR0"),
    (r"\bfbi\b", "FBI"), (r"\bcia\b", "CIA"), (r"\busaf\b|air force", "USAF"),
    (r"new york times|nytimes", "NYT"), (r"newspaper|gazette|tribune|herald|times|post|journal|press", "NEWSPAPER"),
    (r"flying saucer review|\bfsr\b", "FSR"), (r"\bufo evidence\b", "UFOEVIDENCE"),
    (r"dolan", "DOLAN"), (r"eberhart", "EBERHART"), (r"johnson", "JOHNSON"),
    (r"hatch|\bu\b db|udb", "HATCH"), (r"overmeire", "OVERMEIRE"),
    (r"\bapolog|agobard", "AGOBARD"), (r"archive\.org", "ARCHIVE"),
    (r"wikipedia", "WIKIPEDIA"), (r"findagrave", "FINDAGRAVE"),
]
def norm_ref(t):
    s = re.sub(r"\s+", " ", str(t).lower())
    for pat, key in _REFNORM:
        if re.search(pat, s): return key
    m = re.match(r"^[_\*\s]*([a-z][a-z\s\.\-']{3,40})", s)
    if m: return "SRC:" + re.sub(r"[^a-z]", "", m.group(1))[:18].upper()
    return None

def run(mode="strict"):
    global MODE
    MODE = mode
    random.seed(1337)
    recs, ner = corpus.load_all()
    n = len(recs)
    print(f"[p1] mode={MODE} records={n}", flush=True)
    X, vec, cand = dedupe.build(recs, cos_floor=0.05, verbose=False)
    n_text = len(cand)
    pd_cand = dedupe.place_date_candidates(recs, X)
    seen = {(min(i, j), max(i, j)) for i, j, _ in cand}
    extra = [(i, j, v) for i, j, v in pd_cand if (min(i, j), max(i, j)) not in seen]
    cand = cand + extra
    print(f"[p1] candidates={len(cand)} (text={n_text} +place/date={len(extra)})", flush=True)
    scored, sh = dedupe.score_pairs(recs, cand)
    print(f"[p1] pass date+geo gates={len(scored)}", flush=True)

    accepted = []
    for p in scored:
        ok, tier, ts = decide(recs, p)
        if ok:
            p["tier"] = tier; p["ts"] = ts; accepted.append(p)
    print(f"[p1] accepted pairs={len(accepted)}  tiers="
          f"{dict(collections.Counter(p['tier'] for p in accepted))}", flush=True)

    dsu = dedupe.DSU(n)
    for p in accepted: dsu.union(p["i"], p["j"])
    comps = collections.defaultdict(list)
    for i in range(n): comps[dsu.find(i)].append(i)
    pairset = {(min(p["i"], p["j"]), max(p["i"], p["j"])) for p in accepted}

    clusters, nsplit = [], 0
    for root, members in comps.items():
        if len(members) == 1: clusters.append(members); continue
        if cohesive(recs, members): clusters.append(members)
        else:
            nsplit += 1
            clusters.extend(split_component(recs, members, pairset))
    print(f"[p1] components={len(comps)} non-cohesive_split={nsplit} final_clusters={len(clusters)}", flush=True)

    # ------------------------------------------------- cluster-level provenance
    catyear = {v[0]: v[1] for v in corpus.CATALOG_META.values()}
    out = []
    for cid, members in enumerate(sorted(clusters, key=lambda m: -len(m))):
        cats = sorted({recs[m].catalog for m in members})
        refkeys = collections.Counter()
        for m in members:
            for r in recs[m].refs:
                k = norm_ref(r.get("text", ""))
                if k: refkeys[k] += 1
        yrs = [recs[m].year for m in members if recs[m].year]
        best = min(members, key=lambda m: (recs[m].prec != "day", -len(recs[m].desc)))
        pubyears = [(catyear.get(c, 9999), c) for c in cats]
        pubyears.sort()
        geo = [(recs[m].lat, recs[m].lon) for m in members if recs[m].lat is not None]
        out.append(dict(
            event_id=f"OMEGA-{cid:06d}",
            n_records=len(members),
            catalogs=cats, n_catalogs=len(cats),
            cross_reference_count=len(cats),
            provenance_depth=len(refkeys),
            distinct_sources=sorted(refkeys),
            earliest_catalog=pubyears[0][1] if pubyears else None,
            earliest_catalog_pubyear=pubyears[0][0] if pubyears else None,
            year=recs[best].year, month=recs[best].month, day=recs[best].day,
            date_precision=recs[best].prec, date_raw=recs[best].date_raw,
            lat=geo[0][0] if geo else None, lon=geo[0][1] if geo else None,
            n_geocoded=len(geo),
            location=recs[best].location, country=recs[best].country,
            etype=recs[best].etype,
            attrs=sorted({a for m in members for a in recs[m].attrs}),
            credibility=max([recs[m].credibility for m in members if recs[m].credibility is not None], default=None),
            description=recs[best].desc,
            member_uids=[recs[m].uid for m in members],
            member_source_ids=[f"{recs[m].catalog}:{recs[m].source_id}" for m in members],
            citation_chain=[{"catalog": recs[m].catalog, "source_id": recs[m].source_id,
                             "pubyear": catyear.get(recs[m].catalog), "refs": recs[m].refs[:6]}
                            for m in members],
        ))
    return recs, ner, accepted, scored, out, sh

if __name__ == "__main__":
    import pickle
    mode = sys.argv[1] if len(sys.argv) > 1 else "strict"
    recs, ner, accepted, scored, cat, sh = run(mode)
    os.makedirs("/home/user/UFOAI/data/processed/provenance", exist_ok=True)
    pickle.dump(dict(accepted=accepted, scored=scored, clusters=[c["member_uids"] for c in cat]),
                open(f"/tmp/claude-0/-home-user/f0aebeb3-1b62-5042-9067-46af83ba9a9d/scratchpad/omega/phase1_{mode}.pkl", "wb"))
    suffix = "" if mode == "strict" else f"_{mode}"
    with open(f"/home/user/UFOAI/data/processed/provenance/master_catalog{suffix}.json", "w") as f:
        json.dump({"schema_version": "omega-1.0",
                   "n_input_records": len(recs),
                   "n_independent_events": len(cat),
                   "events": cat}, f, ensure_ascii=False)
    print(f"[p1] WROTE master_catalog.json  events={len(cat)}")
