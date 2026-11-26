"""OCR the image-only Trans-en-Provence dossier files (HANDOFF section 5 item 4).

Of the 10 files in case 1981-01-00849, seven carry a usable text layer and three
do not:

  Analyses2 INRA-R.pdf      60 pp  -- the full INRA biochemical series, which is
                                      the quantitative backing for the 30-50%
                                      pigment-loss claim quoted in section 1.2
  PV n°28 (1981308305).pdf  11 pp  -- the gendarmerie procès-verbal
  Photos-R.pdf               3 pp  -- photographic plates

French throughout, so `-l fra`.  OMP_THREAD_LIMIT=1 because tesseract otherwise
spawns a thread per core per process: measured on this corpus, 31,647 ms/page at
the default against 2,090 ms/page with the limit, byte-identical output.
"""
import os, glob, shutil, tempfile, subprocess, concurrent.futures as cf

SRC = "data/raw/geipan/tep"
OUT = "data/processed/geipan_tep"
TARGETS = ["Analyses2_INRA-R.pdf", "PV_n°28_(1981308305).pdf", "Photos-R.pdf"]
OCR_ENV = dict(os.environ, OMP_THREAD_LIMIT="1")
WORKERS = max(2, os.cpu_count() or 4)


def page_jobs():
    jobs = []
    for name in TARGETS:
        src = os.path.join(SRC, name)
        if not os.path.exists(src):
            print(f"  MISSING {name}")
            continue
        td = tempfile.mkdtemp(prefix="tep_")
        subprocess.run(["pdftoppm", "-r", "300", "-gray", "-png", src,
                        os.path.join(td, "p")], capture_output=True, timeout=1800)
        pages = sorted(glob.glob(os.path.join(td, "p*.png")))
        print(f"  {name}: {len(pages)} pages rasterised", flush=True)
        jobs += [(name, td, p) for p in pages]
    return jobs


def ocr_page(job):
    name, td, png = job
    r = subprocess.run(["tesseract", png, "stdout", "-l", "fra", "--psm", "1"],
                       capture_output=True, text=True, errors="replace",
                       timeout=600, env=OCR_ENV)
    return name, os.path.basename(png), r.stdout or ""


def main():
    os.makedirs(OUT, exist_ok=True)
    jobs = page_jobs()
    print(f"\n{len(jobs)} pages to OCR on {WORKERS} workers", flush=True)
    bucket = {}
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for i, (name, pg, txt) in enumerate(ex.map(ocr_page, jobs), 1):
            bucket.setdefault(name, []).append((pg, txt))
            if i % 20 == 0:
                print(f"  [{i}/{len(jobs)}]", flush=True)

    print()
    for name, pages in bucket.items():
        pages.sort()
        body = "\n\n".join(f"--- {pg} ---\n{txt}" for pg, txt in pages)
        dest = os.path.join(OUT, name + ".txt")
        open(dest, "w", encoding="utf-8").write(body)
        print(f"  {name}: {len(pages)} pages, {len(body):,} chars -> {dest}")

    for _, td, _ in jobs:
        shutil.rmtree(td, ignore_errors=True)

    # Also stage the text-layer files so the whole dossier is machine-readable.
    for src in sorted(glob.glob(f"{SRC}/*.pdf")):
        name = os.path.basename(src)
        if name in TARGETS:
            continue
        dest = os.path.join(OUT, name + ".txt")
        if os.path.exists(dest):
            continue
        r = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", src, "-"],
                           capture_output=True, text=True, errors="replace",
                           timeout=300)
        open(dest, "w", encoding="utf-8").write(r.stdout or "")
        print(f"  {name}: text layer, {len(r.stdout or ''):,} chars -> {dest}")

    tot = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
    print(f"\nDONE  {len(os.listdir(OUT))} text files, {tot:,} bytes")


if __name__ == "__main__":
    main()
