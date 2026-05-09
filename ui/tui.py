#!/usr/bin/env python3
import sys
import json
import logging
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Input, Static, RichLog
from textual.widget import Widget
from textual.suggester import Suggester
from textual.message import Message
from rich.markdown import Markdown
from rich.table import Table
from rich.panel import Panel

from config import PROCESSED_DIR

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

COMMANDS = [
    ":ask ", ":search ", ":explore ", ":patterns", ":hotspots",
    ":timeline", ":graph", ":report ", ":connections ", ":status", ":quit",
]

AGENCIES = ["FBI", "Department of War", "NASA", "Department of State", "AARO"]


class CommandSuggester(Suggester):
    async def get_suggestion(self, value: str) -> str | None:
        for cmd in COMMANDS:
            if cmd.startswith(value.lower()):
                return cmd
        for a in AGENCIES:
            if value.lower() in a.lower():
                return a
        return None


class UFOAIApp(App):
    CSS = """
    Screen { layout: grid; grid-size: 1; grid-rows: auto 1fr auto; }
    #main { layout: horizontal; }
    #sidebar { width: 30; border-right: solid $primary; overflow-y: auto; }
    #content { width: 1fr; overflow-y: auto; padding: 0 1; }
    #command-bar { height: 3; border-top: solid $primary; }
    #command-input { width: 100%; }
    .sidebar-item { padding: 0 1; height: 1; }
    .sidebar-item:hover { background: $primary 20%; }
    .sidebar-title { text-style: bold; color: $accent; padding: 0 1; }
    """

    BINDINGS = [
        Binding("/", "focus_command", "Command", show=True),
        Binding("q", "quit", "Quit", show=True),
        Binding("ctrl+l", "clear_log", "Clear", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.chunks = []
        self.title = "🛸 UFOAI — UAP Intelligence Terminal"

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main"):
            with Vertical(id="sidebar"):
                yield Static(self._sidebar_text(), id="sidebar-content")
            with Vertical(id="content"):
                yield RichLog(id="log", highlight=True, markup=True)
        with Horizontal(id="command-bar"):
            yield Input(placeholder="Type a command (/ for commands)...", id="command-input",
                        suggester=CommandSuggester())
        yield Footer()

    def _sidebar_text(self) -> str:
        p = PROCESSED_DIR / "all_chunks.json"
        if p.exists():
            data = json.loads(p.read_text())
            n = len(data)
            agencies = set(d.get("agency", "") for d in data if d.get("agency"))
            locs = set(d.get("incident_location", "") for d in data if d.get("incident_location") and d.get("incident_location") not in ("N/A", "Unknown"))
            return (f"[bold cyan]UFOAI Status[/]\n"
                    f"Chunks: {n}\n"
                    f"Agencies: {len(agencies)}\n"
                    f"Locations: {len(locs)}\n\n"
                    f"[bold cyan]Commands[/]\n"
                    f":ask <question>\n"
                    f":search <query>\n"
                    f":patterns\n"
                    f":hotspots\n"
                    f":timeline\n"
                    f":report <topic>\n"
                    f":connections <doc>\n"
                    f":status\n"
                    f":quit")
        return "No data loaded.\nRun pipeline first."

    def on_mount(self) -> None:
        self.query_one(RichLog).write(Panel(
            "[bold cyan]UFOAI[/] — UAP Intelligence Terminal\n"
            "Type [bold]:help[/] for commands or [bold]/[/] to focus command bar.\n"
            "Use [bold]Tab[/] for autocomplete.",
            border_style="cyan"))
        p = PROCESSED_DIR / "all_chunks.json"
        if p.exists():
            self.chunks = json.loads(p.read_text())

    def action_focus_command(self) -> None:
        self.query_one(Input).focus()

    def action_clear_log(self) -> None:
        self.query_one(RichLog).clear()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        cmd = event.value.strip()
        self.query_one(Input).value = ""
        log = self.query_one(RichLog)
        log.write(f"[bold green]❯[/] {cmd}")

        if not cmd:
            return

        if cmd in (":quit", ":q"):
            self.exit()
            return

        if cmd == ":help":
            log.write(Markdown(
                "## Commands\n"
                "- `:ask <question>` — RAG query\n"
                "- `:search <query>` — Semantic search\n"
                "- `:patterns` — Pattern detection\n"
                "- `:hotspots` — Geographic clusters\n"
                "- `:timeline` — Temporal analysis\n"
                "- `:report <topic>` — Investigation report\n"
                "- `:connections <doc>` — Related documents\n"
                "- `:status` — System status\n"
                "- `:quit` — Exit"))
            return

        if cmd == ":status":
            n = len(self.chunks)
            agencies = set(d.get("agency", "") for d in self.chunks if d.get("agency"))
            locs = set(d.get("incident_location", "") for d in self.chunks if d.get("incident_location") and d.get("incident_location") not in ("N/A", "Unknown"))
            t = Table(title="Status")
            t.add_column("Metric")
            t.add_column("Value", style="cyan")
            t.add_row("Chunks", str(n))
            t.add_row("Agencies", str(len(agencies)))
            t.add_row("Locations", str(len(locs)))
            log.write(t)
            return

        if cmd.startswith(":ask "):
            question = cmd[5:].strip()
            if not question:
                log.write("[yellow]Usage: :ask <question>[/]")
                return
            log.write("[dim]Searching documents...[/]")
            from rag.chain import ask
            result = ask(question, n_results=8)
            log.write(Panel(Markdown(result["answer"]), border_style="green"))
            log.write(f"[dim]Sources: {len(result['sources'])} documents[/]")
            return

        if cmd.startswith(":search "):
            query = cmd[8:].strip()
            if not query:
                log.write("[yellow]Usage: :search <query>[/]")
                return
            from rag.vectorstore import query_similar
            results = query_similar(query, n_results=5)
            t = Table(title=f"Search: {query}")
            t.add_column("File", max_width=40)
            t.add_column("Agency")
            t.add_column("Location")
            for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
                t.add_row(meta.get("source_file", "")[:40], meta.get("agency", ""), meta.get("incident_location", ""))
            log.write(t)
            return

        if cmd == ":patterns":
            log.write("[dim]Detecting patterns...[/]")
            from rag.investigator import detect_patterns
            r = detect_patterns()
            log.write(Panel(Markdown(f"```\n{json.dumps(r.get('patterns', r), indent=2)[:2000]}\n```"),
                            title="Patterns", border_style="cyan"))
            return

        if cmd == ":hotspots":
            log.write("[dim]Finding hotspots...[/]")
            from rag.investigator import find_hotspots
            r = find_hotspots()
            for cl in r.get("clusters", []):
                log.write(f"[cyan]Cluster {cl['cluster_id']}[/]: {cl['total_incidents']} incidents at {', '.join(cl['locations'])}")
            return

        if cmd == ":timeline":
            log.write("[dim]Analyzing timeline...[/]")
            from rag.investigator import timeline_analysis
            r = timeline_analysis()
            log.write(Panel(Markdown(r.get("analysis", "")), title="Timeline", border_style="cyan"))
            return

        if cmd.startswith(":report "):
            topic = cmd[8:].strip()
            if not topic:
                log.write("[yellow]Usage: :report <topic>[/]")
                return
            log.write(f"[dim]Generating report on: {topic}...[/]")
            from rag.investigator import generate_report
            r = generate_report(topic)
            log.write(Panel(Markdown(r.get("report", "")), title=f"Report: {topic}", border_style="green"))
            return

        if cmd.startswith(":connections "):
            doc = cmd[13:].strip()
            if not doc:
                log.write("[yellow]Usage: :connections <doc title>[/]")
                return
            log.write(f"[dim]Finding connections for: {doc}...[/]")
            from rag.investigator import cross_reference
            r = cross_reference(doc)
            if "error" in r:
                log.write(f"[red]{r['error']}[/]")
                return
            for rd in r.get("related_documents", []):
                log.write(f"  [cyan]{rd['source_file'][:50]}[/] | {rd['agency']} | {rd['location']} | {rd['relevance']}")
            return

        log.write(f"[yellow]Unknown command: {cmd}[/]. Type :help for commands.")


def main():
    app = UFOAIApp()
    app.run()


if __name__ == "__main__":
    main()
