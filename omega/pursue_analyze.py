"""PURSUE corpus analysis: what is actually in the Department of War release.

286 of 298 server-side OCR files (18 MB) from archive.org mirror
`pursue-uap-documents-2026`, whose metadata `source` field is
https://www.war.gov/UFO/. Official public disclosure material.
"""
from __future__ import annotations
import sys, os, re, json, collections, math
sys.path.insert(0, "/home/user/UFOAI/omega")
import corpus

TXT = "/tmp/claude-0/-home-user/f0aebeb3-1b62-5042-9067-46af83ba9a9d/scratchpad/omega/pursue/txt"
OUT = "/home/user/UFOAI/data/processed/pursue"

# ---- extraction patterns
DTG   = re.compile(r"\b(\d{6})[:Z]?\d{0,2}Z?([A-Z]{3})(\d{2})\b")          # 281732:00ZOCT25
DATE1 = re.compile(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2}),?\s+(19|20)(\d{2})\b")
MRN   = re.compile(r"\bMRN:\s*(\d{2}\s+[A-Z ]+\d+)")
DOCID = re.compile(r"\b((?:DOW|CIA|DOE|FBI|NASA|DOS|USN|USAF)-UAP-D\d{3,4})\b")
LATLON= re.compile(r"\b(\d{1,2})[^\d\w]{0,3}(\d{1,2})[^\d\w]{0,3}(\d{1,2})?\s*([NS])[,\s]+"
                   r"(\d{1,3})[^\d\w]{0,3}(\d{1,2})[^\d\w]{0,3}(\d{1,2})?\s*([EW])\b")
DECDEG= re.compile(r"\b(-?\d{1,2}\.\d{3,6})[,\s]+(-?\d{1,3}\.\d{3,6})\b")
MGRS  = re.compile(r"\b\d{1,2}[C-X][A-Z]{2}\d{6,10}\b")
CLASS = re.compile(r"\((?:[SU]|TS|SECRET|UNCLASSIFIED|CONFIDENTIAL)(?://[A-Z/ ]+)?\)|"
                   r"\b(?:SECRET|CONFIDENTIAL|UNCLASSIFIED|TOP SECRET)\b(?://[A-Z/]+)?")
PHYS  = {
 "sample/specimen":  r"\bsampl\w*|specimen|swab|aliquot",
 "soil/ground":      r"\bsoil\b|ground\s+sample|sediment|regolith",
 "material/debris":  r"\bdebris|fragment|material\s+(recovered|retrieved|analys)|residue|slag",
 "biologic":         r"\bbiolog\w*|tissue|\bDNA\b|cadaver|corpse|remains|autops",
 "radiolog":         r"\bradiolog\w*|radioactiv\w*|radiation\s+(level|reading|survey)|dosimet",
 "lab analysis":     r"\blaborator\w*|spectro\w*|mass\s+spec|metallurg|assay|chain\s+of\s+custody",
 "recovery/retrieval": r"\bretriev\w*|recover\w*\s+(operation|team|effort)|crash\s+(site|retriev)",
}
PRX = {k: re.compile(v, re.I) for k, v in PHYS.items()}
UAPTERM = re.compile(r"\bUAP\b|unidentified\s+(anomalous|aerial|flying)|\bUFO\b", re.I)

def dms(d, m, s, h):
    v = int(d) + int(m)/60 + (int(s)/3600 if s else 0)
    return -v if h in ("S", "W") else v

