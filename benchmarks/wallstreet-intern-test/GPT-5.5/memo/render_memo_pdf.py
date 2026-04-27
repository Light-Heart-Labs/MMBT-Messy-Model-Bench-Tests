import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "memo/yeti_investment_memo.md"
OUTPUT = ROOT / "memo/yeti_investment_memo.pdf"


def inline(text):
    escaped = html.escape(text)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)
    escaped = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>',
        escaped,
    )
    escaped = escaped.replace("`", "")
    return escaped


def parse_table(lines):
    rows = []
    for line in lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(set(c.replace(":", "").strip()) <= {"-"} for c in cells):
            continue
        rows.append([Paragraph(inline(c), TABLE_HEADER if not rows else TABLE_CELL) for c in cells])
    return rows


styles = getSampleStyleSheet()
TITLE = ParagraphStyle(
    "MemoTitle",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=16,
    leading=19,
    alignment=TA_LEFT,
    spaceAfter=8,
)
H2 = ParagraphStyle(
    "MemoH2",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=10.5,
    leading=12.5,
    textColor=colors.HexColor("#111827"),
    spaceBefore=7,
    spaceAfter=3,
)
BODY = ParagraphStyle(
    "MemoBody",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=8.4,
    leading=10.4,
    spaceAfter=4.5,
)
TABLE_CELL = ParagraphStyle(
    "TableCell",
    parent=BODY,
    fontSize=8,
    leading=9.2,
    spaceAfter=0,
)
TABLE_HEADER = ParagraphStyle(
    "TableHeader",
    parent=TABLE_CELL,
    fontName="Helvetica-Bold",
    textColor=colors.white,
)


def build_story(markdown):
    story = []
    lines = markdown.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line:
            story.append(Spacer(1, 2))
            i += 1
            continue
        if line.startswith("# "):
            story.append(Paragraph(inline(line[2:]), TITLE))
            i += 1
            continue
        if line.startswith("## "):
            story.append(Paragraph(inline(line[3:]), H2))
            i += 1
            continue
        if line.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].startswith("|"):
                table_lines.append(lines[i])
                i += 1
            rows = parse_table(table_lines)
            table = Table(rows, hAlign="LEFT", colWidths=[1.25 * inch, 1.0 * inch, 1.05 * inch])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D1D5DB")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 4),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                        ("TOPPADDING", (0, 0), (-1, -1), 3),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ]
                )
            )
            story.append(table)
            story.append(Spacer(1, 5))
            continue
        story.append(Paragraph(inline(line), BODY))
        i += 1
    return story


def main():
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=LETTER,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.45 * inch,
        bottomMargin=0.45 * inch,
        title="YETI Holdings Investment Memo",
        author="Codex",
    )
    doc.build(build_story(SOURCE.read_text(encoding="utf-8")))

    try:
        from pypdf import PdfReader

        pages = len(PdfReader(str(OUTPUT)).pages)
        print(f"Wrote {OUTPUT.relative_to(ROOT)} ({pages} pages)")
        if pages > 8:
            raise SystemExit("Memo exceeds 8-page limit")
    except ImportError:
        print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
