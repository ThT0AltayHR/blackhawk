from __future__ import annotations

import json
import textwrap
from html import escape
from pathlib import Path

from .models import Session
from .security import safe_report_path


class ReportWriter:
    def __init__(self, directory: str | Path = "reports") -> None:
        self.directory = Path(directory)

    def write_all(self, session: Session, target: str) -> dict[str, Path]:
        data = session.to_dict()
        json_path = safe_report_path(self.directory, target, ".json")
        txt_path = safe_report_path(self.directory, target, ".txt")
        html_path = safe_report_path(self.directory, target, ".html")
        pdf_path = safe_report_path(self.directory, target, ".pdf")
        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        lines = [
            "BLACKHAWK — KAMU KAYNAKLI RAPOR",
            f"Durum: {session.status}",
            f"Hedef: {target}",
            "",
            *(
                f"- [{item.classification}] {item.source_title} | {item.source_url}\n  {item.summary}"
                for item in session.observations
            ),
        ]
        txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        cards = "".join(
            f"<article><h2>{escape(item.source_title)}</h2><p>{escape(item.summary)}</p>"
            f"<a href=\"{escape(item.source_url)}\">{escape(item.source_url)}</a></article>"
            for item in session.observations
        ) or "<p>Bu oturumda bulgu bulunamadı.</p>"
        html_path.write_text(
            f"<!doctype html><html lang='tr'><meta charset='utf-8'><title>BlackHawk</title>"
            f"<body><h1>BlackHawk raporu</h1>{cards}</body></html>",
            encoding="utf-8",
        )
        pdf_path.write_bytes(self._write_pdf_bytes(session, target))
        return {".json": json_path, ".txt": txt_path, ".html": html_path, ".pdf": pdf_path}

    @staticmethod
    def _write_pdf_bytes(session: Session, target: str) -> bytes:
        lines = [
            "BLACKHAWK - KAMU KAYNAKLI RAPOR",
            f"Hedef: {target}",
            f"Durum: {session.status}",
            "",
            "BULGULAR",
        ]
        for item in session.observations:
            lines.extend([f"[{item.classification}] {item.source_title}", item.source_url, item.summary, ""])
        wrapped = [part for line in lines for part in (textwrap.wrap(line, 92) or [""])]
        page_lines = wrapped[:46] or [""]
        content = ["BT", "/F1 9 Tf", "42 760 Td", "12 TL"]
        for line in page_lines:
            safe = line.encode("latin-1", errors="replace").decode("latin-1")
            safe = safe.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            content.append(f"({safe}) Tj T*")
        content.append("ET")
        content_data = "\n".join(content).encode("latin-1", errors="replace")
        objects = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [5 0 R] /Count 1 >>",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>",
            b"<< /Length %d >>\nstream\n%s\nendstream" % (len(content_data), content_data),
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 3 0 R >> >> /Contents 4 0 R >>",
        ]
        pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for index, obj in enumerate(objects, 1):
            offsets.append(len(pdf))
            pdf.extend(f"{index} 0 obj\n".encode())
            pdf.extend(obj)
            pdf.extend(b"\nendobj\n")
        xref = len(pdf)
        pdf.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
        for offset in offsets[1:]:
            pdf.extend(f"{offset:010d} 00000 n \n".encode())
        pdf.extend(
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref}\n%%EOF\n".encode()
        )
        return bytes(pdf)