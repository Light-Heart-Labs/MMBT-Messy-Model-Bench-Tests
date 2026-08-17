#!/usr/bin/env python3
r"""Shared word-counting contract for graders v2 (defect D1).

D1 (see grader-defects.md and PREREGISTRATION.md section 8): the v1 phase-3
graders counted words with the Python regex ``len(re.findall(r"\b\w+\b", text))``
while the graded transcripts show both models overwhelmingly checking their own
length with ``wc -w`` (152/152 Qwen3.6 and 93/95 Qwen3.8 length-gated cells
contain a literal ``wc -w`` call). The two counters disagree by up to ~21% on
real deliverables: markdown punctuation (``##``, ``---``, ``|``) counts as words
under ``wc -w`` but not the regex; hyphenated compounds and contractions
(``Follow-On``, ``hasn't``) count once under ``wc -w`` but split under the regex.

Per the preregistered protocol, v2 graders count words with the same command the
v2 task briefs now name explicitly:

    LC_ALL=C.UTF-8 wc -w <file>

(``C.UTF-8`` is the harness container locale, verified), and apply a +-3%
tolerance band at each ceiling: a deliverable passes the length gate iff

    wc_w_count <= floor(ceiling * 1.03)

Neither counter is ground truth; the point of the band is that a verdict must
not flip on tokenizer choice within a few percent of the ceiling.

stdlib-only.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

WC_LOCALE = "C.UTF-8"
TOLERANCE_PCT = 3.0


def wc_words(path: Path) -> int:
    """Count words in *path* exactly as ``LC_ALL=C.UTF-8 wc -w <path>`` does."""
    env = dict(os.environ)
    env["LC_ALL"] = WC_LOCALE
    proc = subprocess.run(
        ["wc", "-w", str(path)],
        capture_output=True,
        text=True,
        env=env,
        check=True,
    )
    return int(proc.stdout.strip().split()[0])


def effective_ceiling(limit: int) -> int:
    """The graded maximum: floor(limit * (1 + TOLERANCE_PCT/100))."""
    return int(limit * (1.0 + TOLERANCE_PCT / 100.0))


def length_gate(path: Path, limit: int) -> dict:
    """Evaluate the v2 length gate for *path* against *limit*.

    Returns a dict suitable for embedding verbatim in grade.json so the
    counter, the band, and the decision are all on the record.
    """
    count = wc_words(path)
    eff = effective_ceiling(limit)
    return {
        "counter": f"LC_ALL={WC_LOCALE} wc -w",
        "word_count": count,
        "ceiling": limit,
        "tolerance_pct": TOLERANCE_PCT,
        "effective_max": eff,
        "within_word_limit": count <= eff,
    }