def main():
    os.makedirs(OUT, exist_ok=True)
    files = sorted(os.listdir(TXT))
    docs = []
    for fn in files:
        s = open(os.path.join(TXT, fn), encoding="utf-8", errors="replace").read()
        rel = fn.split("__")[0]
        coords = []
        for m in LATLON.finditer(s):
            try:
                la = dms(m.group(1), m.group(2), m.group(3), m.group(4))
                lo = dms(m.group(5), m.group(6), m.group(7), m.group(8))
                if -90 <= la <= 90 and -180 <= lo <= 180 and not (la == 0 and lo == 0):
                    coords.append((round(la, 5), round(lo, 5), "dms"))
            except Exception: pass
        for m in DECDEG.finditer(s):
            try:
                la, lo = float(m.group(1)), float(m.group(2))
                if -90 <= la <= 90 and -180 <= lo <= 180 and abs(la) > 0.5 and abs(lo) > 0.5:
                    coords.append((round(la, 5), round(lo, 5), "decimal"))
            except Exception: pass
        years = sorted({int(m.group(3)+m.group(4)) for m in DATE1.finditer(s)})
        docs.append(dict(
            file=fn, release=rel, nchar=len(s),
            doc_ids=sorted({m.group(1) for m in DOCID.finditer(s)}),
            mrn=sorted({m.group(1).strip() for m in MRN.finditer(s)})[:4],
            years=years[:12],
            n_dtg=len(DTG.findall(s)),
            n_mgrs=len(MGRS.findall(s)),
            coords=coords[:12], n_coords=len(coords),
            class_markings=len(CLASS.findall(s)),
            uap_mentions=len(UAPTERM.findall(s)),
            physical={k: len(rx.findall(s)) for k, rx in PRX.items() if rx.search(s)},
        ))
    print("=" * 86)
    print(f"PURSUE CORPUS: {len(docs)} OCR'd documents, "
          f"{sum(d['nchar'] for d in docs)/1e6:.1f} M characters")
    byrel = collections.Counter(d["release"] for d in docs)
    print(f"  by release: {dict(sorted(byrel.items()))}")
    print(f"  documents mentioning UAP/UFO: {sum(1 for d in docs if d['uap_mentions'])}")
    print(f"  documents with classification markings: {sum(1 for d in docs if d['class_markings'])}")
    print(f"  documents with DTG timestamps: {sum(1 for d in docs if d['n_dtg'])}")
    print(f"  documents with MGRS grid refs: {sum(1 for d in docs if d['n_mgrs'])}")
    print(f"  documents with parseable coordinates: {sum(1 for d in docs if d['n_coords'])}"
          f"  (total coords extracted: {sum(d['n_coords'] for d in docs)})")
    allyears = collections.Counter(y for d in docs for y in d["years"])
    print(f"\n  year mentions, most common: "
          f"{[(y,n) for y,n in allyears.most_common(12)]}")

    print("\n" + "=" * 86)
    print("PHYSICAL-EVIDENCE LANGUAGE ACROSS THE RELEASE")
    pc = collections.Counter()
    for d in docs:
        for k in d["physical"]: pc[k] += 1
    print(f"  {'category':<22}{'documents':>11}{'share':>8}")
    for k, v in pc.most_common():
        print(f"  {k:<22}{v:>11}{v/len(docs)*100:>7.1f}%")
    bio = [d for d in docs if "biologic" in d["physical"]]
    print(f"\n  documents with BIOLOGIC language: {len(bio)}")
    for d in sorted(bio, key=lambda x: -x['physical']['biologic'])[:8]:
        print(f"    {d['physical']['biologic']:>3} hits  {d['release']:<12} "
              f"{d['file'].split('__')[-1][:58]}")

    # ---- cross-reference extracted coordinates against the catalog
    mc = json.load(open("/home/user/UFOAI/data/processed/provenance/master_catalog_inclusive.json"))
    cat = [e for e in mc["events"] if e["lat"] is not None]
    allc = [(c[0], c[1], d["file"]) for d in docs for c in d["coords"]]
    print("\n" + "=" * 86)
    print(f"COORDINATE CROSS-REFERENCE  ({len(allc)} PURSUE coordinates vs "
          f"{len(cat)} geocoded catalog events)")
    if allc:
        import numpy as np
        from scipy.spatial import cKDTree
        import phase2
        cx = phase2.ecef(np.array([e["lat"] for e in cat]), np.array([e["lon"] for e in cat]))
        tree = cKDTree(cx)
        px = phase2.ecef(np.array([c[0] for c in allc]), np.array([c[1] for c in allc]))
        dd, ii = tree.query(px, k=1)
        gc = 2*phase2.R_E*np.arcsin(np.clip(dd/(2*phase2.R_E), 0, 1))
        for band in (10, 25, 50, 100, 250):
            print(f"    PURSUE coords within {band:>4} km of a catalog event: "
                  f"{int((gc<=band).sum())} ({(gc<=band).mean()*100:.1f}%)")
        print(f"    median distance to nearest catalog event: {np.median(gc):.1f} km")
        print("\n  CLOSEST 12 MATCHES (PURSUE coordinate -> catalog event)")
        order = np.argsort(gc)[:12]
        for k in order:
            e = cat[ii[k]]
            print(f"    {gc[k]:>7.2f} km  PURSUE {allc[k][0]:>9.4f},{allc[k][1]:>10.4f}  "
                  f"[{allc[k][2].split('__')[-1][:34]}]  <->  {e['year']} "
                  f"{(e['location'] or '?')[:26]}")
    json.dump(dict(n_docs=len(docs), docs=docs), open(f"{OUT}/pursue_extraction.json", "w"), indent=1)
    print(f"\n  wrote {OUT}/pursue_extraction.json")

if __name__ == "__main__":
    main()
