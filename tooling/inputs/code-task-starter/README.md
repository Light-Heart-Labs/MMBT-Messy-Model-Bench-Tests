# logalyzer

A small CLI tool for analyzing web server access logs. Parses Apache/NGINX-style
log files, lets you filter by various criteria, and produces aggregate reports.

## Features

- Parse Common Log Format (CLF) and Combined Log Format
- Filter by status code, IP, URL pattern, and date range
- Real-time tail mode for live log streams
- Aggregate output: counts by URL, status, hour-of-day
- Output as JSON, CSV, or plain text
- Custom expression filtering for advanced queries

## Install

```bash
pip install -e .
```

## Quick start

```bash
# Show all 5xx errors in the sample log
logalyzer --status 500 samples/access.log

# Top 10 URLs by hit count
logalyzer --aggregate url --top 10 samples/access.log

# Filter by IP and date range
logalyzer --ip 192.168.1.0/24 --since 2026-01-01 samples/access.log
```

## Run tests

```bash
pytest
```

## Run benchmark

```bash
python benchmarks/bench.py
```

## Status

This project is feature-complete and ready for production use.
