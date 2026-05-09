#!/usr/bin/env python3
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer, Input, Static

from config import PROCESSED_DIR


class UFOAIApp(App):
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("UFOAI - Commands: :status :help :quit", id="status")
        yield Input(placeholder="Type command...", id="cmd")
        yield Footer()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        cmd = event.value.strip()
        self.query_one(Input).value = ""
        status = self.query_one(Static)
        
        if cmd == ":quit":
            self.exit()
        elif cmd == ":help":
            status.update("Commands: :status :help :quit | Type and press Enter")
        elif cmd == ":status":
            p = PROCESSED_DIR / "all_chunks.json"
            n = 0
            if p.exists():
                n = len(json.loads(p.read_text()))
            status.update(f"Loaded {n} chunks. Commands: :status :help :quit")
        else:
            status.update(f"Unknown: {cmd}. Commands: :status :help :quit")


if __name__ == "__main__":
    app = UFOAIApp()
    app.run()


def main():
    app = UFOAIApp()
    app.run()