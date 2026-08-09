from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from .legal import LEGAL_TEXT
from .logging_utils import SEVERITIES, format_log
from .models import Session
from .monitoring import MonitoringEngine
from .reports import ReportWriter

MENU = ["Yeni Hedef", "Çoklu Hedef", "Canlı İzleme", "Kaynak Keşfi", "Zaman Çizelgesi",
        "İlişki Grafiği", "Kanıtlar", "Raporlar", "Help", "Ayarlar", "Güvenlik / TCK", "Çıkış"]
HAWK_MARK = "      /\\_/\\\\\n     ( o.o )\n      > ^ <"


class BlackHawkApp(App[None]):
    TITLE = "BLACKHAWK v0.1.0 | OSINT & INTELLIGENCE PLATFORM"
    CSS = """
    Screen { background: #080a0d; color: #dfe6e9; }
    Header { background: #130d10; color: #f0e7e4; }
    #body { height: 1fr; }
    #left { width: 33%; border: round #8f202a; padding: 1 2; }
    #center { width: 67%; }
    .panel { border: round #2c3940; padding: 1 2; margin: 0 0 1 0; }
    #menu { height: 1fr; }
    ListItem { padding: 0 1; }
    ListItem.--highlight { background: #741b25; color: white; }
    #logs { height: 1fr; overflow-y: auto; color: #a5e5b3; }
    #targets { height: 10; color: #93e6a9; }
    .red { color: #ef4b57; }
    .muted { color: #8f9ba3; }
    """
    BINDINGS = [("q", "quit", "Çıkış"), ("r", "scan", "Tarayı çalıştır"), ("h", "help", "Yardım")]

    def __init__(self, session: Session, demo: bool = False):
        super().__init__()
        self.session = session
        self.demo = demo
        self.engine = MonitoringEngine()

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="body"):
            with Vertical(id="left"):
                yield Static(f"[red]{HAWK_MARK}[/red]\n[bold]BLACKHAWK[/bold]\n"
                             "[bold]KAMU KAYNAKLI İSTİHBARAT[/bold]\n\n[red]ETİK MOD[/red] aktif", classes="panel")
                yield ListView(*(ListItem(Label(item)) for item in MENU), id="menu")
                yield Static("↑↓ Gezin  Enter Seç\nr Tarama  h Yardım  q Çıkış", classes="panel")
            with Vertical(id="center"):
                yield Static(id="targets", classes="panel")
                yield Static("CANLI LOG AKIŞI", classes="panel")
                yield Static(id="logs", classes="panel")
                yield Static(id="summary", classes="panel")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        targets = self.query_one("#targets", Static)
        target_text = "[red]AKTİF HEDEFLER[/red]\n" + "\n".join(
            f"[{index:02d}] {item.value:<35} — izleniyor"
            for index, item in enumerate(self.session.targets, 1)
        )
        targets.update(target_text or "[red]AKTİF HEDEFLER[/red]\nHenüz hedef eklenmedi. Demo akış için `--demo` kullanın.")
        logs = self.query_one("#logs", Static)
        logs.update("\n".join(format_log(item) for item in self.session.logs[-14:]) or "Log bekleniyor...")
        summary = self.query_one("#summary", Static)
        summary.update(
            f"[red]SİSTEM DURUMU[/red]\nDurum: {self.session.status}   "
            f"Gözlem: {len(self.session.observations)}   "
            f"Çalışma: {self.session.elapsed_minutes} dk / {self.session.duration_minutes} dk"
        )

    def action_scan(self) -> None:
        self.engine.run_once(self.session, demo=self.demo)
        self._refresh()

    def action_help(self) -> None:
        self.push_screen(HelpScreen())

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        selected = str(event.item.query_one(Label).renderable)
        if selected == "Help":
            self.action_help()
        elif selected == "Güvenlik / TCK":
            self.push_screen(LegalScreen())
        elif selected == "Raporlar":
            if self.session.targets:
                paths = ReportWriter().write_all(self.session, self.session.targets[0].value)
                self.session.logs.append({"timestamp": "now", "module": "REPORT", "level": "AI-SUCCESS",
                                          "message": f"Raporlar yazıldı: {', '.join(str(p) for p in paths.values())}",
                                          "target": self.session.targets[0].value, "confidence": "-"})
                self._refresh()
        elif selected == "Canlı İzleme":
            self.action_scan()


class HelpScreen(ModalScreen[None]):
    def compose(self) -> ComposeResult:
        yield Static("[red]BLACKHAWK HELP[/red]\n\n"
                     "↑ ↓: menüde gezin\nEnter: seç\nr: tek tarama çalıştır\nh: bu yardımı aç\nq: çıkış\n\n"
                     "AI-INFO: bilgilendirme\nAI-VERIFY: kaynak doğrulama\nAI-SHIELD: güvenlik sınırı\n"
                     "AI-WARNING: işlem uyarısı\nAI-GHOST: bulunamayan veya zayıf sinyal\n\n"
                     "Raporlar yerel `reports/` klasörüne HTML, JSON ve TXT olarak yazılır.\n"
                     "Gerçek bulgu için kaynak URL'si gerekir; demo kayıtları raporda işaretlenir.\n\n"
                     "Kapatmak için Escape tuşuna basın.", classes="panel")

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss()


class LegalScreen(ModalScreen[None]):
    def compose(self) -> ComposeResult:
        text = "\n\n".join(f"[red]{title}[/red]\n{body}" for title, body in LEGAL_TEXT)
        yield Static("[red]GÜVENLİK / TCK — ETİK KULLANIM[/red]\n\n" + text +
                     "\n\nKapatmak için Escape tuşuna basın.", classes="panel")

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss()