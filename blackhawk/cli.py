from __future__ import annotations

import argparse
import getpass
import os
import sys
from pathlib import Path

from . import __version__
from .legal import CONTRACT_STEPS
from .logging_utils import make_log
from .models import Session
from .monitoring import MonitoringEngine
from .security import (
    SafetyError,
    store_token_fingerprint,
    store_password_fingerprint,
    validate_profile_password,
    validate_session_token,
    write_encrypted_profile,
)


def _config_dir() -> Path:
    return Path(os.environ.get("BLACKHAWK_HOME", Path.home() / ".blackhawk"))


def _ask_yes(text: str) -> None:
    print(f"\n{text}\n")
    answer = input("Onay için EVET yazın: ").strip().upper()
    if answer != "EVET":
        raise SafetyError("Sözleşme onaylanmadı; güvenli biçimde çıkılıyor.")


def _collect_profile(config_dir: Path) -> dict[str, object]:
    profile_path = config_dir / "lock.file.zip"
    if profile_path.exists():
        return {"name": "Kayıtlı operatör", "profile_file": str(profile_path)}
    name = input("Operatör adınız (rapor kimliği için): ").strip()
    if not name or len(name) > 120:
        raise SafetyError("Operatör adı boş olamaz veya 120 karakteri aşamaz.")
    gender = input("Cinsiyet (belirtmek istemiyorum yazabilirsiniz): ").strip()[:40]
    age_text = input("Yaşınız: ").strip()
    if not age_text.isdigit() or not 13 <= int(age_text) <= 120:
        raise SafetyError("Yaş 13 ile 120 arasında bir sayı olmalıdır.")
    print(
        "\nKişisel profil kasası için yeni bir parola belirleyin. "
        "En az 8 karakter, bir büyük harf ve bir rakam zorunludur.\n"
        "Bu parolayı e-Devlet, MHRS, banka veya sosyal medya parolanızla aynı seçmeyin."
    )
    password = getpass.getpass("Profil kasası parolası: ")
    confirmation = getpass.getpass("Profil kasası parolası tekrar: ")
    if password != confirmation:
        raise SafetyError("Parola doğrulaması başarısız.")
    validate_profile_password(password)
    profile = {"name": name, "gender": gender, "age": int(age_text)}
    write_encrypted_profile(config_dir, profile, password)
    store_password_fingerprint(config_dir, password)
    return profile


def startup_gate(config_dir: Path) -> tuple[str, dict[str, object]]:
    acceptance_path = config_dir / "accepted-contract-v1"
    if not acceptance_path.exists():
        for title, body in CONTRACT_STEPS:
            _ask_yes(f"{title}\n{body}")
        config_dir.mkdir(parents=True, exist_ok=True)
        acceptance_path.write_text("accepted\n", encoding="utf-8")
    try:
        token = getpass.getpass(
            "Oturum tokeni (en az 20 karakter; yalnızca BÜYÜK HARF ve rakam): "
        )
    except (EOFError, KeyboardInterrupt) as exc:
        raise SafetyError("Oturum başlatılamadı.") from exc
    validate_session_token(token)
    store_token_fingerprint(config_dir, token)
    profile = _collect_profile(config_dir)
    return token, profile


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="BlackHawk — yetkili kamu kaynakları için etik Türkçe OSINT terminali"
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--target", action="append", default=[], help="Yetkili kamu URL'si; tekrar edilebilir")
    parser.add_argument("--duration", type=int, default=60, help="Oturum süresi (dakika)")
    parser.add_argument("--reports", default="reports", help="Rapor klasörü")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.duration < 1 or args.duration > 300 * 60:
        print("Süre 1 dakika ile 300 saat arasında olmalıdır.")
        return 2
    try:
        _, profile = startup_gate(_config_dir())
        session = Session(
            duration_minutes=args.duration,
            operator_name=str(profile.get("name", "")),
            operator_gender=str(profile.get("gender", "")),
            operator_age=int(profile["age"]) if "age" in profile else None,
        )
        session.logs.append(make_log("AI-SHIELD", "SECURITY", "Etik kullanım kapısı geçildi"))
        engine = MonitoringEngine()
        for value in args.target:
            engine.add_target(session, value)
        try:
            from .ui import BlackHawkApp
        except ImportError:
            from .terminal_ui import run_ansi

            return run_ansi(session, engine, args.reports)
        BlackHawkApp(session, reports_dir=args.reports).run()
    except (SafetyError, EOFError, KeyboardInterrupt) as exc:
        print(f"\nBlackHawk durduruldu: {exc}")
        return 130 if isinstance(exc, KeyboardInterrupt) else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())