"""Extract witness-level text from harvested GEIPAN dossiers. ONE pipeline.

The C-vs-D test on `Détails` is unidentifiable (HANDOFF section 1.4, failure
mode #7): that field is analyst prose written AFTER classification, and the leak
changes form at every decontamination tier without plateauing.  The dossiers
hold material written BEFORE or INDEPENDENT of the verdict -- gendarmerie
procès-verbaux, enquête reports, witness questionnaires.

WHY EVERYTHING IS RE-OCR'd, AND THE EMBEDDED TEXT LAYER IGNORED
---------------------------------------------------------------
GEIPAN's dossier PDFs are MIXED.  Measured on this corpus:

  * 1951-1954 procès-verbaux carry NO text layer at all (0 tokens) -- pure
    image scans.
  * A 1993 PV carries 12,548 characters of embedded text, but of poor quality:
    "CROQUIS DE L'ÉTAT DES LIEUX" renders as "C R O Q U I S  D E  L 'E'I'A'i'".

So text-layer availability CORRELATES WITH ERA.  And D cases skew older
(section 1.3: the D-rate runs 0.0548 in the 1970s against 0.0155 in the 2010s).
A "pdftotext first, OCR only if short" rule would therefore run TWO DIFFERENT
TEXT PIPELINES, split along a line correlated with the class label -- which is
structurally the same defect as the cross-pipeline geocoding convergence that
falsified the persistence result in section 6.  A classifier could then
separate the arms on OCR characteristics rather than witness content.

Therefore: every document goes through tesseract -l fra at 300 dpi, and the
embedded layer is never used as text.  It is still extracted, but only as a
DIAGNOSTIC, so the correlation above can be reported rather than assumed.

A per-document quality score is stored so the test can check, as a premise,
that text quality does not differ between arms.
"""
import os, re, sys, json, glob, shutil, tempfile, subprocess, collections
import concurrent.futures as cf

# Tesseract links OpenMP and spawns a thread per core BY DEFAULT.  With N
# worker processes that is N*cores threads on `cores` cores, and the contention
# is catastrophic: measured on one 2480x3507 page of this corpus, 3 workers at
# the default gave 31,647 ms/page, and OMP_THREAD_LIMIT=1 gave 2,090 ms/page
# for BYTE-IDENTICAL output (1,222 chars both ways).  A 15x speedup, which
# takes this corpus from ~8.3 h to ~35 min.  Parallelism belongs at the
# process level here, not inside tesseract.
OCR_ENV = dict(os.environ, OMP_THREAD_LIMIT="1")

DOCS = "data/raw/geipan/docs"
OUT = "data/processed/geipan_pv"
OCR_DPI = "300"
# each tesseract is single-threaded now, so use every core
WORKERS = max(2, os.cpu_count() or 4)

CLASSES = [
    ("pv",            re.compile(r"\bP[\s_]*V\b|proces|procès", re.I)),
    ("enquete",       re.compile(r"enqu[eê]te|compte[\s_]*rendu|\bCR\b|rapport", re.I)),
    ("questionnaire", re.compile(r"questionnaire|t[eé]moignage|audition|declaration|déclaration", re.I)),
    ("analyse",       re.compile(r"analyse|expertise|labo|mesure", re.I)),
    ("photo",         re.compile(r"photo|dessin|croquis|image|scan|plan", re.I)),
]
WITNESS_CLASSES = {"pv", "enquete", "questionnaire"}

# French function words: a real French page hits many of these.
FR = set("""le la les un une des du de et est sont a au aux dans sur pour par avec
sans sous ce cette ces il elle ils elles nous vous je tu on que qui quoi dont ou
mais donc or ni car ne pas plus moins tres tout tous toute toutes meme aussi
alors apres avant pendant depuis vers chez entre lors ainsi cela celui celle
etait etaient ete avoir etre fait faire dit vu observe observation phenomene
lumiere ciel nuit heure minutes environ temoin gendarmerie brigade proces verbal
declaration monsieur madame commune departement""".split())
TOK = re.compile(r"[A-Za-zÀ-ÿ]+")


def quality(t):
    toks = [w.lower() for w in TOK.findall(t or "")]
    if len(toks) < 20:
        return {"n_tok": len(toks), "frac1": 0.0, "fr_frac": 0.0, "score": 0.0}
    one = sum(1 for w in toks if len(w) == 1) / len(toks)
    fr = sum(1 for w in toks if w in FR) / len(toks)
    return {"n_tok": len(toks), "frac1": round(one, 4),
            "fr_frac": round(fr, 4), "score": round(fr - one, 4)}


def doc_class(fn):
    for name, rx in CLASSES:
        if rx.search(fn):
            return name
    return "other"


def embedded(path):
    """Diagnostic only -- never used as the analysed text."""
    try:
        r = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", path, "-"],
                           capture_output=True, text=True, errors="replace",
                           timeout=180)
        return r.stdout or ""
    except Exception:
        return ""


