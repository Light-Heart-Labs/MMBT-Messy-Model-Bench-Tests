# PR #1027 Summary

## Claim In Plain English

fix(extensions): bind community extension ports via ${BIND_ADDRESS}

## Audit Restatement

The bind sweep itself is mechanically good (`test-bind-address-sweep.sh` passes and static scan finds no literal community `127.0.0.1` port entries), but on current main the dashboard scanner rejects `${BIND_ADDRESS:-127.0.0.1}`. Direct `_scan_compose_content` proof rejected Continue, Jupyter, and Milvus with 400s. Merge after #1044, or include the scanner update in this PR.

## Metadata

- Author: @yasinBursali
- Draft: False
- Base branch: main
- Head branch: fix/community-extensions-bind-address
- Changed files: 31
- Additions/deletions: +87 / -35
- Labels: none
