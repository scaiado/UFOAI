"""PROJECT OMEGA - Phase 3: descriptor drift across 2,000 years.

Tests whether reported UAP morphology tracks the observer's contemporary
technology (cultural construction) or contains an era-invariant core.

CRITICAL CONFOUND, handled explicitly: the describer is not the witness.
Pre-1800 events exist in this corpus almost only via WondersInTheSky
(Vallee & Aubeck 2009) -- modern English paraphrases of Latin, Chinese and
medieval sources. Hatch writes telegraphic shorthand; Johnson writes prose.
So a raw era contrast is confounded with WHO WROTE THE TEXT AND WHEN.
The analysis therefore reports (a) the raw cross-era test and (b) a
WITHIN-CATALOG stratified test that holds the describer fixed. Only (b)
supports causal reading.
"""
from __future__ import annotations
import sys, re, json, math, collections
import numpy as np
from scipy import stats
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist
from sklearn.metrics import silhouette_score
sys.path.insert(0, "/home/user/UFOAI/omega")
import corpus

RNG = np.random.default_rng(31415)

# ----------------------------------------------------------------- lexicon
# Grouped so that era-referent families can be tested separately from
# shape/behaviour families.
LEX = {
 # --- SHAPE (era-neutral geometry)
 "shape_disc":      r"\b(disc|disk|saucer|discoid|lenticular)\b",
 "shape_sphere":    r"\b(sphere|spherical|ball|globe|globular|orb|round\s+object)\b",
 "shape_cigar":     r"\b(cigar|cylinder|cylindrical|torpedo|tube-?like|spindle)\b",
 "shape_triangle":  r"\b(triangle|triangular|delta|boomerang|chevron|arrow-?head|\bvee\b|v-?shaped|wedge)\b",
 "shape_oval":      r"\b(oval|ovoid|egg-?shaped|elliptical|football-?shaped)\b",
 "shape_cone":      r"\b(cone|conical|funnel|top-?shaped|bell-?shaped)\b",
 "shape_rect":      r"\b(rectangular|rectangle|square|box-?like|cube|slab)\b",
 "shape_cross":     r"\b(cross-?shaped|cruciform|crucifix)\b",
 "shape_crescent":  r"\b(crescent|half-?moon|sickle|horseshoe)\b",
 "shape_wheel":     r"\b(wheel|ring|annular|doughnut|donut|toroid)\b",
 "shape_point":     r"\b(point\s+of\s+light|star-?like|starlike|pinpoint|nocturnal\s+light|night\s+light)\b",
 "shape_cloud":     r"\b(cloud|cloud-?like|nebulous|vapou?r|misty|smoke-?like)\b",
 "shape_dome":      r"\b(dome|domed|cupola|hump)\b",
 # --- BEHAVIOUR (era-neutral kinematics)
 "beh_hover":       r"\b(hover|hovering|hovered|stationary|motionless|suspended)\b",
 "beh_fast":        r"\b(high\s+speed|very\s+fast|tremendous\s+speed|incredible\s+speed|shot\s+(away|up|off)|sped|rapid)\b",
 "beh_zigzag":      r"\b(zig-?zag|erratic|darting|jerky|bobbing|bobbed|wobbl|oscillat)\b",
 "beh_land":        r"\b(land|landed|landing|descend|descended|touch(ed)?\s+down|settled)\b",
 "beh_ascend":      r"\b(ascend|rose|rising|climbed|shot\s+upward|went\s+up)\b",
 "beh_pace":        r"\b(pace[sd]?|paced|paralleled|followed|chased|accompanied|escorted)\b",
 "beh_split":       r"\b(split|divided|separated\s+into|released|ejected|dropped\s+smaller)\b",
 "beh_formation":   r"\b(formation|in\s+a\s+line|abreast|echelon|group\s+of|cluster)\b",
 "beh_vanish":      r"\b(vanish|disappeared\s+(instantly|in\s+place)|blinked\s+out|winked\s+out)\b",
 "beh_rotate":      r"\b(rotat|spinning|spun|revolving|whirling)\b",
 "beh_maneuver":    r"\b(man(o|oe)uvre?|maneuver|right-?angle|90-?degree|sharp\s+turn|abrupt\s+turn)\b",
 # --- SENSORY
 "sens_silent":     r"\b(silent|no\s+(sound|noise)|soundless|noiseless)\b",
 "sens_sound":      r"\b(hum|humming|buzz|whirr|whine|whining|roar|hiss|beeping|whistl)\b",
 "sens_beam":       r"\b(beam|ray|searchlight|shaft\s+of\s+light|spotlight)\b",
 "sens_metallic":   r"\b(metallic|aluminium|aluminum|silver|silvery|shiny|polished|chrome)\b",
 "sens_glow":       r"\b(glow|glowing|luminous|incandescent|brilliant|blazing|fiery)\b",
 "sens_porthole":   r"\b(porthole|window|windows|opening|hatch|door)\b",
 "sens_colour":     r"\b(red|orange|green|blue|yellow|white|amber|purple)\b",
 "sens_trail":      r"\b(trail|contrail|exhaust|wake|tail|sparks|smoke)\b",
 "sens_odour":      r"\b(odou?r|smell|stench|sulphur|sulfur|burning\s+smell)\b",
 # --- PHYSICAL EFFECTS
 "eff_em":          r"\b(engine\s+(stall|stopp|fail)|motor\s+(stall|died)|radio\s+(interference|fail)|"
                    r"headlights?\s+(dim|fail|went\s+out)|power\s+(outage|fail)|compass|instrument)\b",
 "eff_trace":       r"\b(trace|imprint|depression|burn(ed|t)?\s+(ground|grass|vegetation)|"
                    r"tripod|landing\s+marks|scorched|circle\s+of)\b",
 "eff_animal":      r"\b(dog[s]?\s+(bark|howl)|cattle|horse[s]?\s+(shied|bolted|panick)|animals?\s+(panic|flee)|livestock)\b",
 "eff_injury":      r"\b(burn[s]?\s+(on|to)\s+(his|her|the)|injur|nausea|paralys|paraliz|blister|radiation\s+sick)\b",
 "eff_entity":      r"\b(occupant|entity|entities|humanoid|being[s]?|creature|figure[s]?|dwarf|dwarves|"
                    r"little\s+men|small\s+men|alien|ufonaut|pilot\s+seen)\b",
 # --- ERA-REFERENT TECHNOLOGY (the technology-mirror test)
 "tech_airship":    r"\b(airship|air-?ship|dirigible|zeppelin|balloon|gondola|propeller[s]?\s+and\s+wings|aerial\s+navigator)\b",
 "tech_aircraft":   r"\b(aeroplane|airplane|aircraft-?like|like\s+an?\s+(plane|airplane|jet)|wings|fuselage|wingless)\b",
 "tech_rocket":     r"\b(rocket|missile|projectile|ghost\s+rocket|booster|re-?entry)\b",
 "tech_satellite":  r"\b(satellite|sputnik|space\s*craft|spaceship|space\s+vehicle|capsule|module)\b",
 "tech_drone":      r"\b(drone|uav|quad-?copter|unmanned)\b",
 "tech_helicopter": r"\b(helicopter|chopper|rotor)\b",
 "tech_chariot":    r"\b(chariot|shield|lance|spear|cross\s+in\s+the\s+sky|dragon|serpent\s+in\s+the\s+(sky|air)|"
                    r"flaming\s+(sword|torch)|celestial\s+(ship|vessel)|cloudship)\b",
 # --- PRE-MODERN FRAMING
 "frame_portent":   r"\b(portent|omen|prodigy|wonder|sign\s+in\s+the\s+(sky|heavens)|judgment\s+day|"
                    r"apparition|vision|miracle|divine|angel|saint)\b",
 "frame_radar":     r"\b(radar|radarscope|scope|blip[s]?|tracked\s+by|transponder)\b",
 "frame_photo":     r"\b(photograph|photo|film|camera|footage|video|snapshot)\b",
}
RX = {k: re.compile(v, re.I) for k, v in LEX.items()}

