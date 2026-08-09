from __future__ import annotations

import argparse
import getpass
import os
from pathlib import Path

from . import __version__
from .logging_utils import make_log
from .models import Session
from .monitoring import MonitoringEngine
from .security import SafetyError
from .ui import BlackHawkApp


def startup_gate(demo: bool) -> bool:
    """Require an operator acknowledgement before any scan or network action."""
    existing = os.environ.get("BLACKHAWK_SESSION_TOKEN", "")
    if existing:
        return True
    if demo:
        return True
    try:
        token = getpass.getpass("BlackHawk güvenli oturum tokeni (boş: offline/demo): ")
    except (EOFError, KeyboardInterrupt):
        return False
    if not token:
        print("Token verilmedi. Offline/demo modunda çalışabilirsiniz; dış kaynak taraması kapalı.")
        return False
    return True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="BlackHawk etik kamu kaynaklı izleme terminali")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--demo", action="store_true", help="Ağ çağrısı yapmadan demo oturumu aç")
    parser.add_argument("--target", action="append", default=[], help="Yetkili kamu URL'si; tekrar edilebilir")
    parser.add_argument("--duration", type=int, default=60, help="Oturum süresi (dakika)")
    parser.add_argument("--reports", default="reports", help="Rapor klasörü")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.duration < 1 or args.duration > 300 * 60:
        print("Süre 1 dakika ile 300 saat arasında olmalıdır.")
        return 2
    if not startup_gate(args.demo):
        print("Oturum açılmadı. Güvenli biçimde çıkılıyor.")
        return 1
    session = Session(duration_minutes=args.duration)
    session.logs.append(make_log("AI-SHIELD", "SECURITY", "Etik kullanım kapısı geçildi", "-", "uygun"))
    engine = MonitoringEngine()
    try:
        for value in args.target:
            engine.add_target(session, value)
    except SafetyError as exc:
        print(f"Güvenlik sınırı: {exc}")
        return 2
    if args.demo and not session.targets:
        engine.add_target(session, "https://demo.blackhawk.local/public", "BlackHawk demo kaynağı")
    try:
        BlackHawkApp(session, demo=args.demo).run()
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())