from __future__ import annotations

import csv
import re
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "raw" / "transcripts"
OUT_DIR = ROOT / "extracted" / "transcripts"


def normalize_line(line: str) -> str:
    line = re.sub(r"\s+", " ", line).strip()
    return line


def extract_pdf(pdf_path: Path) -> list[dict]:
    reader = PdfReader(str(pdf_path))
    rows: list[dict] = []
    line_no = 0
    for page_idx, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        for raw_line in text.splitlines():
            line = normalize_line(raw_line)
            if not line:
                continue
            line_no += 1
            rows.append(
                {
                    "source_pdf": str(pdf_path.relative_to(ROOT)).replace("\\", "/"),
                    "page": page_idx,
                    "line_no": line_no,
                    "text": line,
                }
            )
    return rows


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    all_rows: list[dict] = []
    for pdf_path in sorted(RAW_DIR.glob("*.pdf")):
        rows = extract_pdf(pdf_path)
        text_path = OUT_DIR / f"{pdf_path.stem}.txt"
        text_path.write_text("\n".join(row["text"] for row in rows) + "\n", encoding="utf-8")
        for row in rows:
            row["text_file"] = str(text_path.relative_to(ROOT)).replace("\\", "/")
        all_rows.extend(rows)
        print(f"Extracted {pdf_path.name}: {len(rows)} lines")

    index_path = ROOT / "extracted" / "transcript_line_index.csv"
    with index_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["source_pdf", "text_file", "page", "line_no", "text"],
        )
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"Wrote {index_path.relative_to(ROOT)} with {len(all_rows)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

