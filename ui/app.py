import json
import streamlit as st
from pathlib import Path

from config import RAW_DIR, PROCESSED_DIR, EMBEDDINGS_DIR


def get_status():
    pdfs = list(RAW_DIR.rglob("*.pdf"))
    videos = [p for ext in ("*.mp4", "*.webm") for p in RAW_DIR.rglob(ext)]
    images = [p for ext in ("*.jpg", "*.jpeg", "*.png") for p in RAW_DIR.rglob(ext)]
    chunks_file = PROCESSED_DIR / "all_chunks.json"
    chunk_count = len(json.loads(chunks_file.read_text())) if chunks_file.exists() else 0
    return len(pdfs), len(videos), len(images), chunk_count


st.set_page_config(page_title="UFOAI - UAP Analysis", page_icon="🛸", layout="wide")
st.title("UFOAI - UAP Data Analysis System")

tab_query, tab_files, tab_status = st.tabs(["Query", "Files", "Status"])

with tab_status:
    st.header("System Status")
    n_pdfs, n_videos, n_images, n_chunks = get_status()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("PDFs", n_pdfs)
    col2.metric("Videos", n_videos)
    col3.metric("Images", n_images)
    col4.metric("Text Chunks", n_chunks)

    try:
        from rag.vectorstore import get_chroma_client, get_or_create_collection
        client = get_chroma_client()
        coll = get_or_create_collection(client)
        st.metric("Vector Embeddings", coll.count())
    except Exception:
        st.warning("Vector store not initialized. Run: `python -m pipeline.orchestrator` then `python -m rag.vectorstore`")

    manifest = PROCESSED_DIR.parent / "data" / "manifest.json"
    if manifest.exists():
        m = json.loads(manifest.read_text())
        st.info(f"Last scrape: {m.get('last_scrape', 'Unknown')}")
    else:
        st.warning("No data scraped yet. Run: `python -m scraper.scheduler`")

with tab_query:
    st.header("Ask Questions About UAP Data")

    col_filters, col_chat = st.columns([1, 3])

    with col_filters:
        st.subheader("Filters")
        agency_filter = st.text_input("Agency", placeholder="e.g., FBI, NASA")
        location_filter = st.text_input("Location", placeholder="e.g., Greece, Iraq")
        top_k = st.slider("Sources", 3, 20, 10)
        use_openrouter = st.checkbox("Use OpenRouter", value=False)
        model_choice = None
        if use_openrouter:
            from rag.openrouter_client import FREE_MODELS
            model_keys = list(FREE_MODELS.keys())
            model_labels = [f"{k} → {v.split('/')[-1].replace(':free','')}" for k, v in FREE_MODELS.items()]
            selected = st.selectbox("Model", range(len(model_keys)), format_func=lambda i: model_labels[i])
            model_choice = FREE_MODELS[model_keys[selected]]

    with col_chat:
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
                with st.spinner("Analyzing documents..."):
                    try:
                        from rag.chain import ask
                        filter_meta = {}
                        if agency_filter:
                            filter_meta["agency"] = agency_filter
                        if location_filter:
                            filter_meta["incident_location"] = location_filter

                        result = ask(
                            prompt,
                            n_results=top_k,
                            use_openrouter=use_openrouter,
                            model=model_choice,
                            filter_metadata=filter_meta or None,
                        )
                        answer = result["answer"]
                        st.markdown(answer)

                        with st.expander(f"Sources ({len(result['sources'])} documents)"):
                            for s in result["sources"]:
                                st.markdown(f"**{s['source_file']}** | {s['agency']} | {s['location']} | {s['date']}")
                                st.caption(s["excerpt"])
                    except Exception as e:
                        answer = f"Error: {e}"
                        st.error(answer)

            st.session_state.messages.append({"role": "assistant", "content": answer})

with tab_files:
    st.header("File Browser")

    chunks_file = PROCESSED_DIR / "all_chunks.json"
    if chunks_file.exists():
        data = json.loads(chunks_file.read_text())
        agencies = sorted(set(d.get("agency", "") for d in data if d.get("agency")))
        types = sorted(set(d.get("chunk_type", "") for d in data if d.get("chunk_type")))

        col1, col2 = st.columns(2)
        with col1:
            sel_agency = st.multiselect("Agency", agencies)
        with col2:
            sel_type = st.multiselect("Type", types)

        filtered = data
        if sel_agency:
            filtered = [d for d in filtered if d.get("agency") in sel_agency]
        if sel_type:
            filtered = [d for d in filtered if d.get("chunk_type") in sel_type]

        st.caption(f"Showing {len(filtered)} of {len(data)} chunks")
        for chunk in filtered[:50]:
            with st.expander(f"{chunk.get('source_file', 'Unknown')} [{chunk.get('chunk_type', '')}]"):
                st.markdown(chunk.get("text", "")[:1000])
                if len(chunk.get("text", "")) > 1000:
                    st.caption(f"... ({len(chunk['text'])} chars total)")
    else:
        st.info("No processed data yet. Run the pipeline first.")
