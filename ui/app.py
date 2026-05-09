import json
from pathlib import Path

import folium
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium
from wordcloud import WordCloud
import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import RAW_DIR, PROCESSED_DIR


def load_chunks():
    p = PROCESSED_DIR / "all_chunks.json"
    return json.loads(p.read_text()) if p.exists() else []


def load_geocodes():
    p = PROCESSED_DIR / "geocoded_locations.json"
    return json.loads(p.read_text()) if p.exists() else {}


@st.cache_data
def get_stats():
    chunks = load_chunks()
    geocodes = load_geocodes()
    pdfs = list(RAW_DIR.rglob("*.pdf"))
    images = list(RAW_DIR.rglob("*.jpg")) + list(RAW_DIR.rglob("*.png"))

    agencies = {}
    locations = {}
    dates = {}
    types = {}
    for c in chunks:
        a = c.get("agency") or "Unknown"
        agencies[a] = agencies.get(a, 0) + 1
        l = c.get("incident_location") or "Unknown"
        locations[l] = locations.get(l, 0) + 1
        d = c.get("incident_date") or "Unknown"
        dates[d] = dates.get(d, 0) + 1
        t = c.get("chunk_type") or "Unknown"
        types[t] = types.get(t, 0) + 1

    return {
        "chunks": chunks, "geocodes": geocodes,
        "n_pdfs": len(pdfs), "n_images": len(images),
        "agencies": agencies, "locations": locations,
        "dates": dates, "types": types,
    }


st.set_page_config(page_title="UFOAI — UAP Intelligence", page_icon="🛸", layout="wide")

stats = get_stats()
chunks = stats["chunks"]
geocodes = stats["geocodes"]

tab_dash, tab_query, tab_timeline, tab_map, tab_gallery, tab_graph, tab_investigate = st.tabs(
    ["📊 Dashboard", "💬 Query", "📅 Timeline", "🗺️ Map", "🖼️ Gallery", "🔗 Graph", "🔍 Investigate"]
)

# ─── DASHBOARD ──────────────────────────────────────────────────────
with tab_dash:
    st.title("🛸 UFOAI — UAP Intelligence Dashboard")
    st.caption("Powered by declassified government documents from war.gov/UFO")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("PDF Documents", stats["n_pdfs"])
    c2.metric("Images", stats["n_images"])
    c3.metric("Text Chunks", len(chunks))
    c4.metric("Unique Locations", len([l for l in stats["locations"] if l not in ("Unknown", "N/A")]))
    c5.metric("Agencies", len([a for a in stats["agencies"] if a != "Unknown"]))

    col1, col2 = st.columns(2)
    with col1:
        agency_data = {k: v for k, v in sorted(stats["agencies"].items(), key=lambda x: -x[1]) if k != "Unknown"}
        fig = px.pie(values=list(agency_data.values()), names=list(agency_data.keys()),
                     title="Documents by Agency", hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig, width='stretch')

    with col2:
        desc_text = " ".join(c.get("description", "") or c.get("text", "")[:200] for c in chunks if c.get("chunk_type") == "metadata")
        if desc_text.strip():
            wc = WordCloud(width=800, height=400, background_color="#0e1117",
                           colormap="plasma", max_words=100).generate(desc_text)
            fig_wc = go.Figure(go.Image(z=np.array(wc)))
            fig_wc.update_layout(title="Key Terms", margin=dict(l=0, r=0, t=30, b=0))
            fig_wc.update_xaxes(visible=False)
            fig_wc.update_yaxes(visible=False)
            st.plotly_chart(fig_wc, use_container_width=True)

    type_data = {k: v for k, v in sorted(stats["types"].items(), key=lambda x: -x[1])}
    fig2 = px.bar(x=list(type_data.keys()), y=list(type_data.values()),
                  title="Chunks by Type", labels={"x": "Type", "y": "Count"},
                  color=list(type_data.keys()), color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig2, use_container_width=True)

