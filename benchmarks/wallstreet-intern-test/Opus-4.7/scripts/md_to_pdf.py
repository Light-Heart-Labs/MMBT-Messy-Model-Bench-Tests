"""Render memo/COCO_memo.md to memo/COCO_memo.pdf using reportlab.

This is intentionally a small renderer. It handles:
  - Headings (h1, h2, h3)
  - Paragraphs
  - Bullet lists
  - Bold and italic via markdown-it inline tokens
  - Tables via markdown-it-py with the table plugin

It does NOT handle: images, code fences (none in the memo), HTML blocks,
or hyperlinks (we render them as the link text only — the markdown source
remains the canonical, clickable version of the memo).
"""
from __future__ import annotations

import pathlib
import re
import sys

from markdown_it import MarkdownIt
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

REPO = pathlib.Path(__file__).resolve().parent.parent


def styles():
    base = getSampleStyleSheet()
    out = {}
    out["title"] = ParagraphStyle("title", parent=base["Title"], fontSize=18, textColor=colors.HexColor("#1F3864"), spaceAfter=4, leading=22)
    out["subtitle"] = ParagraphStyle("subtitle", parent=base["Italic"], fontSize=11, textColor=colors.HexColor("#404040"), spaceAfter=12)
    out["meta"] = ParagraphStyle("meta", parent=base["BodyText"], fontSize=9, textColor=colors.HexColor("#666666"), spaceAfter=18)
    out["h1"] = ParagraphStyle("h1", parent=base["Heading1"], fontSize=14, textColor=colors.HexColor("#1F3864"), spaceBefore=12, spaceAfter=6)
    out["h2"] = ParagraphStyle("h2", parent=base["Heading2"], fontSize=12, textColor=colors.HexColor("#2F5496"), spaceBefore=10, spaceAfter=4)
    out["h3"] = ParagraphStyle("h3", parent=base["Heading3"], fontSize=10.5, textColor=colors.HexColor("#404040"), spaceBefore=6, spaceAfter=2)
    out["body"] = ParagraphStyle("body", parent=base["BodyText"], fontSize=9.5, leading=12.5, spaceAfter=6, alignment=4)  # justified
    out["bullet"] = ParagraphStyle("bullet", parent=out["body"], leftIndent=14, bulletIndent=4, spaceAfter=2)
    return out


def render_inline(tokens, parent_idx=None) -> str:
    """Convert a markdown-it inline token tree to ReportLab paragraph markup."""
    out = []
    for t in tokens:
        if t.type == "text":
            # escape HTML chars for reportlab
            s = t.content
            s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            out.append(s)
        elif t.type == "strong_open":
            out.append("<b>")
        elif t.type == "strong_close":
            out.append("</b>")
        elif t.type == "em_open":
            out.append("<i>")
        elif t.type == "em_close":
            out.append("</i>")
        elif t.type == "code_inline":
            out.append(f"<font face='Courier'>{t.content}</font>")
        elif t.type == "link_open":
            # render as plain text-with-underline; PDF readers can't follow relative
            out.append("<u>")
        elif t.type == "link_close":
            out.append("</u>")
        elif t.type == "softbreak" or t.type == "hardbreak":
            out.append(" ")
        elif t.type == "inline":
            out.append(render_inline(t.children or []))
        else:
            # unknown -- render content if any
            if t.content:
                out.append(t.content)
    return "".join(out)


