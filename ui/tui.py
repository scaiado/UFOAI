#!/usr/bin/env python3
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Input, Static, TextArea

from config import PROCESSED_DIR


class UFOAIApp(App):
    CSS = """
    #sidebar { width: 28; border-right: solid green; }
    #content { width: 1; }
    #output { height: 100%; }
    TextArea { height: 100%; }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("l", "clear", "Clear", show=True),
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
                yield TextArea(id="output", read_only=True)
        yield Input(placeholder="Type command...", id="cmd")
        yield Footer()

    def _sidebar_text(self) -> str:
        p = PROCESSED_DIR / "all_chunks.json"
        if p.exists():
            data = json.loads(p.read_text())
            n = len(data)
            return f"UFOAI\n\nChunks: {n}\n\nCommands:\n:ask\n:search\n:status\n:help\n:quit"
        return "UFOAI\n\nNo data"

    def action_clear(self) -> None:
        ta = self.query_one(TextArea)
        ta.read_only = False
        ta.clear()
        ta.read_only = True

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        cmd = event.value.strip()
        self.query_one(Input).value = ""
        ta = self.query_one(TextArea)

        response = self._handle_command(cmd)
        ta.read_only = False
        if ta.text:
            ta.text = ta.text + "\n" + f"> {cmd}\n" + response
        else:
            ta.text = f"> {cmd}\n{response}"
        ta.read_only = True
        ta.scroll_to_end()

    def _handle_command(self, cmd: str) -> str:
        if cmd == ":quit":
            self.exit()
            return "Goodbye!"
        elif cmd == ":help":
            return "Commands: :ask, :search, :status, :help, :quit"
        elif cmd == ":status":
            return f"Loaded {len(self.chunks)} chunks"
        elif cmd.startswith(":ask "):
            return "[yellow]RAG query not implemented in minimal mode[/]"
        elif cmd.startswith(":search "):
            return "[yellow]Search not implemented in minimal mode[/]"
        else:
            return f"Unknown command: {cmd}"


if __name__ == "__main__":
    app = UFOAIApp()
    app.run()


def main():
    app = UFOAIApp()
    app.run()