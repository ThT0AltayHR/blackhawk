from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .connectors import PublicSourceConnector
from .intelligence import CorrelationEngine
from .logging_utils import make_log
from .models import Observation, Session, Target
from .security import SafetyError, validate_public_target


@dataclass(slots=True)
class MonitorResult:
    observations: list[Observation]
    errors: list[str]


class MonitoringEngine:
    def __init__(self, connector: PublicSourceConnector | None = None):
        self.connector = connector or PublicSourceConnector()
        self.correlator = CorrelationEngine()

    def add_target(self, session: Session, value: str, label: str | None = None) -> Target:
        clean = validate_public_target(value)
        if any(item.value == clean for item in session.targets):
            raise SafetyError("Bu hedef oturumda zaten var.")
        target = Target(value=clean, label=label)
        session.targets.append(target)
        session.logs.append(make_log("AI-SUCCESS", "TARGET", "Hedef eklendi", clean, "bekleniyor"))
        return target

    def run_once(
        self,
        session: Session,
        on_log: Callable[[dict], None] | None = None,
    ) -> MonitorResult:
        observations: list[Observation] = []
        errors: list[str] = []
        session.status = "çalışıyor"
        for target in session.targets:
            session.logs.append(make_log("AI-TRACE", "MONITOR", "Kaynak taraması başlatıldı", target.value, "-"))
            if on_log:
                on_log(session.logs[-1])
            try:
                item = self.connector.observe(target.value)
                observations.append(item)
                session.logs.append(
                    make_log("AI-VERIFY", "VERIFY", "Kaynak gözlemi kaydedildi", target.value, item.classification)
                )
            except Exception as exc:
                message = str(exc)
                errors.append(message)
                session.logs.append(make_log("AI-WARNING", "SOURCE", message[:180], target.value, "zayıf sinyal"))
            if on_log:
                on_log(session.logs[-1])
        session.observations.extend(self.correlator.correlate(observations))
        session.status = "hazır" if not errors else "kısmi sonuç"
        return MonitorResult(observations=observations, errors=errors)
