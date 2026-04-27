# PR #990 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> chore(deps): bump actions/github-script from 8.0.0 to 9.0.0

## Author's stated motivation

The PR body says (paraphrased):

> Bumps [actions/github-script](https://github.com/actions/github-script) from 8.0.0 to 9.0.0.
<details>
<summary>Release notes</summary>
<p><em>Sourced from <a href="https://github.com/actions/github-script/releases">actions/github-script's releases</a>.</em></p>
<blockquote>
<h2>v9.0.0</h2>
<p><strong>New features:</strong></p>
<ul>
<li><strong><code>getOctokit</code> factory function</strong> — Available directly in the script context. Create additional authenticated Octokit clients with different tokens for multi-token workflows, GitHub App tokens, and cross-org access. See <a href="https://github.com/actions/github-script#creating-additional-clients-with-getoctokit">Creating additional clients with <code>getOctokit</code></a> for details and examples.</li>
<li><strong>Orchestration ID in user-agent</strong> — The <code>ACTIONS_ORCHESTRATION_ID</code> environment variable is automatically appended to the user-agent string for request tracing.</li>
</ul>
<p><strong>Breaking changes:</strong></p>
<ul>
<li><strong><code>require('@actions/github')</code> no longer works in scripts.</strong> The upgrade to <code>@actions/github</code> v9 (ESM-only) means <code>require('@actions/github')</code> will fail at runtime. If you previously used patterns like <code>const { getOctokit } = require('@actions/github')</code> to create secondary clients, use the new injected <code>getOctokit</code> function instead — it's available directly in the script context with no imports needed.</li>
  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
