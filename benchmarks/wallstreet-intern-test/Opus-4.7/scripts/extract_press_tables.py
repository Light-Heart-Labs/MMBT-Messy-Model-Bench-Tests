"""Extract HTML tables from a press release / 8-K exhibit.

Walks each <table> element, emits a CSV file per table named
extracted/press_tables/<src>_table_<n>.csv. Cells are stripped of HTML
tags and whitespace-collapsed.
"""
from __future__ import annotations

import csv
import html as H
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent


def _clean(cell: str) -> str:
    cell = re.sub(r"<[^>]+>", " ", cell)
    cell = H.unescape(cell)
    cell = cell.replace("\xa0", " ")
    cell = re.sub(r"\s+", " ", cell).strip()
    return cell


def parse_tables(html: str) -> list[list[list[str]]]:
    out: list[list[list[str]]] = []
    for tab in re.finditer(r"<table\b[^>]*>(.*?)</table>", html, flags=re.S | re.I):
        body = tab.group(1)
        table_rows: list[list[str]] = []
        for row in re.finditer(r"<tr\b[^>]*>(.*?)</tr>", body, flags=re.S | re.I):
            cells = re.findall(r"<t[hd]\b[^>]*>(.*?)</t[hd]>", row.group(1), flags=re.S | re.I)
            cleaned = [_clean(c) for c in cells]
            if any(cleaned):
                table_rows.append(cleaned)
        if table_rows:
            out.append(table_rows)
    return out


def main() -> None:
    if len(sys.argv) < 2:
        # default: process all press releases
        files = sorted((REPO / "raw" / "filings").glob("PR_*.htm"))
    else:
        files = [pathlib.Path(p) for p in sys.argv[1:]]
    out_dir = REPO / "extracted" / "press_tables"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary: list[tuple[str, int]] = []
    for fp in files:
        if not fp.is_absolute():
            fp = REPO / fp
        html = fp.read_text(encoding="utf-8", errors="ignore")
        tables = parse_tables(html)
        stem = fp.stem
        for i, t in enumerate(tables, 1):
            out = out_dir / f"{stem}__table_{i:02d}.csv"
            with out.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerows(t)
        summary.append((stem, len(tables)))
    for s, n in summary:
        print(f"{s}: {n} tables")


if __name__ == "__main__":
    main()
