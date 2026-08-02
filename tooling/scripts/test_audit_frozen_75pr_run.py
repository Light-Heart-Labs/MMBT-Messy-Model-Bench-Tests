from pathlib import Path

import audit_frozen_75pr_run as audit


def test_read_text_or_empty_reads_existing_file(tmp_path: Path) -> None:
    path = tmp_path / "review.md"
    path.write_text("review")
    assert audit.read_text_or_empty(path) == "review"


def test_read_text_or_empty_fails_closed_for_missing_file(tmp_path: Path) -> None:
    assert audit.read_text_or_empty(tmp_path / "missing.md") == ""
