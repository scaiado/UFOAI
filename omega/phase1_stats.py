"""Phase 1 deliverables: collapse factor, catalog inflation, distributions,
top cross-referenced / deepest-provenance events, circular-citation graph."""
import sys, json, collections, itertools, math
sys.path.insert(0, "/home/user/UFOAI/omega")
import corpus

OUT = "/home/user/UFOAI/data/processed/provenance"

def load(mode):
    suf = "" if mode == "strict" else f"_{mode}"
    return json.load(open(f"{OUT}/master_catalog{suf}.json"))

def stats(mc, label):
    ev = mc["events"]; nin = mc["n_input_records"]; nout = len(ev)
    print(f"\n{'='*70}\n{label}: {nin} records -> {nout} events   collapse={nin/nout:.3f}x")
    dist = collections.Counter(e["n_catalogs"] for e in ev)
    cum = 0
    print("\n  catalogs per event:")
    for k in sorted(dist):
        print(f"    in {k:>2} catalog(s): {dist[k]:>6} events ({dist[k]/nout*100:5.2f}%)")
    for thr in (2, 3, 5, 10):
        n = sum(v for k, v in dist.items() if k >= thr)
        print(f"    >= {thr} catalogs: {n} events ({n/nout*100:.2f}%)")
    # per-catalog inflation
    print("\n  per-catalog contribution:")
    print(f"    {'catalog':<20}{'records':>8}{'unique':>8}{'dup':>7}{'infl':>7}")
    rec_by_cat = collections.Counter()
    uniq_by_cat = collections.Counter()
    dup_by_cat = collections.Counter()
    events_touched = collections.Counter()
    for e in ev:
        cats = e["catalogs"]
        for c in e["catalogs"]: events_touched[c] += 1
        for uid in e["member_uids"]:
            c = uid.split("#")[0]; rec_by_cat[c] += 1
        if len(cats) == 1:
            for c in cats: uniq_by_cat[c] += 1
        else:
            for c in cats: dup_by_cat[c] += 1
    rows = []
    for c in sorted(rec_by_cat, key=lambda x: -rec_by_cat[x]):
        n = rec_by_cat[c]; u = uniq_by_cat[c]; d = dup_by_cat[c]
        infl = n / max(1, events_touched[c])
        rows.append((c, n, u, d, infl))
        print(f"    {c:<20}{n:>8}{u:>8}{d:>7}{infl:>7.2f}")
    # redundancy: records that are NOT the first/earliest witness of their event
    redundant = sum(e["n_records"] - 1 for e in ev)
    print(f"\n  redundant records (duplicate copies): {redundant} "
          f"({redundant/nin*100:.1f}% of all records)")
    # top cross-referenced
    print("\n  TOP 20 MOST CROSS-REFERENCED EVENTS (echo-chamber champions):")
    for e in sorted(ev, key=lambda x: (-x["n_catalogs"], -x["n_records"]))[:20]:
        d = f"{e['year']}-{e['month'] or '??'}-{e['day'] or '??'}"
        print(f"    {e['n_catalogs']:>2}cat {e['n_records']:>2}rec {d:<12} "
              f"{(e['location'] or '?')[:30]:<30} {e['description'][:70]}")
    # deepest provenance
    print("\n  TOP 20 DEEPEST PROVENANCE (most distinct source lineages):")
    for e in sorted(ev, key=lambda x: (-x["provenance_depth"], -x["n_catalogs"]))[:20]:
        d = f"{e['year']}-{e['month'] or '??'}-{e['day'] or '??'}"
        print(f"    depth={e['provenance_depth']:>2} {e['n_catalogs']}cat {d:<12} "
              f"{(e['location'] or '?')[:26]:<26} srcs={','.join(e['distinct_sources'][:5])}")
    return dict(n_in=nin, n_out=nout, collapse=nin/nout, dist=dict(dist),
                redundant=redundant, rows=rows)

def citation_graph(mc):
    """Which catalogs cite which other catalogs/sources -> circularity check."""
    catname = {v[0]: k for k, v in corpus.CATALOG_META.items()}
    edges = collections.Counter()
    for e in mc["events"]:
        for ch in e["citation_chain"]:
            src = ch["catalog"]
            for r in ch["refs"]:
                import phase1
                k = phase1.norm_ref(r.get("text", ""))
                if k: edges[(src, k)] += 1
    print("\n  CATALOG -> SOURCE citation edges (top 30):")
    for (a, b), n in edges.most_common(30):
        print(f"    {a:<20} -> {b:<22} {n}")
    # cycles among catalog-identified keys
    cat_keys = {"HATCH", "NICAP", "VALLEE", "DOLAN", "EBERHART", "JOHNSON",
                "OVERMEIRE", "RR0", "PROJECT_BLUEBOOK", "APRO", "CUFOS", "FSR"}
    g = collections.defaultdict(set)
    name2key = {"Hatch_UDB": "HATCH", "NICAP": "NICAP", "Magonia": "VALLEE",
                "WondersInTheSky": "VALLEE", "Dolan": "DOLAN",
                "EberhartUFOI": "EBERHART", "Johnson": "JOHNSON",
                "Overmeire": "OVERMEIRE", "rr0": "RR0",
                "BlueBookUnknowns": "PROJECT_BLUEBOOK"}
    for (a, b), n in edges.items():
        ka = name2key.get(a)
        if ka and b in cat_keys and n >= 3: g[ka].add(b)
    cycles = []
    for a in g:
        for b in g[a]:
            if b in g and a in g[b] and a < b: cycles.append((a, b, "mutual"))
    print("\n  CIRCULAR CITATION (mutual references between compilations):")
    for c in cycles: print(f"    {c[0]} <-> {c[1]}")
    if not cycles: print("    none detected at threshold >=3 refs")
    return edges, cycles

if __name__ == "__main__":
    res = {}
    for mode in ("strict", "inclusive"):
        res[mode] = stats(load(mode), mode.upper())
    print(f"\n{'='*70}\nCOLLAPSE FACTOR INTERVAL")
    s, i = res["strict"], res["inclusive"]
    print(f"  independent events: [{i['n_out']}, {s['n_out']}]")
    print(f"  collapse factor:    [{s['collapse']:.3f}x, {i['collapse']:.3f}x]")
    print(f"  duplicate share:    [{s['redundant']/s['n_in']*100:.1f}%, "
          f"{i['redundant']/i['n_in']*100:.1f}%] of records are redundant copies")
    citation_graph(load("inclusive"))
