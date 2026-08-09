from pathlib import Path

from blackhawk.intelligence import CorrelationEngine, classify_confidence
from blackhawk.models import Observation, Session
from blackhawk.reports import ReportWriter
from blackhawk.security import SafetyError, safe_filename, validate_public_target


def test_public_target_validation():
    assert validate_public_target("https://example.com") == "https://example.com"
    assert validate_public_target("@public-user") == "@public-user"
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