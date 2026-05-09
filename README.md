# 🛸 UFOAI — UAP Intelligence System

**Open-source AI-powered analysis of declassified UAP/UFO government documents.**

Built on the [Presidential Unsealing and Reporting System for UAP Encounters (PURSUE)](https://www.war.gov/UFO/) — the first-ever public release of declassified UAP files by the U.S. Department of War (Release 01, May 8, 2026).

https://github.com/user-attachments/assets/ufoai-preview.gif

---

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌────────────┐
│  Data Sources │────▶│   Pipeline   │────▶│  Vector DB   │────▶│  AI Engine │
│              │     │              │     │              │     │            │
│ • war.gov    │     │ • PDF OCR    │     │ • ChromaDB   │     │ • Ollama   │
│ • AARO.mil   │     │ • Image AI   │     │ • 2,280 emb. │     │ • OpenRouter│
│ • DVIDS API  │     │ • Video AI   │     │ • Cosine sim │     │ • 8 models │
└─────────────┘     └──────────────┘     └──────────────┘     └────────────┘
                                                                      │
        ┌─────────────────────────────────────────────────────────────┘
        │
        ├── 💻 CLI       ── ask, search, shell, investigate, status
        ├── 🌐 Streamlit ── Dashboard, Map, Timeline, Graph, Gallery
        ├── 🖥️ TUI        ── Terminal UI with autocompletion
        └── 🔍 Investigator ── Patterns, Hotspots, Anomalies, Reports
```

## Data Inventory

| Source | Type | Count | Size |
|--------|------|-------|------|
| FBI | PDF case files | 57 | ~800 MB |
| Department of War | Mission reports (PDF) + UAP imagery | 82 | ~1.2 GB |
| NASA | Transcripts + Apollo 17 imagery | 15 | ~200 MB |
| Department of State | Cables + memorandums | 7 | ~50 MB |
| **Total** | **PDFs + Images** | **289 files** | **~2.4 GB** |

- **2,280 text chunks** (1,923 PDF OCR + 196 image descriptions + 161 metadata)
- **36 incident locations** across 5 continents
- **Dates spanning 1944–2026**

## Quickstart

```bash
# 1. Clone & setup
git clone https://github.com/scaiado/UFOAI.git
cd UFOAI
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt  # or: pip install -e .
playwright install chromium      # optional, for future dynamic scraping

# 2. Pull Ollama models
ollama pull llama3.1:8b          # chat
ollama pull nomic-embed-text     # embeddings
ollama pull llava:7b             # vision (optional, for local image description)

# 3. Scrape data from war.gov
python ui/cli.py scrape

# 4. Process files (OCR + image description)
python ui/cli.py process --openrouter --model gemma   # cloud vision
python ui/cli.py process --pdfs-only                   # local OCR

# 5. Embed into vector store
python ui/cli.py embed

# 6. Query
python ui/cli.py ask "What did the FBI investigate about flying saucers?"
```

## Interfaces

### CLI
```bash
python ui/cli.py ask "your question" --openrouter --model nemotron-super --show-sources
python ui/cli.py search "Greece UAP" --top-k 10
python ui/cli.py shell                    # interactive REPL
python ui/cli.py status                   # system status
```

### Streamlit Dashboard
```bash
streamlit run ui/app.py
```
7 tabs: Dashboard, Query, Timeline, Map, Gallery, Graph, Investigate

### TUI (Terminal UI)
```bash
python ui/cli.py tui
```
Split-pane interface with autocompletion. Type `/` to focus command bar.

## AI Investigation Tools

```bash
python ui/cli.py investigate patterns        # Detect recurring UAP shapes, behaviors
python ui/cli.py investigate hotspots        # Geographic clustering (DBSCAN)
python ui/cli.py investigate timeline        # Temporal analysis with wave detection
python ui/cli.py investigate anomalies       # Score incidents 0-100 anomaly scale
python ui/cli.py investigate contradictions  # Find conflicting accounts
python ui/cli.py investigate report "Greece" # Auto-generate investigation report
python ui/cli.py investigate connections "DOW-UAP-D33"  # Find related documents
python ui/cli.py investigate entities "FBI file"        # Extract named entities
```

## Supported Models

### Local (Ollama)
| Model | Purpose | RAM |
|-------|---------|-----|
| `llama3.1:8b` | Chat / RAG | ~6 GB |
| `nomic-embed-text` | Embeddings | ~0.3 GB |
| `llava:7b` | Vision (images) | ~5 GB |

### OpenRouter Free
| Key | Model | Best For |
|-----|-------|----------|
| `nemotron-super` | nvidia/nemotron-3-super-120b-a12b:free | Analysis |
| `nemotron-reasoning` | nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free | Reasoning |
| `gpt-oss` | openai/gpt-oss-120b:free | General |
| `owl-alpha` | openrouter/owl-alpha | Research |
| `laguna` | poolside/laguna-m.1:free | Programming |
| `glm-air` | z-ai/glm-4.5-air:free | Technology |
| `gemma` | google/gemma-4-31b-it:free | Vision + general |
| `minimax` | minimax/minimax-m2.5:free | SEO/analysis |

## Configuration

Copy `.env.example` to `.env`:
```
OPENROUTER_API_KEY=your_key_here     # Optional, for cloud models
OLLAMA_BASE_URL=http://localhost:11434
```

## Tech Stack

- **Language**: Python 3.12
- **RAG**: LangChain + ChromaDB
- **LLM**: Ollama (local) + OpenRouter (cloud)
- **Scraping**: curl_cffi (browser TLS impersonation)
- **OCR**: Tesseract + PyMuPDF
- **Vision**: Ollama llava / OpenRouter vision API
- **Embeddings**: nomic-embed-text (Ollama)
- **Web UI**: Streamlit + Plotly + Folium + PyVis
- **TUI**: Textual
- **Graph**: NetworkX + PyVis
- **Clustering**: scikit-learn (DBSCAN)

## Project Structure

```
UFOAI/
├── config.py              # Configuration & paths
├── models.py              # Pydantic data models
├── scraper/
│   ├── war_gov_scraper.py # war.gov/UFO CSV + file downloader
│   ├── aaro_scraper.py    # AARO.mil scraper
│   └── scheduler.py       # Automated scraping scheduler
├── pipeline/
│   ├── pdf_processor.py   # PDF OCR (Tesseract + PyMuPDF)
│   ├── image_processor.py # Image description (Ollama/OpenRouter)
│   ├── video_processor.py # Video frame extraction + description
│   ├── orchestrator.py    # Pipeline coordinator
│   ├── metadata_enricher.py # Fuzzy match chunks → CSV records
│   └── geocoder.py        # Location → lat/lng geocoding
├── rag/
│   ├── vectorstore.py     # ChromaDB embedding management
│   ├── chain.py           # RAG chain (Ollama + OpenRouter)
│   ├── openrouter_client.py # OpenRouter model registry
│   ├── investigator.py    # 8 AI investigation tools
│   └── graph_builder.py   # Knowledge graph (NetworkX + PyVis)
├── ui/
│   ├── cli.py             # Rich CLI with investigate commands
│   ├── app.py             # Streamlit 7-tab dashboard
│   └── tui.py             # Textual TUI with autocompletion
└── data/
    ├── raw/               # Downloaded files
    ├── processed/         # Chunks, geocodes, graph
    └── embeddings/        # ChromaDB persistent store
```

## License

MIT — All scraped data is from publicly accessible U.S. government sources (war.gov, aaro.mil).