def parse_yaml_front_matter(text: str) -> tuple[dict, str]:
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end > 0:
            head = text[4:end]
            body = text[end + 5:]
            meta = {}
            for line in head.splitlines():
                if ":" in line:
                    k, _, v = line.partition(":")
                    meta[k.strip()] = v.strip().strip('"')
            return meta, body
    return {}, text


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: md_to_pdf.py <input.md> <output.pdf>")
        sys.exit(2)
    inp = pathlib.Path(sys.argv[1])
    if not inp.is_absolute():
        inp = REPO / inp
    out = pathlib.Path(sys.argv[2])
    if not out.is_absolute():
        out = REPO / out

    text = inp.read_text(encoding="utf-8")
    meta, body = parse_yaml_front_matter(text)

    md = MarkdownIt("commonmark", {"breaks": False, "html": False}).enable("table")
    tokens = md.parse(body)

    s = styles()
    flow = []

    # Title block from frontmatter
    if meta.get("title"):
        flow.append(Paragraph(meta["title"], s["title"]))
    if meta.get("subtitle"):
        flow.append(Paragraph(meta["subtitle"], s["subtitle"]))
    if meta.get("date"):
        flow.append(Paragraph(f"{meta.get('author', '')} &nbsp;·&nbsp; {meta['date']}", s["meta"]))

    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t.type == "heading_open":
            level = int(t.tag[1:])
            inner = tokens[i + 1]
            content = render_inline(inner.children or [])
            style = s.get(f"h{level}", s["h3"])
            flow.append(Paragraph(content, style))
            i += 3  # heading_open, inline, heading_close
            continue
        if t.type == "paragraph_open":
            inner = tokens[i + 1]
            content = render_inline(inner.children or [])
            flow.append(Paragraph(content, s["body"]))
            i += 3
            continue
        if t.type == "bullet_list_open":
            j = i + 1
            while tokens[j].type != "bullet_list_close":
                if tokens[j].type == "list_item_open":
                    # find inline within
                    k = j + 1
                    bullet_text_parts = []
                    while tokens[k].type != "list_item_close":
                        if tokens[k].type == "paragraph_open":
                            inner = tokens[k + 1]
                            bullet_text_parts.append(render_inline(inner.children or []))
                            k += 3
                        else:
                            k += 1
                    flow.append(Paragraph("• " + " ".join(bullet_text_parts), s["bullet"]))
                    j = k
                j += 1
            i = j + 1
            continue
        if t.type == "ordered_list_open":
            j = i + 1
            n = 1
            while tokens[j].type != "ordered_list_close":
                if tokens[j].type == "list_item_open":
                    k = j + 1
                    parts = []
                    while tokens[k].type != "list_item_close":
                        if tokens[k].type == "paragraph_open":
                            inner = tokens[k + 1]
                            parts.append(render_inline(inner.children or []))
                            k += 3
                        else:
                            k += 1
                    flow.append(Paragraph(f"{n}. " + " ".join(parts), s["bullet"]))
                    n += 1
                    j = k
                j += 1
            i = j + 1
            continue
        if t.type == "table_open":
            # build table data; wrap each cell in Paragraph so inline bold renders
            cell_style = ParagraphStyle("cell", parent=s["body"], fontSize=8.5, leading=11, alignment=0, spaceAfter=0, spaceBefore=0)
            head_style = ParagraphStyle("head", parent=cell_style, textColor=colors.white, fontName="Helvetica-Bold")
            rows = []
            j = i + 1
            current = None
            in_header = False
            while tokens[j].type != "table_close":
                tt = tokens[j].type
                if tt == "thead_open":
                    in_header = True
                elif tt == "thead_close":
                    in_header = False
                elif tt == "tr_open":
                    current = []
                elif tt in ("th_open", "td_open"):
                    inner = tokens[j + 1]
                    text_ = render_inline(inner.children or [])
                    style_ = head_style if (tt == "th_open" or in_header) else cell_style
                    current.append(Paragraph(text_, style_))
                    j += 2
                elif tt == "tr_close":
                    if current is not None:
                        rows.append(current)
                    current = None
                j += 1
            if rows:
                # Table styling
                table = Table(rows, repeatRows=1)
                ts = TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2F5496")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#BFBFBF")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F2F2")]),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                ])
                table.setStyle(ts)
                flow.append(Spacer(1, 4))
                flow.append(table)
                flow.append(Spacer(1, 6))
            i = j + 1
            continue
        if t.type == "hr":
            flow.append(Spacer(1, 4))
            i += 1
            continue
        if t.type == "fence":
            flow.append(Paragraph(f"<font face='Courier' size='8'>{t.content}</font>", s["body"]))
            i += 1
            continue
        i += 1

    out.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(out),
        pagesize=LETTER,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        title=meta.get("title", "Investment Memo"),
        author=meta.get("author", ""),
    )
    doc.build(flow)
    print(f"OK wrote {out.relative_to(REPO).as_posix()}")


if __name__ == "__main__":
    main()
