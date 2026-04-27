"""Extract transcript text from a Motley Fool earnings call HTML page.

The article body uses <p>...</p> tags. Speakers appear as <strong>Name:</strong>.
We extract every paragraph in order, prefixing speaker labels when present, and
write one paragraph per line so the output can be cited as file:line."""
from __future__ import annotations

import html as H
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent


def extract(html_path: pathlib.Path) -> list[str]:
    text = html_path.read_text(encoding="utf-8", errors="ignore")
    paras: list[str] = []
    for m in re.finditer(r"<p\b[^>]*>(.*?)</p>", text, flags=re.S | re.I):
        body = m.group(1)
        # extract a leading <strong>Speaker:</strong> if present
        speaker_match = re.match(r"\s*<strong[^>]*>(.*?)</strong>\s*", body, flags=re.S | re.I)
        speaker = ""
        if speaker_match:
            speaker = re.sub(r"<[^>]+>", "", speaker_match.group(1)).strip().rstrip(":")
            body = body[speaker_match.end():]
        clean = re.sub(r"<[^>]+>", "", body)
        clean = H.unescape(clean)
        clean = re.sub(r"\s+", " ", clean).strip()
        if not clean and not speaker:
            continue
        if speaker:
            line = f"[{speaker}] {clean}"
        else:
            line = clean
        # filter very short artifacts
        if len(line) < 5:
            continue
        paras.append(line)
    return paras


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: extract_fool_transcript.py <input_html> <output_txt>")
        sys.exit(2)
    inp = pathlib.Path(sys.argv[1])
    if not inp.is_absolute():
        inp = REPO / inp
    out = pathlib.Path(sys.argv[2])
    if not out.is_absolute():
        out = REPO / out
    paras = extract(inp)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(paras) + "\n", encoding="utf-8")
    print(f"OK {inp.relative_to(REPO).as_posix()} -> {out.relative_to(REPO).as_posix()} ({len(paras)} paragraphs)")


if __name__ == "__main__":
    main()
