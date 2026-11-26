"""Redaction extent from INLINE exemption substitutions — correcting §1.7.

§1.7 concluded: "Redaction is invisible in PURSUE text: zero [REDACTED] markers,
but 964 FOIA exemption citations ... Withholdings are applied to the page image,
so OCR returns nothing with no marker. Detecting extent needs JP2 page-image
analysis, not text search."

THAT IS INCOMPLETE. It searched for the literal token `[REDACTED]`. The release
does not use it. It substitutes the exemption code IN PLACE of the withheld span,
inline, in the text layer:

    AT 0823Z, (b)(1)1.4a TOOK OFF FROM OJMS VIA SLR. (b)(1)1.4a PROCEEDED TO
    FRAGGED TASKING. AT 0649Z, (b)(1)1.4a WAS 7-LINED

Each `(b)(1)1.4a` is a redaction, positioned exactly where the removed text was,
and it carries its own justification: the trailing code is the E.O. 13526 §1.4
subsection. So extent IS measurable from text — by counting and locating these —
and the JP2 black bars are a SECOND, independent mechanism layered on top.

E.O. 13526 §1.4 classification categories
  1.4(a) military plans, weapons systems, or operations
  1.4(b) foreign government information
  1.4(c) intelligence activities, sources, methods, or cryptology
  1.4(d) foreign relations or foreign activities of the United States
  1.4(e) scientific, technological, or economic matters relating to national security
  1.4(f) USG programs for safeguarding nuclear materials or facilities
  1.4(g) vulnerabilities of systems, installations, infrastructure, projects, plans
  1.4(h) weapons of mass destruction
"""
import json, os, re, sys, collections

SP = os.environ.get("OMEGA_SCRATCH", "")
OUT = "evidence_vault/05_SCRUBBED_CONTENT"
ROOTS = [f"{SP}/uap/djvu", "data/raw/pursue_ocr/txt"]

# (b)(1) with an optional E.O. 13526 subsection suffix, and the other exemptions
INLINE = re.compile(r"\(b\)\s*\((\d)\)\s*(1\.4\s*([a-h]))?", re.I)
EO = {"a": "military plans/weapons/operations", "b": "foreign government information",
      "c": "intelligence activities/sources/methods", "d": "foreign relations",
      "e": "sci/tech/economic re national security", "f": "nuclear safeguards",
      "g": "infrastructure vulnerabilities", "h": "weapons of mass destruction"}
LITERAL = re.compile(r"\[REDACTED\]|\[DELETED\]|\bREDACTED\b", re.I)


def main():
    os.makedirs(OUT, exist_ok=True)
    docs, exempt, eo_sub, ndoc = {}, collections.Counter(), collections.Counter(), 0
    lit = 0
    for root in ROOTS:
        if not os.path.isdir(root):
            continue
        for f in sorted(os.listdir(root)):
            if not f.endswith(".txt"):
                continue
            t = open(os.path.join(root, f), encoding="utf-8", errors="replace").read()
            ndoc += 1
            ms = list(INLINE.finditer(t))
            nlit = len(LITERAL.findall(t))
            lit += nlit
            if not ms and not nlit:
                continue
            per_sub = collections.Counter()
            for m in ms:
                exempt[f"(b)({m.group(1)})"] += 1
                if m.group(3):
                    s = m.group(3).lower()
                    eo_sub[s] += 1
                    per_sub[s] += 1
            # positional spread: a legend clusters, inline redactions spread
            pos = [m.start() / max(1, len(t)) for m in ms]
            deciles = len({int(p * 10) for p in pos})
            docs[f] = {"chars": len(t), "inline_redactions": len(ms),
                       "per_1k_chars": round(1000 * len(ms) / max(1, len(t)), 2),
                       "eo_subsections": dict(per_sub),
                       "deciles_touched": deciles,
                       "literal_markers": nlit,
                       "pattern": "DISTRIBUTED" if deciles >= 5 else
                                  ("CLUSTERED" if len(ms) else "none")}

    print(f"documents scanned: {ndoc}")
    print(f"documents with inline redactions: {len(docs)}")
    print(f"literal [REDACTED]-style markers, whole corpus: {lit}")
    print()
    print("=== exemptions cited inline ===")
    for k, v in exempt.most_common():
        print(f"  {k:<10}{v:>7}")
    print()
    print("=== E.O. 13526 section 1.4 subsections (the stated reason) ===")
    for k, v in eo_sub.most_common():
        print(f"  1.4({k})  {v:>6}   {EO.get(k,'?')}")
    print()
    print("=== heaviest documents by inline redaction density ===")
    print(f"  {'per1k':>7}{'n':>6}{'dec':>5}  {'pattern':<12} document")
    for f, d in sorted(docs.items(), key=lambda x: -x[1]["per_1k_chars"])[:14]:
        print(f"  {d['per_1k_chars']:>7.2f}{d['inline_redactions']:>6}"
              f"{d['deciles_touched']:>5}  {d['pattern']:<12} {f[:56]}")
    tot = sum(d["inline_redactions"] for d in docs.values())
    dist = sum(1 for d in docs.values() if d["pattern"] == "DISTRIBUTED")
    print()
    print(f"total inline redactions: {tot}")
    print(f"documents where they are DISTRIBUTED (>=5 deciles, i.e. applied to "
          f"running text rather than a legend): {dist}/{len(docs)}")
    json.dump({"documents": docs, "exemptions": dict(exempt),
               "eo_subsections": dict(eo_sub), "total_inline": tot,
               "literal_markers_corpus": lit, "docs_scanned": ndoc},
              open(f"{OUT}/redaction_inline.json", "w"), indent=1)
    print(f"\nwrote {OUT}/redaction_inline.json")


if __name__ == "__main__":
    main()
