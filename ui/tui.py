#!/usr/bin/env python3
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Input, Static, RichLog
from textual.suggester import Suggester
from rich.panel import Panel

from config import PROCESSED_DIR


class CommandSuggester(Suggester):
    async def get_suggestion(self, value: str) -> str | None:
        commands = [":ask ", ":search ", ":help", ":status", ":quit", ":patterns", ":hotspots", ":timeline"]
        for cmd in commands:
            if cmd.startswith(value.lower()):
                return cmd
        return None


class UFOAIApp(App):
    CSS = """
    #sidebar { width: 28; border-right: solid green; }
    #content { width: 1; }
    #log { height: 100%; }
    #cmd { margin: 1; }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("l", "clear_log", "Clear", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.chunks = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Static(self._sidebar_text())
            with Vertical(id="content"):
                yield RichLog(id="log", highlight=True, markup=True, auto_scroll=True)
        yield Input(placeholder="Type command...", id="cmd")
        yield Footer()

    def on_mount(self) -> None:
        log = self.query_one(RichLog)
        log.write("[cyan]Welcome to UFOAI TUI[/]")
        log.write("[cyan]Type :help for commands[/]")

    def _sidebar_text(self) -> str:
        p = PROCESSED_DIR / "all_chunks.json"
        if p.exists():
            data = json.loads(p.read_text())
            n = len(data)
            return f"[cyan]UFOAI[/]\n\n[n]Chunks: {n}\n\n[cyan]Commands[/]\n:ask\n:search\n:status\n:help\n:quit"
        return "[cyan]UFOAI[/]\n\n[red]No data[/]"

    def action_clear_log(self) -> None:
        self.query_one(RichLog).clear()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        cmd = event.value.strip()
        self.query_one(Input).value = ""
        log = self.query_one(RichLog)
        log.write(f"[green]>[/] {cmd}")

        if cmd == ":quit":
            self.exit()
        elif cmd == ":help":
            log.write(Panel("Commands: :ask, :search, :status, :help, :quit"))
        elif cmd == ":status":
            log.write(f"Loaded {len(self.chunks)} chunks")
        elif cmd.startswith(":ask "):
            log.write("[yellow]RAG query not implemented in minimal mode[/]")
        else:
            log.write("[yellow]Unknown command[/]")


if __name__ == "__main__":
    app = UFOAIApp()
    app.run()


def main():
    app = UFOAIApp()
    app.run()