# ─── QUERY ──────────────────────────────────────────────────────────
with tab_query:
    st.header("💬 Query the Evidence")
    col_f, col_c = st.columns([1, 3])

    with col_f:
        st.subheader("Filters")
        agency_filter = st.text_input("Agency", placeholder="FBI, NASA...")
        location_filter = st.text_input("Location", placeholder="Greece, Iraq...")
        top_k = st.slider("Sources", 3, 20, 10)
        use_openrouter = st.checkbox("Use OpenRouter", value=False)
        model_choice = None
        if use_openrouter:
            from rag.openrouter_client import FREE_MODELS
            keys = list(FREE_MODELS.keys())
            labels = [f"{k} → {v.split('/')[-1].replace(':free','')}" for k, v in FREE_MODELS.items()]
            sel = st.selectbox("Model", range(len(keys)), format_func=lambda i: labels[i])
            model_choice = FREE_MODELS[keys[sel]]

    with col_c:
        if "messages" not in st.session_state:
            st.session_state.messages = []
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask about UAP documents..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Analyzing..."):
                    try:
                        from rag.chain import ask
                        fm = {}
                        if agency_filter: fm["agency"] = agency_filter
                        if location_filter: fm["incident_location"] = location_filter
                        result = ask(prompt, n_results=top_k, use_openrouter=use_openrouter,
                                     model=model_choice, filter_metadata=fm or None)
                        st.markdown(result["answer"])
                        with st.expander(f"Sources ({len(result['sources'])} documents)"):
                            for s in result["sources"]:
                                st.markdown(f"**{s['source_file'][:60]}** | {s['agency']} | {s['location']} | {s['date']}")
                                st.caption(s["excerpt"])
                        answer = result["answer"]
                    except Exception as e:
                        answer = f"Error: {e}"
                        st.error(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

# ─── TIMELINE ────────────────────────────────────────────────────────
with tab_timeline:
    st.header("📅 Incident Timeline")
    if st.button("Run Temporal Analysis"):
        with st.spinner("Analyzing temporal patterns..."):
            from rag.investigator import timeline_analysis
            tl = timeline_analysis()
            st.markdown(tl.get("analysis", ""))
        years = tl.get("by_year", {})
        if years:
            fig_t = px.bar(x=list(years.keys()), y=list(years.values()),
                           title="Incidents by Year", labels={"x": "Year", "y": "Chunks"})
            st.plotly_chart(fig_t, use_container_width=True)
        decades = tl.get("by_decade", {})
        if decades:
            fig_d = px.bar(x=[str(d) for d in decades.keys()], y=list(decades.values()),
                           title="Incidents by Decade", labels={"x": "Decade", "y": "Chunks"})
            st.plotly_chart(fig_d, use_container_width=True)

# ─── MAP ─────────────────────────────────────────────────────────────
with tab_map:
    st.header("🗺️ Incident Locations")
    if geocodes:
        loc_counts = {}
        for c in chunks:
            loc = c.get("incident_location", "")
            if loc and loc in geocodes and loc not in ("Moon", "Low Earth Orbit", "N/A", "Unknown"):
                loc_counts[loc] = loc_counts.get(loc, 0) + 1

        m = folium.Map(location=[30, 30], zoom_start=2, tiles="CartoDB dark_matter")
        for loc, count in loc_counts.items():
            coords = geocodes[loc]
            lat = coords[0] if isinstance(coords, (list, tuple)) else coords
            lng = coords[1] if isinstance(coords, (list, tuple)) else coords
            radius = min(5 + count * 2, 30)
            folium.CircleMarker(
                location=[lat, lng], radius=radius,
                popup=f"<b>{loc}</b><br>{count} chunks",
                color="#00d4ff", fill=True, fill_color="#00d4ff", fill_opacity=0.6,
            ).add_to(m)
        st_folium(m, width="100%", height=600)
    else:
        st.info("No geocoded locations. Run geocoder first.")

# ─── GALLERY ─────────────────────────────────────────────────────────
with tab_gallery:
    st.header("🖼️ Image Gallery")
    img_chunks = [c for c in chunks if c.get("chunk_type") == "image"]
    cols = st.columns(4)
    for i, ic in enumerate(img_chunks[:32]):
        with cols[i % 4]:
            st.caption(ic.get("source_file", "")[:40])
            desc = ic.get("text", "")[:200]
            if desc:
                st.markdown(f"<small>{desc}</small>", unsafe_allow_html=True)

# ─── GRAPH ───────────────────────────────────────────────────────────
with tab_graph:
    st.header("🔗 Knowledge Graph")
    if st.button("Build Knowledge Graph"):
        with st.spinner("Building graph..."):
            from rag.graph_builder import build_knowledge_graph, graph_to_pyvis
            G = build_knowledge_graph()
            html_path = graph_to_pyvis(G)
            st.components.v1.html(open(html_path).read(), height=700)
            from rag.graph_builder import get_document_clusters
            clusters = get_document_clusters(G)
            st.subheader(f"Document Clusters ({len(clusters)})")
            for i, cluster in enumerate(clusters[:20]):
                with st.expander(f"Cluster {i+1} ({len(cluster)} docs)"):
                    for doc in cluster[:10]:
                        node = G.nodes.get(doc, {})
                        st.markdown(f"- **{node.get('title', doc)[:60]}** | {node.get('agency','')} | {node.get('location','')}")

# ─── INVESTIGATE ─────────────────────────────────────────────────────
with tab_investigate:
    st.header("🔍 AI Investigation Tools")
    tool = st.selectbox("Tool", ["Patterns", "Hotspots", "Timeline", "Anomaly Scores",
                                  "Contradictions", "Report", "Cross-Reference", "Entities"])
    topic = st.text_input("Topic / Document", placeholder="e.g., Greece incidents or DOW-UAP-D33")

    if st.button("Run Analysis"):
        from rag import investigator
        with st.spinner(f"Running {tool}..."):
            if tool == "Patterns":
                r = investigator.detect_patterns()
                st.json(r.get("patterns", r))
            elif tool == "Hotspots":
                r = investigator.find_hotspots()
                for cl in r.get("clusters", []):
                    st.markdown(f"**Cluster {cl['cluster_id']}** — {cl['total_incidents']} incidents at {', '.join(cl['locations'])}")
            elif tool == "Timeline":
                r = investigator.timeline_analysis()
                st.markdown(r.get("analysis", ""))
            elif tool == "Anomaly Scores":
                r = investigator.score_anomalies()
                for s in r.get("scores", []):
                    score = s.get("score", 0)
                    color = "🔴" if score > 60 else "🟡" if score > 30 else "🟢"
                    st.markdown(f"{color} **{s.get('title','')[:50]}** — Score: {score}\n> {s.get('reasoning','')}")
            elif tool == "Contradictions":
                r = investigator.find_contradictions()
                for c in r.get("contradictions", []):
                    st.markdown(f"- {c}")
            elif tool == "Report" and topic:
                r = investigator.generate_report(topic)
                st.markdown(r.get("report", ""))
            elif tool == "Cross-Reference" and topic:
                r = investigator.cross_reference(topic)
                for rd in r.get("related_documents", []):
                    st.markdown(f"**{rd['source_file'][:50]}** | {rd['agency']} | {rd['location']} | {rd['relevance']}")
            elif tool == "Entities" and topic:
                r = investigator.extract_entities(topic)
                st.json(r.get("entities", {}))
            else:
                st.warning("Please enter a topic/document.")
