"""Extract witness-level text from harvested GEIPAN dossiers.

The C-vs-D test on `Détails` is unidentifiable (HANDOFF section 1.4, failure
mode #7): that field is analyst prose written after classification, and the leak
changes form at every decontamination tier without plateauing.

The dossiers hold material written BEFORE or INDEPENDENT of the verdict:

  * gendarmerie procès-verbaux   -- "PV", "PV AERO", "PV n°..."
  * investigation reports        -- "Compte rendu enquête", "Enquête", "Rapport"
  * witness instruments          -- "Questionnaire", "Témoignage", "Audition"
  * laboratory analyses          -- "Analyse", "Expertise"

Those are police and lab documents. The analyst-verdict leak channels
(verdict sentence, verdict lexicon, conjugated analyst verbs such as
`manquons`, cause nouns) are structurally absent from them.

Extraction is two-stage because many dossier PDFs are image-only scans:
pdftotext first, then tesseract -l fra at 300 dpi when the text layer is thin.
"""
import os, re, sys, json, subprocess, collections

DOCS = "data/raw/geipan/docs"
OUT = "data/processed/geipan_pv"
MIN_TEXT = 200          # chars below which a PDF is treated as image-only
OCR_DPI = "300"

# Document-class patterns, matched against the filename.
CLASSES = [
    ("pv",            re.compile(r"\bP[\s_]*V\b|proces|procès", re.I)),
    ("enquete",       re.compile(r"enqu[eê]te|compte[\s_]*rendu|\bCR\b|rapport", re.I)),
    ("questionnaire", re.compile(r"questionnaire|t[eé]moignage|audition|declaration|déclaration", re.I)),
    ("analyse",       re.compile(r"analyse|expertise|labo|mesure", re.I)),
    ("photo",         re.compile(r"photo|dessin|croquis|image|scan|plan", re.I)),
]
WITNESS_CLASSES = {"pv", "enquete", "questionnaire"}


def doc_class(fn):
    for name, rx in CLASSES:
        if rx.search(fn):
            return name
    return "other"


def pdftotext(path):
    try:
        r = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", path, "-"],
                           capture_output=True, text=True, errors="replace",
                           timeout=180)
        return r.stdout or ""
    except Exception:
        return ""


def ocr(path, tmpdir):
    """Rasterise then OCR in French. Returns text, or '' on failure."""
    base = os.path.join(tmpdir, "pg")
    try:
        subprocess.run(["pdftoppm", "-r", OCR_DPI, "-gray", "-png", path, base],
                       capture_output=True, timeout=1200, check=False)
        pages = sorted(f for f in os.listdir(tmpdir) if f.startswith("pg"))
        out = []
        for p in pages:
            r = subprocess.run(["tesseract", os.path.join(tmpdir, p), "stdout",
                                "-l", "fra", "--psm", "1"],
                               capture_output=True, text=True, errors="replace",
                               timeout=600)
            out.append(r.stdout or "")
            os.remove(os.path.join(tmpdir, p))
        return "\n".join(out)
    except Exception:
        return ""


def main():
    log = json.load(open("data/raw/geipan/harvest_log.json", encoding="utf-8"))
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, "_tmp")
    os.makedirs(tmp, exist_ok=True)

    recs = []
    stats = collections.Counter()
    cids = [c for c, v in log.items() if v.get("n")]
    print(f"cases with files: {len(cids)}", flush=True)

    for i, cid in enumerate(cids, 1):
        v = log[cid]
        cdir = os.path.join(DOCS, cid)
        if not os.path.isdir(cdir):
            continue
        for fn in sorted(os.listdir(cdir)):
            path = os.path.join(cdir, fn)
            kls = doc_class(fn)
            stats[f"file:{kls}"] += 1
            if not fn.lower().endswith(".pdf"):
                stats["skip:not_pdf"] += 1
                continue
            cache = os.path.join(OUT, f"{cid}__{fn}.txt")
            if os.path.exists(cache):
                txt = open(cache, encoding="utf-8", errors="replace").read()
                meth = "cache"
            else:
                txt = pdftotext(path)
                meth = "pdftotext"
                if len(txt.strip()) < MIN_TEXT:
                    o = ocr(path, tmp)
                    if len(o.strip()) > len(txt.strip()):
                        txt, meth = o, "ocr"
                open(cache, "w", encoding="utf-8").write(txt)
            stats[f"method:{meth}"] += 1
            recs.append({"cid": cid, "arm": v["arm"], "year": v.get("year"),
                         "title": v.get("title"), "file": fn, "cls": kls,
                         "method": meth, "chars": len(txt.strip()),
                         "witness": kls in WITNESS_CLASSES})
        if i % 10 == 0:
            print(f"  [{i}/{len(cids)}] docs={len(recs)}", flush=True)

    json.dump(recs, open("data/processed/geipan_pv/index.json", "w"),
              indent=1, ensure_ascii=False)

    print("\n=== extraction summary ===")
    for k in sorted(stats):
        print(f"  {k:<24}{stats[k]:>6}")
    wit = [r for r in recs if r["witness"] and r["chars"] >= MIN_TEXT]
    print(f"\n  usable witness-level docs: {len(wit)}")
    byarm = collections.Counter(r["arm"] for r in wit)
    print(f"  by arm: {dict(byarm)}")
    cases = collections.defaultdict(set)
    for r in wit:
        cases[r["arm"]].add(r["cid"])
    print(f"  distinct cases with usable witness text: "
          f"{ {k: len(v) for k, v in cases.items()} }")
    tot = sum(r["chars"] for r in wit)
    print(f"  total witness chars: {tot:,}")


if __name__ == "__main__":
    main()
