from __future__ import annotations

from typing import cast

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Input, Label, ListItem, ListView, Static, TextArea

from .legal import LEGAL_TEXT
from .logging_utils import SEVERITIES, format_log
from .models import Session
from .monitoring import MonitoringEngine
from .reports import ReportWriter
from .security import SafetyError

MENU = [
    "Yeni Hedef",
    "Çoklu Hedef",
    "Olay Analizi",
    "Canlı İzleme",
    "Kaynak Keşfi",
    "Hashtag Arama",
    "Zaman Çizelgesi",
    "İlişki Grafiği",
    "Kanıtlar",
    "Raporlar",
    "Ajanlar",
    "Help",
    "Ayarlar",
    "Güvenlik / TCK",
    "İletişim",
    "Çıkış",
]

HAWK_MARK = (
    "       __/\\\n"
    "      /  _ \\\n"
    "     /  /_)  \\\n"
    "    /__/     \\\n"
    "   <  BLACKHAWK  >"
)


class BlackHawkApp(App[None]):
    TITLE = "BLACKHAWK v1.0.0 | OSINT & INTELLIGENCE PLATFORM"
    CSS = """
    Screen { background: #07090c; color: #dfe6e9; }
    Header { background: #140c10; color: #f2eeee; }
    Footer { background: #130d10; color: #91a0aa; }
    #body { height: 1fr; }
    #left { width: 31%; min-width: 31; border: round #8f202a; padding: 1 2; }
    #center { width: 69%; padding: 0 1; }
    .panel { border: round #313b43; padding: 1 2; margin: 0 0 1 0; }
    .brand { border: round #a4232d; color: #dfe6e9; }
    #menu { height: 1fr; overflow-y: auto; }
    ListItem { padding: 0 1; color: #b6c1c6; }
    ListItem.--highlight { background: #741b25; color: white; }
    #targets { height: 13; color: #8ee0a0; }
    #workspace { height: 1fr; }
    #logs { width: 63%; height: 1fr; overflow-y: auto; color: #a5e5b3; }
    #right { width: 37%; }
    #critical { height: 1fr; color: #ff8a91; }
    #agents { height: 15; color: #a8ddb4; }
    #summary { height: 10; color: #9eb2bc; }
    .red { color: #ef4b57; }
    .green { color: #7edb91; }
    .muted { color: #8f9ba3; }
    .modal { width: 90%; height: 86%; border: round #a4232d; background: #0a0d11; padding: 1 2; }
    .modal-title { color: #ef4b57; text-style: bold; }
    .modal-copy { height: 1fr; overflow-y: auto; color: #cbd4d8; }
    Input, TextArea { margin: 1 0; border: round #38464f; background: #10151a; color: #f0f3f4; }
    Button { margin: 0 1 0 0; background: #52151e; color: white; }
    @media (max-width: 90) {
      #left { width: 38%; min-width: 27; }
      #center { width: 62%; }
      #logs { width: 100%; }
      #right { display: none; }
    }
    @media (max-width: 60) {
      #body { height: auto; overflow-y: auto; }
      #left, #center { width: 100%; }
      #menu { height: 22; }
    }
    """
    BINDINGS = [
        ("q", "quit", "Çıkış"),
        ("r", "scan", "Tarama"),
        ("h", "help", "Yardım"),
        ("escape", "back", "Geri"),
    ]

    def __init__(self, session: Session, reports_dir: str = "reports"):
        super().__init__()
        self.session = session
        self.engine = MonitoringEngine()
        self.report_writer = ReportWriter(reports_dir)
        self._agent_tick = 0

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="body"):
            with Vertical(id="left"):
                yield Static(
                    f"[red]{HAWK_MARK}[/red]\n"
                    "[bold]BLACKHAWK[/bold]  [dim]v1.0.0 STABLE[/dim]\n"
                    "[bold]KAMU KAYNAKLI İSTİHBARAT[/bold]\n"
                    "[red]ETHICAL INTELLIGENCE / TURKHACKTEAM[/red]\n\n"
                    f"Geliştirici: [bold]ThT0AltayHR[/bold]\n"
                    "Telegram: [bold]@AltayHR[/bold]\n"
                    "Durum: [green]READY / OFFLINE-FIRST[/green]",
                    classes="panel brand",
                )
                yield ListView(
                    *(ListItem(Label(item), id=f"menu-{index}") for index, item in enumerate(MENU)),
                    id="menu",
                )
                yield Static(
                    "↑↓ Gezin   Enter Aç\n"
                    "r Tarama   h Yardım\n"
                    "Esc Geri   q Çıkış",
                    classes="panel muted",
                )
            with Vertical(id="center"):
                yield Static(id="targets", classes="panel")
                with Horizontal(id="workspace"):
                    yield Static(id="logs", classes="panel")
                    with Vertical(id="right"):
                        yield Static(id="critical", classes="panel")
                        yield Static(id="agents", classes="panel")
                        yield Static(id="summary", classes="panel")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh()
        self.set_interval(1.0, self._tick)

    def _tick(self) -> None:
        self._agent_tick += 1
        self._refresh()

    def _refresh(self) -> None:
        target_text = "[red]AKTİF HEDEFLER / AUTHORIZED SOURCES[/red]\n"
        target_text += "\n".join(
            f"[{index:02d}] {item.display_name[:30]:<30} — {item.risk}"
            for index, item in enumerate(self.session.targets, 1)
        )
        self.query_one("#targets", Static).update(target_text or target_text + "Kaynak bekleniyor.")

        logs = self.session.logs[-18:]
        self.query_one("#logs", Static).update(
            "[red]CANLI LOG AKIŞI[/red]\n"
            + ("\n".join(format_log(item) for item in logs) or "Log bekleniyor...")
        )
        critical = [
            item for item in self.session.logs if item.get("level") in {"AI-CRITICAL", "AI-WARNING"}
        ][-8:]
        self.query_one("#critical", Static).update(
            "[red]KRİTİK / UYARI BULGULARI[/red]\n"
            + ("\n".join(format_log(item) for item in critical) or "Kritik bulgu yok.")
        )
        agent_messages = [
            "SOURCE WATCH  [green]● AKTİF[/green]  kamu kaynağı doğruluyor",
            "EVIDENCE LINK [green]● AKTİF[/green]  kaynak-zaman korelasyonu",
            "AI REVIEW      [green]● AKTİF[/green]  bulgu sınıfını özetliyor",
            "REPORT WRITER  [dim]○ BEKLEMEDE[/dim]  rapor talebi bekliyor",
            "SHIELD         [green]● AKTİF[/green]  yetki ve gizli veri sınırı",
        ]
        offset = self._agent_tick % len(agent_messages)
        self.query_one("#agents", Static).update(
            "[red]AJAN DURUMU  4/5 AKTİF[/red]\n"
            + "\n".join(agent_messages[offset:] + agent_messages[:offset])
        )
        self.query_one("#summary", Static).update(
            "[red]SİSTEM DURUMU[/red]\n"
            f"Durum: {self.session.status}\n"
            f"Hedef: {len(self.session.targets)}   Gözlem: {len(self.session.observations)}\n"
            f"Rapor: {len(self.session.observations)} kaynaklı kayıt\n"
            f"Süre: {self.session.elapsed_minutes} dk / {self.session.duration_minutes} dk"
        )

    def action_scan(self) -> None:
        self.engine.run_once(self.session, on_log=lambda _: self._refresh())
        self._refresh()

    def action_help(self) -> None:
        self.push_screen(HelpScreen())

    def action_back(self) -> None:
        if len(self.screen_stack) > 1:
            self.pop_screen()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id or ""
        try:
            selected = MENU[int(item_id.removeprefix("menu-"))]
        except (ValueError, IndexError):
            self.session.logs.append(
                {"timestamp": "now", "module": "UI", "level": "AI-WARNING",
                 "message": "Geçersiz menü seçimi engellendi.", "target": "-", "confidence": "-"}
            )
            self._refresh()
            return
        if selected == "Help":
            self.action_help()
        elif selected == "Güvenlik / TCK":
            self.push_screen(LegalScreen())
        elif selected == "Raporlar":
            self.push_screen(ModuleScreen(selected, self.session, "Rapor oluşturmak için BAŞLAT'a basın."))
        elif selected == "Çıkış":
            self.exit()
        elif selected == "Canlı İzleme":
            self.push_screen(ModuleScreen(selected, self.session, "Yetkili hedefler için canlı taramayı başlatın."))
        elif selected == "Yeni Hedef":
            self.push_screen(ModuleScreen(selected, self.session, "Yalnızca yetkili kamu URL'si ekleyin.", input_kind="target"))
        elif selected == "Olay Analizi":
            self.push_screen(
                ModuleScreen(
                    selected,
                    self.session,
                    "Olayı kendi kelimelerinizle yazın. BlackHawk metni yapılandırır; "
                    "soruşturma, suç isnadı veya otomatik doğrulama yapmaz.",
                    input_kind="incident",
                )
            )
        else:
            self.push_screen(ModuleScreen(selected, self.session, MODULE_COPY.get(selected, "Modül hazır.")))


