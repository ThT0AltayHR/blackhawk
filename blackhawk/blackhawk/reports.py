from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from .models import Session
from .security import safe_report_path


class ReportWriter:
    def __init__(self, directory: str | Path = "reports"):
        self.directory = Path(directory)

    def write_all(self, session: Session, target: str) -> dict[str, Path]:
        return {
            ".json": self.write_json(session, target),
            ".txt": self.write_txt(session, target),
            ".html": self.write_html(session, target),
        }

    def write_json(self, session: Session, target: str) -> Path:
        path = safe_report_path(self.directory, target, ".json")
        path.write_text(json.dumps(session.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def write_txt(self, session: Session, target: str) -> Path:
        path = safe_report_path(self.directory, target, ".txt")
        lines = [
            "BLACKHAWK — KAMU KAYNAKLI İZLEME RAPORU",
            f"Üretim zamanı: {datetime.now(timezone.utc).isoformat()}",
            f"Durum: {session.status}",
            f"İzleme süresi: {session.elapsed_minutes} dakika / {session.duration_minutes} dakika",
            "",
            "HEDEFLER",
        ]
        lines.extend(f"- {item.display_name} | risk: {item.risk}" for item in session.targets)
        lines.append("\nBULGULAR")
        for item in session.observations:
            lines.append(
                f"- [{item.classification}] {item.source_title} | {item.source_url} | "
                f"güven %{int(item.confidence * 100)}\n  {item.summary}"
            )
        lines.append("\nGÜVENLİK NOTU\nBu rapor yalnızca kamuya açık ve yetkili kullanım için hazırlanmıştır.")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    def write_html(self, session: Session, target: str) -> Path:
        path = safe_report_path(self.directory, target, ".html")
        cards = "".join(
            f"""<article class="finding">
              <div class="finding-top"><span class="badge">{escape(item.classification)}</span>
              <span class="confidence">%{int(item.confidence * 100)} güven</span></div>
              <h3>{escape(item.source_title)}</h3>
              <p>{escape(item.summary)}</p>
              <a href="{escape(item.source_url)}" rel="noreferrer">{escape(item.source_url)}</a>
            </article>"""
            for item in session.observations
        ) or '<div class="empty">Bu oturumda doğrulanabilir kamu bulgusu bulunamadı.</div>'
        rows = "".join(
            f"<tr><td>{escape(log['timestamp'])}</td><td>{escape(log['level'])}</td>"
            f"<td>{escape(log['message'])}</td><td>{escape(log['target'])}</td></tr>"
            for log in session.logs
        )
        html = f"""<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>BlackHawk | {escape(target)}</title>
<style>
:root{{color-scheme:dark;--bg:#080a0c;--panel:#101419;--line:#30383f;--red:#d52b36;--green:#69d58a;--muted:#93a0aa}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at top right,#281016,#080a0c 45%);
font:15px Inter,system-ui,sans-serif;color:#edf1f3}}main{{max-width:1180px;margin:auto;padding:42px 24px}}
header{{border-bottom:1px solid var(--line);padding-bottom:28px;margin-bottom:28px}}.eyebrow{{color:var(--red);letter-spacing:.18em;font-size:11px}}
h1{{font-size:clamp(34px,6vw,76px);letter-spacing:.08em;margin:10px 0 4px}}h2{{font-size:18px;margin-top:34px}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}.stat,.finding,.logs{{background:linear-gradient(145deg,#151a20,#0d1014);border:1px solid var(--line);border-radius:8px;padding:18px}}
.stat strong{{display:block;color:var(--green);font-size:28px;margin-top:5px}}.stat span,.confidence{{color:var(--muted);font-size:12px}}
.findings{{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}}.finding-top{{display:flex;justify-content:space-between}}
.badge{{border:1px solid var(--red);color:#ff7880;border-radius:999px;padding:4px 8px;font-size:11px}}
.finding h3{{margin-bottom:6px}}.finding p{{color:#bcc5cb;line-height:1.55}}a{{color:#79b9ff;word-break:break-all}}
table{{width:100%;border-collapse:collapse;font-size:13px}}td{{border-bottom:1px solid #252c31;padding:10px;text-align:left}}td:nth-child(2){{color:var(--green)}}
.empty{{padding:40px;color:var(--muted);border:1px dashed var(--line)}}footer{{margin-top:34px;color:var(--muted);font-size:12px}}
@media(max-width:700px){{.grid,.findings{{grid-template-columns:1fr}}main{{padding:24px 16px}}}}
</style></head><body><main><header><div class="eyebrow">BLACKHAWK / ETHICAL INTELLIGENCE</div>
<h1>İZLEME RAPORU</h1><div>{escape(target)} · {escape(session.status)}</div></header>
<section class="grid"><div class="stat"><span>Hedef</span><strong>{len(session.targets)}</strong></div>
<div class="stat"><span>Kaynaklı gözlem</span><strong>{len(session.observations)}</strong></div>
<div class="stat"><span>Çalışma süresi</span><strong>{session.elapsed_minutes} dk</strong></div></section>
<h2>Bulgular ve kanıt özeti</h2><section class="findings">{cards}</section>
<h2>Audit log</h2><section class="logs"><table><thead><tr><td>Zaman</td><td>Seviye</td><td>Açıklama</td><td>Hedef</td></tr></thead>
<tbody>{rows}</tbody></table></section>
<footer>Bu rapor yalnızca kamuya açık ve yetkili kullanım içindir. Kaynaksız iddia üretilmemiştir.</footer>
</main></body></html>"""
        path.write_text(html, encoding="utf-8")
        return path