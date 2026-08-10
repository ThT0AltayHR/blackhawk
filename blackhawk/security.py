from __future__ import annotations

import re
import hashlib
import hmac
import secrets
import zipfile
import json
from pathlib import Path
from urllib.parse import urlparse


class SafetyError(ValueError):
    """Raised when an input is outside the public-source safety boundary."""


def validate_public_target(value: str) -> str:
    candidate = value.strip()
    if not candidate or len(candidate) > 2048:
        raise SafetyError("Hedef boş olamaz ve 2048 karakteri aşamaz.")
    if any(marker in candidate.lower() for marker in ("password=", "passwd=", "secret=", "token=", "apikey=")):
        raise SafetyError("Kimlik bilgisi veya gizli veri içeren hedefler kabul edilmez.")
    if candidate.startswith(("@", "#")):
        return candidate
    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise SafetyError("Yalnızca açık http/https URL'leri kabul edilir.")
    if parsed.username or parsed.password:
        raise SafetyError("Kullanıcı adı veya parola içeren URL'ler kabul edilmez.")
    return candidate


def safe_filename(value: str) -> str:
    stem = re.sub(r"https?://", "", value.strip(), flags=re.IGNORECASE)
    stem = re.sub(r"[^a-zA-Z0-9._-]+", "-", stem).strip(".-_")
    return (stem or "blackhawk-session")[:100]


def safe_report_path(directory: Path, target: str, extension: str) -> Path:
    if extension not in {".json", ".txt", ".html", ".pdf"}:
        raise SafetyError("Desteklenmeyen rapor uzantısı.")
    root = directory.resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{safe_filename(target)}{extension}"


def validate_session_token(value: str) -> str:
    """Legacy validator retained for callers; startup no longer calls it."""
    candidate = value.strip()
    if not re.fullmatch(r"[A-Z0-9]{20,256}", candidate):
        raise SafetyError("Oturum tokeni en az 20 karakter ve yalnızca büyük harf/rakam olmalıdır.")
    return candidate


def validate_profile_password(value: str) -> str:
    """Legacy validator retained for callers; startup no longer asks for it."""
    candidate = value.strip()
    if not re.fullmatch(r"(?=.*[A-Z])(?=.*\d).{8,}", candidate):
        raise SafetyError("Profil parolası en az 8 karakter, bir büyük harf ve bir rakam içermelidir.")
    return candidate


def write_encrypted_profile(directory: Path, profile: dict[str, object], password: str) -> Path:
    """Write a dependency-free encrypted compatibility archive."""
    raw = json.dumps(profile, ensure_ascii=False, sort_keys=True).encode("utf-8")
    salt = secrets.token_bytes(16)
    nonce = secrets.token_bytes(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 210_000, 64)
    stream = b"".join(
        hmac.new(key[:32], nonce + counter.to_bytes(8, "big"), hashlib.sha256).digest()
        for counter in range((len(raw) // 32) + 1)
    )
    ciphertext = bytes(left ^ right for left, right in zip(raw, stream))
    tag = hmac.new(key[32:], nonce + ciphertext, hashlib.sha256).digest()
    directory.mkdir(parents=True, exist_ok=True)
    archive_path = directory / "lock.file.zip"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("profile.enc", salt + nonce + tag + ciphertext)
    return archive_path