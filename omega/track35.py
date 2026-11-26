"""TRACK 3 + TRACK 5: deep-provenance audit and echo-chamber mapping.

Both are fully offline. Track 5 builds the directed citation graph over the
whole corpus and measures per-catalog duplicate inflation; Track 3 produces
per-event dossiers for the deeply-attested subset.
"""
from __future__ import annotations
import sys, json, re, csv, collections, math
import numpy as np
sys.path.insert(0, "/home/user/UFOAI/omega")
import corpus, phase1

MC = "/home/user/UFOAI/data/processed/provenance/master_catalog_inclusive.json"
OUT = "/home/user/UFOAI/data/processed/provenance"
RNG = np.random.default_rng(917917)

# Which normalized ref keys correspond to catalogs that are THEMSELVES in this
# corpus (i.e. downstream compilations) vs genuine upstream primaries.
IN_CORPUS = {"HATCH","NICAP","VALLEE","DOLAN","EBERHART","JOHNSON","OVERMEIRE","RR0",
             "UFOEVIDENCE","PROJECT_BLUEBOOK"}
PRIMARY_KIND = {
 "PROJECT_BLUEBOOK":"government investigation", "FBI":"government", "CIA":"government",
 "USAF":"government", "CONDON":"government-funded study", "NEWSPAPER":"contemporary press",
 "NYT":"contemporary press", "APRO":"civilian research org", "NICAP":"civilian research org",
 "MUFON":"civilian research org", "CUFOS":"civilian research org", "FSR":"civilian journal",
 "NUFORC":"civilian reporting centre", "HYNEK":"named investigator",
 "KEYHOE":"named investigator", "VALLEE":"named investigator",
 "AGOBARD":"primary manuscript", "ARCHIVE":"archive copy", "WIKIPEDIA":"tertiary",
 "FINDAGRAVE":"tertiary/biographical",
}

