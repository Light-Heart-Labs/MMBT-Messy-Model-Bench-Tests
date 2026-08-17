#!/usr/bin/env python3
r"""Unit tests for wordcount_v2 (D1 word-counter contract).

Runnable as `python3 -m pytest` or plain `python3 test_wordcount_v2.py`.
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

V2DIR = Path(__file__).resolve().parents[1]
if str(V2DIR) not in sys.path:
    sys.path.insert(0, str(V2DIR))

import wordcount_v2  # noqa: E402


def _tmpfile(tmpdir: Path, text: str) -> Path:
    p = tmpdir / "sample.md"
    p.write_text(text, encoding="utf-8")
    return p


def test_wc_counts_whitespace_tokens():
    with tempfile.TemporaryDirectory() as td:
        p = _tmpfile(Path(td), "one two three\n")
        assert wordcount_v2.wc_words(p) == 3


def test_wc_diverges_from_v1_regex_on_markdown():
    # The D1 signature: markdown punctuation counts as words under wc -w but
    # not under the v1 regex; hyphenated compounds count once under wc -w but
    # split under the regex.
    text = "## Header\n---\n| cell | cell2 |\nFollow-On plan\n"
    with tempfile.TemporaryDirectory() as td:
        p = _tmpfile(Path(td), text)
        wc = wordcount_v2.wc_words(p)
        regex = len(re.findall(r"\b\w+\b", text))
        # wc -w: ##, Header, ---, |, cell, |, cell2, |, Follow-On, plan
        assert wc == 10
        # v1 regex: Header, cell, cell2, Follow, On, plan
        assert regex == 6
        assert wc != regex


def test_effective_ceilings():
    # floor(ceiling * 1.03) at every ceiling used by the study
    assert wordcount_v2.effective_ceiling(700) == 721
    assert wordcount_v2.effective_ceiling(250) == 257
    assert wordcount_v2.effective_ceiling(350) == 360
    assert wordcount_v2.effective_ceiling(400) == 412
    assert wordcount_v2.effective_ceiling(500) == 515


def test_band_boundary_at_700():
    with tempfile.TemporaryDirectory() as td:
        at_gate = _tmpfile(Path(td), " ".join(["w"] * 721) + "\n")
        gate = wordcount_v2.length_gate(at_gate, 700)
        assert gate["word_count"] == 721
        assert gate["within_word_limit"] is True

        over = Path(td) / "over.md"
        over.write_text(" ".join(["w"] * 722) + "\n", encoding="utf-8")
        gate2 = wordcount_v2.length_gate(over, 700)
        assert gate2["word_count"] == 722
        assert gate2["within_word_limit"] is False


def test_gate_records_contract():
    with tempfile.TemporaryDirectory() as td:
        p = _tmpfile(Path(td), "hello world\n")
        gate = wordcount_v2.length_gate(p, 700)
        assert gate["counter"] == "LC_ALL=C.UTF-8 wc -w"
        assert gate["ceiling"] == 700
        assert gate["tolerance_pct"] == 3.0
        assert gate["effective_max"] == 721
    assert wordcount_v2.WC_LOCALE == "C.UTF-8"


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as e:
                failures += 1
                print(f"FAIL {name}: {e}")
    sys.exit(1 if failures else 0)
