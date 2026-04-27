# PR #1043 Diff Analysis

## Claimed Change

fix(installer): custom menu's 'n' answers were not actually disabling services

## Actual Change Characterization

Fixes custom-menu `n` answers for most services, but leaves `embeddings` enabled when RAG is disabled, so opt-out still pulls/starts a RAG service.

## Surface Area

- Subsystems: installer, extensions/compose
- Changed files: 2
- Additions/deletions: +47 / -47

## Fit Assessment

The change affects behavior that needs revision before it fits DreamServer's current architecture and merge queue.
