"""Tests for aggregations."""
from datetime import datetime, timezone

from logalyzer.aggregate import by_hour, by_status, by_url, total_bytes
from logalyzer.parser import LogEntry


def make_entry(**kw):
    defaults = dict(
        ip="10.0.0.1",
        user="-",
        timestamp=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        method="GET",
        url="/",
        protocol="HTTP/1.1",
        status=200,
        bytes=100,
    )
    defaults.update(kw)
    return LogEntry(**defaults)


def test_by_status_counts_correctly():
    entries = [
        make_entry(status=200),
        make_entry(status=200),
        make_entry(status=404),
        make_entry(status=500),
    ]
    result = by_status(entries)
    assert result[200] == 2
    assert result[404] == 1
    assert result[500] == 1


def test_by_url_returns_sorted_descending():
    entries = [
        make_entry(url="/a"),
        make_entry(url="/b"),
        make_entry(url="/a"),
        make_entry(url="/a"),
    ]
    result = by_url(entries)
    assert result[0] == ("/a", 3)
    assert result[1] == ("/b", 1)


def test_by_url_top_n_truncates():
    entries = [make_entry(url=f"/u{i}") for i in range(20)]
    result = by_url(entries, top=5)
    assert len(result) == 5


def test_by_hour_uses_utc_not_local_time():
    """Entries timestamped 12:00 UTC must be bucketed into the 12 hour."""
    entries = [
        make_entry(timestamp=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)),
        make_entry(timestamp=datetime(2026, 1, 1, 12, 30, 0, tzinfo=timezone.utc)),
        make_entry(timestamp=datetime(2026, 1, 1, 14, 0, 0, tzinfo=timezone.utc)),
    ]
    result = by_hour(entries)
    assert result[12] == 2
    assert result[14] == 1


def test_total_bytes_sums():
    entries = [make_entry(bytes=100), make_entry(bytes=200), make_entry(bytes=50)]
    assert total_bytes(entries) == 350
