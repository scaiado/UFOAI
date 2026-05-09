#!/usr/bin/env python3
import sys
import json
import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer, Input, Static, LoadingIndicator

from config import PROCESSED_DIR
from rag.chain import ask

_executor = ThreadPoolExecutor(max_workers=1)


class UFOAIApp(App):
    CSS = """
    Screen { overflow: hidden; }
    Static { padding: 1; }
    Input { margin: 1; }
    #status { border-bottom: solid green; }
    #answer { margin: 1 2; }
    #sources { margin: 1 2; }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("c", "clear", "Clear", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("UFOAI - :ask <q> :search <q> :status :help :quit", id="status")
        yield Static("Type :status or :help for options", id="answer")
        yield Static("", id="sources")
        yield Input(placeholder="Type command...", id="cmd")
        yield Footer()

    def action_clear(self) -> None:
        self.query_one("#answer", Static).update("Type :status or :help for options")
        self.query_one("#sources", Static).update("")
        self.refresh()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        cmd = event.value.strip()
        self.query_one(Input).value = ""
        
        if not cmd:
            return

        status = self.query_one("#status", Static)
        answer = self.query_one("#answer", Static)
        sources = self.query_one("#sources", Static)
        
        if cmd == ":quit":
            self.exit()
            return
        elif cmd == ":c" or cmd == ":clear":
            self.action_clear()
            return
        elif cmd == ":help":
            status.update("Commands: :ask <q> :search <q> :status :help :clear :quit")
            answer.update("Type :ask <question> for RAG queries")
            sources.update("")
            self.refresh()
            return
        elif cmd == ":status":
            p = PROCESSED_DIR / "all_chunks.json"
            n = 0
            if p.exists():
                n = len(json.loads(p.read_text()))
            status.update(f"Loaded {n} chunks | Commands: :ask :search :status :help")
            answer.update("Ask something! Try: :ask What is Nimrod?")
            sources.update("")
            self.refresh()
            return
        elif cmd.startswith(":ask ") or cmd.startswith(":search "):
            query = cmd.split(" ", 1)[1] if " " in cmd else cmd
            status.update(f"Searching: {query[:50]}...")
            answer.update("Thinking...")
            sources.update("")
            self.refresh()
            
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            def run_query():
                result = ask(query, n_results=5, use_openrouter=True)
                return result
            
            try:
                result = await asyncio.wait_for(
                    loop.run_in_executor(_executor, run_query),
                    timeout=60.0
                )
                answer_text = result.get("answer", "No answer")[:500]
                answer.update(answer_text + "..." if len(answer_text) > 500 else answer_text)
                
                srcs = result.get("sources", [])[:3]
                if srcs:
                    src_text = "Sources: " + "; ".join([s.get("source_file", "?")[:30] for s in srcs])
                    sources.update(src_text)
                else:
                    sources.update("No sources found")
            except asyncio.TimeoutError:
                answer.update("Timeout - try a simpler query")
                sources.update("")
            except Exception as e:
                answer.update(f"Error: {str(e)[:100]}")
                sources.update("")
            
            status.update(f"Commands: :ask :search :status :help")
            self.refresh()
        else:
            status.update(f"Unknown: {cmd}")
            answer.update("Try :help for commands")
            sources.update("")
            self.refresh()


if __name__ == "__main__":
    app = UFOAIApp()
    app.run()


def main():
    app = UFOAIApp()
    app.run()