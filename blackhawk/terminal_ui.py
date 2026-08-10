from __future__ import annotations

import os
import shutil

from .logging_utils import format_log
from .models import Session
from .monitoring import MonitoringEngine
from .reports import ReportWriter
from .security import SafetyError


def _clear() -> None:
    if os.getenv("TERMUX_VERSION") or os.getenv("PREFIX", "").endswith("/com.termux/files/usr"):
        print("\033[2J\033[H", end="")
    elif os.name != "nt":
        os.system("clear")
    else:
        os.system("cls")


def run_ansi(session: Session, engine: MonitoringEngine, reports_dir: str) -> int:
    """Dependency-free menu that works in Termux, pipes and small terminals."""
    while True:
        _clear()
        width = min(shutil.get_terminal_size((80, 24)).columns, 120)
        print("\033[31m" + "BLACKHAWK / ETHICAL INTELLIGENCE".center(width) + "\033[0m")
        print("Termux uyumluluk modu — oturum tokeni gerekmez.\n")
        print("[1] Yeni hedef   [2] Canlı izleme   [3] Raporlar   [4] Yardım   [q] Çıkış")
        print(f"\nDurum: {session.status} | Hedef: {len(session.targets)} | Gözlem: {len(session.observations)}")
        for entry in session.logs[-8:]:
            print(format_log(entry))
        try:
            choice = input("\nSeçim: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nBlackHawk kapatıldı.")
            return 0
        if choice == "q":
            return 0
        if choice == "1":
            try:
                engine.add_target(session, input("Yetkili http/https URL'si: "))
            except (SafetyError, EOFError) as exc:
                print(f"Reddedildi: {exc}")
            input("Devam için Enter...")
        elif choice == "2":
            result = engine.run_once(session)
            print(f"Tamamlandı: {len(result.observations)} bulgu, {len(result.errors)} hata.")
            input("Devam için Enter...")
        elif choice == "3":
            target = session.targets[0].value if session.targets else "blackhawk-session"
            paths = ReportWriter(reports_dir).write_all(session, target)
            print("Raporlar: " + ", ".join(str(path) for path in paths.values()))
            input("Devam için Enter...")
        elif choice == "4":
            print("Yalnızca yetkili ve kamuya açık http/https kaynaklarını kullanın.")
            input("Ana menüye dönmek için Enter...")
        else:
            print("Geçersiz seçim.")
            input("Devam için Enter...")