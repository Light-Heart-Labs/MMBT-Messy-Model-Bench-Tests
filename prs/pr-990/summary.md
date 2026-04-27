# PR #990 Summary

## Claim In Plain English

chore(deps): bump actions/github-script from 8.0.0 to 9.0.0

## Audit Restatement

`actions/github-script` v9 pin bump is safe for the touched scripts: no `require('@actions/github')` / `getOctokit` pattern is present, scripts use the injected `github.rest`, and YAML parsing passes for both changed workflows.

## Metadata

- Author: @app/dependabot
- Draft: False
- Base branch: main
- Head branch: dependabot/github_actions/actions/github-script-9.0.0
- Changed files: 2
- Additions/deletions: +5 / -5
- Labels: dependencies, github_actions
