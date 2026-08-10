from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def make_log(level: str, module: str, message: str, target: str = "-") -> dict[str, Any]:
    return {
        "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S"),
        "level": level,
        "module": module,
        "message": message,
        "target": target,
    }


def format_log(entry: dict[str, Any]) -> str:
    return (
        f"[{entry.get('timestamp', '--:--:--')}] "
        f"{entry.get('level', 'INFO'):<10} {entry.get('module', 'APP'):<8} "
        f"{entry.get('message', '')} ({entry.get('target', '-')})"
    )