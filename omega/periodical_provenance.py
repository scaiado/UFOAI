"""Do the "unverifiable" events have a primary-publication origin after all?

Phase 1 / Track 3 found 12 events appearing in 5-6 separate catalogues where
EVERY citation points at another compilation inside the same corpus -- zero
upstream roots. They have the appearance of strong corroboration and no
traceable origin. Named in the report: Galesburg IL 1967-03-09 (6 catalogues),
"a small town in Texas" 1966-09-05 (6), Dallas TX 1965-08-04 (5),
Wright-Patterson AFB 1951-06-01 (5).

Phase 1's stated limitation was that it could only measure which compilations
cite which -- never what the cited sources say, because the periodicals were not
held. They are now: 860 contemporaneous issues, MUFON/Skylook 1967-2008, APRO
Bulletin from Vol 1 No 1 (1952), IUR.

THE TEST IS DECISIVE EITHER WAY
  * found in a contemporaneous bulletin -> the event HAS a primary origin and
    "zero upstream roots" was an artefact of a corpus that excluded periodicals
  * absent from 860 issues spanning the relevant years -> the echo-chamber
    finding strengthens sharply: the corroboration is circular all the way down

A CONTROL IS REQUIRED, or "absent" means nothing. If the search cannot find
events that are KNOWN to be in these bulletins, absence proves only that the
method does not work. So four heavily-documented cases of the same era are run
as positive controls: Socorro 1964, Exeter 1965, Kecksburg 1965, Trans-en-
Provence 1981. Detection on the controls validates absence on the targets.
"""
import json, os, re, sys, collections

S = os.environ.get("OMEGA_SCRATCH", "")
PD = f"{S}/periodicals/txt"
OUT = "evidence_vault/07_PERIODICALS_PRIMARY"

TARGETS = [
  {"id": "galesburg_1967",   "place": r"Galesburg",            "year": 1967,
   "month": 3,  "note": "6 catalogues, zero upstream roots", "kind": "TARGET"},
  {"id": "texas_town_1966",  "place": r"\bTexas\b",            "year": 1966,
   "month": 9,  "note": "'a small town in Texas', 6 catalogues", "kind": "TARGET"},
  {"id": "dallas_1965",      "place": r"Dallas",               "year": 1965,
   "month": 8,  "note": "5 catalogues", "kind": "TARGET"},
  {"id": "wpafb_1951",       "place": r"Wright.?Patterson",    "year": 1951,
   "month": 6,  "note": "5 catalogues; APRO begins 1952", "kind": "TARGET"},
  # positive controls -- well-documented cases of the same era
  {"id": "socorro_1964",     "place": r"Socorro",              "year": 1964,
   "month": 4,  "note": "control: Zamora, heavily documented", "kind": "CONTROL"},
  {"id": "exeter_1965",      "place": r"Exeter",               "year": 1965,
   "month": 9,  "note": "control: Exeter NH", "kind": "CONTROL"},
  {"id": "kecksburg_1965",   "place": r"Kecksburg",            "year": 1965,
   "month": 12, "note": "control: Kecksburg PA", "kind": "CONTROL"},
  {"id": "tep_1981",         "place": r"Trans.?en.?Provence",  "year": 1981,
   "month": 1,  "note": "control: TEP, GEPAN NT-16", "kind": "CONTROL"},
]

MONTHS = ["January","February","March","April","May","June","July","August",
          "September","October","November","December"]
WIN = 320


def main():
    if not os.path.isdir(PD):
        print(f"no periodical corpus at {PD}", file=sys.stderr)
        sys.exit(2)
    os.makedirs(OUT, exist_ok=True)
    files = sorted(f for f in os.listdir(PD) if f.endswith(".txt"))
    texts = {}
    for f in files:
        texts[f] = open(os.path.join(PD, f), encoding="utf-8", errors="replace").read()
    chars = sum(len(t) for t in texts.values())
    src = collections.Counter(f.split("__")[0] for f in files)
    print(f"corpus: {len(files)} issues, {chars:,} chars  {dict(src)}\n")

    results = {}
    for t in TARGETS:
        prx = re.compile(t["place"], re.I)
        yr = str(t["year"])
        mon = MONTHS[t["month"] - 1]
        mabbr = mon[:3]
        hits, strong = [], []
        for f, txt in texts.items():
            for m in prx.finditer(txt):
                ctx = " ".join(txt[max(0, m.start()-WIN): m.end()+WIN].split())
                has_yr = yr in ctx
                has_mon = bool(re.search(rf"{mon}|{mabbr}\b", ctx, re.I))
                rec = {"issue": f, "year_in_ctx": has_yr,
                       "month_in_ctx": has_mon, "context": ctx[:300]}
                hits.append(rec)
                if has_yr and has_mon:
                    strong.append(rec)
        results[t["id"]] = {**t, "place_mentions": len(hits),
                            "issues_with_place": len({h["issue"] for h in hits}),
                            "date_corroborated": len(strong),
                            "examples": strong[:3] or hits[:2]}
        flag = "" if t["kind"] == "CONTROL" else "  <-- target"
        print(f"  [{t['kind']:<7}] {t['id']:<18} place_hits={len(hits):<5} "
              f"issues={len({h['issue'] for h in hits}):<4} "
              f"date_corroborated={len(strong):<4}{flag}")

    print()
    ctl = [v for v in results.values() if v["kind"] == "CONTROL"]
    tgt = [v for v in results.values() if v["kind"] == "TARGET"]
    cdet = sum(1 for v in ctl if v["date_corroborated"])
    tdet = sum(1 for v in tgt if v["date_corroborated"])
    print("=" * 74)
    print(f"CONTROLS detected with date corroboration: {cdet}/{len(ctl)}")
    print(f"TARGETS  detected with date corroboration: {tdet}/{len(tgt)}")
    print("=" * 74)
    if cdet == 0:
        print("METHOD FAILS ITS OWN CONTROLS. Absence on the targets is")
        print("uninterpretable -- the search cannot find cases known to be there.")
    elif tdet == 0:
        print("Controls detected, targets absent -> the 'unverifiable' events have")
        print("NO contemporaneous primary publication in 860 issues. The")
        print("echo-chamber finding strengthens: corroboration is circular.")
    else:
        print("Some targets DO appear in contemporaneous bulletins -> they have a")
        print("primary origin, and 'zero upstream roots' was partly an artefact of")
        print("a citation corpus that excluded the periodicals.")
    json.dump({"corpus_issues": len(files), "corpus_chars": chars,
               "results": results}, open(f"{OUT}/provenance_test.json", "w"),
              indent=1, ensure_ascii=False)
    print(f"\nwrote {OUT}/provenance_test.json")


if __name__ == "__main__":
    main()
