from __future__ import annotations

import argparse
import os
import sys

from . import __version__
from .logging_utils import make_log
from .models import Session
from .monitoring import MonitoringEngine


def is_termux() -> bool:
    return bool(os.getenv("TERMUX_VERSION")) or os.getenv("PREFIX", "").endswith("/com.termux/files/usr")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="BlackHawk — yalnızca yetkili kamu kaynakları için Termux uyumlu terminal"
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--target", action="append", default=[], help="Yetkili http/https URL'si; tekrar edilebilir")
    parser.add_argument("--duration", type=int, default=60, help="Oturum süresi (dakika)")
    parser.add_argument("--reports", default="reports", help="Rapor klasörü")
    parser.add_argument("--ui", choices=("auto", "ansi", "textual"), default="auto", help="Arayüz seçimi")
    return parser


def _run_textual(session: Session, reports_dir: str) -> int:
    try:
        from .ui import BlackHawkApp
        BlackHawkApp(session, reports_dir=reports_dir).run()
        return 0
    except (ImportError, ModuleNotFoundError) as exc:
        print(f"Textual kullanılamıyor ({exc}); ANSI moda geçiliyor.", file=sys.stderr)
        from .terminal_ui import run_ansi
        return run_ansi(session, MonitoringEngine(), reports_dir)
    except Exception as exc:
        print(f"Textual arayüzü başlatılamadı ({exc}); ANSI moda geçiliyor.", file=sys.stderr)
        from .terminal_ui import run_ansi
        return run_ansi(session, MonitoringEngine(), reports_dir)


def main() -> int:
    args = build_parser().parse_args()
    if not 1 <= args.duration <= 300 * 60:
        print("Süre 1 dakika ile 300 saat arasında olmalıdır.")
        return 2
    session = Session(duration_minutes=args.duration)
    engine = MonitoringEngine()
    session.logs.append(make_log("SHIELD", "START", "Oturum tokeni olmadan güvenli başlatma"))
    for value in args.target:
        try:
            engine.add_target(session, value)
        except ValueError as exc:
            print(f"Hedef atlandı: {exc}", file=sys.stderr)
            return 2
    if args.ui == "ansi" or (args.ui == "auto" and is_termux()):
        from .terminal_ui import run_ansi
        return run_ansi(session, engine, args.reports)
    return _run_textual(session, args.reports)


if __name__ == "__main__":
    raise SystemExit(main())