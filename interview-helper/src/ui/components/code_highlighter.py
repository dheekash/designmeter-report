"""Convert Markdown + code blocks to styled HTML for QTextBrowser."""

from __future__ import annotations

import re
from typing import Optional

try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, guess_lexer, TextLexer
    from pygments.formatters import HtmlFormatter
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False

try:
    import markdown as _markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False


_DARK_CSS = """
body { font-family: 'Segoe UI', system-ui, sans-serif; font-size: 13px;
       color: #c9d1d9; background: #0d1117; line-height: 1.7; padding: 4px 8px; }
h1,h2 { color: #58a6ff; font-weight: 700; margin-top: 16px; margin-bottom: 6px; }
h2 { font-size: 14px; border-bottom: 1px solid #21262d; padding-bottom: 4px; }
h3 { color: #79c0ff; font-size: 13px; margin-top: 12px; }
p { margin: 6px 0; }
ul, ol { margin: 6px 0 6px 20px; }
li { margin: 3px 0; }
strong { color: #e6edf3; }
em { color: #a5d6ff; }
code { font-family: 'Fira Code', 'Cascadia Code', monospace; font-size: 12px;
       background: #161b22; color: #e6edf3; padding: 2px 5px; border-radius: 4px; }
pre { background: #161b22; border: 1px solid #21262d; border-radius: 8px;
      padding: 12px 16px; margin: 10px 0; overflow-x: auto; }
pre code { background: transparent; padding: 0; border-radius: 0; }
blockquote { border-left: 3px solid #58a6ff; padding-left: 12px;
             color: #8b949e; margin: 8px 0; font-style: italic; }
hr { border: none; border-top: 1px solid #21262d; margin: 12px 0; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; }
th { background: #161b22; color: #58a6ff; padding: 8px 12px; text-align: left;
     border: 1px solid #21262d; }
td { padding: 6px 12px; border: 1px solid #21262d; color: #c9d1d9; }
tr:nth-child(even) td { background: #161b22; }
.highlight { border-radius: 6px; overflow: hidden; margin: 10px 0; }
"""

_LIGHT_CSS = """
body { font-family: 'Segoe UI', system-ui, sans-serif; font-size: 13px;
       color: #24292f; background: #ffffff; line-height: 1.7; padding: 4px 8px; }
h1,h2 { color: #0969da; font-weight: 700; margin-top: 16px; margin-bottom: 6px; }
h2 { font-size: 14px; border-bottom: 1px solid #d0d7de; padding-bottom: 4px; }
h3 { color: #0550ae; font-size: 13px; margin-top: 12px; }
p { margin: 6px 0; }
ul, ol { margin: 6px 0 6px 20px; }
li { margin: 3px 0; }
strong { color: #24292f; }
code { font-family: 'Fira Code', 'Cascadia Code', monospace; font-size: 12px;
       background: #f6f8fa; color: #0550ae; padding: 2px 5px; border-radius: 4px; }
pre { background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 8px;
      padding: 12px 16px; margin: 10px 0; }
blockquote { border-left: 3px solid #0969da; padding-left: 12px;
             color: #57606a; margin: 8px 0; font-style: italic; }
hr { border: none; border-top: 1px solid #d0d7de; margin: 12px 0; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; }
th { background: #f6f8fa; color: #0969da; padding: 8px 12px; border: 1px solid #d0d7de; }
td { padding: 6px 12px; border: 1px solid #d0d7de; }
.highlight { border-radius: 6px; overflow: hidden; margin: 10px 0; }
"""


def _highlight_code_block(code: str, lang: str, dark: bool) -> str:
    if not PYGMENTS_AVAILABLE:
        return f"<pre><code>{_escape(code)}</code></pre>"
    style = "monokai" if dark else "friendly"
    formatter = HtmlFormatter(style=style, noclasses=True, nowrap=False)
    try:
        lexer = get_lexer_by_name(lang) if lang else guess_lexer(code)
    except Exception:
        from pygments.lexers import TextLexer as TL
        lexer = TL()
    return highlight(code, lexer, formatter)


def _escape(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


_CODE_FENCE_RE = re.compile(r"```(\w*)\n?(.*?)```", re.DOTALL)


def markdown_to_html(text: str, dark: bool = True) -> str:
    """Convert markdown text (with code fences) to styled HTML."""
    css = _DARK_CSS if dark else _LIGHT_CSS

    # First pass: pull out code blocks and highlight them
    code_blocks: list[str] = []

    def _replace_code(m: re.Match) -> str:
        lang = m.group(1).strip().lower() or ""
        code = m.group(2)
        html = _highlight_code_block(code, lang, dark)
        placeholder = f"CODEBLOCK_{len(code_blocks)}_END"
        code_blocks.append(html)
        return placeholder

    processed = _CODE_FENCE_RE.sub(_replace_code, text)

    # Convert remaining markdown
    if MARKDOWN_AVAILABLE:
        import markdown as md_lib
        body = md_lib.markdown(
            processed,
            extensions=["tables", "nl2br"],
        )
    else:
        # Minimal fallback: paragraphs + bold + italic
        body = processed.replace("\n\n", "</p><p>").replace("\n", "<br/>")
        body = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", body)
        body = re.sub(r"\*(.*?)\*", r"<em>\1</em>", body)
        body = f"<p>{body}</p>"

    # Restore code blocks
    for i, cb in enumerate(code_blocks):
        body = body.replace(f"CODEBLOCK_{i}_END", cb)
        # markdown lib may have escaped the placeholder
        body = body.replace(f"<p>CODEBLOCK_{i}_END</p>", cb)

    return f"<!DOCTYPE html><html><head><style>{css}</style></head><body>{body}</body></html>"