ERAS = [("1_preindustrial", -10000, 1800), ("2_industrial", 1800, 1945),
        ("3_atomic", 1945, 1957), ("4_spaceage", 1957, 1990),
        ("5_digital", 1990, 2030)]
def era_of(y):
    for name, lo, hi in ERAS:
        if lo <= y < hi: return name
    return None

def featurize(events):
    keys = list(LEX)
    rows, meta = [], []
    for e in events:
        if not e["year"]: continue
        er = era_of(e["year"])
        if er is None: continue
        d = e["description"] or ""
        v = [1 if RX[k].search(d) else 0 for k in keys]
        rows.append(v)
        meta.append(dict(era=er, year=e["year"], catalog=e["catalogs"][0],
                         ncat=e["n_catalogs"], cred=e["credibility"],
                         prov=e["provenance_depth"], nchar=len(d)))
    return np.array(rows, dtype=np.int8), keys, meta

def mutual_info_bits(x, era_idx, n_eras):
    """MI between a binary descriptor and era, in bits."""
    n = len(x)
    mi = 0.0
    px = np.array([1 - x.mean(), x.mean()])
    for e in range(n_eras):
        pe = (era_idx == e).mean()
        if pe == 0: continue
        for b in (0, 1):
            pxe = ((x == b) & (era_idx == e)).mean()
            if pxe > 0 and px[b] > 0:
                mi += pxe * math.log2(pxe / (px[b] * pe))
    return mi

