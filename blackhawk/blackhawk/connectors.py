from __future__ import annotations

import re
import time
from html import unescape
from urllib.request import Request, urlopen

from .models import Observation
from .security import SafetyError, validate_public_target


class PublicSourceConnector:
    """Fetches a small, attributable snapshot from a public URL."""

    def __init__(self, timeout: float = 8.0, user_agent: str = "BlackHawk/0.1 (+ethical-public-research)"):
        self.timeout = timeout
        self.user_agent = user_agent
        self._last_request = 0.0

    def observe(self, target: str) -> Observation:
        target = validate_public_target(target)
        if target.startswith("@"):
            raise SafetyError("Kullanıcı adı için doğrudan ağ taraması yapılmaz; yalnızca yetkili kamu URL'si girin.")
        delay = 1.0 - (time.monotonic() - self._last_request)
        if delay > 0:
            time.sleep(delay)
        request = Request(target, headers={"User-Agent": self.user_agent, "Accept": "text/html"})
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
                kind="kamu web kaynağı",
                summary=text[:500],
                confidence=0.35,
                classification="tek kaynak",
                verified=False,
                metadata={"status": response.status, "content_type": response.headers.get_content_type()},
            )