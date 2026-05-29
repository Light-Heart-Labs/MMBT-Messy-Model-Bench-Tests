"""Tests for filter predicates."""
from datetime import datetime, timezone

from logalyzer.filters import (
    date_range_filter,
    ip_allowlist_filter,
    status_filter,
    url_regex_filter,
)
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


def test_status_filter_matches_when_int_provided():
    pred = status_filter(404)
    assert pred(make_entry(status=404)) is True
    assert pred(make_entry(status=200)) is False


def test_status_filter_works_with_cli_string_input():
    """The CLI passes --status as a string. The filter must work either way."""
    pred = status_filter("404")
    assert pred(make_entry(status=404)) is True


def test_url_regex_finds_substring_match():
    """A pattern like 'admin' should match URLs containing /admin/, not just URLs starting with admin."""
    pred = url_regex_filter("admin")
    assert pred(make_entry(url="/admin/login")) is True
    assert pred(make_entry(url="/api/admin/users")) is True
    assert pred(make_entry(url="/index.html")) is False


def test_url_regex_anchored_works():
    """Anchored regexes like '^/admin' should also work."""
    pred = url_regex_filter(r"^/admin")
    assert pred(make_entry(url="/admin/login")) is True
    assert pred(make_entry(url="/api/admin")) is False


def test_ip_allowlist_with_list_works():
    pred = ip_allowlist_filter(["10.0.0.1", "10.0.0.2"])
    assert pred(make_entry(ip="10.0.0.1")) is True
    assert pred(make_entry(ip="10.0.0.3")) is False


def test_date_range_inclusive_endpoints():
    since = datetime(2026, 1, 1, tzinfo=timezone.utc)
    until = datetime(2026, 1, 2, tzinfo=timezone.utc)
    pred = date_range_filter(since, until)
    assert pred(make_entry(timestamp=since)) is True
    assert pred(make_entry(timestamp=until)) is True
    assert pred(make_entry(timestamp=datetime(2025, 12, 31, tzinfo=timezone.utc))) is False