def ocr(path):
    td = tempfile.mkdtemp(prefix="geipan_ocr_")
    try:
        subprocess.run(["pdftoppm", "-r", OCR_DPI, "-gray", "-png",
                        path, os.path.join(td, "p")],
                       capture_output=True, timeout=2400)
        out = []
        for png in sorted(glob.glob(os.path.join(td, "p*.png"))):
            r = subprocess.run(["tesseract", png, "stdout", "-l", "fra", "--psm", "1"],
                               capture_output=True, text=True, errors="replace",
                               timeout=600, env=OCR_ENV)
            out.append(r.stdout or "")
            os.remove(png)
        return "\n".join(out), len(out)
    except Exception as e:
        return "", 0
    finally:
        shutil.rmtree(td, ignore_errors=True)


def job(task):
    cid, arm, year, title, fn = task
    path = os.path.join(DOCS, cid, fn)
    cache = os.path.join(OUT, f"{cid}__{fn}.txt")
    emb_cache = os.path.join(OUT, "_embedded", f"{cid}__{fn}.txt")
    if os.path.exists(cache):
        txt = open(cache, encoding="utf-8", errors="replace").read()
        npg, meth = -1, "cache"
    else:
        txt, npg = ocr(path)
        meth = "ocr"
        open(cache, "w", encoding="utf-8").write(txt)
    if not os.path.exists(emb_cache):
        os.makedirs(os.path.dirname(emb_cache), exist_ok=True)
        open(emb_cache, "w", encoding="utf-8").write(embedded(path))
    emb = open(emb_cache, encoding="utf-8", errors="replace").read()
    q, qe = quality(txt), quality(emb)
    return {"cid": cid, "arm": arm, "year": year, "title": title, "file": fn,
            "cls": doc_class(fn), "method": meth, "pages": npg,
            "witness": doc_class(fn) in WITNESS_CLASSES,
            "chars": len(txt.strip()), "q": q,
            "embedded_tok": qe["n_tok"], "embedded_score": qe["score"]}


def main():
    log = json.load(open("data/raw/geipan/harvest_log.json", encoding="utf-8"))
    os.makedirs(OUT, exist_ok=True)
    tasks = []
    for cid, v in log.items():
        if not v.get("n"):
            continue
        for fn in v["files"]:
            if not fn.lower().endswith(".pdf"):
                continue
            if doc_class(fn) not in WITNESS_CLASSES:
                continue
            tasks.append((cid, v["arm"], v.get("year"), v.get("title"), fn))
    print(f"witness-class PDFs to OCR: {len(tasks)}  workers: {WORKERS}", flush=True)

    recs = []
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for i, r in enumerate(ex.map(job, tasks), 1):
            recs.append(r)
            if i % 20 == 0:
                print(f"  [{i}/{len(tasks)}] "
                      f"ok={sum(1 for x in recs if x['chars']>200)}", flush=True)

    json.dump(recs, open(f"{OUT}/index.json", "w"), indent=1, ensure_ascii=False)

    print("\n=== EXTRACTION SUMMARY ===")
    print(f"  documents           : {len(recs)}")
    usable = [r for r in recs if r["chars"] >= 200 and r["q"]["n_tok"] >= 40]
    print(f"  usable (>=200ch, >=40tok): {len(usable)}")
    byarm = collections.Counter(r["arm"] for r in usable)
    print(f"  usable docs by arm  : {dict(byarm)}")
    cases = collections.defaultdict(set)
    for r in usable:
        cases[r["arm"]].add(r["cid"])
    print(f"  CASES with usable witness text: "
          f"{ {k: len(v) for k, v in cases.items()} }")
    print(f"  total chars         : {sum(r['chars'] for r in usable):,}")

    print("\n=== PREMISE: does text quality differ between arms? ===")
    for a in ("D", "C"):
        s = [r["q"]["score"] for r in usable if r["arm"] == a]
        t = [r["q"]["n_tok"] for r in usable if r["arm"] == a]
        if s:
            s_sorted = sorted(s)
            print(f"  {a}: n={len(s)}  median quality={s_sorted[len(s)//2]:.4f}  "
                  f"mean={sum(s)/len(s):.4f}  median tokens={sorted(t)[len(t)//2]}")

    print("\n=== DIAGNOSTIC: embedded text layer vs era (the reason for one pipeline) ===")
    era = collections.defaultdict(lambda: [0, 0])
    for r in recs:
        try:
            d = (int(str(r["year"])[:4]) // 10) * 10
        except (TypeError, ValueError):
            continue
        era[d][0] += 1
        if r["embedded_tok"] >= 20:
            era[d][1] += 1
    for d in sorted(era):
        n, hasl = era[d]
        print(f"  {d}s: {hasl}/{n} documents carry an embedded text layer "
              f"({hasl/n:.0%})")


if __name__ == "__main__":
    main()