def cramers_v(table):
    chi2, p, dof, exp = stats.chi2_contingency(table)
    n = table.sum()
    return math.sqrt(chi2 / (n * (min(table.shape) - 1))), chi2, p, dof

def main():
    mc = json.load(open("/home/user/UFOAI/data/processed/provenance/master_catalog_inclusive.json"))
    X, keys, meta = featurize(mc["events"])
    eras = [m["era"] for m in meta]
    enames = [e[0] for e in ERAS]
    era_idx = np.array([enames.index(e) for e in eras])
    print(f"[p3] events featurized={len(X)}  descriptors={len(keys)}")
    print("     per era:", {e: int((era_idx == i).sum()) for i, e in enumerate(enames)})
    print("     median description length by era:",
          {e: int(np.median([m["nchar"] for m in meta if m["era"] == e])) for e in enames})

    # ---------- 1. raw cross-era descriptor frequencies + MI
    print(f"\n{'descriptor':<18}" + "".join(f"{e.split('_')[1][:9]:>10}" for e in enames)
          + f"{'MI(bits)':>10}{'chi2 p':>11}")
    res = []
    for j, k in enumerate(keys):
        x = X[:, j].astype(np.int64)
        freqs = [x[era_idx == i].mean() if (era_idx == i).sum() else float("nan")
                 for i in range(len(enames))]
        tab = np.array([[int(((x == 1) & (era_idx == i)).sum()),
                         int(((x == 0) & (era_idx == i)).sum())] for i in range(len(enames))]).T
        tab = tab[:, tab.sum(axis=0) > 0]
        try: v, chi2, p, dof = cramers_v(tab)
        except Exception: v, chi2, p = float("nan"), float("nan"), float("nan")
        mi = mutual_info_bits(x, era_idx, len(enames))
        res.append(dict(key=k, freqs=freqs, mi=mi, p=p, v=v))
        print(f"{k:<18}" + "".join(f"{f*100:>9.1f}%" for f in freqs) + f"{mi:>10.4f}{p:>11.2e}")

    # ---------- 2. omnibus: descriptor x era independence
    big = np.array([[int(((X[:, j] == 1) & (era_idx == i)).sum()) for i in range(len(enames))]
                    for j in range(len(keys))])
    v, chi2, p, dof = cramers_v(big)
    print(f"\n[OMNIBUS] descriptor x era: chi2={chi2:.1f} dof={dof} p={p:.3e} Cramer's V={v:.4f}")

    # ---------- 3. the invariant core
    print("\n### INVARIANT CORE (MI < 0.01 bits with era)")
    core = sorted([r for r in res if r["mi"] < 0.01], key=lambda r: r["mi"])
    for r in core:
        print(f"  {r['key']:<18} MI={r['mi']:.5f}  freqs=" +
              " ".join(f"{f*100:.1f}%" for f in r["freqs"]))
    print(f"  -> {len(core)} of {len(keys)} descriptors are era-invariant at MI<0.01 bits")
    print("\n### MOST ERA-DEPENDENT (top 10 by MI)")
    for r in sorted(res, key=lambda r: -r["mi"])[:10]:
        print(f"  {r['key']:<18} MI={r['mi']:.4f}  freqs=" +
              " ".join(f"{f*100:.1f}%" for f in r["freqs"]))

    # ---------- 4. WITHIN-CATALOG control (describer held fixed)
    print("\n### WITHIN-CATALOG DRIFT (controls for who wrote the description)")
    cats = collections.Counter(m["catalog"] for m in meta)
    for cat, n in cats.most_common(6):
        sel = np.array([m["catalog"] == cat for m in meta])
        if sel.sum() < 300: continue
        ei = era_idx[sel]; Xs = X[sel]
        present = [i for i in range(len(enames)) if (ei == i).sum() >= 30]
        if len(present) < 2: continue
        sub = np.array([[int(((Xs[:, j] == 1) & (ei == i)).sum()) for i in present]
                        for j in range(len(keys))])
        sub = sub[sub.sum(axis=1) > 0]
        try:
            v2, chi2b, pb, dofb = cramers_v(sub)
            print(f"  {cat:<18} n={int(sel.sum()):<6} eras={[enames[i].split('_')[1] for i in present]}"
                  f"  V={v2:.4f} p={pb:.2e}")
        except Exception as ex:
            print(f"  {cat:<18} n={int(sel.sum())} -> {ex}")

    # ---------- 5. morphology clustering (Ward + silhouette)
    print("\n### MORPHOLOGY CLUSTERS (Ward, Jaccard distance, sampled)")
    shape_keys = [j for j, k in enumerate(keys) if k.startswith(("shape_", "beh_"))]
    mask = X[:, shape_keys].sum(axis=1) > 0
    idx = np.flatnonzero(mask)
    samp = RNG.choice(idx, size=min(6000, len(idx)), replace=False)
    Xs = X[np.ix_(samp, shape_keys)].astype(float)
    Dm = pdist(Xs, metric="jaccard")
    Z = linkage(Dm, method="ward")
    best = None
    for k in range(2, 11):
        lab = fcluster(Z, k, criterion="maxclust")
        if len(set(lab)) < 2: continue
        s = silhouette_score(Xs, lab, metric="jaccard")
        print(f"  k={k:<3} silhouette={s:.4f}")
        if best is None or s > best[1]: best = (k, s, lab)
    k, s, lab = best
    print(f"  -> optimal k={k} (silhouette {s:.4f})")
    sera = era_idx[samp]
    for c in sorted(set(lab)):
        m = lab == c
        top = sorted(((Xs[m][:, i].mean(), keys[shape_keys[i]]) for i in range(len(shape_keys))),
                     reverse=True)[:4]
        dist = [f"{(sera[m] == i).mean()*100:.0f}%" for i in range(len(enames))]
        print(f"  cluster {c} n={int(m.sum()):<5} era-mix={dist}  top=" +
              ", ".join(f"{nm}({fr*100:.0f}%)" for fr, nm in top))

    # ---------- 6. credibility bias
    print("\n### CREDIBILITY BIAS (Hatch credibility, high >=8 vs low <=6)")
    cred = np.array([m["cred"] if m["cred"] is not None else np.nan for m in meta])
    hi = cred >= 8; lo = (cred <= 6) & ~np.isnan(cred)
    print(f"  n_high={int(hi.sum())}  n_low={int(lo.sum())}")
    print(f"  {'descriptor':<18}{'high':>9}{'low':>9}{'ratio':>8}{'p':>11}")
    credrows = []
    for j, kk in enumerate(keys):
        a, b = X[hi, j].sum(), X[lo, j].sum()
        na, nb = hi.sum(), lo.sum()
        if a + b < 40: continue
        t = np.array([[a, na - a], [b, nb - b]])
        try: _, p = stats.fisher_exact(t)
        except Exception: p = float("nan")
        ra = (a / na) / max(1e-9, b / nb)
        credrows.append(dict(key=kk, hi=float(a/na), lo=float(b/nb), ratio=float(ra), p=float(p)))
        if p < 0.001 and (ra > 1.25 or ra < 0.8):
            print(f"  {kk:<18}{a/na*100:>8.1f}%{b/nb*100:>8.1f}%{ra:>8.2f}{p:>11.1e}")

    # ---------- 7. DECISIVE TEST: is the high-credibility subset MORE or LESS
    # era-dependent? The claim under test is "high-credibility witnesses report
    # era-invariant morphology => real phenomenon".
    print("\n### ERA-DEPENDENCE WITHIN CREDIBILITY STRATA")
    for label, sel in (("high cred (>=8)", hi), ("low cred (<=6)", lo)):
        ei = era_idx[sel]; Xs2 = X[sel]
        present = [i for i in range(len(enames)) if (ei == i).sum() >= 30]
        sub = np.array([[int(((Xs2[:, j] == 1) & (ei == i)).sum()) for i in present]
                        for j in range(len(keys))])
        sub = sub[sub.sum(axis=1) > 0]
        v3, chi3, p3, dof3 = cramers_v(sub)
        mis = [mutual_info_bits(Xs2[:, j].astype(np.int64), ei, len(enames)) for j in range(len(keys))]
        ninv = sum(1 for m in mis if m < 0.01)
        print(f"  {label:<18} n={int(sel.sum()):<6} Cramer's V={v3:.4f} p={p3:.2e}"
              f"  mean MI={np.mean(mis):.5f}  era-invariant descriptors={ninv}/{len(keys)}")
    out = dict(n=len(X), eras={e: int((era_idx == i).sum()) for i, e in enumerate(enames)},
               omnibus=dict(chi2=float(chi2), dof=int(dof), p=float(p), cramers_v=float(v)),
               descriptors=[{k2: (v2 if not isinstance(v2, list) else [float(x) for x in v2])
                             for k2, v2 in r.items()} for r in res],
               invariant_core=[r["key"] for r in core], optimal_k=int(best[0]),
               silhouette=float(best[1]), credibility=credrows)
    import os
    os.makedirs("/home/user/UFOAI/data/processed/descriptor_drift", exist_ok=True)
    json.dump(out, open("/home/user/UFOAI/data/processed/descriptor_drift/drift.json", "w"), indent=1)

if __name__ == "__main__":
    main()
