# PR #1044 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(dashboard-api): accept ${VAR:-127.0.0.1} in compose port-binding scan

## Author's stated motivation

The PR body says (paraphrased):

> ## Summary

The compose security scanner `_scan_compose_content` rejects extensions whose ports do not bind to literal `127.0.0.1`. PR #964 made the loopback bind address configurable by changing core port bindings from `127.0.0.1:HOST:CONTAINER` to `${BIND_ADDRESS:-127.0.0.1}:HOST:CONTAINER`, but the scanner was not updated. As a result, any extension that adopts the sanctioned LAN-toggle pattern fails the install path with:

```
Extension rejected: port binding '${BIND_ADDRESS:-127.0.0.1}:${CONTINUE_PORT:-8890}:8080'
in continue must use 127.0.0.1
```

The dashboard install path goes through `_scan_compose_content`; the bare `docker compose up` from the installer does not, which is why core services started cleanly but `dashboard install` of community extensions failed silently.

## What this changes

- New `_host_part_is_loopback(host)` helper accepts exactly two host-part forms:
  1. literal `"127.0.0.1"`
  2. `"\${VAR:-127.0.0.1}"` — variable expansion with literal-127.0.0.1 default
- New `_split_port_host(port_str)` correctly extracts the host part from `\${VAR:-127.0.0.1}:HOST:CONTAINER` (naive `str.split(':')` is wrong because the `:-` default operator contains a colon; on `\${BIND_ADDRESS:-127.0.0.1}:8080:80` it yields four parts and the host check then compares against `\"\${BIND_ADDRESS\"`, which is why the strict equality always failed).
- Both list-form and dict-form (`host_ip:`) bindings use the helper.
- `re.fullmatch` (not `re.match`) so the `\$`-anchor cannot  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
