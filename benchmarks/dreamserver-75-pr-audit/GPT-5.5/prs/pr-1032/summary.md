# PR #1032 Summary

## Claim In Plain English

fix(extensions): mirror manifest depends_on in anythingllm / localai / continue

## Audit Restatement

The compose `depends_on` additions are correct, including Continue's Apple overlay, but the PR does not solve first-start dashboard installs by itself because the same branch still has host-agent `_handle_install` running `docker compose up -d --no-deps <service>`. Proof: source inspection reports `--no-deps-in-install=True`. Merge after #1021, or stack the host-agent change here.

## Metadata

- Author: @yasinBursali
- Draft: False
- Base branch: main
- Head branch: fix/community-depends-on-mirror
- Changed files: 6
- Additions/deletions: +51 / -0
- Labels: none