MODULE_COPY = {
    "Çoklu Hedef": "Birden fazla yetkili kamu kaynağını satır satır ekleyin; her kaynak ayrı denetlenir.",
    "Kaynak Keşfi": "URL'yi, kaynak başlığını ve erişim zamanını kanıt zincirinde tutun.",
    "Hashtag Arama": "Hashtag araması yalnızca sizin verdiğiniz açık kaynak URL'leri ve metinleri düzenler.",
    "Zaman Çizelgesi": "Gözlemleri UTC erişim zamanına göre kronolojik olarak görüntüler.",
    "İlişki Grafiği": "Hedef, kaynak ve gözlem bağlarını açıklanabilir biçimde özetler.",
    "Kanıtlar": "Kaynaklı gözlemleri güven puanı ve çelişki durumuna göre filtreleyin.",
    "Ajanlar": "Aktif ajanlar yalnızca yerel görev durumunu gösterir; gizli erişim veya arka kapı yoktur.",
    "Ayarlar": "Rapor klasörü ve oturum davranışı CLI seçenekleriyle yönetilir.",
    "İletişim": "Öneri ve hata bildirimleri için geliştirici Telegram: @AltayHR. Token veya kişisel veri göndermeyin.",
}


class ModuleScreen(ModalScreen[None]):
    def __init__(self, title: str, session: Session, copy: str, input_kind: str | None = None):
        super().__init__()
        self.title_text = title
        self.session = session
        self.copy = copy
        self.input_kind = input_kind

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal"):
            yield Static(f"[red]BLACKHAWK / {self.title_text.upper()}[/red]", classes="modal-title")
            yield Static(self.copy, classes="modal-copy")
            if self.input_kind == "target":
                yield Input(placeholder="https://yetkili-kamu-kaynagi.example", id="target-value")
            elif self.input_kind == "incident":
                yield TextArea(
                    text="",
                    language="markdown",
                    id="incident-value",
                    show_line_numbers=False,
                )
            with Horizontal():
                yield Button("BAŞLAT", id="run")
                yield Button("GERİ", id="back")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        app = cast(BlackHawkApp, self.app)
        if event.button.id == "back":
            self.dismiss()
            return
        if event.button.id != "run":
            return
        if self.title_text == "Yeni Hedef":
            value = self.query_one("#target-value", Input).value
            try:
                app.engine.add_target(app.session, value)
                app._refresh()
                self.dismiss()
            except SafetyError as exc:
                self.query_one("#target-value", Input).value = ""
                self.query_one(".modal-copy", Static).update(f"[red]Reddedildi:[/red] {exc}")
        elif self.title_text == "Olay Analizi":
            text = self.query_one("#incident-value", TextArea).text.strip()
            if not text:
                return
            app.session.incident = text
            app.session.incident_analysis = analyze_incident(text)
            app.session.logs.append(
                {"timestamp": "now", "module": "AI-REVIEW", "level": "AI-INFO",
                 "message": "Olay metni kaynak gerektiren analiz taslağına dönüştürüldü.",
                 "target": "incident", "confidence": "taslak"}
            )
            app._refresh()
            self.dismiss()
        elif self.title_text == "Canlı İzleme":
            app.action_scan()
            self.dismiss()
        elif self.title_text == "Raporlar":
            target = app.session.targets[0].value if app.session.targets else "blackhawk-session"
            paths = app.report_writer.write_all(app.session, target)
            app.session.logs.append(
                {"timestamp": "now", "module": "REPORT", "level": "AI-SUCCESS",
                 "message": f"Raporlar yazıldı: {', '.join(str(path) for path in paths.values())}",
                 "target": target, "confidence": "-"}
            )
            app._refresh()
            self.dismiss()


