"""Extract the article body from a Motley Fool transcript HTML and emit a clean
line-numbered .txt file suitable for citation by file:line."""
from __future__ import annotations

import html
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent


def clean(html_path: pathlib.Path) -> str:
    text = html_path.read_text(encoding="utf-8", errors="ignore")
    # try to grab the article element
    m = re.search(r'<article[^>]*>(.*?)</article>', text, flags=re.S | re.I)
    body = m.group(1) if m else text
    # paragraphs
    paras = re.findall(r'<(?:p|h[1-6]|li)[^>]*>(.*?)</(?:p|h[1-6]|li)>', body, flags=re.S | re.I)
    out_lines: list[str] = []
    for p in paras:
        # strip nested tags
        s = re.sub(r'<[^>]+>', '', p)
        s = html.unescape(s).strip()
        if not s:
            continue
        # collapse whitespace
        s = re.sub(r'\s+', ' ', s)
        out_lines.append(s)
    return "\n".join(out_lines)


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: clean_transcript.py <input_html> <output_txt>")
        sys.exit(2)
    inp = pathlib.Path(sys.argv[1])
    if not inp.is_absolute():
        inp = REPO / inp
    out = pathlib.Path(sys.argv[2])
    if not out.is_absolute():
        out = REPO / out
    text = clean(inp)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text + "\n", encoding="utf-8")
    n = text.count("\n") + 1
    print(f"OK {inp.relative_to(REPO).as_posix()} -> {out.relative_to(REPO).as_posix()} ({n} lines)")


if __name__ == "__main__":
    main()
