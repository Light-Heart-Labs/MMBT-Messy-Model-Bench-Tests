#!/usr/bin/env python3
"""Validate OpenAI-compatible chat and native tool-call behavior for Gemma."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import urllib.error
import urllib.request
import uuid
from typing import Any


SAMPLING = {"temperature": 1.0, "top_p": 0.95, "top_k": 64}


def post(base_url: str, payload: dict[str, Any], timeout: float) -> tuple[int, bytes]:
    request = urllib.request.Request(
        base_url.rstrip("/") + "/v1/chat/completions",
        data=json.dumps(payload, separators=(",", ":")).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


def write_json(path: pathlib.Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def decode(status: int, body: bytes, label: str) -> dict[str, Any]:
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{label}: non-JSON HTTP {status}: {body[:1000]!r}") from exc
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--model", default="Gemma-4-31B-it-QAT-Q4_0")
    parser.add_argument("--label", required=True)
    parser.add_argument("--output-root", required=True, type=pathlib.Path)
    parser.add_argument("--timeout", type=float, default=900)
    parser.add_argument("--seed", type=int, default=424242)
    args = parser.parse_args()

    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = args.output_root / f"{args.label}-{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=False)
    marker = f"MMBT_CONTRACT_{uuid.uuid4().hex}"

    base = {
        "model": args.model,
        **SAMPLING,
        "seed": args.seed,
        "max_tokens": 1024,
        "stream": False,
    }
    chat_request = {
        **base,
        "messages": [
            {"role": "system", "content": "Follow the user's exact response-format request."},
            {"role": "user", "content": f"Reply with exactly {marker} and nothing else."},
        ],
    }
    chat_status, chat_body = post(args.endpoint, chat_request, args.timeout)
    (out_dir / "chat.response.json").write_bytes(chat_body)
    chat = decode(chat_status, chat_body, "chat")
    chat_content = chat.get("choices", [{}])[0].get("message", {}).get("content", "")
    chat_passed = chat_status == 200 and marker in (chat_content or "")

    tool_name = "return_benchmark_marker"
    tool_request = {
        **base,
        "messages": [
            {
                "role": "user",
                "content": f"Call {tool_name} once with marker set exactly to {marker}. Do not answer in prose.",
            }
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": "Return the exact benchmark marker supplied by the user.",
                    "parameters": {
                        "type": "object",
                        "properties": {"marker": {"type": "string"}},
                        "required": ["marker"],
                        "additionalProperties": False,
                    },
                },
            }
        ],
        "tool_choice": "required",
    }
    tool_status, tool_body = post(args.endpoint, tool_request, args.timeout)
    (out_dir / "tool-call.response.json").write_bytes(tool_body)
    tool_response = decode(tool_status, tool_body, "tool-call")
    assistant_message = tool_response.get("choices", [{}])[0].get("message", {})
    tool_calls = assistant_message.get("tool_calls") or []
    parsed_calls: list[dict[str, Any]] = []
    for call in tool_calls:
        function = call.get("function") or {}
        arguments = function.get("arguments") or "{}"
        try:
            parsed_arguments = json.loads(arguments) if isinstance(arguments, str) else arguments
        except json.JSONDecodeError:
            parsed_arguments = {"_unparseable": arguments}
        parsed_calls.append(
            {"id": call.get("id"), "name": function.get("name"), "arguments": parsed_arguments}
        )
    tool_passed = (
        tool_status == 200
        and len(parsed_calls) == 1
        and parsed_calls[0]["name"] == tool_name
        and parsed_calls[0]["arguments"].get("marker") == marker
    )

    followup_passed = False
    followup: dict[str, Any] | None = None
    followup_status: int | None = None
    if tool_passed:
        call_id = parsed_calls[0]["id"]
        followup_request = {
            **base,
            "messages": tool_request["messages"]
            + [
                assistant_message,
                {
                    "role": "tool",
                    "tool_call_id": call_id,
                    "content": json.dumps({"marker": marker}),
                },
                {
                    "role": "user",
                    "content": f"Now reply with exactly {marker} and nothing else.",
                },
            ],
            "tools": tool_request["tools"],
            "tool_choice": "auto",
        }
        followup_status, followup_body = post(args.endpoint, followup_request, args.timeout)
        (out_dir / "tool-followup.response.json").write_bytes(followup_body)
        followup = decode(followup_status, followup_body, "tool-followup")
        followup_content = followup.get("choices", [{}])[0].get("message", {}).get("content", "")
        followup_passed = followup_status == 200 and marker in (followup_content or "")

    summary = {
        "schema_version": 1,
        "timestamp": timestamp,
        "label": args.label,
        "endpoint": args.endpoint,
        "model": args.model,
        "sampling": SAMPLING,
        "seed": args.seed,
        "marker": marker,
        "chat": {
            "http_status": chat_status,
            "finish_reason": chat.get("choices", [{}])[0].get("finish_reason"),
            "error": chat.get("error"),
            "passed": chat_passed,
        },
        "tool_call": {
            "http_status": tool_status,
            "finish_reason": tool_response.get("choices", [{}])[0].get("finish_reason"),
            "error": tool_response.get("error"),
            "parsed_calls": parsed_calls,
            "passed": tool_passed,
        },
        "tool_followup": {
            "attempted": followup is not None,
            "http_status": followup_status,
            "finish_reason": None
            if followup is None
            else followup.get("choices", [{}])[0].get("finish_reason"),
            "error": None if followup is None else followup.get("error"),
            "passed": followup_passed,
        },
        "passed": chat_passed and tool_passed and followup_passed,
    }
    write_json(out_dir / "summary.json", summary)
    sums = []
    for path in sorted(out_dir.iterdir()):
        if path.is_file() and path.name != "SHA256SUMS":
            sums.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
    (out_dir / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
