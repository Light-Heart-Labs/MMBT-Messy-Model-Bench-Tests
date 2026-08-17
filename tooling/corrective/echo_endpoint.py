#!/usr/bin/env python3
"""Throwaway OpenAI-compatible echo endpoint for the seed-plumb dry run.

Serves /v1/models (so run_microbench.sh's reachability check and the harness
receipt capture succeed) and /v1/chat/completions, which RECORDS each request
body to the capture file and returns a plain finish_reason=stop completion
(no tool calls) so the harness ends after one model turn. stdlib only.
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(sys.argv[1])
ALIAS = sys.argv[2]
CAPTURE = sys.argv[3]


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, obj):
        body = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/v1/models":
            self._send({"data": [{"id": ALIAS, "meta": {"n_ctx": 262144}}]})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n)
        with open(CAPTURE, "ab") as f:
            f.write(body + b"\n")
        self._send({
            "choices": [{"message": {"role": "assistant",
                                     "content": "plumb-check complete"},
                         "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 5},
        })


HTTPServer(("127.0.0.1", PORT), H).serve_forever()
