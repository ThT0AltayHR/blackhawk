from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .connectors import PublicSourceConnector
from .logging_utils import make_log
from .models import Observation, Session, Target
from .security import SafetyError, validate_public_target


@dataclass(slots=True)
class MonitorResult:
    observations: list[Observation]
    errors: list[str]


class MonitoringEngine:
    def __init__(self, connector: PublicSourceConnector | None = None) -> None:
        self.connector = connector or PublicSourceConnector()

    def add_target(self, session: Session, value: str) -> Target:
        clean = validate_public_target(value)
        if any(item.value == clean for item in session.targets):
            raise SafetyError("Bu hedef oturumda zaten var.")
        target = Target(clean)
        session.targets.append(target)
        session.logs.append(make_log("SUCCESS", "TARGET", "Hedef eklendi", clean))
        return target

    def run_once(
        self, session: Session, on_log: Callable[[dict[str, object]], None] | None = None
    ) -> MonitorResult:
        found: list[Observation] = []
        errors: list[str] = []
        session.status = "çalışıyor"
        for target in session.targets:
            session.logs.append(make_log("TRACE", "MONITOR", "Kaynak okunuyor", target.value))
            if on_log:
                on_log(session.logs[-1])
            try:
                item = self.connector.observe(target.value)
                found.append(item)
                session.observations.append(item)
                session.logs.append(make_log("VERIFY", "SOURCE", "Gözlem kaydedildi", target.value))
            except Exception as exc:
                message = str(exc) or exc.__class__.__name__
                errors.append(message)
                session.logs.append(make_log("WARNING", "SOURCE", message[:180], target.value))
            if on_log:
                on_log(session.logs[-1])
        session.status = "hazır" if not errors else "kısmi sonuç"
        return MonitorResult(found, errors)