"""PROJECT OMEGA - Phase 9: physical-trace site dossiers for soil assay.

The only route to the one evidence class that could settle the question (a
retained specimen with non-solar-system isotope ratios) is to go to ground
where the catalog says material was deposited. This generates ranked,
coordinate-level dossiers.

ASSAY DESIGN NOTE. The brief asked for "plutonium-244 and other
extraterrestrial markers". Pu-244 is the wrong test: it is an r-process
primordial nuclide used as a marker in deep-sea ferromanganese crusts over
Myr timescales, not a soil signature of a craft. The actual cosmochemical
standard for non-terrestrial origin is MASS-INDEPENDENT ISOTOPE ANOMALY:
solar-system material falls on a mass-fractionation line, extra-solar
material does not. The assays specified below follow that standard.
"""
from __future__ import annotations
import sys, re, json, csv, math, collections
sys.path.insert(0, "/home/user/UFOAI/omega")
import corpus

MC = "/home/user/UFOAI/data/processed/provenance/master_catalog_inclusive.json"
OUT = "/home/user/UFOAI/data/processed/soil_assay"

# Hatch codes bearing on deposited physical material, weighted by how
# directly they imply recoverable substrate.
TRACE_W = {
    "SMP": 5.0,   # sampling of plant/animal/soil/tissue/specimens taken
    "RDA": 5.0,   # radiation / high-energy fields detected
    "DRT": 4.0,   # dirt/soil traces/marks/footprints
    "TRC": 4.0,   # physical traces
    "VEG": 3.0,   # plants affected or sampled / crop circles
    "LND": 2.0,   # UFO landing or any part touches ground
    "ANI": 1.5,   # animals affected or injuries/marks
    "INJ": 1.5,   # injuries, illness, mutilations
    "SUB": 1.0,   # submerged/emerged (water-sediment case)
}
TEXT_TRACE = {
    "burn":      (r"\bburn(ed|t|ing)?\b|scorch|charred|singe", 3.0),
    "depression":(r"\bdepression|imprint|indentation|tripod|pod\s*marks|landing\s+marks", 4.0),
    "soil":      (r"\bsoil|earth\s+(was|were)|ground\s+(was|were)|sand\s+(was|were)|dirt\b", 3.0),
    "ring":      (r"\b(circle|ring)\s+of\s+(dried|dead|burnt|scorched|flattened)|crop\s+circle", 4.0),
    "residue":   (r"\bresidue|deposit|slag|metal\s+fragment|molten|oily|substance\s+found", 5.0),
    "radiation": (r"\bradiation|radioactiv|geiger|counts?\s+per|roentgen|millirem", 5.0),
    "magnetic":  (r"\bmagnet(ic|ised|ized)|compass\s+(deviat|anomal)", 3.0),
    "vegdeath":  (r"\b(grass|vegetation|crops?|plants?|trees?)\s+(was|were|had)?\s*"
                  r"(dead|dying|withered|wilted|flattened|burnt|burned|scorched|discoloured|discolored)", 3.5),
}
TRX = {k: (re.compile(v[0], re.I), v[1]) for k, v in TEXT_TRACE.items()}

ASSAYS = {
 "residue": ["PGE suite by ICP-MS (Ir, Os, Pt, Pd, Ru, Rh); compare Ir/Os to chondritic 1.0-1.1",
             "Cr isotopes (54Cr/52Cr) and Ti isotopes (50Ti/46Ti) by MC-ICP-MS - mass-INDEPENDENT anomaly is the diagnostic test for non-solar-system origin",
             "Oxygen three-isotope (d17O vs d18O) vs terrestrial fractionation line",
             "SEM-EDS on any metallic fragment for unequilibrated phases"],
 "radiation": ["HPGe gamma spectrometry: Cs-137, Co-60, Am-241, Ra-226 (presence indicates MUNDANE contamination and is an exclusion test)",
               "alpha spectrometry for actinides; U-235/U-238 ratio vs natural 0.00725",
               "if any anomaly: accelerator MS for Fe-60 / Al-26"],
 "burn":      ["thermoluminescence / OSL on quartz grains to date and bound peak temperature",
               "magnetic susceptibility profile vs depth (thermal remanence)",
               "FTIR / XRD for mineral phase change (quartz -> cristobalite indicates >1000 C)"],
 "depression":["bulk density and penetrometer transect vs off-site control",
               "micromorphology thin-section for compaction fabric"],
 "soil":      ["major/trace element ICP-MS vs paired off-site control at matched depth",
               "pH, EC, organic carbon vs control"],
 "ring":      ["node elongation and cell-wall expansion in affected stems (microwave signature)",
               "soil nitrate/ammonium vs control; magnetite microsphere count"],
 "magnetic":  ["magnetic susceptibility mapping; magnetite spherule separation and SEM-EDS"],
 "vegdeath":  ["plant tissue ICP-MS; chlorophyll fluorescence on regrowth; soil phytotoxicity assay"],
}

