"""Optional Textual UI.

 The import is intentionally lazy in cli.py so Termux never needs Textual.
 The stylesheet contains only broadly supported Textual rules; responsive
 stylesheet blocks are deliberately avoided for compatibility.
"""

from __future__ import annotations

from typing import cast

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Input, Label, ListItem, ListView, Static

from .models import Session
from .monitoring import MonitoringEngine
from .reports import ReportWriter
from .security import SafetyError


class BlackHawkApp(App[None]):
    TITLE = "BLACKHAWK | PUBLIC SOURCE MONITOR"
    CSS = """
    Screen { background: #07090c; color: #dfe6e9; }
    Header { background: #140c10; color: #f2eeee; }
    Footer { background: #130d10; color: #91a0aa; }
    #body { height: 1fr; }
    #left { width: 34%; min-width: 24; border: round #8f202a; padding: 1 2; }
    #center { width: 66%; padding: 0 1; }
    .panel { border: round #313b43; padding: 1 2; margin: 0 0 1 0; }
    #menu { height: 1fr; overflow-y: auto; }
    ListItem { padding: 0 1; color: #b6c1c6; }
    ListItem.--highlight { background: #741b25; color: white; }
    #logs { height: 1fr; overflow-y: auto; color: #a5e5b3; }
    Input { margin: 1 0; border: round #38464f; background: #10151a; color: #f0f3f4; }
    """

    def __init__(self, session: Session, reports_dir: str) -> None:
        super().__init__()
        self.session = session
        self.engine = MonitoringEngine()
        self.reports_dir = reports_dir

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="body"):
            with Vertical(id="left"):
                yield Static("BLACKHAWK\nKamu kaynaklı, yetkili izleme\nToken gerekmez.", classes="panel")
                yield ListView(
                    ListItem(Label("Yeni Hedef"), id="new"),
                    ListItem(Label("Canlı İzleme"), id="scan"),
                    ListItem(Label("Raporlar"), id="reports"),
                    ListItem(Label("Çıkış"), id="quit"),
                    id="menu",
                )
            with Vertical(id="center"):
                yield Static(id="logs", classes="panel")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        text = f"Durum: {self.session.status}\nHedef: {len(self.session.targets)} | Gözlem: {len(self.session.observations)}\n\n"
        text += "\n".join(format_item(item) for item in self.session.logs[-16:]) or "Hazır."
        self.query_one("#logs", Static).update(text)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        app = cast("BlackHawkApp", self.app)
        if event.item.id == "quit":
            app.exit()
        elif event.item.id == "scan":
            self.engine.run_once(self.session)
            self._refresh()
        elif event.item.id == "reports":
            target = self.session.targets[0].value if self.session.targets else "blackhawk-session"
            ReportWriter(self.reports_dir).write_all(self.session, target)
            self._refresh()
        elif event.item.id == "new":
            self.push_screen(TargetScreen(self.session, self.engine, self._refresh))


def format_item(item: dict[str, object]) -> str:
    return f"[{item.get('timestamp', '--:--:--')}] {item.get('level', 'INFO')} {item.get('message', '')}"


class TargetScreen(ModalScreen[None]):
    def __init__(self, session: Session, engine: MonitoringEngine, refresh) -> None:
        super().__init__()
        self.session, self.engine, self.refresh = session, engine, refresh

    def compose(self) -> ComposeResult:
        with Vertical(classes="panel"):
            yield Static("Yetkili kamu URL'si ekle")
            yield Input(placeholder="https://example.com", id="target")
            yield Button("Geri", id="back")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        try:
            self.engine.add_target(self.session, event.value)
            self.refresh()
            self.dismiss()
        except SafetyError as exc:
            event.input.value = ""
            event.input.placeholder = str(exc)[:80]

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()