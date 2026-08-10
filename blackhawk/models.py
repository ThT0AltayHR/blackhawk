from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class Observation:
    target: str
    source_url: str
    source_title: str
    observed_at: datetime = field(default_factory=utc_now)
    kind: str = "kaynak"
    summary: str = ""
    confidence: float = 0.0
    classification: str = "tek kaynak"
    verified: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["observed_at"] = self.observed_at.isoformat()
        return result


@dataclass(slots=True)
class Target:
    value: str
    label: str | None = None
    group: str = "Varsayılan"
    tags: list[str] = field(default_factory=list)
    favorite: bool = False
    risk: str = "belirleniyor"

    @property
    def display_name(self) -> str:
        return self.label or self.value

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Session:
    started_at: datetime = field(default_factory=utc_now)
    duration_minutes: int = 60
    status: str = "hazır"
    targets: list[Target] = field(default_factory=list)
    observations: list[Observation] = field(default_factory=list)
    logs: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    operator_name: str = ""
    operator_age: int | None = None
    operator_gender: str = ""
    incident: str = ""
    incident_analysis: dict[str, Any] = field(default_factory=dict)

    @property
    def elapsed_minutes(self) -> int:
        return max(0, int((utc_now() - self.started_at).total_seconds() // 60))

    def to_dict(self) -> dict[str, Any]:
        return {
            "started_at": self.started_at.isoformat(),
            "duration_minutes": self.duration_minutes,
            "status": self.status,
            "targets": [target.to_dict() for target in self.targets],
            "observations": [item.to_dict() for item in self.observations],
            "logs": self.logs,
            "notes": self.notes,
            "operator_name": self.operator_name,
            "operator_age": self.operator_age,
            "operator_gender": self.operator_gender,
            "incident": self.incident,
            "incident_analysis": self.incident_analysis,
        }