from __future__ import annotations

import re
import time
from html import unescape
from urllib.request import Request, urlopen

from .models import Observation
from .security import validate_public_target


class PublicSourceConnector:
    """Fetch one small, attributable snapshot from a public web URL."""

    def __init__(self, timeout: float = 8.0) -> None:
        self.timeout = timeout
        self._last_request = 0.0

    def observe(self, target: str) -> Observation:
        target = validate_public_target(target)
        delay = 1.0 - (time.monotonic() - self._last_request)
        if delay > 0:
            time.sleep(delay)
        request = Request(
            target,
            headers={"User-Agent": "BlackHawk/1.0 (+ethical-public-research)", "Accept": "text/html"},
        )
        self._last_request = time.monotonic()
        with urlopen(request, timeout=self.timeout) as response:
            raw = response.read(512_000)
            charset = response.headers.get_content_charset() or "utf-8"
            body = raw.decode(charset, errors="replace")
            title_match = re.search(r"<title[^>]*>(.*?)</title>", body, flags=re.I | re.S)
            title = re.sub(r"\s+", " ", unescape(title_match.group(1))).strip() if title_match else target
            text = re.sub(r"<[^>]+>", " ", body)
            text = re.sub(r"\s+", " ", unescape(text)).strip()
            return Observation(
                target=target,
                source_url=target,
                source_title=title[:200],
                summary=text[:500],
                confidence=0.35,
                metadata={"status": response.status, "content_type": response.headers.get_content_type()},
            )