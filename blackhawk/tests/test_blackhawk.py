from pathlib import Path

from blackhawk.intelligence import CorrelationEngine, classify_confidence
from blackhawk.models import Observation, Session
from blackhawk.reports import ReportWriter
from blackhawk.security import (
    SafetyError,
    safe_filename,
    validate_public_target,
    validate_profile_password,
    validate_session_token,
    write_encrypted_profile,
)


def test_public_target_validation():
    assert validate_public_target("https://example.com") == "https://example.com"
    assert validate_public_target("@public-user") == "@public-user"
    assert validate_public_target("#public-topic") == "#public-topic"
    for value in ("file:///etc/passwd", "https://a:b@example.com", "https://x.test/?token=secret"):
        try:
            validate_public_target(value)
        except SafetyError:
            pass
        else:
            raise AssertionError("unsafe target accepted")


def test_confidence_labels():
    assert classify_confidence(0.9, 2) == "doğrulanmış"
    assert classify_confidence(0.3, 1) == "tek kaynak"
    assert classify_confidence(0.0, 0) == "zayıf sinyal"


def test_correlation_upgrades_independent_sources():
    items = [
        Observation("target", "https://a.example", "A", confidence=0.7),
        Observation("target", "https://b.example", "B", confidence=0.7),
    ]
    result = CorrelationEngine().correlate(items)
    assert all(item.classification == "doğrulanmış" for item in result)


def test_report_writer_escapes_html(tmp_path: Path):
    session = Session()
    session.observations.append(
        Observation("<script>", "https://example.com/?q=x", "<unsafe>", summary="<script>alert(1)</script>")
    )
    paths = ReportWriter(tmp_path).write_all(session, "<script>")
    assert all(path.exists() for path in paths.values())
    assert "&lt;script&gt;" in paths[".html"].read_text(encoding="utf-8")
    assert safe_filename("@user/name") == "user-name"


def test_credentials_are_validated_and_profile_archive_is_encrypted(tmp_path: Path):
    assert validate_session_token("A" * 20) == "A" * 20
    assert validate_profile_password("SecureA1")
    for value in ("short", "lowercasepassword1", "bad-token-with-dash"):
        try:
            validate_session_token(value)
        except SafetyError:
            pass
        else:
            raise AssertionError("unsafe token accepted")
    archive = write_encrypted_profile(tmp_path, {"name": "Test"}, "SecureA1")
    assert archive.exists()
    assert b"Test" not in archive.read_bytes()


def test_pdf_report_is_created(tmp_path: Path):
    paths = ReportWriter(tmp_path).write_all(Session(), "session")
    assert paths[".pdf"].read_bytes().startswith(b"%PDF-1.4")