# Known non-UAP high-energy events that score high on "physical traces" for
# obvious reasons, and the nuclear-detonation records Phase 2 found embedded in
# these catalogs. Excluded by the same rule used in phase2c.
EXCLUDE = re.compile(r"""atomic\s+bomb|nuclear\s+(weapon|device|test)|is\s+detonated|
 hiroshima|nagasaki|enola\s+gay|bockscar|castle\s+bravo|trinity\s+site|
 tunguska|podkamennaya|chelyabinsk|meteorite\s+fall|crater\s+(was|is)\s+formed|
 volcan|eruption|earthquake\s+damage|aircraft\s+crash(ed)?\s+|plane\s+crash""",
 re.I | re.X)

def main():
    import os
    os.makedirs(OUT, exist_ok=True)
    mc = json.load(open(MC))
    rows = []
    for e in mc["events"]:
        if e["lat"] is None or not e["year"]: continue
        codes = set(e["attrs"])
        cw = sum(TRACE_W.get(c, 0) for c in codes)
        d = e["description"] or ""
        thits = {k: w for k, (rx, w) in TRX.items() if rx.search(d)}
        tw = sum(thits.values())
        if cw + tw < 4.0: continue
        if EXCLUDE.search(d): continue
        # substrate class drives the assay list
        assays, seen = [], set()
        for k in list(thits) + ([ "residue"] if "SMP" in codes else []) + \
                 (["radiation"] if "RDA" in codes else []) + \
                 (["soil"] if ("DRT" in codes or "TRC" in codes) else []) + \
                 (["vegdeath"] if "VEG" in codes else []):
            for a in ASSAYS.get(k, []):
                if a not in seen: seen.add(a); assays.append(a)
        score = (cw + tw)
        score *= 1.0 + 0.15 * min(e["n_catalogs"] - 1, 6)        # corroboration
        score *= 1.0 + 0.04 * min(e["provenance_depth"], 10)      # lineage depth
        if e["credibility"]: score *= 1.0 + 0.03 * min(e["credibility"] - 6, 8)
        rows.append(dict(
            event_id=e["event_id"], score=round(score, 2),
            date=f"{e['year']:04d}-{e['month'] or 0:02d}-{e['day'] or 0:02d}",
            lat=round(e["lat"], 5), lon=round(e["lon"], 5),
            location=e["location"] or "", country=e["country"] or "",
            n_catalogs=e["n_catalogs"], provenance_depth=e["provenance_depth"],
            credibility=e["credibility"],
            trace_codes=",".join(sorted(c for c in codes if c in TRACE_W)),
            trace_text=",".join(sorted(thits)),
            code_weight=cw, text_weight=round(tw, 1),
            assays=assays, description=d[:400],
            catalogs=",".join(e["catalogs"]),
            site_access="UNVERIFIED - requires imagery/land-registry check",
        ))
    rows.sort(key=lambda r: -r["score"])
    # ---- RETAINED-SAMPLE TRACK -------------------------------------------
    # Digging a 60-year-old field is a poor bet: a thin surface deposit is
    # dispersed by ploughing, leaching and bioturbation. But SMP marks events
    # where material WAS collected at the time. Those samples went to APRO,
    # CUFOS, NICAP, Blue Book or university labs, and surviving archived
    # material is far more likely to be assayable than in-situ soil.
    retained = [r for r in rows if "SMP" in r["trace_codes"]]
    for r in retained:
        r["archive_leads"] = [c for c in r["catalogs"].split(",")]
    json.dump(dict(n=len(retained), note="events where physical samples were "
                   "collected at the time; pursue archived material, not the site",
                   sites=retained),
              open(f"{OUT}/retained_sample_leads.json", "w"), indent=1)
    print(f"[p9] retained-sample leads (SMP coded): {len(retained)}")
    json.dump(dict(n=len(rows), generated="omega-phase9", sites=rows),
              open(f"{OUT}/soil_assay_targets.json", "w"), indent=1)
    with open(f"{OUT}/soil_assay_targets.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rank","event_id","score","date","lat","lon","location","country",
                    "n_catalogs","provenance_depth","credibility","trace_codes",
                    "trace_text","n_assays","catalogs"])
        for i, r in enumerate(rows, 1):
            w.writerow([i, r["event_id"], r["score"], r["date"], r["lat"], r["lon"],
                        r["location"], r["country"], r["n_catalogs"],
                        r["provenance_depth"], r["credibility"], r["trace_codes"],
                        r["trace_text"], len(r["assays"]), r["catalogs"]])
    print(f"[p9] physical-trace candidate sites: {len(rows)}")
    print(f"[p9] wrote {OUT}/soil_assay_targets.json and .csv")
    byc = collections.Counter(r["country"] or "?" for r in rows)
    print("     by country:", dict(byc.most_common(10)))
    bydec = collections.Counter(int(r["date"][:4]) // 10 * 10 for r in rows)
    print("     by decade:", dict(sorted(bydec.items())))
    print(f"\n  TOP 25 PRIORITY SITES")
    print(f"  {'#':>3} {'score':>6} {'date':<11} {'lat':>10} {'lon':>11} {'cat':>4} "
          f"{'codes':<18} {'location':<28} desc")
    for i, r in enumerate(rows[:25], 1):
        print(f"  {i:>3} {r['score']:>6.1f} {r['date']:<11} {r['lat']:>10.4f} {r['lon']:>11.4f} "
              f"{r['n_catalogs']:>4} {r['trace_codes'][:17]:<18} {r['location'][:27]:<28} "
              f"{r['description'][:60]}")
    return rows

if __name__ == "__main__":
    main()
