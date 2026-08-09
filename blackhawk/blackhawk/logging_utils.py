from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SEVERITIES = {
    "AI-INFO": "cyan",
    "AI-WARNING": "yellow",
    "AI-CRITICAL": "red",
    "AI-SUCCESS": "green",
    "AI-GHOST": "magenta",
    "AI-WOLF": "bright_red",
    "AI-TRACE": "blue",
    "AI-VERIFY": "bright_green",
    "AI-SHIELD": "bright_cyan",
}


def make_log(level: str, module: str, message: str, target: str = "-", confidence: str = "-") -> dict[str, Any]:
    if level not in SEVERITIES:
        level = "AI-INFO"
    return {
        "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S"),
        "module": module,
        "level": level,
        "message": message,
        "target": target,
        "confidence": confidence,
    }


def format_log(entry: dict[str, Any]) -> str:
    return (
        f"[{entry['timestamp']}] {entry['level']:<12} "
        f"{entry['module']:<10} {entry['message']} "
        f"({entry['target']}; güven: {entry['confidence']})"
    )