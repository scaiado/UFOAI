"""Scrubbed-content detection across the PURSUE release.

Three measurable things, and one that is NOT measurable from text:

  1. NUMBERING GAPS -- documents absent from an otherwise continuous
     agency/series sequence.
  2. IMAGE-ONLY DOCUMENTS -- stems with page images but no text derivative, so
     their content is invisible to every text-based analysis in this project.
  3. CLASSIFICATION AND EXEMPTION MARKINGS -- what the release says about its
     own withholdings.

  NOT MEASURABLE FROM TEXT: redaction EXTENT. Section 1.7 established that
  withholdings are applied to the page IMAGE, so OCR returns nothing and leaves
  no marker -- a fully blacked-out paragraph and a blank margin are identical in
  the text layer. Measuring extent requires the JP2 page images; see
  omega/jp2_redaction.py.

ID-PARSING DISCIPLINE. Section 1.7 records that three of four gap findings in an
earlier session were artefacts of this project's own parser: a trailing `\\b`
failing on `_` (underscore is a word character, so the boundary never fires),
CIA's mid-series convention change CIA-UAP-018 -> CIA-UAP-D020, NASA's two
parallel series D1-D7 and D015-D032, and DOW-UAP-PR being sparse parallel
numbering. I reproduced the `\\b` bug AGAIN this session while looking for the
DIRDs and got zero hits for 37 documents that are plainly there. So:

  * boundaries are `(?![0-9])`, never `\\b`
  * every series is reported with its OBSERVED numbering style
  * a gap inside a series that mixes styles is reported as SUSPECT, not as a gap
"""
import json, os, re, sys, collections

SP = os.environ.get("OMEGA_SCRATCH", "")
META = f"{SP}/uap/pursue_meta.json"
OUT = "evidence_vault/05_SCRUBBED_CONTENT"

# agency-prefix, optional D, number -- the D is optional because CIA and NASA
# both change convention mid-series.
IDRX = re.compile(r"\b((?:DOW|CIA|DOE|DOS|NASA|ODNI|FBI|USG|DIA)-UAP)-(PR-?)?(D?)(\d{1,4})(?![0-9])")
SUFFIX = re.compile(r"(_djvu\.txt|_jp2\.zip|\.pdf|_text\.pdf|_chocr\.html\.gz|_hocr\.html|"
                    r"_page_numbers\.json|_djvu\.xml|_scandata\.xml|_hocr_pageindex\.json\.gz|"
                    r"_hocr_searchtext\.txt\.gz|_abbyy\.gz|_orig_jp2\.tar|_text_pdfmeta\.json|"
                    r"_imgonly_pdfmeta\.json|_imgonly)$")

# The archive LABELS its own image-only documents: the derivative is named
# `<stem>_imgonly_pdfmeta.json`. That is a direct marker and far better than
# inferring image-only status from a missing text derivative, which conflates
# "no text was extracted" with "no derivative was generated yet".
IMGONLY = re.compile(r"_imgonly")

MARKINGS = {
    "banner_TS":  re.compile(r"\bTOP\s*SECRET\b", re.I),
    "banner_S":   re.compile(r"(?<!\w)SECRET(?!\w)"),
    "banner_C":   re.compile(r"\bCONFIDENTIAL\b", re.I),
    "portion_TS": re.compile(r"\(TS(?://[A-Z/]+)?\)"),
    "portion_S":  re.compile(r"\(S(?://[A-Z/]+)?\)"),
    "portion_C":  re.compile(r"\(C\)"),
    "portion_U":  re.compile(r"\(U\)"),
    "foia_b1":    re.compile(r"\(b\)\s*\(1\)"),
    "foia_b3":    re.compile(r"\(b\)\s*\(3\)"),
    "foia_b5":    re.compile(r"\(b\)\s*\(5\)"),
    "foia_b6":    re.compile(r"\(b\)\s*\(6\)"),
    "foia_b7":    re.compile(r"\(b\)\s*\(7\)"),
    "cav_NOFORN": re.compile(r"\bNOFORN\b|\bNOT RELEASABLE TO FOREIGN\b", re.I),
    "cav_FOUO":   re.compile(r"\bFOR OFFICIAL USE ONLY\b|\bFOUO\b", re.I),
    "cav_ORCON":  re.compile(r"\bORCON\b|\bORIGINATOR CONTROLLED\b", re.I),
    "cav_SCI":    re.compile(r"\bSI\b//|\bTK\b//|\bHCS\b|\bSCI\b"),
    "cav_BYEMAN": re.compile(r"\bBYEMAN\b", re.I),
    "redact_mark": re.compile(r"\[REDACTED\]|\[DELETED\]|\bREDACTED\b", re.I),
    "decl_date":  re.compile(r"\bDECLASSIFI(?:ED|CATION)\b", re.I),
}


