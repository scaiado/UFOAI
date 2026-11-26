"""NUFORC -> corpus.Rec, as the modern-era arm.

HANDOFF section 1.8: 134,906 records (the 137,094 figure is a line count --
quoted fields contain embedded newlines).  Columns: month_year_of_event,
event_date_time, city, state_provinces, shape, duration, summary, posted.
NO latitude, NO longitude, NO country column.  Country is parenthetical inside
`city` ("Lachute (Canada)") for 18,188 rows.  33,976 distinct city|state pairs.

DELIBERATELY NOT REGISTERED IN corpus.CATALOG_META.  Adding a 134,906-record
catalogue to `load_all` would silently change every established result in
section 6.  This arm is opt-in: `load_nuforc()` here, explicitly.

CAVEAT carried from section 1.8: the `summary` column is NUFORC's short summary
line, not the full narrative.  `desc` is therefore a summary, and `Rec.summary`
is set True for every record so downstream code cannot mistake it for a full
report.
"""
import os, re, sys, csv, json, math, collections

sys.path.insert(0, "/home/user/UFOAI")
csv.field_size_limit(10 ** 7)

OUT = "data/processed/nuforc"
GAZ = "data/raw/gazetteer"

# ("Lachute (Canada)") -> country
PAREN = re.compile(r"\(([^)]{2,40})\)\s*$")
WS = re.compile(r"\s+")

# NUFORC writes a few hundred country spellings; only normalise the common ones.
COUNTRY_FIX = {
    "canada": "Canada", "uk/england": "United Kingdom",
    "uk/scotland": "United Kingdom", "uk/wales": "United Kingdom",
    "uk/northern ireland": "United Kingdom", "united kingdom": "United Kingdom",
    "mexico": "Mexico", "australia": "Australia", "new zealand": "New Zealand",
    "india": "India", "ireland": "Ireland", "germany": "Germany",
    "france": "France", "japan": "Japan", "brazil": "Brazil",
    "south africa": "South Africa", "netherlands": "Netherlands",
    "spain": "Spain", "italy": "Italy", "philippines": "Philippines",
    "puerto rico": "Puerto Rico",
}

US_STATES = set("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD "
                "MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD "
                "TN TX UT VT VA WA WV WI WY PR VI GU".split())
CA_PROV = set("AB BC MB NB NL NS NT NU ON PE QC SK YT".split())


def norm_name(s):
    """Fold a place name for joining: lowercase, strip accents/punct/suffixes."""
    s = (s or "").lower().strip()
    s = s.replace("&", "and")
    for a, b in (("á", "a"), ("à", "a"), ("â", "a"), ("ä", "a"), ("é", "e"),
                 ("è", "e"), ("ê", "e"), ("ë", "e"), ("í", "i"), ("î", "i"),
                 ("ï", "i"), ("ó", "o"), ("ô", "o"), ("ö", "o"), ("ú", "u"),
                 ("û", "u"), ("ü", "u"), ("ç", "c"), ("ñ", "n")):
        s = s.replace(a, b)
    s = re.sub(r"\b(city|town|village|township|borough|municipality|cdp)\b", " ", s)
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return WS.sub(" ", s).strip()


def split_city(raw):
    """-> (city, country_or_empty).  NUFORC puts country in parentheses."""
    c = (raw or "").strip()
    m = PAREN.search(c)
    if not m:
        return c, ""
    inner = m.group(1).strip()
    low = inner.lower()
    # Parentheses are also used for disambiguation ("close to", "near") --
    # only treat as a country when it looks like one.
    if any(k in low for k in ("near", "close", "outside", "between", "approx")):
        return WS.sub(" ", PAREN.sub("", c)).strip(), ""
    return WS.sub(" ", PAREN.sub("", c)).strip(), COUNTRY_FIX.get(low, inner)


DATE_RX = [
    (re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{2,4})"), ("m", "d", "y")),
    (re.compile(r"^(\d{4})-(\d{1,2})-(\d{1,2})"), ("y", "m", "d")),
]
MY_RX = re.compile(r"^(\d{1,2})/(\d{4})$")


