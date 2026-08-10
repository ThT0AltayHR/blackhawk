from __future__ import annotations

import os
import shutil
import sys
from contextlib import contextmanager
from typing import Iterator

from .logging_utils import format_log
from .models import Session
from .monitoring import MonitoringEngine
from .reports import ReportWriter
from .security import SafetyError

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[91m"
MAROON = "\033[31m"
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
WHITE = "\033[97m"
BG_PANEL = "\033[48;5;233m"
BG_SELECTED = "\033[48;5;52m"

MENU = (
    ("1", "YENİ HEDEF"),
    ("2", "CANLI İZLEME"),
    ("3", "RAPORLAR"),
    ("4", "YARDIM"),
    ("q", "ÇIKIŞ"),
)


def _clear() -> None:
    """Clear the visible screen without relying on the Termux `clear` binary."""
    print("\033[2J\033[H", end="", flush=True)


def _hide_cursor() -> None:
    print("\033[?25l", end="", flush=True)


def _show_cursor() -> None:
    print("\033[?25h", end="", flush=True)


def _term_width() -> int:
    return max(72, min(shutil.get_terminal_size((100, 30)).columns, 140))


def _clip(value: object, width: int) -> str:
    text = str(value).replace("\n", " ")
    return text if len(text) <= width else text[: max(0, width - 1)] + "…"


def _line(width: int, left: str = "", right: str = "", fill: str = " ") -> str:
    inner = max(1, width - 2)
    content = left + (fill * max(0, inner - len(left) - len(right))) + right
    return "│" + content[:inner] + "│"


def _box(title: str, lines: list[str], width: int, color: str = RED) -> list[str]:
    inner = max(1, width - 2)
    title_text = f" {title} "
    top = "┌" + color + BOLD + title_text + RESET + "─" * max(0, inner - len(title_text)) + "┐"
    result = [top]
    for line in lines:
        result.append("│" + _clip(line, inner).ljust(inner) + "│")
    result.append("└" + "─" * inner + "┘")
    return result


def _header(width: int, session: Session) -> list[str]:
    title = f"{RED}{BOLD} BLACKHAWK {RESET}{DIM} / ETHICAL PUBLIC INTELLIGENCE{RESET}"
    meta = f"{GREEN}● ONLINE{RESET}  {DIM}v1.0.2  •  TOKEN GEREKMEZ{RESET}"
    inner = width - 2
    plain_title = " BLACKHAWK  / ETHICAL PUBLIC INTELLIGENCE"
    plain_meta = "● ONLINE  v1.0.2  •  TOKEN GEREKMEZ"
    return [
        "┏" + "━" * inner + "┓",
        "┃" + title + " " * max(0, inner - len(plain_title)) + "┃",
        "┃" + meta + " " * max(0, inner - len(plain_meta)) + "┃",
        "┗" + "━" * inner + "┛",
    ]


def _menu(width: int, selected: str) -> list[str]:
    lines = [
        f"{RED}{BOLD}KONTROL MERKEZİ{RESET}",
        "",
    ]
    for key, label in MENU:
        mark = "◆" if key == selected else "◇"
        color = RED if key == selected else DIM
        lines.append(f"{color}{mark}{RESET} {BOLD if key == selected else ''}[{key}] {label}{RESET}")
    lines.extend(
        [
            "",
            f"{DIM}Mobil terminal kısayolları{RESET}",
            f"{DIM}Numara seç • q çıkış{RESET}",
        ]
    )
    return _box("MENU", lines, width, MAROON)


def _dashboard(width: int, session: Session) -> list[str]:
    logs = session.logs[-7:]
    log_lines = [f"{RED}{BOLD}CANLI LOG AKIŞI{RESET}", ""]
    log_lines.extend(format_log(entry) for entry in logs)
    if not logs:
        log_lines.append(f"{DIM}Henüz log yok.{RESET}")
    return _box("WORKSPACE", log_lines, width, RED)


def _status(width: int, session: Session) -> list[str]:
    lines = [
        f"{GREEN}● {session.status.upper()}{RESET}",
        "",
        f"{DIM}HEDEF{RESET}       {BOLD}{len(session.targets)}{RESET}",
        f"{DIM}GÖZLEM{RESET}      {BOLD}{len(session.observations)}{RESET}",
        f"{DIM}SÜRE{RESET}        {session.elapsed_minutes} / {session.duration_minutes} dk",
        "",
        f"{CYAN}SHIELD{RESET}      {GREEN}AKTİF{RESET}",
        f"{CYAN}SOURCE WATCH{RESET} {GREEN}HAZIR{RESET}",
        f"{CYAN}REPORT WRITER{RESET} {YELLOW}BEKLEMEDE{RESET}",
    ]
    return _box("SİSTEM DURUMU", lines, width, CYAN)


def _render(session: Session, selected: str) -> None:
    width = _term_width()
    _clear()
    print(*_header(width, session), sep="\n")
    usable = width - 6
    left_width = max(28, min(34, usable // 3))
    right_width = max(24, min(30, usable // 4))
    center_width = max(32, usable - left_width - right_width)
    left = _menu(left_width, selected)
    center = _dashboard(center_width, session)
    right = _status(right_width, session)
    rows = max(len(left), len(center), len(right))
    print()
    for index in range(rows):
        columns = []
        for panel, panel_width in ((left, left_width), (center, center_width), (right, right_width)):
            value = panel[index] if index < len(panel) else ""
            columns.append(value.ljust(panel_width))
        print("  ".join(columns))
    print()
    print(f"{BG_PANEL}{WHITE}{BOLD} Seçim yapın: [1] Hedef  [2] İzleme  [3] Rapor  [4] Yardım  [q] Çıkış {RESET}")
    print(f"{DIM}BlackHawk • yalnızca yetkili ve kamuya açık kaynaklar{RESET}")


@contextmanager
def _screen() -> Iterator[None]:
    """Use the alternate screen on real terminals and always restore the cursor."""
    interactive = sys.stdout.isatty()
    if interactive:
        print("\033[?1049h", end="", flush=True)
    _hide_cursor()
    try:
        yield
    finally:
        _show_cursor()
        if interactive:
            print("\033[?1049l", end="", flush=True)


def _pause(message: str = "Devam için Enter...") -> None:
    _show_cursor()
    try:
        input(f"\n{YELLOW}{message}{RESET}")
    except (EOFError, KeyboardInterrupt):
        pass
    finally:
        _hide_cursor()


def _add_target(session: Session, engine: MonitoringEngine) -> None:
    _show_cursor()
    try:
        value = input(f"\n{CYAN}Yetkili http/https URL'si:{RESET} ").strip()
        engine.add_target(session, value)
        session.logs.append(
            {
                "timestamp": "now",
                "level": "SUCCESS",
                "module": "TARGET",
                "message": "Hedef menüden eklendi",
                "target": value,
            }
        )
    except (SafetyError, EOFError, KeyboardInterrupt) as exc:
        if isinstance(exc, SafetyError):
            print(f"\n{RED}Reddedildi:{RESET} {exc}")
        else:
            print(f"\n{YELLOW}İşlem iptal edildi.{RESET}")
        _pause()
    finally:
        _hide_cursor()


def _run_scan(session: Session, engine: MonitoringEngine) -> None:
    result = engine.run_once(session)
    print(
        f"\n{GREEN}Tarama tamamlandı:{RESET} "
        f"{len(result.observations)} bulgu, {len(result.errors)} hata."
    )
    _pause()


def _write_reports(session: Session, reports_dir: str) -> None:
    target = session.targets[0].value if session.targets else "blackhawk-session"
    paths = ReportWriter(reports_dir).write_all(session, target)
    print(f"\n{GREEN}Raporlar hazır:{RESET}")
    for path in paths.values():
        print(f"  {CYAN}•{RESET} {path}")
    _pause()


def _help() -> None:
    print(
        f"\n{RED}{BOLD}BLACKHAWK / YARDIM{RESET}\n\n"
        "1  Yetkili bir http/https kamu URL'si ekler.\n"
        "2  Eklenen kaynakları tek istekle gözlemler.\n"
        "3  JSON, TXT, HTML ve PDF raporu oluşturur.\n"
        "4  Bu yardım ekranını gösterir.\n"
        "q  Uygulamadan çıkar.\n\n"
        f"{DIM}Oturum tokeni, profil parolası ve gizli hesap erişimi yoktur.{RESET}"
    )
    _pause()


def run_ansi(session: Session, engine: MonitoringEngine, reports_dir: str) -> int:
    """Full-screen ANSI dashboard for Termux and minimal Python installations."""
    selected = "1"
    with _screen():
        while True:
            _render(session, selected)
            try:
                choice = input().strip().lower()
            except (EOFError, KeyboardInterrupt):
                return 0
            selected = choice if choice in {item[0] for item in MENU} else selected
            if choice == "q":
                return 0
            if choice == "1":
                _add_target(session, engine)
            elif choice == "2":
                _run_scan(session, engine)
            elif choice == "3":
                _write_reports(session, reports_dir)
            elif choice == "4":
                _help()
            elif choice:
                print(f"\n{RED}Geçersiz seçim.{RESET}")
                _pause()