def main():
    mc = json.load(open(MC)); ev = mc["events"]
    catyear = {v[0]: v[1] for v in corpus.CATALOG_META.values()}

    # ───────────────────────── TRACK 5: citation graph
    edges = collections.Counter()
    refkeys_per_event = []
    for e in ev:
        ks = collections.Counter()
        for ch in e["citation_chain"]:
            src = ch["catalog"]
            for r in ch["refs"]:
                k = phase1.norm_ref(r.get("text", ""))
                if k:
                    edges[(src, k)] += 1
                    ks[k] += 1
        refkeys_per_event.append(ks)

    print("=" * 86)
    print("TRACK 5  ECHO-CHAMBER MAP")
    allkeys = collections.Counter()
    for ks in refkeys_per_event: allkeys.update(ks)
    print(f"  distinct normalized source keys: {len(allkeys)}")
    print(f"  citation edges (catalog -> source): {len(edges)}  total citations: {sum(edges.values())}")

    # root sources = cited keys that are NOT themselves catalogs in this corpus
    roots = {k: v for k, v in allkeys.items() if k not in IN_CORPUS}
    print(f"\n  ROOT SOURCES (cited, not themselves a corpus catalog): {len(roots)}")
    print(f"  {'source':<26}{'citations':>10}  kind")
    for k, v in sorted(roots.items(), key=lambda x: -x[1])[:22]:
        print(f"  {k:<26}{v:>10}  {PRIMARY_KIND.get(k,'uncategorised')}")

    # per-catalog duplicate inflation
    print(f"\n  PER-CATALOG DUPLICATE INFLATION")
    print(f"  {'catalog':<20}{'records':>9}{'events':>8}{'unique':>8}{'infl':>7}{'dup_share':>11}")
    rec_by = collections.Counter(); ev_by = collections.Counter(); uniq_by = collections.Counter()
    for e in ev:
        for uid in e["member_uids"]: rec_by[uid.split("#")[0]] += 1
        for c in set(e["catalogs"]):
            ev_by[c] += 1
            if e["n_catalogs"] == 1: uniq_by[c] += 1
    rows = []
    for c in sorted(rec_by, key=lambda x: -rec_by[x]):
        n, nev, u = rec_by[c], ev_by[c], uniq_by[c]
        rows.append((c, n, nev, u, n / max(nev, 1), 1 - u / max(nev, 1)))
        print(f"  {c:<20}{n:>9}{nev:>8}{u:>8}{n/max(nev,1):>7.2f}{(1-u/max(nev,1))*100:>10.1f}%")

    # echo depth: longest publication-year span within an event's catalog set
    depths = []
    for e in ev:
        ys = [catyear.get(c) for c in e["catalogs"] if catyear.get(c)]
        depths.append((max(ys) - min(ys)) if len(ys) >= 2 else 0)
    depths = np.array(depths)
    print(f"\n  ECHO SPAN (years between earliest and latest compilation citing an event)")
    print(f"    mean={depths.mean():.1f}  median={np.median(depths):.0f}  max={depths.max()}")
    for t in (0, 10, 25, 50, 75):
        print(f"    span >= {t:>2} yr: {int((depths>=t).sum())} events ({(depths>=t).mean()*100:.1f}%)")

    # ───────────────────────── TRACK 3: the deep-provenance subset
    deep = [ (e, refkeys_per_event[i]) for i, e in enumerate(ev) if e["n_catalogs"] >= 5 ]
    print("\n" + "=" * 86)
    print(f"TRACK 3  DEEP-PROVENANCE AUDIT  (events in >=5 catalogs: {len(deep)})")
    dossiers = []
    for e, ks in deep:
        root_ks = {k: v for k, v in ks.items() if k not in IN_CORPUS}
        downstream = {k: v for k, v in ks.items() if k in IN_CORPUS}
        ys = [catyear.get(c) for c in e["catalogs"] if catyear.get(c)]
        indep = len(root_ks)
        # independence class
        if indep == 0:
            cls = "UNVERIFIABLE - cites only other compilations"
        elif indep == 1:
            cls = "SINGLE-ROOT - all attestation traces to one upstream source"
        elif indep <= 3:
            cls = "MULTI-ROOT (2-3 upstream sources)"
        else:
            cls = f"MULTI-ROOT ({indep} upstream sources)"
        dossiers.append(dict(
            event_id=e["event_id"],
            date=f"{e['year']}-{e['month'] or 0:02d}-{e['day'] or 0:02d}",
            location=e["location"], lat=e["lat"], lon=e["lon"],
            n_catalogs=e["n_catalogs"], n_records=e["n_records"],
            catalogs=e["catalogs"],
            earliest_compilation=min(ys) if ys else None,
            latest_compilation=max(ys) if ys else None,
            echo_span_years=(max(ys) - min(ys)) if len(ys) >= 2 else 0,
            n_independent_roots=indep,
            independence_class=cls,
            root_sources={k: int(v) for k, v in sorted(root_ks.items(), key=lambda x: -x[1])},
            downstream_citations={k: int(v) for k, v in sorted(downstream.items(), key=lambda x: -x[1])},
            credibility=e["credibility"], attrs=e["attrs"],
            description=e["description"][:500],
        ))
    cc = collections.Counter(d["independence_class"].split(" ")[0] for d in dossiers)
    print(f"\n  INDEPENDENCE CLASSIFICATION of the {len(dossiers)} deeply-attested events:")
    for k, v in cc.most_common():
        print(f"    {k:<16}{v:>5} ({v/len(dossiers)*100:.1f}%)")
    nroots = np.array([d["n_independent_roots"] for d in dossiers])
    print(f"\n  independent upstream roots per event: mean={nroots.mean():.2f} "
          f"median={np.median(nroots):.0f} max={nroots.max()}")
    print(f"    0 roots: {int((nroots==0).sum())}   1 root: {int((nroots==1).sum())}   "
          f">=4 roots: {int((nroots>=4).sum())}")

    # NULL TEST: is observed root diversity higher than chance given citation counts?
    print("\n  NULL TEST: permute source attributions across events, preserving each")
    print("  event's citation COUNT and the corpus-wide source frequency distribution.")
    pool = []
    for ks in refkeys_per_event: pool += [k for k, v in ks.items() for _ in range(v)]
    pool = np.array(pool)
    counts = np.array([sum(ks.values()) for e, ks in deep])
    obs_mean = nroots.mean()
    null = np.empty(2000)
    for i in range(2000):
        draw = RNG.choice(pool, size=counts.sum(), replace=False) if counts.sum() <= len(pool) \
               else RNG.choice(pool, size=counts.sum(), replace=True)
        pos = 0; tot = 0
        for c in counts:
            seg = draw[pos:pos+c]; pos += c
            tot += len({x for x in seg if x not in IN_CORPUS})
        null[i] = tot / len(counts)
    p = (1 + int((null >= obs_mean).sum())) / 2001
    print(f"    observed mean independent roots = {obs_mean:.3f}")
    print(f"    null = {null.mean():.3f} +/- {null.std(ddof=1):.3f}   p = {p:.4f}")
    verdict = ("observed diversity is LOWER than chance -> attestation is concentrated "
               "in few sources (echo chamber)" if obs_mean < null.mean() else
               "observed diversity exceeds chance -> genuinely multi-sourced")
    print(f"    -> {verdict}")

    json.dump(dict(n=len(dossiers), null_test=dict(observed=float(obs_mean),
              null_mean=float(null.mean()), null_sd=float(null.std(ddof=1)), p=p),
              dossiers=dossiers), open(f"{OUT}/track3_deep_provenance.json", "w"), indent=1)
    json.dump(dict(root_sources=dict(roots), edges={f"{a}|{b}": int(v) for (a, b), v in edges.items()},
              inflation=[dict(catalog=r[0], records=r[1], events=r[2], unique=r[3],
                              inflation=r[4], dup_share=r[5]) for r in rows]),
              open(f"{OUT}/track5_echo_chamber.json", "w"), indent=1)
    with open(f"{OUT}/track3_deep_provenance.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["event_id","date","location","lat","lon","n_catalogs","n_records",
                    "echo_span_years","n_independent_roots","independence_class",
                    "root_sources","credibility"])
        for d in dossiers:
            w.writerow([d["event_id"],d["date"],d["location"],d["lat"],d["lon"],
                        d["n_catalogs"],d["n_records"],d["echo_span_years"],
                        d["n_independent_roots"],d["independence_class"],
                        ";".join(d["root_sources"]),d["credibility"]])
    print(f"\n  wrote track3_deep_provenance.{{json,csv}} and track5_echo_chamber.json")

    print("\n  TOP 20 BY INDEPENDENT UPSTREAM ROOTS")
    print(f"  {'roots':>6}{'cat':>5}{'span':>6}  {'date':<12}{'location':<28} roots")
    for d in sorted(dossiers, key=lambda x: (-x["n_independent_roots"], -x["n_catalogs"]))[:20]:
        print(f"  {d['n_independent_roots']:>6}{d['n_catalogs']:>5}{d['echo_span_years']:>6}  "
              f"{d['date']:<12}{(d['location'] or '?')[:27]:<28} "
              f"{','.join(list(d['root_sources'])[:5])}")
    print("\n  THE UNVERIFIABLE SET: deeply-attested events whose every citation")
    print("  points at another compilation in this same corpus (zero upstream roots):")
    zero = [d for d in dossiers if d["n_independent_roots"] == 0]
    for d in zero[:15]:
        print(f"    {d['n_catalogs']}cat {d['date']:<12} {(d['location'] or '?')[:30]:<31} "
              f"{d['description'][:52]}")
    print(f"    ... {len(zero)} such events total")

if __name__ == "__main__":
    main()
