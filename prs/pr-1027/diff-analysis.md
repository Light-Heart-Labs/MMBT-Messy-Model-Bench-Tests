# PR #1027 Diff Analysis

## Claimed Change

fix(extensions): bind community extension ports via ${BIND_ADDRESS}

## Actual Change Characterization

The bind sweep itself is mechanically good (`test-bind-address-sweep.sh` passes and static scan finds no literal community `127.0.0.1` port entries), but on current main the dashboard scanner rejects `${BIND_ADDRESS:-127.0.0.1}`. Direct `_scan_compose_content` proof rejected Continue, Jupyter, and Milvus with 400s. Merge after #1044, or include the scanner update in this PR.

## Surface Area

- Subsystems: dashboard, extensions/compose
- Changed files: 31
- Additions/deletions: +87 / -35

## Fit Assessment

The change affects behavior that needs revision before it fits DreamServer's current architecture and merge queue.
