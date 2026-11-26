"""Context-extracting term search across every corpus on disk — Tracks A-D.

A keyword count is not a finding.  This records, for every occurrence: the
document, the surrounding text, and a FRAME classification, because the same
word means different things in different frames and the project has already
been burned three times by not checking:

  aurora    -- 28 hits, 25 of them the northern lights, a satellite, or
               astronauts describing an actual aurora
  stargate  -- 27 hits, 0 for the programme; it is a wormhole geometry in a DIA
               physics paper, plus a witness naming a TV series
  3418      -- a private collection in a house in Fortaleza, 14 away from
               GEIPAN's 3,404

FRAMES
  QUOTED_FICTION  the text names a film, novel, TV series or game
  HYPOTHETICAL    hedged by alleged/rumored/supposed/claimed/reportedly/if
  THIRD_PARTY     the document is relaying someone else's claim or a press item
  PHYSICS_TERM    the term is used as a technical noun, not a programme name
  DIRECT          none of the above -- the document asserts it in its own voice

Only DIRECT occurrences can support a claim.  Everything else is recorded so the
distinction is auditable rather than asserted.
"""
import json, os, re, sys, collections

SP = os.environ.get("OMEGA_SCRATCH", "")
OUT = "evidence_vault/10_HIDDEN_BURIED"
WIN = 240

CORPORA = [
    ("pursue_server", f"{SP}/uap/djvu"),
    ("pursue_ours",   "data/raw/pursue_ocr/txt"),
    ("aawsap_dirds",  "evidence_vault/01_PURSUE_PRIMARY/AAWSAP_DIRDs"),
    ("doe_nuclear",   "evidence_vault/01_PURSUE_PRIMARY/nuclear_facility"),
    ("range_fouler",  "evidence_vault/01_PURSUE_PRIMARY/range_fouler"),
    ("geipan_tep",    "data/processed/geipan_tep"),
    ("geipan_ctl",    "data/processed/geipan_trace_controls"),
    ("geipan_pv",     "data/processed/geipan_pv"),
]

TRACKS = {
 "A_contact_signal": [
   r"communication attempt", r"attempt(?:ed)? to (?:transmit|communicate|signal)",
   r"active interrogation", r"two.way communication", r"establish(?:ing)? contact",
   r"\bELF\b", r"\bVLF\b", r"laser communication", r"signal(?:l)?ing to",
   r"broadcast to", r"transmit(?:ted)? to the (?:object|craft|phenomen)",
 ],
 "A_contact_field": [
   r"field effect", r"modulat(?:e|ed|ion) (?:the )?field", r"carrier wave",
   r"information.bearing field", r"field.mediated",
 ],
 "A_contact_quantum": [
   r"quantum entanglement", r"nonlocal(?:ity)?", r"gravitational wave communicat",
   r"entangle(?:d|ment).based communicat",
 ],
 "B_maintained_contact": [
   r"\bliaison\b", r"joint programme?", r"joint program",
   r"collaborat(?:e|ed|ion) with (?:the )?(?:non.human|alien|extraterrestrial|entit)",
   r"technology transfer", r"exchange programme?", r"exchange program",
   r"sustained (?:contact|interaction)", r"ongoing (?:contact|dialogue)",
 ],
 "C_entities_in_power": [
   r"non.human (?:personnel|employee|staff|officer|official|representative)",
   r"human.looking", r"indistinguishable from (?:a )?human",
   r"infiltrat(?:e|ed|ion)", r"breakaway civili[sz]ation", r"shadow government",
   r"organic robot", r"pseudo.human", r"security clearance.{0,40}(?:non.human|alien|entit)",
 ],
 "D_interdimensional": [
   r"interdimensional", r"extradimensional", r"ultraterrestrial",
   r"other dimension", r"parallel universe",
 ],
 "D_time": [r"time travel", r"temporal displacement", r"closed timelike", r"retrocausal"],
 "D_consciousness": [
   r"remote viewing", r"telepath(?:y|ic)", r"psychokine", r"consciousness.mediated",
   r"psychic", r"precognit",
 ],
 "D_simulation": [r"holographic projection", r"\bprojection\b.{0,30}not physical", r"simulat(?:ion|ed) hypothesis"],
 "D_exotic_tech": [
   r"programmable matter", r"metamaterial", r"zero.point energy", r"vacuum energy",
   r"negative mass", r"exotic matter", r"antigravity", r"anti.gravity",
   r"spacetime metric", r"traversable wormhole", r"invisibility cloak",
 ],
 "E_biologics": [
   r"non.human biologic", r"biologic(?:al)? (?:specimen|material) of (?:non.human|unknown)",
   r"crash retrieval", r"reverse.engineer", r"recovered (?:hardware|material|craft)",
 ],
 "F_named_claims": [
   r"\bMJ.?12\b", r"majestic", r"\bserpo\b", r"glimmer glass", r"kona blue",
   r"looking glass", r"\bteaball\b", r"moon dust", r"immaculate constellation",
   r"skinwalker", r"utah ranch",
 ],
 "G_named_encounters": [
   r"\bgimbal\b", r"go.?fast", r"\bnimitz\b", r"tic.?tac", r"\bFLIR\b",
   r"cash.landrum", r"\brendlesham\b", r"\bsocorro\b", r"\bdelphos\b",
 ],
}

