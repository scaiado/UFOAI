"""Extract text from the GEIPAN physical-trace CONTROL dossiers.

Trans-en-Provence is the only class-D case in the 3,404-case French archive with
a physical-sample laboratory analysis.  The other four sample-bearing cases were
identified (A) or probably identified (B), which makes them the matched control
set TEP has never been given: what did the labs find in the cases that WERE
explained?

  2001-06-01567  BARBEZIEUX (16)               B   Analyse echantillons sol
  1986-03-01088  MAISONNAIS-SUR-TARDOIRE (87)   A   Expertise echantillons
  1997-04-01755  CHAMBERY (73)                  A   Analyses echantillons
  1985-02-01063  SAINT-SULPICE-DE-ROYAN (17)    A   Expertise APAVE + CREA
  1983-05-00977  LABATUT (40)                   B   Laboratoire de Recherche
                                                    sur la Foudre (lightning)

One pipeline for the image-only files, as in geipan_pv_extract: tesseract -l fra
at 300 dpi with OMP_THREAD_LIMIT=1.  Text-layer files are taken as published and
flagged as such, because here the comparison is between DOCUMENTS, not between
arms of a classifier -- there is no label for a mixed pipeline to track.
"""
import os, glob, shutil, tempfile, subprocess, collections
import concurrent.futures as cf

SRC = "data/raw/geipan/trace_controls"
OUT = "data/processed/geipan_trace_controls"
OCR_ENV = dict(os.environ, OMP_THREAD_LIMIT="1")
WORKERS = max(2, os.cpu_count() or 4)
MIN_TEXT = 200
# Photo-plate collections: dozens of pages of images with no prose to recover.
SKIP = ("34photos", "Photos")


def ocr_pdf(path):
    td = tempfile.mkdtemp(prefix="ctl_")
    try:
        subprocess.run(["pdftoppm", "-r", "300", "-gray", "-png", path,
                        os.path.join(td, "p")], capture_output=True, timeout=2400)
        pages = sorted(glob.glob(os.path.join(td, "p*.png")))
        out = []
        for png in pages:
            r = subprocess.run(["tesseract", png, "stdout", "-l", "fra",
                                "--psm", "1"], capture_output=True, text=True,
                               errors="replace", timeout=600, env=OCR_ENV)
            out.append(r.stdout or "")
            os.remove(png)
        return "\n".join(out), len(pages)
    finally:
        shutil.rmtree(td, ignore_errors=True)


def job(path):
    rel = os.path.relpath(path, SRC).replace("/", "__")
    dest = os.path.join(OUT, rel + ".txt")
    if os.path.exists(dest):
        return rel, "cache", len(open(dest, encoding="utf-8").read())
    if any(k in os.path.basename(path) for k in SKIP):
        return rel, "skipped_photo_plates", 0
    lay = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", path, "-"],
                         capture_output=True, text=True, errors="replace",
                         timeout=300).stdout or ""
    if len(lay.strip()) >= MIN_TEXT:
        open(dest, "w", encoding="utf-8").write(lay)
        return rel, "text_layer", len(lay)
    txt, _ = ocr_pdf(path)
    open(dest, "w", encoding="utf-8").write(txt)
    return rel, "ocr", len(txt)


def main():
    os.makedirs(OUT, exist_ok=True)
    pdfs = sorted(glob.glob(f"{SRC}/*/*.pdf"))
    print(f"{len(pdfs)} PDFs, {WORKERS} workers", flush=True)
    stats = collections.Counter()
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for rel, how, n in ex.map(job, pdfs):
            stats[how] += 1
            print(f"  [{how:<22}] {n:>8,} chars  {rel}", flush=True)
    print(f"\n{dict(stats)}")
    tot = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
    print(f"{len(os.listdir(OUT))} text files, {tot:,} bytes")


if __name__ == "__main__":
    main()
