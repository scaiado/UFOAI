"""Measure redaction EXTENT from the PURSUE JP2 page images.

WHY THIS IS THE ONLY HONEST ROUTE. Across 326 text documents the release carries
454 `(b)(1)` citations (classified national defence) and 409 `(b)(6)` (privacy),
but only 5 documents contain any literal `[REDACTED]` marker, 6 occurrences in
all. Withholdings are applied to the PAGE IMAGE, so OCR returns nothing and
leaves no trace: in the text layer a blacked-out paragraph and a wide margin are
indistinguishable. Extent cannot be measured from text. It can be measured from
pixels.

METHOD
  grayscale -> dark mask (<50) -> connected components (scipy.ndimage.label) ->
  for each component: area, bounding box, FILL RATIO (component area / bbox
  area), aspect. A redaction bar is a large, nearly-solid, rectangular dark
  region: fill ratio near 1.0 inside its own bbox.

WHITE-OUT REDACTION, AND WHY IT HAD TO BE ADDED
  The first run measured only dark bars and reported the four heaviest `(b)(1)`
  citers as redacted (D3 with 66 bars over 5.87% of page area, D107/D108/D109
  with 22-33 each) -- but returned ZERO bars for D32 Syria (59 `(b)(1)`
  citations), D27 UAE (42), D25 Greece (42) and D28 East China Sea (35). A
  detector that finds nothing in a document citing 59 national-defence
  exemptions is more likely incomplete than the document unredacted. So white
  excisions are measured too: large near-white rectangles lying INSIDE the
  page's own ink bounding box, i.e. surrounded by text rather than page margin.
  Reporting only black bars would have systematically understated redaction in
  exactly the documents that white out.

WHAT IS DELIBERATELY NOT CLAIMED
  A large dark blob is not necessarily a redaction. Photographs, dark scans,
  seals and scanner artefacts all produce one. So every component is reported
  with its fill ratio and aspect so a human can audit the call, and pages whose
  dark pixels are high-variance (photographic) are flagged separately rather
  than silently counted. The output is a measurement with its discriminants
  attached, not a verdict.
"""
import io, json, os, sys, zipfile, collections
import numpy as np
from PIL import Image
from scipy import ndimage

SP = os.environ.get("OMEGA_SCRATCH", "")
ZD = f"{SP}/jp2"
OUT = "evidence_vault/05_SCRUBBED_CONTENT"

DARK = 50            # grayscale value below which a pixel is "ink-dark"
MIN_FRAC = 0.002     # ignore components under 0.2% of page area
FILL_MIN = 0.80      # a bar is near-solid within its own bounding box
MAXDIM = 1400        # downscale for speed; redaction bars are large features


def analyse_page(im):
    im = im.convert("L")
    w, h = im.size
    if max(w, h) > MAXDIM:
        s = MAXDIM / max(w, h)
        im = im.resize((max(1, int(w * s)), max(1, int(h * s))))
    a = np.asarray(im, dtype=np.uint8)
    H, W = a.shape
    page = float(H * W)
    dark = a < DARK
    dark_frac = float(dark.sum() / page)

    # --- white excisions inside the inked region --------------------
    # Margins are white too, so the search is confined to the bounding box of
    # the page's own ink; a white rectangle there sits among text.
    ink = a < 200
    white_bars = []
    if ink.any():
        rows = np.where(ink.any(axis=1))[0]
        cols = np.where(ink.any(axis=0))[0]
        r0, r1, c0, c1 = rows[0], rows[-1] + 1, cols[0], cols[-1] + 1
        inner = a[r0:r1, c0:c1]
        iH, iW = inner.shape
        iarea = float(iH * iW)
        if iarea > 0:
            wmask = inner > 225
            wlab, wn = ndimage.label(wmask)
            if wn:
                wobjs = ndimage.find_objects(wlab)
                wsz = ndimage.sum(wmask, wlab, range(1, wn + 1))
                for i, sl in enumerate(wobjs):
                    ar = float(wsz[i])
                    if ar / iarea < 0.01:          # white gaps are big or noise
                        continue
                    bh = sl[0].stop - sl[0].start
                    bw = sl[1].stop - sl[1].start
                    bbox = float(bh * bw)
                    fill = ar / bbox if bbox else 0.0
                    # a line gap spans the full text width; an excision is a
                    # block, so require it not to be a thin full-width strip
                    if fill >= 0.90 and bh > 0.02 * iH and bw < 0.98 * iW:
                        white_bars.append({"area_frac": round(ar / iarea, 5),
                                           "fill": round(fill, 3),
                                           "aspect": round(bw / bh, 2) if bh else None})

    lab, n = ndimage.label(dark)
    bars, phot = [], 0
    if n:
        objs = ndimage.find_objects(lab)
        sizes = ndimage.sum(dark, lab, range(1, n + 1))
        for i, sl in enumerate(objs):
            area = float(sizes[i])
            if area / page < MIN_FRAC:
                continue
            bh = sl[0].stop - sl[0].start
            bw = sl[1].stop - sl[1].start
            bbox = float(bh * bw)
            fill = area / bbox if bbox else 0.0
            # variance of the ORIGINAL grey inside the bbox separates a solid
            # bar from a photograph: a bar is uniform, a photo is not.
            patch = a[sl]
            var = float(patch.std())
            rec = {"area_frac": round(area / page, 5),
                   "fill": round(fill, 3),
                   "aspect": round(bw / bh, 2) if bh else None,
                   "std_inside": round(var, 1)}
            if fill >= FILL_MIN and var < 40:
                bars.append(rec)
            elif fill >= FILL_MIN:
                phot += 1
    return {"dark_frac": round(dark_frac, 5),
            "bar_count": len(bars),
            "bar_area_frac": round(sum(b["area_frac"] for b in bars), 5),
            "white_count": len(white_bars),
            "white_area_frac": round(sum(b["area_frac"] for b in white_bars), 5),
            "photographic_blobs": phot,
            "bars": sorted(bars, key=lambda x: -x["area_frac"])[:12],
            "white_bars": sorted(white_bars, key=lambda x: -x["area_frac"])[:12]}


