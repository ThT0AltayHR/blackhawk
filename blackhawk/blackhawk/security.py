from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

ALLOWED_SCHEMES = {"http", "https"}
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
    if candidate.startswith("@"):
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
    if extension not in {".html", ".json", ".txt"}:
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