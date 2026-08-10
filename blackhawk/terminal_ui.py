from __future__ import annotations

import os
import shutil
from pathlib import Path

from .logging_utils import format_log
from .models import Session
from .monitoring import MonitoringEngine
from .reports import ReportWriter


def run_ansi(session: Session, engine: MonitoringEngine, reports_dir: str) -> int:
    """Minimal ANSI fallback for Termux or terminals without Textual support."""
    while True:
        os.system("clear" if os.name != "nt" else "cls")
        width = min(shutil.get_terminal_size((100, 30)).columns, 120)
        print("\033[31m" + "BLACKHAWK / ETHICAL INTELLIGENCE".center(width) + "\033[0m")
        print("TUI uyumluluk modu — Textual kurulamadı; tüm işlemler klavye ile çalışır.\n")
        print("[1] Yeni hedef   [2] Canlı izleme   [3] Raporlar   [4] Yardım   [q] Çıkış")
        print(f"\nDurum: {session.status} | Hedef: {len(session.targets)} | Gözlem: {len(session.observations)}")
        for entry in session.logs[-8:]:
            print(format_log(entry))
        choice = input("\nSeçim: ").strip().lower()
        if choice == "q":
            return 0
        if choice == "1":
            value = input("Yetkili http/https URL'si: ").strip()
            try:
                engine.add_target(session, value)
            except ValueError as exc:
                print(f"Reddedildi: {exc}")
                input("Devam için Enter...")
        elif choice == "2":
            engine.run_once(session)
        elif choice == "3":
            target = session.targets[0].value if session.targets else "blackhawk-session"
            paths = ReportWriter(reports_dir).write_all(session, target)
            print("Raporlar: " + ", ".join(str(path) for path in paths.values()))
            input("Devam için Enter...")
        elif choice == "4":
            print("Yalnızca yetkili kamu kaynaklarını kullanın. Esc/geri yok; ana menüye dönmek için Enter.")
            input()