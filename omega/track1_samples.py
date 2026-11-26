"""TRACK 1: retained-sample chain-of-custody database.

346 events carry Hatch's SMP code -- "Sampling of plant/animal/soil/tissue/
specimens" -- meaning material was collected AT THE TIME. Archived material is
far more likely to be assayable than 60-year-old in-situ soil, and it carries
chain of custody a fresh dig never will.

SCOPE LIMIT, stated up front: whether a given sample is still EXTANT cannot be
determined from this corpus or from any host reachable here (CUFOS, APRO,
GEPAN/SEPRA, university archives are all unreachable). This builds the
catalog-derived half: what was collected, where, when, by whom where named,
which organisation the citation chain points to, and what analysis the record
mentions. The extant/custody columns are explicitly marked UNVERIFIED and are
the researcher's contact list, not an assessment.
"""
from __future__ import annotations
import sys, json, re, csv, collections
sys.path.insert(0, "/home/user/UFOAI/omega")
import corpus

MC = "/home/user/UFOAI/data/processed/provenance/master_catalog_inclusive.json"
OUT = "/home/user/UFOAI/data/processed/soil_assay"

# Organisations that historically held UAP physical material, matched against
# the citation chain and description text.
ORGS = {
 "APRO": r"\bAPRO\b|Aerial Phenomena Research",
 "NICAP": r"\bNICAP\b",
 "CUFOS": r"\bCUFOS\b|Center for UFO Studies|Hynek",
 "MUFON": r"\bMUFON\b",
 "Project Blue Book": r"blue\s*book|\bBBU?\b|Project 10073",
 "GEPAN/SEPRA/GEIPAN": r"\bGEPAN\b|\bSEPRA\b|GEIPAN|CNES",
 "FSR": r"Flying Saucer Review|\bFSR\b",
 "LDLN": r"Lumi[eè]res dans la Nuit|\bLDLN\b",
 "USAF/military": r"\bUSAF\b|Air Force|\bAFB\b|military investigat",
 "university/lab": r"universit|laborator|institute of tech|\bNASA\b|analys(is|ed|is was)\s+by",
 "police/gendarmerie": r"police|sheriff|gendarmerie|constab",
}
ORX = {k: re.compile(v, re.I) for k, v in ORGS.items()}

SAMPLE_TYPE = {
 "soil":       r"\bsoil|earth\s+sample|dirt|sand\s+sample|ground\s+sample",
 "vegetation": r"\bplant|grass|crop|vegetation|stem|leaf|leaves|wheat|corn|tree",
 "metal/residue": r"\bmetal|fragment|residue|slag|molten|sliver|shard|magnesium|alloy",
 "oily/chemical": r"\boily|oil\s|substance|liquid|chemical|deposit",
 "radiation reading": r"radiation|radioactiv|geiger|counts?\s+per|roentgen|millirem",
 "biological/tissue": r"\btissue|blood|organ|animal\s+sample|carcass",
 "water": r"\bwater\s+sample|pond|lake\s+sample",
 "photographic": r"\bphotograph|film|negative|plate",
}
SRX = {k: re.compile(v, re.I) for k, v in SAMPLE_TYPE.items()}

ANALYSIS_DONE = {
 "analysed (unspecified)": r"analys|assay|tested|examin(ed|ation)\s+by|laboratory",
 "spectrograph/spectro":  r"spectrograph|spectrometr|spectral analysis|mass\s+spec",
 "metallurgical":          r"metallurg|microscop|crystallograph|x-?ray diffract",
 "radiological":           r"radiation\s+(was|were)?\s*(measured|detected)|geiger|counts per",
 "botanical":              r"botan|cell|chlorophyll|node|germinat",
 "no analysis mentioned":  r"^$",
}
ARX = {k: re.compile(v, re.I) for k, v in ANALYSIS_DONE.items() if k != "no analysis mentioned"}

