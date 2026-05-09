#!/usr/bin/env python3
import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from config import PROCESSED_DIR, EMBEDDINGS_DIR

console = Console()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def cmd_scrape(args):
    from scraper.scheduler import scrape_all

    with console.status("[bold green]Scraping data sources..."):
        records = scrape_all(force=args.force)
    console.print(f"[bold green]Collected {len(records)} records[/bold green]")


def cmd_process(args):
    import os
    if args.openrouter:
        os.environ["UFOAI_USE_OPENROUTER"] = "1"
        if args.model:
            from rag.openrouter_client import FREE_MODELS
            os.environ["UFOAI_OPENROUTER_MODEL"] = FREE_MODELS.get(args.model, args.model)
        console.print("[bold cyan]Using OpenRouter for image description[/bold cyan]")

    from pipeline.orchestrator import process_all

    skip_pdf = getattr(args, "images_only", False)
    skip_img = getattr(args, "pdfs_only", False)

    console.print("[bold green]Processing files (this may take a while)...[/bold green]")
    chunks = process_all(force=args.force, pdfs=not skip_pdf, images=not skip_img)
    console.print(f"[bold green]Generated {len(chunks)} new chunks[/bold green]")


def cmd_embed(args):
    from rag.vectorstore import embed_chunks

    with console.status("[bold green]Embedding chunks into vector store..."):
        added = embed_chunks()
    console.print(f"[bold green]Added {added} new embeddings[/bold green]")


def cmd_pipeline(args):
    cmd_scrape(args)
    cmd_process(args)
    cmd_embed(args)


def cmd_ask(args):
    from rag.chain import ask

    question = " ".join(args.question)
    filter_meta = {}
    if args.agency:
        filter_meta["agency"] = args.agency
    if args.location:
        filter_meta["incident_location"] = args.location

    with console.status("[bold green]Searching documents..."):
        model_id = None
        if args.model:
            from rag.openrouter_client import FREE_MODELS
            model_id = FREE_MODELS.get(args.model, args.model)
        result = ask(
            question,
            n_results=args.top_k,
            use_openrouter=args.openrouter,
            model=model_id,
            filter_metadata=filter_meta or None,
        )

    console.print(Panel(Markdown(result["answer"]), title="Answer", border_style="green"))

    if args.show_sources:
        table = Table(title="Sources", show_lines=True)
        table.add_column("File", style="cyan", max_width=40)
        table.add_column("Agency", style="magenta")
        table.add_column("Location", style="yellow")
        table.add_column("Date", style="blue")
        for s in result["sources"][:10]:
            table.add_row(
                s["source_file"][:40],
                s["agency"],
                s["location"],
                s["date"],
            )
        console.print(table)


def cmd_search(args):
    from rag.vectorstore import query_similar

    query = " ".join(args.query)
    results = query_similar(query, n_results=args.top_k)

    table = Table(title=f"Search: {query}", show_lines=True)
    table.add_column("#", style="dim")
    table.add_column("File", style="cyan", max_width=40)
    table.add_column("Agency", style="magenta")
    table.add_column("Excerpt", max_width=60)

    for i, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
        table.add_row(str(i + 1), meta.get("source_file", "")[:40], meta.get("agency", ""), doc[:60])
    console.print(table)


def cmd_status(args):
    from config import RAW_DIR

    table = Table(title="UFOAI System Status")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    pdfs = list(RAW_DIR.rglob("*.pdf"))
    videos = [p for ext in ("*.mp4", "*.webm") for p in RAW_DIR.rglob(ext)]
    images = [p for ext in ("*.jpg", "*.jpeg", "*.png") for p in RAW_DIR.rglob(ext)]

    chunks_file = PROCESSED_DIR / "all_chunks.json"
    chunk_count = len(json.loads(chunks_file.read_text())) if chunks_file.exists() else 0

    try:
        from rag.vectorstore import get_chroma_client, get_or_create_collection

        client = get_chroma_client()
        coll = get_or_create_collection(client)
        embed_count = coll.count()
    except Exception:
        embed_count = 0

    manifest_file = PROCESSED_DIR.parent / "data" / "manifest.json"
    last_scrape = "Never"
    if manifest_file.exists():
        m = json.loads(manifest_file.read_text())
        last_scrape = m.get("last_scrape", "Unknown")

    table.add_row("PDFs", str(len(pdfs)))
    table.add_row("Videos", str(len(videos)))
    table.add_row("Images", str(len(images)))
    table.add_row("Text Chunks", str(chunk_count))
    table.add_row("Embeddings", str(embed_count))
    table.add_row("Last Scrape", last_scrape)

    console.print(table)