def parse_dt(event_dt, month_year):
    """-> (year, month, day, precision)."""
    s = (event_dt or "").strip()
    for rx, order in DATE_RX:
        m = rx.match(s)
        if m:
            g = dict(zip(order, m.groups()))
            try:
                y, mo, d = int(g["y"]), int(g["m"]), int(g["d"])
            except (ValueError, KeyError):
                continue
            if y < 100:
                y += 1900 if y > 25 else 2000
            if 1400 <= y <= 2030 and 1 <= mo <= 12 and 1 <= d <= 31:
                return y, mo, d, "day"
    m = MY_RX.match((month_year or "").strip())
    if m:
        mo, y = int(m.group(1)), int(m.group(2))
        if 1400 <= y <= 2030 and 1 <= mo <= 12:
            return y, mo, None, "month"
    m = re.search(r"(19|20)\d{2}", s + " " + (month_year or ""))
    if m:
        return int(m.group(0)), None, None, "year"
    return None, None, None, "none"


# Geocode precision tiers, best first.  Recorded per record in
# kv["GeocodeSource"] so downstream analysis can filter BY PRECISION rather
# than trusting every coordinate equally -- section 6 records that the
# persistence result was falsified as a cross-pipeline geocoding artefact, so
# coordinate provenance is kept, not discarded.
TIERS = [("SET_", "wikidata_settlement"),   # P31/P279* human settlement, via box
         ("NOM_", "nominatim"),             # fallback geocoder
         ("",     "wikidata_anyentity")]    # P131+ recall set, no class filter


def load_gazetteer():
    """{tier_name: {(state, folded_name): (lat, lon, pop)}}, best population
    wins within a tier.  Lookup walks TIERS in order."""
    g = {name: {} for _, name in TIERS}
    if not os.path.isdir(GAZ):
        return g
    for fn in sorted(os.listdir(GAZ)):
        if not fn.endswith(".json"):
            continue
        stem = fn[:-5]
        tier = next(name for pre, name in TIERS
                    if pre and stem.startswith(pre)) \
            if any(pre and stem.startswith(pre) for pre, _ in TIERS) \
            else "wikidata_anyentity"
        st = stem.split("_")[-1]
        # gazetteer_nominatim.py files empty-state pairs (foreign cities such as
        # London and Sydney, which NUFORC leaves stateless) under the sentinel
        # "XX", because a filename cannot end in "_". The lookup key built below
        # uses the raw state field, which is "" for those rows, so without this
        # mapping every stateless pair would be geocoded and then never matched
        # back -- silently discarding that part of the Nominatim run.
        if st == "XX":
            st = ""
        try:
            rows = json.load(open(os.path.join(GAZ, fn), encoding="utf-8"))
        except Exception:
            continue
        d = g[tier]
        for r in rows:
            k = (st, norm_name(r.get("name")))
            if not k[1]:
                continue
            pop = r.get("pop") or 0
            old = d.get(k)
            if old is None or (pop or 0) > (old[2] or 0):
                d[k] = (r["lat"], r["lon"], pop)
    return g


def lookup(gaz, key):
    """-> (lat, lon, tier_name) or (None, None, "")."""
    for _, name in TIERS:
        hit = gaz.get(name, {}).get(key)
        if hit:
            return hit[0], hit[1], name
    return None, None, ""