FICTION = re.compile(r"star.?wars|star.?trek|stargate sg|science.?fiction|\bnovel\b|\bmovie\b|"
                     r"\bfilm\b|television|\bTV\b|comic|video game|hollywood", re.I)
HEDGE = re.compile(r"alleged|rumo(?:u)?red|supposed|purport|claim(?:s|ed)?|reportedly|"
                   r"\bif\b.{0,20}(?:were|could|exist)|hypothetic|speculat|anecdot", re.I)
THIRD = re.compile(r"newspaper|press|tabloid|magazine|website|internet|blog|per the author|"
                   r"according to (?:the )?(?:author|witness|report)|letter to|correspondent", re.I)
PHYSICS = re.compile(r"equation|metric|tensor|lagrangian|einstein|solution|figure \d|"
                     r"table \d|wormhole physics|GeV|joule|kelvin|hamiltonian", re.I)


def frame(ctx):
    if FICTION.search(ctx):
        return "QUOTED_FICTION"
    if HEDGE.search(ctx):
        return "HYPOTHETICAL"
    if THIRD.search(ctx):
        return "THIRD_PARTY"
    if PHYSICS.search(ctx):
        return "PHYSICS_TERM"
    return "DIRECT"


def main():
    hits = collections.defaultdict(list)
    ndoc = 0
    for cname, root in CORPORA:
        if not os.path.isdir(root):
            continue
        for f in sorted(os.listdir(root)):
            if not f.endswith(".txt"):
                continue
            t = open(os.path.join(root, f), encoding="utf-8", errors="replace").read()
            ndoc += 1
            for track, pats in TRACKS.items():
                for pat in pats:
                    for m in re.finditer(pat, t, re.I):
                        ctx = " ".join(t[max(0, m.start()-WIN): m.end()+WIN].split())
                        hits[(track, pat)].append({
                            "corpus": cname, "doc": f, "match": m.group(0),
                            "frame": frame(ctx), "context": ctx})
    os.makedirs(OUT, exist_ok=True)

    print(f"corpora scanned: {ndoc} documents\n")
    summary = {}
    for track in TRACKS:
        rows = [(p, hits.get((track, p), [])) for p in TRACKS[track]]
        tot = sum(len(v) for _, v in rows)
        direct = sum(1 for _, v in rows for h in v if h["frame"] == "DIRECT")
        print(f"=== {track}  total={tot}  DIRECT={direct} ===")
        for p, v in sorted(rows, key=lambda x: -len(x[1])):
            if not v:
                print(f"  {'0':>5}  {p[:58]}   ZERO")
                continue
            fr = collections.Counter(h["frame"] for h in v)
            nd = len({h["doc"] for h in v})
            print(f"  {len(v):>5}  {p[:58]}   docs={nd}  {dict(fr)}")
        summary[track] = {"total": tot, "direct": direct,
                          "terms": {p: len(v) for p, v in rows}}
        print()

    json.dump({"corpora_docs": ndoc, "summary": summary,
               "hits": {f"{t}||{p}": v for (t, p), v in hits.items()}},
              open(f"{OUT}/deep_terms.json", "w"), indent=1, ensure_ascii=False)
    print(f"wrote {OUT}/deep_terms.json")


if __name__ == "__main__":
    main()
