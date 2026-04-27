# PR #959 — Review notes

Line-by-line review notes against `prs/pr-959/raw/diff.patch`. Severity:

- ★★★ — must address before merge
- ★★ — would address before merge
- ★ — observation, not blocking

## Findings

_TBD — auditor reads the diff and notes findings here._

## Convention adherence (per `research/upstream-context.md`)

- [ ] No new `eval` of script output
- [ ] No new `2>/dev/null`, `\|\| true`, broad `except: pass`
- [ ] No new retry/fallback chains
- [ ] If touches port bindings: defaults to loopback or `${BIND_ADDRESS:-127.0.0.1}`
- [ ] If adds new file in `installers/lib/`: pure (no I/O)
- [ ] If adds new env var: schema and example updated together
- [ ] If touches manifest: schema-valid (no breaking the resolver)

_TBD — auditor checks each item._
