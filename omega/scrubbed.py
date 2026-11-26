"""Document-gap and redaction analysis of the PURSUE release.

Three questions, each answerable from the release itself:
  1. Which published documents carry no extractable text, and is that an
     archival artifact (image-only scan) or a withholding?
  2. Are there gaps in the agency ID sequences?  A gap means a document number
     was assigned and the document was not published.
  3. How much of the published text is redacted, and under which FOIA exemption?

A gap is reported as a gap.  It is not reported as a suppression: ID sequences
routinely skip for mundane reasons (merged exhibits, withdrawn duplicates,
numbers reserved and unused).  What the analysis gives is the list to ask about.
"""
import os, re, json, collections, statistics, sys

SP = "/tmp/claude-0/-home-user/f0aebeb3-1b62-5042-9067-46af83ba9a9d/scratchpad/omega/pursue"
META = f"{SP}/pursue_meta.json"
TXT = f"{SP}/txt"

# agency-prefixed document IDs used by the release
# No trailing \b: "_" is a word character, so IDs followed by "_" (e.g.
# CIA-UAP-D020_Memorandum) would not match and vanished from the sequences.
IDRX = re.compile(r"(DOW|DoW|DOD|CIA|DOE|DOS|NASA|ODNI|FAA|NOAA|DIA|NSA|USAF)"
                  r"[-_ ]?UAP[-_ ]?([A-Z]{0,3})[-_ ]?(\d{1,4})", re.I)

REDACT = {
    "bracket_redacted": re.compile(r"\[\s*(?:REDACTED|DELETED|WITHHELD|EXEMPT|EXCISED)[^\]]{0,40}\]", re.I),
    "foia_exemption":   re.compile(r"\(\s*b\s*\)\s*\(\s*([1-9])\s*\)"),
    "block_glyphs":     re.compile(r"[█▓▒░■▬]{3,}"),
    "withheld_phrase":  re.compile(r"WITHHELD\s+IN\s+(?:FULL|PART)|DENIED\s+IN\s+(?:FULL|PART)|"
                                   r"NOT\s+RELEASABLE|RELEASED\s+IN\s+PART", re.I),
    "classif_strip":    re.compile(r"\b(?:SECRET|CONFIDENTIAL|TOP\s*SECRET)\b"),
}
# OCR-garble proxy: fraction of alpha tokens that are not plausible words
_TOKA = re.compile(r"[A-Za-z]{2,}")
def garble(txt):
    ts = _TOKA.findall(txt)
    if len(ts) < 50: return None
    bad = sum(1 for t in ts if not re.match(r"^[A-Za-z]+$", t)
              or (len(t) > 3 and not re.search(r"[aeiouAEIOU]", t)))
    return bad / len(ts)

def load_meta():
    m = json.load(open(META, encoding="utf-8-sig"))
    files = m["files"]
    by_fmt = collections.defaultdict(list)
    for f in files: by_fmt[f.get("format", "?")].append(f["name"])
    return m, by_fmt

def stem(name):
    """Strip archive.org derivative suffixes to get the source document stem."""
    n = name
    for suf in ("_djvu.txt", "_chocr.html.gz", "_hocr.html", "_djvu.xml",
                "_hocr_pageindex.json.gz", "_hocr_searchtext.txt.gz",
                "_jp2.zip", "_page_numbers.json", "_scandata.xml",
                "_text.pdf", "_meta.json", ".pdf", ".jpg", ".jpeg"):
        if n.endswith(suf): n = n[:-len(suf)]; break
    return n