def analyze_incident(text: str) -> dict[str, object]:
    words = [word.strip(".,!?;:()[]{}\"'").lower() for word in text.split()]
    keywords = sorted({word for word in words if len(word) > 3})[:30]
    urgent = any(word in words for word in ("bıçak", "bıçakladı", "tehdit", "yaralama", "acil"))
    return {
        "summary": "Metin yerel olarak yapılandırıldı; bağımsız kaynak doğrulaması yoktur.",
        "keywords": keywords,
        "urgent_safety_signal": urgent,
        "recommended_next_step": "Acil tehlikede 112; olay bildiriminde resmi kolluk kanalları.",
        "evidence_needed": ["olay zamanı", "yer", "tanıklar", "kamuya açık kaynak URL'leri", "belge saklama zamanı"],
    }


class HelpScreen(ModalScreen[None]):
    def compose(self) -> ComposeResult:
        help_text = """
[red]BLACKHAWK v1.0.0 — KULLANIM REHBERİ[/red]

AMAÇ
BlackHawk; açıkça yetkilendirilmiş kamu kaynaklarını, erişim zamanını ve gözlemleri
yerel bir terminal akışında toplar. Özel hesaplara girmez, şifre/token istemez,
gizli servisleri taramaz, kaynak yoksa iddia üretmez.

BAŞLANGIÇ
1. blackhawk komutunu çalıştırın.
2. Sözleşme ekranlarının her birinde EVET yazıp Enter'a basın.
3. En az 20 karakterli, yalnızca BÜYÜK HARF ve rakamlardan oluşan oturum tokeni girin.
4. Menüde Yeni Hedef ile yetkili http/https URL'si ekleyin.
5. Canlı İzleme veya r ile kaynak gözlemini başlatın.
6. Raporlar bölümünde JSON, TXT, HTML ve PDF çıktısını reports/ klasörüne yazın.

KLAVYE
↑/↓: menü | Enter: aç | r: tarama | h: yardım | Esc: geri | q: çıkış

MODÜLLER
Yeni Hedef ve Canlı İzleme ağ erişimi yapabilir; hedefin yetkisini siz doğrularsınız.
Olay Analizi yalnızca verdiğiniz metni anahtar kelimeler ve delil ihtiyaçları halinde
özetler; yerel yapay zekâ veya kolluk veri tabanı değildir.
Hashtag Arama, yalnızca kamuya açık ve yetkili metinleri düzenlemek için bir çalışma
etiketidir; gizli profil keşfi veya kişi takibi yapmaz.
Raporlar kaynak URL'si, erişim zamanı, güven sınıfı ve audit log üretir.

GÜVENLİK
Tokenler rapora yazılmaz ve yalnızca yerel oturum kapısı içindir. Profil şifrenizi
başka yerde kullandığınız şifreyle aynı seçmeyin; e-devlet, MHRS veya banka
şifrelerinizi asla kullanmayın. Token, parola, özel URL veya kişisel veriyi issue,
Telegram veya rapor paylaşımında göndermeyin.

YASAL SINIR
Yetkisiz erişim, rate limit aşma, doxxing, taciz, tehdit, hedefli zarar, kimlik
bilgisi deneme ve gizli veri toplama desteklenmez. Güncel TCK/KVKK metni için
resmi mevzuatı esas alın; bu yardım hukuki danışmanlık değildir. Acil tehlikede 112'yi,
olay bildirimi için ilgili resmi kolluk kanalını kullanın.

İLETİŞİM
Öneri ve hata bildirimi: Telegram @AltayHR. Bildirimde token, parola, canlı hedef
ve gereksiz kişisel veri paylaşmayın. Topluluk: TurkHackTeam.

Bu araçta demo modu yoktur. Gerçek olmayan bulgu, sahte ajan veya sahte doğrulama
başarılı kabul edilmez.

Kapatmak için Escape.
"""
        yield Static(help_text, classes="modal modal-copy")

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss()


class LegalScreen(ModalScreen[None]):
    def compose(self) -> ComposeResult:
        text = "\n\n".join(f"[red]{title}[/red]\n{body}" for title, body in LEGAL_TEXT)
        yield Static(
            "[red]GÜVENLİK / TCK — ETİK KULLANIM[/red]\n\n"
            + text
            + "\n\nKapatmak için Escape.",
            classes="modal modal-copy",
        )

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss()