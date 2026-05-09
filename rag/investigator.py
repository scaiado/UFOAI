import json
import logging
import os
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.cluster import DBSCAN

from config import PROCESSED_DIR, OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_DEFAULT_MODEL
from rag.vectorstore import get_chroma_client, get_or_create_collection, query_similar

logger = logging.getLogger(__name__)

CHUNKS_PATH = PROCESSED_DIR / "all_chunks.json"


def _load_chunks() -> list[dict]:
    if CHUNKS_PATH.exists():
        return json.loads(CHUNKS_PATH.read_text())
    return []


def _ask_llm(prompt: str, system: str = "") -> str:
    if not OPENROUTER_API_KEY:
        import ollama
        from config import OLLAMA_BASE_URL, CHAT_MODEL
        client = ollama.Client(host=OLLAMA_BASE_URL)
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        resp = client.chat(model=CHAT_MODEL, messages=messages)
        return resp["message"]["content"].strip()

    from openai import OpenAI
    client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=OPENROUTER_API_KEY)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    resp = client.chat.completions.create(model=OPENROUTER_DEFAULT_MODEL, messages=messages)
    return resp.choices[0].message.content.strip()


def detect_patterns() -> dict:
    chunks = _load_chunks()
    descriptions = [c["text"] for c in chunks if c.get("chunk_type") == "metadata" and c.get("text")]
    if not descriptions:
        return {"patterns": [], "error": "No metadata chunks found"}

    sample = descriptions[:80]
    prompt = (
        "Analyze these UAP incident descriptions and identify the TOP patterns:\n"
        "1. Most common SHAPES described (e.g., spherical, disc, triangular, orb, diamond)\n"
        "2. Most common MOVEMENTS (e.g., hovering, rapid acceleration, 90-degree turns)\n"
        "3. Most common OBSERVATION CONDITIONS (e.g., IR sensor, radar, visual, night)\n"
        "4. Most common DURATIONS\n"
        "5. Any CORRELATIONS between shape, location, and time period\n\n"
        "Return as JSON with keys: shapes, movements, conditions, durations, correlations.\n"
        "Each key maps to a list of {pattern, count, examples}.\n\n"
        f"Descriptions:\n{chr(10).join(f'- {d[:300]}' for d in sample)}"
    )

    raw = _ask_llm(prompt, system="You are a data analyst. Return ONLY valid JSON.")
    try:
        if "```" in raw:
            raw = raw.split("```")[1].split("```")[0]
            if raw.startswith("json"):
                raw = raw[4:]
        return {"patterns": json.loads(raw.strip()), "total_analyzed": len(sample)}
    except json.JSONDecodeError:
        return {"patterns": raw, "total_analyzed": len(sample)}


def find_hotspots(eps_km: float = 1000) -> dict:
    from pipeline.geocoder import geocode_all

    geocodes = geocode_all()
    chunks = _load_chunks()

    loc_groups = {}
    for c in chunks:
        loc = c.get("incident_location", "")
        if loc and loc in geocodes and loc not in ("Moon", "Low Earth Orbit", "N/A", ""):
            loc_groups.setdefault(loc, []).append(c)

    points = []
    labels = []
    for loc, cs in loc_groups.items():
        lat, lng = geocodes[loc]
        if isinstance(lat, (list, tuple)):
            lat, lng = lat[0], lat[1]
        points.append([lat, lng])
        labels.append({"location": loc, "count": len(cs), "chunks": cs[:5]})

    if len(points) < 2:
        return {"clusters": [], "total_locations": len(points)}

    coords = np.radians(np.array(points))
    from sklearn.metrics.pairwise import haversine_distances

    dists = haversine_distances(coords) * 6371
    clustering = DBSCAN(eps=eps_km, metric="precomputed", min_samples=1).fit(dists)

    clusters = {}
    for i, label in enumerate(clustering.labels_):
        clusters.setdefault(int(label), []).append(labels[i])

    result = []
    for cid, members in sorted(clusters.items(), key=lambda x: -len(x[1])):
        total = sum(m["count"] for m in members)
        result.append({
            "cluster_id": cid,
            "locations": [m["location"] for m in members],
            "total_incidents": total,
            "center_lat": np.mean([geocodes[m["location"]][0] if isinstance(geocodes[m["location"]], tuple) else geocodes[m["location"]][0] for m in members]),
            "center_lng": np.mean([geocodes[m["location"]][1] if isinstance(geocodes[m["location"]], tuple) else geocodes[m["location"]][1] for m in members]),
        })

    return {"clusters": result, "total_locations": len(points)}


def timeline_analysis() -> dict:
    chunks = _load_chunks()
    date_chunks = {}
    for c in chunks:
        d = c.get("incident_date", "")
        if d and d != "N/A":
            date_chunks.setdefault(d, []).append(c)

    decades = Counter()
    years = Counter()
    for date, cs in date_chunks.items():
        parts = date.split("/")
        try:
            if len(parts) == 3:
                yr = int(parts[2]) if len(parts[2]) == 4 else (int(parts[2]) + 2000 if int(parts[2]) < 50 else int(parts[2]) + 1900)
            elif len(parts) == 2:
                yr = int(parts[1]) if len(parts[1]) == 4 else 2000
            else:
                yr = int(date.strip()[-4:]) if date.strip()[-4:].isdigit() else None
            if yr:
                years[yr] += len(cs)
                decades[(yr // 10) * 10] += len(cs)
        except (ValueError, IndexError):
            pass

    prompt = (
        f"Analyze this temporal distribution of UAP incidents:\n"
        f"By decade: {dict(sorted(decades.items()))}\n"
        f"By year: {dict(sorted(years.items()))}\n"
        f"Identify: 1) Waves/spikes, 2) Gaps, 3) Correlations with historical events, 4) Trends.\n"
        f"Return a brief analysis (3-5 paragraphs)."
    )
    analysis = _ask_llm(prompt)

    return {
        "by_decade": dict(sorted(decades.items())),
        "by_year": dict(sorted(years.items())),
        "total_dated_incidents": sum(years.values()),
        "analysis": analysis,
    }


def cross_reference(doc_title: str, n: int = 10) -> dict:
    chunks = _load_chunks()
    matches = [c for c in chunks if doc_title.lower() in c.get("source_file", "").lower()]
    if not matches:
        matches = [c for c in chunks if doc_title.lower() in c.get("title", "").lower()]
    if not matches:
        return {"error": f"No document found matching '{doc_title}'"}

    source_text = matches[0].get("text", "")
    results = query_similar(source_text[:500], n_results=n)

    related = []
    for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
        if meta.get("source_file", "").lower() != matches[0]["source_file"].lower():
            related.append({
                "source_file": meta.get("source_file", ""),
                "agency": meta.get("agency", ""),
                "location": meta.get("incident_location", ""),
                "date": meta.get("incident_date", ""),
                "relevance": f"{(1 - dist) * 100:.1f}%",
                "excerpt": doc[:200],
            })

    return {"source": matches[0], "related_documents": related[:n]}


def generate_report(topic: str) -> dict:
    results = query_similar(topic, n_results=15)
    context = "\n\n".join(
        f"[{m.get('source_file','')} | {m.get('agency','')} | {m.get('incident_location','')} | {m.get('incident_date','')}]\n{d[:500]}"
        for d, m in zip(results["documents"][0], results["metadatas"][0])
    )

    prompt = (
        f"Generate a comprehensive investigation report on: {topic}\n\n"
        f"Based on these declassified documents:\n{context}\n\n"
        f"Structure the report with:\n"
        f"1. EXECUTIVE SUMMARY\n2. KEY EVIDENCE\n3. PATTERN ANALYSIS\n"
        f"4. GEOGRAPHIC DISTRIBUTION\n5. TEMPORAL ANALYSIS\n6. ASSESSMENT\n7. OPEN QUESTIONS\n\n"
        f"Cite specific documents. Be objective and evidence-based."
    )

    report = _ask_llm(prompt)
    return {"topic": topic, "report": report, "sources_used": len(results["documents"][0])}


def find_contradictions() -> dict:
    chunks = _load_chunks()
    loc_groups = {}
    for c in chunks:
        loc = c.get("incident_location", "")
        if loc and loc != "N/A" and loc != "Unknown":
            loc_groups.setdefault(loc, []).append(c)

    contradictory = []
    for loc, cs in loc_groups.items():
        if len(cs) < 2:
            continue
        texts = [c["text"][:300] for c in cs[:10]]
        prompt = (
            f"Compare these {len(texts)} UAP reports from {loc}. Find any contradictions "
            f"in descriptions, timelines, or assessments. Return as JSON array of "
            f"{{doc1, doc2, contradiction, detail}} or empty array if none found.\n\n"
            + "\n\n".join(f"Doc {i+1}: {t}" for i, t in enumerate(texts))
        )
        raw = _ask_llm(prompt, system="Return ONLY valid JSON array.")
        try:
            if "```" in raw:
                raw = raw.split("```")[1].split("```")[0]
                if raw.lstrip().startswith("json"):
                    raw = raw[4:]
            found = json.loads(raw.strip())
            if found:
                contradictory.extend(found)
        except (json.JSONDecodeError, IndexError):
            pass

    return {"contradictions": contradictory, "locations_checked": len(loc_groups)}


def extract_entities(doc_title: str) -> dict:
    chunks = _load_chunks()
    matches = [c for c in chunks if doc_title.lower() in c.get("source_file", "").lower()]
    if not matches:
        return {"error": f"Document not found: {doc_title}"}

    text = "\n".join(c["text"][:1000] for c in matches[:5])
    prompt = (
        "Extract all named entities from this text. Return JSON with keys: "
        "people, locations, organizations, equipment, dates, vehicles, phenomena. "
        "Each value is a list of strings.\n\n" + text
    )
    raw = _ask_llm(prompt, system="Return ONLY valid JSON.")
    try:
        if "```" in raw:
            raw = raw.split("```")[1].split("```")[0]
            if raw.lstrip().startswith("json"):
                raw = raw[4:]
        entities = json.loads(raw.strip())
    except (json.JSONDecodeError, IndexError):
        entities = {"raw": raw}

    return {"document": doc_title, "entities": entities}


def score_anomalies() -> dict:
    chunks = _load_chunks()
    metadata = [c for c in chunks if c.get("chunk_type") == "metadata" and c.get("text")]
    if not metadata:
        return {"scores": [], "error": "No metadata to score"}

    batch = metadata[:40]
    prompt = (
        "Score each UAP incident on a 0-100 'anomaly scale' where:\n"
        "- 0-30: Likely prosaic (balloon, bird, lens flare, satellite)\n"
        "- 31-60: Unusual but possibly explainable\n"
        "- 61-80: Genuinely anomalous\n"
        "- 81-100: Highly anomalous (no conventional explanation)\n\n"
        "Consider: sensor data quality, number of witnesses, object behavior, "
        "corroboration, and whether similar prosaic explanations exist.\n\n"
        "Return JSON array of {title, score, reasoning}.\n\n"
        + "\n".join(f"- [{b.get('title','')}] {b.get('text','')[:200]}" for b in batch)
    )

    raw = _ask_llm(prompt, system="Return ONLY valid JSON array.")
    try:
        if "```" in raw:
            raw = raw.split("```")[1].split("```")[0]
            if raw.lstrip().startswith("json"):
                raw = raw[4:]
        scores = json.loads(raw.strip())
    except (json.JSONDecodeError, IndexError):
        scores = [{"raw": raw}]

    return {"scores": scores, "total_scored": len(batch)}
