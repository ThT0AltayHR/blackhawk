from __future__ import annotations

from collections import defaultdict
from urllib.parse import urlparse

from .models import Observation


def classify_confidence(score: float, independent_sources: int, contradictory: bool = False) -> str:
    if contradictory:
        return "çelişkili"
    if independent_sources >= 2 and score >= 0.75:
        return "doğrulanmış"
    if independent_sources >= 2 and score >= 0.5:
        return "muhtemel"
    if score > 0.0:
        return "tek kaynak"
    return "zayıf sinyal"


class CorrelationEngine:
    def correlate(self, observations: list[Observation]) -> list[Observation]:
        by_key: dict[str, list[Observation]] = defaultdict(list)
        for item in observations:
            # Group the same target and observation kind together so genuinely
            # independent hosts can raise confidence; source URLs are counted
            # separately below.
            key = f"{item.target.lower()}::{item.kind}"
            by_key[key].append(item)
        result: list[Observation] = []
        for group in by_key.values():
            sources = {item.source_url for item in group}
            score = min(0.98, max(item.confidence for item in group) + 0.12 * (len(sources) - 1))
            classification = classify_confidence(score, len(sources))
            for item in group:
                item.confidence = round(score, 2)
                item.classification = classification
                item.verified = classification == "doğrulanmış"
                result.append(item)
        return result

    def detect_conflicts(self, observations: list[Observation]) -> list[str]:
        conflicts: list[str] = []
        grouped: dict[str, set[str]] = defaultdict(set)
        for item in observations:
            grouped[item.target].add(item.source_title)
        for target, titles in grouped.items():
            if len(titles) > 3:
                conflicts.append(f"{target}: farklı kaynak başlıkları bağımsız doğrulama gerektiriyor.")
        return conflicts