def main():
    if not os.path.isdir(ZD):
        print(f"no JP2 directory at {ZD}; set OMEGA_SCRATCH", file=sys.stderr)
        sys.exit(2)
    os.makedirs(OUT, exist_ok=True)
    zips = sorted(f for f in os.listdir(ZD) if f.endswith(".zip"))
    print(f"{len(zips)} JP2 bundles\n")
    report = {}
    print(f"  {'document':<46}{'pg':>4}{'dark%':>7}{'bars':>6}{'bar%':>7}"
          f"{'wht':>5}{'wht%':>7}")
    for z in zips:
        stem = z.replace("_jp2.zip", "")
        try:
            zf = zipfile.ZipFile(os.path.join(ZD, z))
        except Exception as e:
            print(f"  {stem[:52]:<52} ZIP ERROR {e}")
            continue
        pages = sorted(n for n in zf.namelist()
                       if n.lower().endswith((".jp2", ".jpg", ".png", ".tif")))
        res = []
        for p in pages:
            try:
                im = Image.open(io.BytesIO(zf.read(p)))
                res.append(analyse_page(im))
            except Exception:
                continue
        if not res:
            continue
        nbar = sum(r["bar_count"] for r in res)
        barf = sum(r["bar_area_frac"] for r in res) / len(res)
        darkf = sum(r["dark_frac"] for r in res) / len(res)
        phot = sum(r["photographic_blobs"] for r in res)
        npg_bar = sum(1 for r in res if r["bar_count"])
        nwht = sum(r["white_count"] for r in res)
        whtf = sum(r["white_area_frac"] for r in res) / len(res)
        print(f"  {stem[:46]:<46}{len(res):>4}{100*darkf:>7.2f}{nbar:>6}"
              f"{100*barf:>7.2f}{nwht:>5}{100*whtf:>7.2f}")
        report[stem] = {"pages": len(res), "pages_with_bars": npg_bar,
                        "total_white": nwht,
                        "mean_white_area_frac": round(whtf, 5),
                        "mean_dark_frac": round(darkf, 5),
                        "total_bars": nbar,
                        "mean_bar_area_frac": round(barf, 5),
                        "photographic_blobs": phot,
                        "per_page": res}
    json.dump(report, open(f"{OUT}/jp2_redaction_map.json", "w"), indent=1)
    print(f"\nwrote {OUT}/jp2_redaction_map.json")

    tot_pg = sum(v["pages"] for v in report.values())
    tot_bar = sum(v["total_bars"] for v in report.values())
    wb = sum(v["pages_with_bars"] for v in report.values())
    print(f"\n{len(report)} documents, {tot_pg} pages")
    print(f"pages carrying >=1 solid dark bar: {wb} ({wb/max(1,tot_pg):.1%})")
    print(f"total solid dark bars detected   : {tot_bar}")


if __name__ == "__main__":
    main()
