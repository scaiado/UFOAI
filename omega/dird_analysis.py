"""What ARE the 37 AAWSAP DIRDs? The question that decides what they are worth.

The DIRDs are the strongest remaining "positive" in this project: 37
government-commissioned Defense Intelligence Reference Documents on wormholes,
warp drive, antigravity, negative mass, quantum-vacuum energy extraction,
metamaterials and invisibility cloaking. They have only ever been GREPPED here.

ONE QUESTION DECIDES THEIR INTERPRETATION:

  Do they cite observed UAP performance as motivation or design requirement,
  or are they open-literature reviews built from published physics?

  If the latter, "the government funded research into NHI-level technology"
  deflates to "a threat-assessment office paid contractors to survey the
  journals" -- which is what such an office does whether or not anything has
  been observed. If even one DIRD cites observed performance characteristics as
  a requirement, it is a different document class entirely.

MEASURED PER DOCUMENT
  * UAP/anomalous-phenomena references, with context and frame
  * whether observed performance appears as a design driver
  * reference-list composition: journal/arXiv/book (open) vs internal/classified
  * the verdict the document itself reaches on feasibility
  * declared performer/author organisation
"""
import json, os, re, sys, collections

D = "evidence_vault/01_PURSUE_PRIMARY/AAWSAP_DIRDs"
OUT = "evidence_vault/01_PURSUE_PRIMARY"

UAP = re.compile(r"\bUAP\b|\bUFO\b|unidentified aerial|unidentified flying|"
                 r"anomalous aerial|flying saucer|\bAAV\b|advanced aerospace vehicle",
                 re.I)
# performance stated as a requirement/observation rather than a theory result
PERF = re.compile(r"observed (?:performance|acceleration|velocit|manoeuvr|maneuver)|"
                  r"reported (?:performance|acceleration|velocit)|"
                  r"performance (?:characteristic|requirement|envelope)|"
                  r"design (?:requirement|driver|target)|"
                  r"observed .{0,24}(?:g\b|g-force|gee)", re.I)
OPEN_REF = re.compile(r"\b(?:Phys\.?\s?Rev|Physical Review|Nature|Science|"
                      r"J\.?\s?Appl|Astrophys|arXiv|Class\.?\s?Quantum|"
                      r"Gen\.?\s?Rel|Am\.?\s?J\.?\s?Phys|Proc\.?|IEEE|AIAA|"
                      r"Springer|Wiley|Cambridge Univ|Oxford Univ|McGraw|"
                      r"Phys\.?\s?Lett|Found\.?\s?Phys|doi:)", re.I)
CLOSED_REF = re.compile(r"\b(?:classified|SECRET|NOFORN|internal report|"
                        r"personal communication|private communication|"
                        r"unpublished|proprietary)\b", re.I)
FEAS = {
 "infeasible_now": re.compile(r"not (?:currently |presently )?(?:feasible|possible|practical)|"
                              r"beyond (?:current|present|foreseeable)|"
                              r"is not easy|no known (?:way|method)|"
                              r"cannot be (?:built|constructed|achieved)|"
                              r"prohibitiv|insurmountab", re.I),
 "far_future":     re.compile(r"far future|distant future|centuries|many decades|"
                              r"long.term prospect", re.I),
 "near_term":      re.compile(r"near.?term|within (?:a )?decade|currently achievable|"
                              r"demonstrated in the laborator|already demonstrated", re.I),
}
PERFORMER = re.compile(r"Prepared by[:\s]+(.{0,90})|Performer[:\s]+(.{0,60})|"
                       r"\b(EarthTech|Institute for Advanced Studies at Austin|"
                       r"Lockheed|Northrop|Boeing|Raytheon|BAE|SAIC|"
                       r"Los Alamos|Sandia|Livermore|MIT|Caltech|"
                       r"Defense Intelligence Agency)\b", re.I)


def main():
    rows = {}
    agg = collections.Counter()
    for f in sorted(os.listdir(D)):
        if not f.endswith(".txt"):
            continue
        t = open(os.path.join(D, f), encoding="utf-8", errors="replace").read()
        did = re.search(r"DOW-UAP-(D\d+)", f)
        title = re.sub(r"^DOW-UAP-D\d+_?\s*AAWSA?P?-DIRD-", "", f)
        title = re.sub(r"-(January|February|March|April|May|June|July|August|"
                       r"September|October|November|December)-\d+.*$", "", title)
        title = title.replace("-", " ").replace("_djvu.txt", "").strip()

        uap = [m for m in UAP.finditer(t)]
        perf = [m for m in PERF.finditer(t)]
        nopen = len(OPEN_REF.findall(t))
        nclosed = len(CLOSED_REF.findall(t))
        feas = {k: len(rx.findall(t)) for k, rx in FEAS.items()}
        perfm = collections.Counter(g for m in PERFORMER.finditer(t)
                                    for g in m.groups() if g)
        rows[did.group(1) if did else f] = {
            "title": title[:78], "chars": len(t),
            "uap_mentions": len(uap),
            "uap_contexts": [" ".join(t[max(0, m.start()-150): m.end()+150].split())
                             for m in uap[:4]],
            "performance_as_driver": len(perf),
            "performance_contexts": [" ".join(t[max(0, m.start()-150): m.end()+150].split())
                                     for m in perf[:3]],
            "open_refs": nopen, "closed_refs": nclosed,
            "feasibility": feas,
            "performer_hints": [k for k, _ in perfm.most_common(3)],
        }
        agg["uap_any"] += 1 if uap else 0
        agg["perf_any"] += 1 if perf else 0
        agg["docs"] += 1

    print(f"{agg['docs']} DIRDs analysed\n")
    print(f"  {'id':<6}{'UAP':>5}{'perf':>6}{'open':>6}{'clsd':>6}  {'feas(no/far/near)':<18} title")
    for k, v in sorted(rows.items(), key=lambda x: int(x[0][1:]) if x[0][1:].isdigit() else 0):
        fz = v["feasibility"]
        print(f"  {k:<6}{v['uap_mentions']:>5}{v['performance_as_driver']:>6}"
              f"{v['open_refs']:>6}{v['closed_refs']:>6}  "
              f"{fz['infeasible_now']:>3}/{fz['far_future']:>3}/{fz['near_term']:<10}"
              f"{v['title'][:50]}")

    print()
    print("=" * 78)
    print("THE DECIDING NUMBERS")
    print("=" * 78)
    print(f"  DIRDs mentioning UAP/UFO/anomalous aerial at all : "
          f"{agg['uap_any']}/{agg['docs']}")
    print(f"  DIRDs citing observed performance as a driver    : "
          f"{agg['perf_any']}/{agg['docs']}")
    to = sum(v["open_refs"] for v in rows.values())
    tc = sum(v["closed_refs"] for v in rows.values())
    print(f"  open-literature citation markers  : {to}")
    print(f"  closed/internal citation markers  : {tc}")
    print(f"  ratio open:closed                 : "
          f"{to/max(1,tc):.1f}:1")
    fi = sum(v["feasibility"]["infeasible_now"] for v in rows.values())
    ff = sum(v["feasibility"]["far_future"] for v in rows.values())
    fn = sum(v["feasibility"]["near_term"] for v in rows.values())
    print(f"  feasibility language: infeasible-now {fi}, far-future {ff}, "
          f"near-term {fn}")
    json.dump(rows, open(f"{OUT}/dird_analysis.json", "w"), indent=1,
              ensure_ascii=False)
    print(f"\nwrote {OUT}/dird_analysis.json")


if __name__ == "__main__":
    main()