def main():
    m, by_fmt = load_meta()
    R = {"source": m["metadata"].get("source"), "identifier": m["metadata"]["identifier"]}

    # ---------------------------------------------------- 1. OCR coverage
    textpdf = set(stem(n) for n in by_fmt.get("Text PDF", []))
    imgpdf  = set(stem(n) for n in by_fmt.get("Image Container PDF", []))
    addlpdf = set(stem(n) for n in by_fmt.get("Additional Text PDF", []))
    ocr     = set(stem(n) for n in by_fmt.get("DjVuTXT", []))
    jpg     = set(stem(n) for n in by_fmt.get("JPEG", []))
    allpdf  = textpdf | imgpdf | addlpdf
    no_ocr  = sorted(allpdf - ocr)
    R["ocr_coverage"] = {
        "text_pdf": len(textpdf), "image_only_pdf": len(imgpdf),
        "additional_text_pdf": len(addlpdf), "jpeg": len(jpg),
        "distinct_pdfs": len(allpdf), "with_ocr": len(allpdf & ocr),
        "without_ocr": len(no_ocr),
        "image_only_without_ocr": len(sorted(imgpdf - ocr)),
        "text_pdf_without_ocr": len(sorted(textpdf - ocr)),
        "without_ocr_list": no_ocr,
    }
    print("=== 1. OCR COVERAGE ===")
    for k, v in R["ocr_coverage"].items():
        if k != "without_ocr_list": print(f"  {k:26s} {v}")
    print(f"  --- documents with no extractable text ({len(no_ocr)}) ---")
    for n in no_ocr[:40]: print(f"    {n}")

    # ---------------------------------------------------- 2. ID sequence gaps
    # Three conventions in the release break naive sequence parsing, and all three
    # produced false gaps on the first pass.  They are handled explicitly:
    #   CIA  switched from CIA-UAP-018 to CIA-UAP-D020 mid-series -> one series.
    #   NASA runs two independent series: D1..D7 (Apollo/Skylab) and D015..D022
    #        (Gemini, zero-padded).  Treated separately.
    #   DOW-UAP-PR is a sparse parallel series (PR20, PR130, PR131 only), not a
    #        dense sequence; span-based gap counting is meaningless for it.
    SPARSE = {"DOW-UAP-PR"}                 # report presence, never gaps
    MERGE  = {"CIA-UAP-": "CIA-UAP", "CIA-UAP-D": "CIA-UAP"}
    ids = collections.defaultdict(set)
    for f in m["files"]:                     # the COMPLETE manifest, not PDFs only
        for mm in IDRX.finditer(f["name"]):
            agency = mm.group(1).upper(); sub = mm.group(2).upper(); num = int(mm.group(3))
            key = f"{agency}-UAP-{sub}"
            key = MERGE.get(key, key)
            if key == "NASA-UAP-D":          # split the two NASA series
                key = "NASA-UAP-D(Apollo)" if num <= 7 else "NASA-UAP-D(Gemini)"
            ids[key].add(num)
    print("\n=== 2. ID SEQUENCE GAPS (full manifest; naming conventions reconciled) ===")
    seqs = {}
    for k in sorted(ids):
        s = sorted(ids[k])
        sparse = k in SPARSE
        lo, hi = s[0], s[-1]
        missing = [] if (sparse or len(s) < 3) else [i for i in range(lo, hi + 1) if i not in ids[k]]
        runs = []
        for i in missing:
            if runs and i == runs[-1][-1] + 1: runs[-1].append(i)
            else: runs.append([i])
        seqs[k] = {"n_present": len(s), "min": lo, "max": hi, "sparse_series": sparse,
                   "n_missing": len(missing), "missing": missing,
                   "longest_run": max((len(r) for r in runs), default=0),
                   "runs_ge_3": [r for r in runs if len(r) >= 3],
                   "density": None if sparse else len(s) / (hi - lo + 1)}
        tag = "  [sparse parallel series - gaps not meaningful]" if sparse else ""
        print(f"  {k:22s} present={len(s):4d}  range={lo}-{hi}  missing={len(missing):4d}"
              f"{'' if sparse else f'  density={len(s)/(hi-lo+1):.3f}'}{tag}")
        if missing:
            print(f"      MISSING: {missing}")
            for r in seqs[k]["runs_ge_3"]:
                print(f"      RUN OF {len(r)}: {r[0]}-{r[-1]}")
    R["id_sequences"] = seqs

    # ---------------------------------------------------- 3. redaction in text
    print("\n=== 3. REDACTION MARKERS IN OCR TEXT ===")
    files = sorted(f for f in os.listdir(TXT) if f.endswith(".txt")) if os.path.isdir(TXT) else []
    per = {}; agg = collections.Counter(); aggdocs = collections.Counter()
    exempt = collections.Counter()
    shorts = []; garbles = []
    for f in files:
        txt = open(os.path.join(TXT, f), encoding="utf-8", errors="replace").read()
        d = {}
        for k, rx in REDACT.items():
            hits = rx.findall(txt)
            if hits:
                d[k] = len(hits); agg[k] += len(hits); aggdocs[k] += 1
                if k == "foia_exemption": exempt.update(hits)
        g = garble(txt)
        if g is not None: garbles.append((f, g))
        if len(txt) < 1500: shorts.append((f, len(txt)))
        if d: per[f] = {"chars": len(txt), **d}
    for k in REDACT:
        print(f"  {k:18s} docs={aggdocs[k]:4d}  occurrences={agg[k]:7d}")
    print(f"  FOIA exemptions cited: " + ", ".join(f"(b)({e})={n}" for e, n in sorted(exempt.items())))
    R["redaction"] = {"per_doc": per, "aggregate": dict(agg), "docs_with": dict(aggdocs),
                      "foia_exemptions": dict(exempt), "n_scanned": len(files)}

    # ---------------------------------------------------- 4. short / garbled
    garbles.sort(key=lambda x: -x[1])
    gv = [g for _, g in garbles]
    print(f"\n=== 4. TEXT QUALITY ({len(files)} OCR files scanned) ===")
    if gv:
        print(f"  OCR garble fraction: median={statistics.median(gv):.4f} "
              f"p90={sorted(gv)[int(.9*len(gv))]:.4f} max={max(gv):.4f}")
        print("  worst 10:")
        for f, g in garbles[:10]: print(f"    {g:.4f}  {f[:90]}")
    print(f"  documents under 1500 chars: {len(shorts)}")
    for f, n in sorted(shorts, key=lambda x: x[1])[:15]: print(f"    {n:6d}  {f[:90]}")
    R["text_quality"] = {"garble_median": statistics.median(gv) if gv else None,
                         "garble_worst": garbles[:25],
                         "short_docs": sorted(shorts, key=lambda x: x[1])}

    os.makedirs("data/processed/scrubbed", exist_ok=True)
    json.dump(R, open("data/processed/scrubbed/scrubbed_content_report.json", "w"), indent=1)
    print("\nwrote data/processed/scrubbed/scrubbed_content_report.json")

if __name__ == "__main__":
    main()
