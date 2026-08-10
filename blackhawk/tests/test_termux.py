from __future__ import annotations

from pathlib import Path

from blackhawk.cli import is_termux
from blackhawk.models import Session
from blackhawk.reports import ReportWriter
from blackhawk.security import SafetyError, validate_public_target


def test_public_target_rules() -> None:
    assert validate_public_target("https://example.com") == "https://example.com"
    for value in ("file:///etc/passwd", "https://user:pass@example.com", "https://example.com/?token=secret"):
        try:
            validate_public_target(value)
        except SafetyError:
            pass
        else:
            raise AssertionError("unsafe target accepted")


def test_reports_are_dependency_free(tmp_path: Path) -> None:
    result = ReportWriter(tmp_path).write_all(Session(), "session")
    assert set(result) == {".json", ".txt", ".html", ".pdf"}
    assert all(path.exists() for path in result.values())


def test_termux_detection(monkeypatch) -> None:
    monkeypatch.setenv("TERMUX_VERSION", "0.118")
    assert is_termux()