def main():
    csv_path = None
    for a in sys.argv[1:]:
        if a.endswith(".csv"):
            csv_path = a
    if not csv_path or not os.path.exists(csv_path):
        print("usage: nuforc_ingest.py <path/to/ufo_sightings.csv>")
        sys.exit(2)
    os.makedirs(OUT, exist_ok=True)

    gaz = load_gazetteer()
    ntot = sum(len(v) for v in gaz.values())
    for _, name in TIERS:
        print(f"  gazetteer tier {name:<24}{len(gaz.get(name, {})):>8} keys")
    print(f"  total {ntot} keys"
          f"{'  (EMPTY -- records will carry no coordinates)' if not ntot else ''}")

    recs = []
    stats = collections.Counter()
    pairs = collections.Counter()
    with open(csv_path, newline="", encoding="utf-8", errors="replace") as fh:
        for i, row in enumerate(csv.DictReader(fh)):
            city, country = split_city(row.get("city"))
            st = (row.get("state_provinces") or "").strip().upper()
            y, mo, d, prec = parse_dt(row.get("event_date_time"),
                                      row.get("month_year_of_event"))
            if not country:
                country = ("United States" if st in US_STATES else
                           "Canada" if st in CA_PROV else "")
            key = (st, norm_name(city))
            pairs[f"{city}|{st}"] += 1
            la, lo, tier = lookup(gaz, key)
            stats["total"] += 1
            stats[f"prec:{prec}"] += 1
            stats["geocoded" if tier else "ungeocoded"] += 1
            if tier:
                stats[f"tier:{tier}"] += 1
            if country:
                stats["has_country"] += 1
            desc = WS.sub(" ", str(row.get("summary") or "")).strip()
            recs.append({
                "uid": f"NUFORC#{i}", "catalog": "NUFORC", "source": "NUFORC",
                "source_id": str(i), "date_raw": (row.get("event_date_time") or "").strip(),
                "year": y, "month": mo, "day": d, "prec": prec,
                "date_uncertain": prec in ("year", "none"),
                "lat": la, "lon": lo,
                "location": (f"{city}, {st}" if st else city)[:200],
                "country": country[:60], "desc": desc[:4000],
                "etype": (row.get("shape") or "").strip(),
                "duration": (row.get("duration") or "").strip(),
                "summary": True,          # NUFORC `summary` is a summary line
                "_city": city, "_state": st,
                "kv": {"Country": country, "Duration": (row.get("duration") or "").strip(),
                       "Shape": (row.get("shape") or "").strip(),
                       "Posted": (row.get("posted") or "").strip(),
                       "GeocodeSource": tier},
            })

    json.dump({"nuforc": [{k: v for k, v in r.items() if not k.startswith("_")}
                          for r in recs]},
              open(f"{OUT}/nuforc.json", "w"), ensure_ascii=False)
    json.dump({k: v for k, v in pairs.most_common()},
              open(f"{OUT}/city_state_pairs.json", "w"), ensure_ascii=False, indent=0)
    # Pairs that resolved in NO tier, by record count -- the Nominatim worklist.
    #
    # BUILT FROM THE PARSED FIELDS, NOT FROM THE DISPLAY STRING.  The first
    # version did `r["location"].rpartition(", ")`, and for a stateless location
    # rpartition returns ("", "", "London") -- so the city landed in BOTH fields
    # and 4,478 of 11,430 pairs (8,847 records) came out as 'London|London',
    # 'Sydney|Sydney', 'Melbourne|Melbourne'.  Nominatim was then queried with
    # state="London", and even its successes could not be matched back because
    # the lookup key carries an empty state.  NUFORC leaves `state_provinces`
    # blank for non-US/CA sightings, so this hit essentially every foreign city.
    #
    # Country is carried too: with no state, it is the only disambiguator
    # Nominatim can use.
    ung_pairs = collections.Counter()
    for r in recs:
        if r["lat"] is None:
            ung_pairs[f"{r['_city']}|{r['_state']}|{r['kv']['Country']}"] += 1
    json.dump({k: v for k, v in ung_pairs.most_common()},
              open(f"{OUT}/ungeocoded_pairs.json", "w"), ensure_ascii=False, indent=0)

    print(f"\n=== INGEST ===")
    print(f"  records            : {stats['total']}")
    print(f"  distinct city|state: {len(pairs)}")
    print(f"  with country       : {stats['has_country']} "
          f"({stats['has_country']/stats['total']:.1%})")
    print(f"  geocoded           : {stats['geocoded']} "
          f"({stats['geocoded']/stats['total']:.1%})")
    print(f"  ungeocoded         : {stats['ungeocoded']}")
    for _, name in TIERS:
        k = f"tier:{name}"
        if stats[k]:
            print(f"    via {name:<24}{stats[k]:>8} "
                  f"({stats[k]/stats['total']:.1%})")
    print(f"  date precision     : " + ", ".join(
        f"{k.split(':')[1]}={stats[k]}" for k in sorted(stats) if k.startswith("prec:")))
    dayprec = sum(v for k, v in stats.items() if k == "prec:day")
    print(f"  day-precision      : {dayprec} ({dayprec/stats['total']:.1%})")
    gd = sum(1 for r in recs if r["lat"] is not None and r["prec"] == "day")
    print(f"  day-precision AND geocoded (the usable modern arm): {gd}")
    print(f"\n  wrote {OUT}/nuforc.json  ({os.path.getsize(f'{OUT}/nuforc.json'):,} bytes)")
    print(f"  wrote {OUT}/city_state_pairs.json")
    print(f"\n  top ungeocoded pairs by record count:")
    ung = collections.Counter()
    for r in recs:
        if r["lat"] is None:
            ung[r["location"]] += 1
    for k, v in ung.most_common(10):
        print(f"    {v:>6}  {k}")


if __name__ == "__main__":
    main()
