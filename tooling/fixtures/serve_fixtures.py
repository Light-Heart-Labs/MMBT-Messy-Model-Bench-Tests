#!/usr/bin/env python3
"""Deterministic offline fixture server for frozen MMBT task families.

Serves the snapshot corpus under a fixture root (default:
tooling/fixtures/p3_market/) so benchmark agents can research against frozen
pages instead of the live web. Every response is byte-identical across
requests: bodies are the exact frozen snapshot bytes, and all
response headers are fixed (the Date header is frozen).

URL scheme: a snapshot of  https://<host>/<path>  is served at
    http://<bind-host>:<port>/<host>/<path>
"/" returns a deterministic HTML catalog of every snapshot (original URL,
mirror path, capture time, sha256, bytes). "/index.json" returns the raw
corpus index.

Intended use (campaign runner): run this server in a container pinned at
172.29.0.2 on the --internal docker network `mmbt-p3-offline`, with the
sandbox attached to the same network (see tooling/fixtures/README.md). Agents
then reach the mirror at http://172.29.0.2:8377 and nothing else — Docker
>= 28 blocks container-to-host traffic on --internal networks, so the server
must live on the network itself, not on the host.

python3 stdlib only.
"""
from __future__ import annotations

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

FROZEN_DATE = "Sat, 16 Aug 2026 00:00:00 GMT"
SERVER_NAME = "MMBTFixtures/1.0"

NOT_FOUND_BODY = (
    b"404 fixture-not-found\n"
    b"This is the MMBT frozen fixture mirror. Only snapshotted pages exist.\n"
    b"GET / for the catalog of available snapshots.\n"
)


def serve_paths_for(url: str):
    """Mirror paths for an original URL: /<host><path>, with and without a
    trailing slash so curl of either variant hits the same frozen bytes."""
    sp = urlsplit(url)
    path = sp.path if sp.path else "/"
    base = "/" + sp.netloc + path
    keys = {base}
    if base.endswith("/") and len(base) > 1:
        keys.add(base.rstrip("/"))
    else:
        keys.add(base + "/")
    return keys


def build_state(root: Path):
    index_path = root / "index.json"
    index_bytes = index_path.read_bytes()
    index = json.loads(index_bytes)
    routes = {}
    rows = []
    for fx in sorted(index["fixtures"], key=lambda r: r["url"]):
        body = (root / fx["path"]).read_bytes()
        if len(body) != fx["bytes"]:
            print(f"WARNING: {fx['path']} size {len(body)} != index bytes "
                  f"{fx['bytes']}", file=sys.stderr)
        ctype = fx.get("content_type") or "text/html"
        primary = sorted(serve_paths_for(fx["url"]), key=len, reverse=True)[0]
        for key in serve_paths_for(fx["url"]):
            if key in routes and routes[key][2]["url"] != fx["url"]:
                print(f"WARNING: route collision on {key}: keeping "
                      f"{routes[key][2]['url']}, skipping {fx['url']}",
                      file=sys.stderr)
                continue
            routes[key] = (body, ctype, fx)
        rows.append(
            "<tr><td><code>{u}</code></td><td><code>{p}</code></td>"
            "<td>{t}</td><td><code>{s}</code></td><td>{b}</td></tr>".format(
                u=fx["url"], p=primary, t=fx["fetch_time_utc"],
                s=fx["sha256"], b=fx["bytes"]))
    catalog = (
        "<!doctype html><html><head><meta charset=\"utf-8\">"
        "<title>MMBT frozen fixture mirror: p3_market</title></head><body>"
        "<h1>MMBT frozen fixture mirror</h1>"
        "<p>Task family: <b>{fam}</b>. Corpus created {created} (UTC) on "
        "{host}. {n} snapshots. This mirror is the ONLY network resource "
        "available; each snapshot is byte-frozen. Cite the ORIGINAL URL "
        "(left column) for every fact, and record the capture time and "
        "sha256 in your sources file. Machine-readable catalog: "
        "<a href=\"/index.json\">/index.json</a>.</p>"
        "<table border=\"1\" cellpadding=\"4\"><tr><th>original url</th>"
        "<th>mirror path</th><th>captured (UTC)</th><th>sha256</th>"
        "<th>bytes</th></tr>{rows}</table></body></html>\n").format(
            fam=index.get("task_family", "?"),
            created=index.get("created_utc", "?"),
            host=index.get("fetch_host", "?"),
            n=len(index["fixtures"]),
            rows="".join(rows)).encode("utf-8")
    return routes, catalog, index_bytes


def make_handler(routes, catalog, index_bytes):
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def version_string(self):
            return SERVER_NAME

        def date_time_string(self, timestamp=None):
            return FROZEN_DATE  # frozen: responses must be byte-stable

        def _reply(self, status, body, ctype, extra=None):
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            for k, v in (extra or []):
                self.send_header(k, v)
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        def do_GET(self):
            path = unquote(self.path.split("?", 1)[0])
            if path in ("/", "/index.html"):
                self._reply(200, catalog, "text/html; charset=utf-8")
                return
            if path == "/index.json":
                self._reply(200, index_bytes, "application/json")
                return
            hit = routes.get(path)
            if hit is None:
                self._reply(404, NOT_FOUND_BODY, "text/plain; charset=utf-8")
                return
            body, ctype, fx = hit
            self._reply(200, body, ctype, extra=[
                ("X-Fixture-Original-URL", fx["url"]),
                ("X-Fixture-Fetched-At", fx["fetch_time_utc"]),
                ("X-Fixture-SHA256", fx["sha256"]),
            ])

        do_HEAD = do_GET

        def log_message(self, fmt, *args):
            print("%s - %s" % (self.address_string(), fmt % args),
                  file=sys.stderr)

    return Handler


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=None,
                    help="Fixture root containing index.json "
                         "(default: <script_dir>/p3_market)")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8377)
    args = ap.parse_args()
    root = Path(args.root) if args.root else (
        Path(__file__).resolve().parent / "p3_market")
    routes, catalog, index_bytes = build_state(root)
    handler = make_handler(routes, catalog, index_bytes)
    httpd = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"serving {root} on {args.host}:{args.port} "
          f"({len(routes)} routes)", file=sys.stderr)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
