# PR #961 Summary

## Claim In Plain English

feat: add mobile paths for Android Termux and iOS a-Shell

## Audit Restatement

Mobile preview dispatch and syntax are broadly coherent, but the Android localhost automation bridge lacks an origin/token gate on action POST endpoints; malicious local-browser pages can trigger automation requests.

## Metadata

- Author: @gabsprogrammer
- Draft: False
- Base branch: main
- Head branch: mobile-termux-ashell-preview
- Changed files: 30
- Additions/deletions: +6891 / -26
- Labels: none
