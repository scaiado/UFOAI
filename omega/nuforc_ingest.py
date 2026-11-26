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


def load_gazetteer():
    """{(state_code, normalised_name): (lat, lon, pop)}, best population wins."""
    g = {}
    if not os.path.isdir(GAZ):
        return g
    for fn in sorted(os.listdir(GAZ)):
        if not fn.endswith(".json"):
            continue
        st = fn[:-5].split("_")[-1]
        try:
            rows = json.load(open(os.path.join(GAZ, fn), encoding="utf-8"))
        except Exception:
            continue
        for r in rows:
            k = (st, norm_name(r.get("name")))
            if not k[1]:
                continue
            pop = r.get("pop") or 0
            old = g.get(k)
            if old is None or (pop or 0) > (old[2] or 0):
                g[k] = (r["lat"], r["lon"], pop)
    return g


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
    print(f"gazetteer entries: {len(gaz)}"
          f"{'  (EMPTY -- records will carry no coordinates)' if not gaz else ''}")

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
            hit = gaz.get(key)
            stats["total"] += 1
            stats[f"prec:{prec}"] += 1
            stats["geocoded" if hit else "ungeocoded"] += 1
            if country:
                stats["has_country"] += 1
            desc = WS.sub(" ", str(row.get("summary") or "")).strip()
            recs.append({
                "uid": f"NUFORC#{i}", "catalog": "NUFORC", "source": "NUFORC",
                "source_id": str(i), "date_raw": (row.get("event_date_time") or "").strip(),
                "year": y, "month": mo, "day": d, "prec": prec,
                "date_uncertain": prec in ("year", "none"),
                "lat": hit[0] if hit else None, "lon": hit[1] if hit else None,
                "location": (f"{city}, {st}" if st else city)[:200],
                "country": country[:60], "desc": desc[:4000],
                "etype": (row.get("shape") or "").strip(),
                "duration": (row.get("duration") or "").strip(),
                "summary": True,          # NUFORC `summary` is a summary line
                "kv": {"Country": country, "Duration": (row.get("duration") or "").strip(),
                       "Shape": (row.get("shape") or "").strip(),
                       "Posted": (row.get("posted") or "").strip(),
                       "GeocodeSource": "wikidata_gazetteer" if hit else ""},
            })

    json.dump({"nuforc": recs}, open(f"{OUT}/nuforc.json", "w"), ensure_ascii=False)
    json.dump({k: v for k, v in pairs.most_common()},
              open(f"{OUT}/city_state_pairs.json", "w"), ensure_ascii=False, indent=0)

    print(f"\n=== INGEST ===")
    print(f"  records            : {stats['total']}")
    print(f"  distinct city|state: {len(pairs)}")
    print(f"  with country       : {stats['has_country']} "
          f"({stats['has_country']/stats['total']:.1%})")
    print(f"  geocoded           : {stats['geocoded']} "
          f"({stats['geocoded']/stats['total']:.1%})")
    print(f"  ungeocoded         : {stats['ungeocoded']}")
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
