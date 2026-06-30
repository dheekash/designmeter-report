"""Export interview history to Markdown, HTML, PDF, and JSON."""

from __future__ import annotations

import json
import textwrap
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .logger import get_logger

log = get_logger("exporter")


def _session_header(title: str = "Interview Helper — Export") -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"# {title}\n\nExported: {ts}\n\n---\n\n"


def to_markdown(records: List[dict], output_path: Path) -> Path:
    lines = [_session_header()]
    for i, r in enumerate(records, 1):
        lines.append(f"## Q{i}: {r.get('category', 'General')} — {r.get('question', '')[:80]}\n")
        lines.append(f"**Asked:** {r.get('created_at', '')}\n\n")
        lines.append(r.get("answer", ""))
        lines.append("\n\n---\n\n")
    output_path.write_text("".join(lines), encoding="utf-8")
    log.info("Exported Markdown → %s", output_path)
    return output_path


def to_html(records: List[dict], output_path: Path) -> Path:
    try:
        import markdown as md_lib
    except ImportError:
        md_lib = None

    items = []
    for i, r in enumerate(records, 1):
        answer_html = (
            md_lib.markdown(r.get("answer", ""), extensions=["fenced_code", "tables"])
            if md_lib
            else f"<pre>{r.get('answer', '')}</pre>"
        )
        items.append(
            f"""
            <div class="card">
              <h2>Q{i}: <span class="cat">{r.get('category','')}</span></h2>
              <p class="question">{r.get('question','')}</p>
              <div class="answer">{answer_html}</div>
              <small>{r.get('created_at','')}</small>
            </div>"""
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Interview Helper Export</title>
<style>
  body {{ font-family: 'Segoe UI', sans-serif; background:#0f0f0f; color:#e0e0e0; padding:2rem; }}
  h1 {{ color:#6ec6ff; }} .card {{ background:#1e1e2e; border-radius:12px; padding:1.5rem; margin:1.5rem 0; }}
  .cat {{ background:#3b4cca; color:#fff; padding:2px 8px; border-radius:6px; font-size:.85em; }}
  .question {{ color:#cdd6f4; font-size:1.05em; font-style:italic; }}
  .answer {{ margin-top:1rem; line-height:1.7; }}
  pre {{ background:#181825; padding:1rem; border-radius:8px; overflow-x:auto; }}
  code {{ font-family:Fira Code,monospace; font-size:.9em; }}
  table {{ border-collapse:collapse; width:100%; }}
  td,th {{ border:1px solid #313244; padding:.5rem; }}
</style>
</head>
<body>
<h1>Interview Helper — Export</h1>
<p>Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
{''.join(items)}
</body>
</html>"""

    output_path.write_text(html, encoding="utf-8")
    log.info("Exported HTML → %s", output_path)
    return output_path


def to_json(records: List[dict], output_path: Path) -> Path:
    output_path.write_text(
        json.dumps(records, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    log.info("Exported JSON → %s", output_path)
    return output_path


def to_pdf(records: List[dict], output_path: Path) -> Path:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
        from reportlab.lib import colors

        doc = SimpleDocTemplate(str(output_path), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle("Title2", parent=styles["Title"], fontSize=22, textColor=colors.HexColor("#6ec6ff"))
        q_style = ParagraphStyle("Q", parent=styles["Normal"], fontSize=10, textColor=colors.HexColor("#888888"))
        ans_style = ParagraphStyle("Ans", parent=styles["Normal"], fontSize=11, leading=16)

        story.append(Paragraph("Interview Helper — Export", title_style))
        story.append(Spacer(1, 0.5 * cm))

        for i, r in enumerate(records, 1):
            story.append(Paragraph(f"Q{i} [{r.get('category','')}]: {r.get('question','')}", styles["Heading2"]))
            story.append(Paragraph(str(r.get("created_at", "")), q_style))
            story.append(Spacer(1, 0.3 * cm))
            answer_text = r.get("answer", "").replace("\n", "<br/>")
            story.append(Paragraph(answer_text, ans_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
            story.append(Spacer(1, 0.5 * cm))

        doc.build(story)
        log.info("Exported PDF → %s", output_path)
    except ImportError:
        log.warning("reportlab not installed — saving as text fallback")
        to_markdown(records, output_path.with_suffix(".md"))
    return output_path
