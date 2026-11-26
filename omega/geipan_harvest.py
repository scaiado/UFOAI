"""Harvest GEIPAN case dossiers: the D arm plus a matched C arm.

Why: the narrative test on `Détails` is confounded because that field is analyst
prose written after classification (see geipan_t3_final.py).  The dossiers hold
pre-verdict, witness-level material -- gendarmerie proces-verbaux ("PV n°..."),
investigation reports ("Compte rendu enquete"), laboratory analyses -- which is
what an identified test needs.

Mechanics: case pages are Drupal-rendered and take 3-28 s each, so they are
fetched in batches through a single curl invocation that reuses the TLS
connection.  Static files under /sites/default/files/ answer in ~0.3 s.  Only
cases the export says carry a document are requested, so no page is fetched
pointlessly.  One honest user agent; batches keep total connections far below
one-per-file.
"""
import os, re, sys, json, time, urllib.parse, subprocess, random, collections

UA = "omega-research/1.0 (academic UAP data study; non-commercial)"
BASE = "https://www.geipan.fr"
OUT = "data/raw/geipan/docs"
PAGES = "data/raw/geipan/pages"
FILE_RX = re.compile(
    r'href="(https://www\.geipan\.fr/sites/default/files/'
    r'[^"]+\.(?:pdf|jpg|jpeg|png|doc|docx|xls|xlsx|zip|kmz|kml|txt))"', re.I)

def curl_batch(pairs, timeout=240):
    """pairs = [(url, dest)]; one curl invocation, connection reused."""
    if not pairs: return {}
    cmd = ["curl", "-sS", "-A", UA, "-L", "--max-time", str(timeout),
           "--retry", "1", "--retry-delay", "2", "-w", "%{http_code} %{size_download}\n"]
    for u, d in pairs:
        cmd += ["-o", d, u]
    r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    codes = [l.split() for l in r.stdout.strip().splitlines() if l.strip()]
    out = {}
    for i, (u, d) in enumerate(pairs):
        out[u] = tuple(codes[i]) if i < len(codes) else ("000", "0")
    return out

def safe(name):
    return re.sub(r"[^\w.\-() °]", "_", urllib.parse.unquote(name))[:150]

def main():
    cases = json.load(open("data/raw/geipan/geipan_cases.json", encoding="utf-8-sig"))
    def has_doc(r):
        d = str(r.get("Document pour cas") or "").strip()
        return d and d != "/" and "." in d
    byc = collections.defaultdict(list)
    for r in cases: byc[(r.get("Classification") or "").strip().upper()].append(r)
    D = [r for r in byc["D"] if has_doc(r)]
    rng = random.Random(42)
    Cpool = [r for r in byc["C"] if has_doc(r)]
    C = rng.sample(Cpool, min(len(D) * 2, len(Cpool)))
    targets = [("D", r) for r in D] + [("C", r) for r in C]
    print(f"targets: D={len(D)} (of {len(byc['D'])} D cases)  "
          f"C={len(C)} (of {len(Cpool)} C with docs)  total={len(targets)}", flush=True)
    os.makedirs(OUT, exist_ok=True); os.makedirs(PAGES, exist_ok=True)

    # ---- phase 1: case pages, batched
    todo = [(a, r) for a, r in targets
            if not os.path.exists(f"{PAGES}/{r['ID Etude de Cas']}.html")]
    B = 8
    for i in range(0, len(todo), B):
        batch = todo[i:i + B]
        res = curl_batch([(f"{BASE}/fr/cas/{r['ID Etude de Cas']}",
                           f"{PAGES}/{r['ID Etude de Cas']}.html") for _, r in batch])
        ok = sum(1 for v in res.values() if v[0] == "200")
        print(f"  pages {i+len(batch)}/{len(todo)}  ok={ok}/{len(batch)}", flush=True)
        time.sleep(1.0)

    # ---- phase 2: files, batched
    log = {}
    allfiles = []
    for arm, r in targets:
        cid = r["ID Etude de Cas"]
        p = f"{PAGES}/{cid}.html"
        if not os.path.exists(p) or os.path.getsize(p) < 2000:
            log[cid] = {"arm": arm, "status": "no_page"}; continue
        html = open(p, encoding="utf-8", errors="replace").read()
        urls = sorted(set(FILE_RX.findall(html)))
        # the site-wide technical questionnaire is linked from every page; drop it
        urls = [u for u in urls if "Questionnaire%20Technique" not in u]
        if not urls:
            log[cid] = {"arm": arm, "status": "no_files", "n": 0}; continue
        d = os.path.join(OUT, cid); os.makedirs(d, exist_ok=True)
        log[cid] = {"arm": arm, "status": "pending", "title": r.get("Titre du Cas"),
                    "year": r.get("Année"), "urls": urls, "files": []}
        for u in urls:
            dest = os.path.join(d, safe(os.path.basename(u)))
            if os.path.exists(dest) and os.path.getsize(dest) > 500:
                log[cid]["files"].append(os.path.basename(dest)); continue
            allfiles.append((u, dest, cid))
    print(f"  files to fetch: {len(allfiles)}", flush=True)
    B = 12
    for i in range(0, len(allfiles), B):
        batch = allfiles[i:i + B]
        res = curl_batch([(u, d) for u, d, _ in batch])
        for u, d, cid in batch:
            c, sz = res.get(u, ("000", "0"))
            if c == "200" and os.path.exists(d) and os.path.getsize(d) > 500:
                log[cid]["files"].append(os.path.basename(d))
            else:
                try: os.remove(d)
                except OSError: pass
        print(f"  files {i+len(batch)}/{len(allfiles)}", flush=True)
        time.sleep(0.8)
    for cid, v in log.items():
        if v.get("status") == "pending":
            v["status"] = "ok" if v["files"] else "all_failed"
            v["n"] = len(v["files"])
    json.dump(log, open("data/raw/geipan/harvest_log.json", "w"), indent=1, ensure_ascii=False)
    nD = sum(1 for v in log.values() if v["arm"] == "D" and v.get("n"))
    nC = sum(1 for v in log.values() if v["arm"] == "C" and v.get("n"))
    nf = sum(v.get("n", 0) for v in log.values())
    print(f"\nDONE  D cases with files: {nD}  C cases with files: {nC}  total files: {nf}")

if __name__ == "__main__":
    main()