# Named priority cases, matched on date+place rather than asserted from memory.
NAMED = {
 "Socorro / Zamora":      (1964, 4, r"Socorro"),
 "Valensole / Masse":     (1965, 7, r"Valensole"),
 "Delphos":               (1971, 11, r"Delphos"),
 "Trans-en-Provence":     (1981, 1, r"Trans-en-Provence|Trans en Provence"),
 "Rosedale":              (1980, 9, r"Rosedale"),
 "Cash-Landrum":          (1980, 12, r"Dayton|Huffman|Cash"),
 "Delphos ring":          (1971, 11, r"Delphos"),
}

def main():
    import os
    os.makedirs(OUT, exist_ok=True)
    ev = json.load(open(MC))["events"]
    rows = []
    # WIDENED CRITERION. The SMP code alone misses canonical sampled cases:
    # Delphos 1971 and Trans-en-Provence 1981 -- the best-instrumented trace
    # case in the literature, with actual GEPAN laboratory analysis -- carry
    # DRT/LND/TRC/VEG but NOT SMP. Cash-Landrum carries only RDA/TRC. So SMP
    # does not reliably track "material was collected" and the SMP-only set is
    # an undercount. Criterion widened to: SMP, or a physical-substrate code
    # (DRT soil/dirt, TRC traces, VEG plants, RDA radiation) accompanied by
    # evidence in the text that something was taken, measured or analysed.
    TOOK = re.compile(r"\bsampl|collect|took\s+(a|some|soil|samples)|gathered|"
                      r"analys|assay|laborator|tested|examined by|sent to|"
                      r"measured|geiger|counts per|residue|fragment", re.I)
    SUBSTRATE = {"DRT","TRC","VEG","RDA","SMP"}
    for e in ev:
        attrs = set(e["attrs"] or [])
        if "SMP" not in attrs:
            if not (attrs & SUBSTRATE): continue
            if not TOOK.search(e["description"] or ""): continue
        d = e["description"] or ""
        chain = " ".join(
            (r.get("text","") + " " + r.get("url",""))
            for c in e["citation_chain"] for r in c.get("refs", []))
        hay = d + " " + chain + " " + " ".join(e["catalogs"])
        orgs = [k for k, rx in ORX.items() if rx.search(hay)]
        stypes = [k for k, rx in SRX.items() if rx.search(d)]
        anal = [k for k, rx in ARX.items() if rx.search(d)]
        # named-case flag, matched not asserted
        named = None
        for nm, (yy, mm, pat) in NAMED.items():
            if e["year"] == yy and re.search(pat, (e["location"] or "") + " " + d, re.I):
                named = nm; break
        # collector: a capitalised personal name adjacent to a collection verb
        mcol = re.search(r"\b([A-Z][a-z]+(?:\s+[A-Z]\.)?\s+[A-Z][a-z]+)\b[^.]{0,60}"
                         r"\b(collect|took|gathered|removed|sampled|dug)", d)
        rows.append(dict(
            event_id=e["event_id"],
            named_case=named,
            date=f"{e['year']:04d}-{e['month'] or 0:02d}-{e['day'] or 0:02d}",
            lat=e["lat"], lon=e["lon"],
            location=e["location"] or "", country=e["country"] or "",
            n_catalogs=e["n_catalogs"], provenance_depth=e["provenance_depth"],
            credibility=e["credibility"],
            sample_types=stypes or ["unspecified"],
            custodian_candidates=orgs or ["UNKNOWN - no organisation in the citation chain"],
            analysis_mentioned=anal or ["none mentioned in the record"],
            collector_named=mcol.group(1) if mcol else None,
            trace_codes=[c for c in e["attrs"] if c in
                         ("SMP","TRC","DRT","VEG","ANI","RDA","LND","INJ","SUB")],
            extant_status="UNVERIFIED - requires contact with the custodian archive",
            custody_status="UNVERIFIED - requires archive accession records",
            modern_assay_feasible="UNKNOWN until extant status established",
            description=d[:400],
            catalogs=e["catalogs"],
        ))
    # priority score: what the catalog can actually support
    for r in rows:
        s = 0.0
        s += 3.0 * len([t for t in r["sample_types"] if t != "unspecified"])
        s += 2.5 if any("metal" in t or "residue" in t for t in r["sample_types"]) else 0
        s += 2.0 * len([a for a in r["analysis_mentioned"] if "none" not in a])
        s += 2.0 if r["collector_named"] else 0
        s += 1.5 * len([o for o in r["custodian_candidates"] if "UNKNOWN" not in o])
        s *= 1.0 + 0.15 * min(r["n_catalogs"] - 1, 6)
        s *= 1.0 + 0.04 * min(r["provenance_depth"], 10)
        if r["named_case"]: s += 10.0
        r["priority_score"] = round(s, 2)
    rows.sort(key=lambda r: -r["priority_score"])
    json.dump(dict(n=len(rows), scope_limit=(
        "extant/custody/assay columns are UNVERIFIED; the archives that would "
        "settle them (CUFOS, APRO, GEPAN/SEPRA, university collections) are not "
        "reachable from this environment"), samples=rows),
        open(f"{OUT}/retained_sample_custody.json", "w"), indent=1)
    with open(f"{OUT}/retained_sample_custody.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rank","event_id","named_case","date","lat","lon","location","country",
                    "n_catalogs","provenance_depth","credibility","sample_types",
                    "custodian_candidates","analysis_mentioned","collector_named",
                    "priority_score","extant_status"])
        for i, r in enumerate(rows, 1):
            w.writerow([i, r["event_id"], r["named_case"] or "", r["date"], r["lat"], r["lon"],
                        r["location"], r["country"], r["n_catalogs"], r["provenance_depth"],
                        r["credibility"], "|".join(r["sample_types"]),
                        "|".join(r["custodian_candidates"]), "|".join(r["analysis_mentioned"]),
                        r["collector_named"] or "", r["priority_score"], r["extant_status"]])
    print(f"[t1] candidate sampled events (widened criterion): {len(rows)}")
    print(f"[t1]   of which SMP-coded: {sum(1 for r in rows if 'SMP' in r['trace_codes'])}")
    print(f"[t1]   recovered by widening: {sum(1 for r in rows if 'SMP' not in r['trace_codes'])}")
    print(f"[t1] wrote retained_sample_custody.{{json,csv}}")
    print(f"\n  custodian candidates identified from citation chains:")
    co = collections.Counter(o for r in rows for o in r["custodian_candidates"])
    for k, v in co.most_common(): print(f"    {k:<48}{v:>5}")
    print(f"\n  sample types:")
    cs = collections.Counter(t for r in rows for t in r["sample_types"])
    for k, v in cs.most_common(): print(f"    {k:<24}{v:>5}")
    print(f"\n  analysis mentioned in the record:")
    ca = collections.Counter(a for r in rows for a in r["analysis_mentioned"])
    for k, v in ca.most_common(): print(f"    {k:<28}{v:>5}")
    print(f"\n  collector named in the record: {sum(1 for r in rows if r['collector_named'])}"
          f" of {len(rows)}")
    print(f"  named priority cases matched: {sum(1 for r in rows if r['named_case'])}")
    print(f"\n  TOP 15 BY PRIORITY SCORE")
    print(f"  {'#':>3}{'score':>7}  {'date':<11}{'named':<20}{'types':<34}{'custodians'}")
    for i, r in enumerate(rows[:15], 1):
        print(f"  {i:>3}{r['priority_score']:>7.1f}  {r['date']:<11}"
              f"{(r['named_case'] or '-')[:19]:<20}"
              f"{'|'.join(r['sample_types'])[:33]:<34}"
              f"{'|'.join(c for c in r['custodian_candidates'] if 'UNKNOWN' not in c)[:40]}")

if __name__ == "__main__":
    main()
