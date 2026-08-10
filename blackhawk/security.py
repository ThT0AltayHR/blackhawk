from __future__ import annotations

import hashlib
import hmac
import re
import secrets
import zipfile
from pathlib import Path
from urllib.parse import urlparse

ALLOWED_SCHEMES = {"http", "https"}
TOKEN_PATTERN = re.compile(r"^[A-Z0-9]{20,256}$")
PASSWORD_PATTERN = re.compile(r"^(?=.*[A-Z])(?=.*\d).{8,}$")
SECRET_PATTERNS = [
    re.compile(r"(?i)(bearer\s+)[a-z0-9._\-]+"),
    re.compile(r"(?i)(api[_-]?key\s*[=:]\s*)\S+"),
    re.compile(r"(?i)(token\s*[=:]\s*)\S+"),
]


class SafetyError(ValueError):
    """Raised when an input falls outside the ethical safety boundary."""


def validate_public_target(value: str) -> str:
    candidate = value.strip()
    if not candidate or len(candidate) > 2048:
        raise SafetyError("Hedef boş olamaz ve 2048 karakteri aşamaz.")
    if any(marker in candidate.lower() for marker in ("password=", "passwd=", "secret=", "token=")):
        raise SafetyError("Kimlik bilgisi veya gizli veri içeren hedefler kabul edilmez.")
    if candidate.startswith(("@", "#")):
        return candidate
    parsed = urlparse(candidate)
    if parsed.scheme not in ALLOWED_SCHEMES or not parsed.netloc:
        raise SafetyError("Yalnızca açık http/https URL'leri veya @kullanıcı adı kabul edilir.")
    if parsed.username or parsed.password:
        raise SafetyError("Kullanıcı adı/parola içeren URL'ler kabul edilmez.")
    return candidate


def safe_filename(value: str, fallback: str = "blackhawk-raporu") -> str:
    stem = re.sub(r"^@", "", value.strip())
    stem = re.sub(r"https?://", "", stem, flags=re.IGNORECASE)
    stem = re.sub(r"[^a-zA-Z0-9._-]+", "-", stem).strip(".-_")
    return (stem or fallback)[:100]


def safe_report_path(directory: Path, target: str, extension: str) -> Path:
    if extension not in {".html", ".json", ".txt", ".pdf"}:
        raise SafetyError("Desteklenmeyen rapor uzantısı.")
    root = directory.resolve()
    root.mkdir(parents=True, exist_ok=True)
    candidate = (root / f"{safe_filename(target)}{extension}").resolve()
    if candidate.parent != root:
        raise SafetyError("Güvensiz rapor yolu.")
    return candidate


def mask_secrets(text: str) -> str:
    masked = text
    for pattern in SECRET_PATTERNS:
        masked = pattern.sub(lambda match: f"{match.group(1)}***", masked)
    return masked


def validate_session_token(value: str) -> str:
    """Validate the operator's local session token without ever persisting it."""
    candidate = value.strip()
    if not TOKEN_PATTERN.fullmatch(candidate):
        raise SafetyError(
            "Oturum tokeni en az 20 karakter olmalı ve yalnızca büyük harf/rakam içermelidir."
        )
    return candidate


def validate_profile_password(value: str) -> str:
    candidate = value.strip()
    if not PASSWORD_PATTERN.fullmatch(candidate):
        raise SafetyError(
            "Profil parolası en az 8 karakter, en az bir büyük harf ve bir rakam içermelidir."
        )
    return candidate


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def store_fingerprint(directory: Path, value: str, filename: str) -> Path:
    """Store only a SHA-256 fingerprint, never the original secret."""
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / filename
    path.write_text(f"sha256:{sha256_hex(value)}\n", encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass
    return path


def store_token_fingerprint(directory: Path, token: str) -> Path:
    return store_fingerprint(directory, token, "session-token.sha256")


def store_password_fingerprint(directory: Path, password: str) -> Path:
    return store_fingerprint(directory, password, "scaret.txt")


def write_encrypted_profile(directory: Path, profile: dict[str, object], password: str) -> Path:
    """Write a small authenticated encrypted profile inside lock.file.zip.

    The ZIP is a transport container; the profile payload is encrypted before it
    enters the container. This keeps the implementation dependency-free on Termux.
    """
    import json

    raw = json.dumps(profile, ensure_ascii=False, sort_keys=True).encode("utf-8")
    salt = secrets.token_bytes(16)
    nonce = secrets.token_bytes(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 210_000, 64)
    stream = bytearray()
    for counter in range((len(raw) // 32) + 1):
        stream.extend(hmac.new(key[:32], nonce + counter.to_bytes(8, "big"), hashlib.sha256).digest())
    ciphertext = bytes(left ^ right for left, right in zip(raw, stream))
    tag = hmac.new(key[32:], nonce + ciphertext, hashlib.sha256).digest()
    directory.mkdir(parents=True, exist_ok=True)
    archive_path = directory / "lock.file.zip"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("profile.enc", salt + nonce + tag + ciphertext)
        archive.writestr(
            "README.txt",
            "BlackHawk yerel profil kasası. profile.enc içeriği parola tabanlı "
            "şifreli ve doğrulamalıdır; ZIP başlıkları gizli veri içermez.\n",
        )
    try:
        archive_path.chmod(0o600)
    except OSError:
        pass
    return archive_path