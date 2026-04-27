# Tests run for PR #988

This PR adds no tests, and the project doesn't have an automated test for
the default-bind contract. The author reports verifying manually on macOS
Apple Silicon (`lsof -nP -iTCP:7710 -sTCP:LISTEN` showing 127.0.0.1).
The auditor's checks below are diff-inspection sanity, not a substitute
for an integration test.

## Manual check 1 — host-agent fallback on Linux

Read `bin/dream-host-agent.py:2241` to confirm
`_detect_docker_bridge_gateway()` returns `None` on failure (so the `or`
falls through to `"127.0.0.1"`). The function definition lives earlier in
the same file and clearly has `return None` as a fallthrough. Behavior
matches the PR's claim.

## Manual check 2 — Windows path covers both backends

Inspection of `installers/windows/install-windows.ps1` confirms `$bindAddr`
is used for **both** the Lemonade `serve` invocation (line 287) and the
`llama-server` invocation (line 370). A natural mistake would be updating
only one. The PR caught both.

## Manual check 3 — `.env.example` doc matches code

Diff lines 6-13 say `# Linux: auto-detects … Falls back to 127.0.0.1 if
detection fails.` The host-agent code at line 2241 implements exactly
that. Doc matches code.

## Tests not run (and why)

- **Real Linux installer + bridge-detection-fail scenario** — would
  require a Linux environment with Docker not yet running. Skipped: the
  one-line code change is unambiguous and easy to read.
- **macOS native install + llama-server start** — auditor doesn't have
  Apple Silicon hardware. Skipped; relied on diff inspection. Author's
  `lsof` evidence is in the PR body.
- **Windows install on Strix Halo** — auditor has Windows but not Strix
  Halo / Lemonade. Skipped.
- **BATS regression-shield** — none exists for this contract; PR #1018
  (draft) is the right place to add one. Recommended to the maintainer
  in `verdict.md`.