def cmd_shell(args):
    from rag.chain import ask

    console.print("[bold cyan]UFOAI Interactive Query Shell[/bold cyan]")
    console.print("Type your question or 'quit' to exit.\n")

    while True:
        try:
            question = console.input("[bold green]❯ [/bold green]")
            if question.strip().lower() in ("quit", "exit", "q"):
                break
            if not question.strip():
                continue

            with console.status("[bold green]Thinking..."):
                result = ask(question, n_results=10)

            console.print(Panel(Markdown(result["answer"]), border_style="green"))
            console.print(f"[dim]Sources: {len(result['sources'])} documents[/dim]\n")
        except KeyboardInterrupt:
            console.print("\n[bold]Goodbye![/bold]")
            break


def main():
    parser = argparse.ArgumentParser(
        prog="ufoai",
        description="UFOAI - UAP data collection, analysis & RAG system",
    )
    sub = parser.add_subparsers(dest="command")

    p_scrape = sub.add_parser("scrape", help="Scrape data from war.gov and AARO")
    p_scrape.add_argument("--force", action="store_true", help="Re-download all files")

    p_process = sub.add_parser("process", help="Process downloaded files")
    p_process.add_argument("--force", action="store_true", help="Re-process all files")
    p_process.add_argument("--openrouter", action="store_true", help="Use OpenRouter for image description")
    p_process.add_argument("--model", type=str, help="OpenRouter model key")
    p_process.add_argument("--images-only", action="store_true", help="Only process images (skip PDFs)")
    p_process.add_argument("--pdfs-only", action="store_true", help="Only process PDFs (skip images)")

    p_embed = sub.add_parser("embed", help="Embed chunks into vector store")

    p_pipeline = sub.add_parser("pipeline", help="Full pipeline: scrape + process + embed")
    p_pipeline.add_argument("--force", action="store_true")
    p_pipeline.add_argument("--openrouter", action="store_true", help="Use OpenRouter for processing")
    p_pipeline.add_argument("--model", type=str, help="OpenRouter model key")

    p_ask = sub.add_parser("ask", help="Ask a question about the data")
    p_ask.add_argument("question", nargs="+")
    p_ask.add_argument("--top-k", type=int, default=10)
    p_ask.add_argument("--agency", type=str, help="Filter by agency")
    p_ask.add_argument("--location", type=str, help="Filter by location")
    p_ask.add_argument("--openrouter", action="store_true", help="Use OpenRouter")
    p_ask.add_argument("--model", type=str, help="OpenRouter model key (nemotron-super, gpt-oss, laguna, owl-alpha, glm-air, minimax, nemotron-reasoning, gemma)")
    p_ask.add_argument("--show-sources", action="store_true", help="Show source documents")

    p_search = sub.add_parser("search", help="Search documents")
    p_search.add_argument("query", nargs="+")
    p_search.add_argument("--top-k", type=int, default=5)

    sub.add_parser("status", help="Show system status")

    sub.add_parser("shell", help="Interactive query shell")

    args = parser.parse_args()

    commands = {
        "scrape": cmd_scrape,
        "process": cmd_process,
        "embed": cmd_embed,
        "pipeline": cmd_pipeline,
        "ask": cmd_ask,
        "search": cmd_search,
        "status": cmd_status,
        "shell": cmd_shell,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
