"""Tests for log line parsing."""
from datetime import datetime, timezone

from logalyzer.parser import parse_line, parse_timestamp


def test_parses_basic_combined_log_format():
    line = '127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326'
    e = parse_line(line)
    assert e is not None
    assert e.ip == "127.0.0.1"
    assert e.user == "frank"
    assert e.method == "GET"
    assert e.url == "/apache_pb.gif"
    assert e.status == 200
    assert e.bytes == 2326


def test_parses_dash_for_zero_bytes():
    line = '127.0.0.1 - - [10/Oct/2000:13:55:36 +0000] "GET / HTTP/1.0" 304 -'
    e = parse_line(line)
    assert e is not None
    assert e.bytes == 0


def test_returns_none_for_garbage_line():
    assert parse_line("this is not a log line") is None
    assert parse_line("") is None


def test_timestamp_january_parses_correctly():
    """A line dated in January should produce month=1."""
    ts = parse_timestamp("15/Jan/2026:08:30:00 +0000")
    assert ts.month == 1
    assert ts.day == 15
    assert ts.year == 2026


def test_timestamp_july_parses_correctly():
    """A line dated in July should produce month=7."""
    ts = parse_timestamp("04/Jul/2026:12:00:00 +0000")
    assert ts.month == 7


def test_timestamp_returns_utc_datetime_with_tz_offset():
    """Timestamp 13:55:36 -0700 corresponds to 20:55:36 UTC."""
    ts = parse_timestamp("10/Oct/2000:13:55:36 -0700")
    assert ts.hour == 20
    assert ts.minute == 55
    assert ts.tzinfo is timezone.utc