def main():
    if not os.path.exists(META):
        print(f"manifest not found: {META}\nset OMEGA_SCRATCH", file=sys.stderr)
        sys.exit(2)
    os.makedirs(OUT, exist_ok=True)
    m = json.load(open(META))
    names = [f["name"] for f in m["files"] if "/" in f["name"]]
    stems = sorted({SUFFIX.sub("", n) for n in names})

    # ---------- derivative coverage per document stem -------------------
    have = collections.defaultdict(set)
    for n in names:
        st = SUFFIX.sub("", n)
        if n.endswith("_djvu.txt"):
            have[st].add("txt")
        elif n.endswith("_jp2.zip"):
            have[st].add("jp2")
        elif n.endswith(".pdf") and "_text" not in n:
            have[st].add("pdf")

    # Declared image-only, from the archive's own naming.
    declared_imgonly = sorted({SUFFIX.sub("", n) for n in names if IMGONLY.search(n)})
    # Inferred: has page images but no text derivative.
    img_only = sorted(set(declared_imgonly) |
                      {s for s in stems if "jp2" in have[s] and "txt" not in have[s]})
    no_deriv = sorted(s for s in stems if not have[s])

    # ---------- series parsing ------------------------------------------
    series = collections.defaultdict(dict)   # (agency, style) -> {num: stem}
    unparsed = []
    for s in stems:
        base = s.split("/")[-1]
        mt = IDRX.search(base)
        if not mt:
            unparsed.append(s)
            continue
        agency, pr, d, raw = mt.group(1), mt.group(2), mt.group(3), mt.group(4)
        num = int(raw)
        # Width is part of the style. Section 1.7 records NASA running D1-D7 and
        # D015-D032 as two parallel series; collapsing the padding invents a
        # gap at 8-14 that is really the boundary between them. I reproduced
        # that artefact before adding this.
        # ZERO-PADDING distinguishes series; MAGNITUDE does not. D3, D10 and
        # D100 are one sequence counting upward, so splitting on digit width
        # shattered DOW-UAP-D into four fake series. D017 vs D17 is a real
        # convention difference; D17 vs D170 is not.
        pad = "pad%d" % len(raw) if raw.startswith("0") else "bare"
        style = ("PR" if pr else "") + ("D" if d else "bare") + ":" + pad
        series[(agency, style)][num] = s

    report = {"stems": len(stems), "image_only": img_only,
              "no_derivatives": no_deriv, "unparsed_ids": unparsed, "series": {}}

    print(f"document stems: {len(stems)}")
    print(f"image-only (page images, NO text derivative): {len(img_only)}")
    print(f"no derivatives at all: {len(no_deriv)}")
    print(f"unparsed IDs: {len(unparsed)}")
    print()
    print("=== SERIES, with observed numbering style ===")
    print(f"  {'series':<22}{'style':<12}{'n':>5}{'min':>6}{'max':>6}{'gaps':>6}  note")
    agencies = collections.defaultdict(list)
    for (agency, style), d in sorted(series.items()):
        agencies[agency].append(style)
    for (agency, style), d in sorted(series.items()):
        nums = sorted(d)
        lo, hi = nums[0], nums[-1]
        missing = [i for i in range(lo, hi + 1) if i not in d]
        mixed = len(agencies[agency]) > 1
        note = "SUSPECT: agency mixes styles " + "/".join(agencies[agency]) if mixed else ""
        print(f"  {agency:<22}{style:<12}{len(d):>5}{lo:>6}{hi:>6}{len(missing):>6}  {note}")
        report["series"][f"{agency}|{style}"] = {
            "n": len(d), "min": lo, "max": hi, "missing": missing,
            "density": round(len(d) / (hi - lo + 1), 4),
            "agency_styles": sorted(agencies[agency]),
            "verdict": "SUSPECT_MIXED_STYLE" if mixed else "CLEAN_SINGLE_STYLE",
        }

    # ---------- agency-level UNION, which is the defensible question ----
    # "Was document N released?" does not care whether the number was written
    # D17 or D017. Per-style series are diagnostic (they expose convention
    # changes); the UNION is what a gap claim must rest on. A number counts as
    # missing only if NO style in that agency has it. PR is excluded: section
    # 1.7 established DOW-UAP-PR is sparse PARALLEL numbering, not part of the
    # main sequence, so folding it in would invent gaps.
    # WHEN IS A UNION VALID? Two styles in one agency mean one of two things,
    # and they demand opposite treatment:
    #
    #   OVERLAPPING number ranges -> a CONVENTION CHANGE mid-series (CIA wrote
    #     CIA-UAP-018 then switched to CIA-UAP-D020). The union is correct and
    #     merging removes fake gaps.
    #   DISJOINT number ranges -> two PARALLEL series (NASA runs D1-D7 and
    #     D015-D032 as separate sequences). The union is WRONG: merging invents
    #     a gap across the empty span between them, which is exactly the 8-14
    #     artefact section 1.7 caught.
    #
    # So overlap is tested before merging, and disjoint agencies are reported
    # per-series instead.
    bystyle = collections.defaultdict(list)
    for (agency, style), d in series.items():
        if style.startswith("PR"):
            continue
        bystyle[agency].append((style, d))
    union, parallel = collections.defaultdict(dict), {}
    for agency, lst in bystyle.items():
        spans = [(min(d), max(d)) for _, d in lst]
        disjoint = all(a2 > b1 or b2 < a1
                       for i, (a1, b1) in enumerate(spans)
                       for j, (a2, b2) in enumerate(spans) if i < j) and len(spans) > 1
        if disjoint:
            parallel[agency] = [(st, min(d), max(d), sorted(d)) for st, d in lst]
        else:
            for _, d in lst:
                union[agency].update(d)
    print()
    print("=== AGENCY UNION (all numbering styles merged, PR excluded) ===")
    print(f"  {'agency':<12}{'n':>5}{'min':>6}{'max':>6}{'missing':>9}{'density':>9}  longest runs")
    report["union"] = {}
    for agency, d in sorted(union.items()):
        nums = sorted(d)
        lo, hi = nums[0], nums[-1]
        miss = [i for i in range(lo, hi + 1) if i not in d]
        runs, cur = [], None
        for x in miss:
            if cur and x == cur[-1] + 1:
                cur.append(x)
            else:
                cur = [x]; runs.append(cur)
        runs.sort(key=len, reverse=True)
        pretty = ", ".join(f"{r[0]}-{r[-1]}" if len(r) > 1 else str(r[0])
                           for r in runs[:6]) or "-"
        print(f"  {agency:<12}{len(d):>5}{lo:>6}{hi:>6}{len(miss):>9}"
              f"{len(d)/(hi-lo+1):>9.3f}  {pretty}")
        report["union"][agency] = {
            "n": len(d), "min": lo, "max": hi, "missing": miss,
            "density": round(len(d) / (hi - lo + 1), 4),
            "longest_runs": [[r[0], r[-1]] for r in runs[:10]],
        }

    if parallel:
        print()
        print("=== PARALLEL SERIES (disjoint ranges -- union would invent gaps) ===")
        report["parallel_series"] = {}
        for agency, lst in sorted(parallel.items()):
            for st, lo, hi, nums in sorted(lst):
                miss = [i for i in range(lo, hi + 1) if i not in set(nums)]
                print(f"  {agency:<12}{st:<12}{len(nums):>4} docs  D{lo}-D{hi}"
                      f"  missing {miss if miss else '-'}")
                report["parallel_series"][f"{agency}|{st}"] = {
                    "n": len(nums), "min": lo, "max": hi, "missing": miss}
        print("  (the span BETWEEN these series is not a gap -- it is the boundary)")

    print()
    print("=== GAPS in single-style series only (diagnostic) ===")
    for k, v in sorted(report["series"].items()):
        if v["verdict"] != "CLEAN_SINGLE_STYLE" or not v["missing"]:
            continue
        runs, cur = [], [v["missing"][0]]
        for x in v["missing"][1:]:
            if x == cur[-1] + 1:
                cur.append(x)
            else:
                runs.append(cur); cur = [x]
        runs.append(cur)
        runs.sort(key=len, reverse=True)
        pretty = ", ".join(f"{r[0]}-{r[-1]}" if len(r) > 1 else str(r[0]) for r in runs[:8])
        print(f"  {k:<28} {len(v['missing'])} missing of {v['max']-v['min']+1}"
              f"  density {v['density']:.3f}")
        print(f"       longest runs: {pretty}")

    # ---------- markings over the text corpus ---------------------------
    roots = [f"{SP}/uap/djvu", "data/raw/pursue_ocr/txt"]
    tally = collections.defaultdict(lambda: {"docs": 0, "hits": 0})
    ndoc = 0
    for r in roots:
        if not os.path.isdir(r):
            continue
        for f in sorted(os.listdir(r)):
            if not f.endswith(".txt"):
                continue
            t = open(os.path.join(r, f), encoding="utf-8", errors="replace").read()
            ndoc += 1
            for k, rx in MARKINGS.items():
                n = len(rx.findall(t))
                if n:
                    tally[k]["docs"] += 1
                    tally[k]["hits"] += n
    print()
    print(f"=== MARKINGS over {ndoc} text documents ===")
    print(f"  {'marking':<16}{'docs':>6}{'hits':>8}")
    for k in sorted(tally, key=lambda x: -tally[x]["docs"]):
        print(f"  {k:<16}{tally[k]['docs']:>6}{tally[k]['hits']:>8}")
    report["markings"] = {k: dict(v) for k, v in tally.items()}
    report["markings_corpus_docs"] = ndoc

    json.dump(report, open(f"{OUT}/numbering_gaps.json", "w"), indent=1)
    json.dump({"image_only": img_only, "no_derivatives": no_deriv},
              open(f"{OUT}/image_only_docs/index.json", "w"), indent=1)
    print(f"\nwrote {OUT}/numbering_gaps.json")


if __name__ == "__main__":
    main()
