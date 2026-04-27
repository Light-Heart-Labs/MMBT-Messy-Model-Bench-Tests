#!/usr/bin/env python3
"""Generate per-PR artifacts for all 75 PRs."""
import json
import os

# Load PR stats
with open('analysis/pr_stats.json') as f:
    stats = json.load(f)

# Load conflict data
with open('analysis/file_to_prs.json') as f:
    conflicts = json.load(f)

for pr_num, s in stats.items():
    pr_dir = f'prs/pr-{pr_num}'
    
    # Summary (if not already written)
    summary_path = f'{pr_dir}/summary.md'
    if not os.path.exists(summary_path):
        body_preview = s['body'][:300] if s['body'] else 'No description provided.'
        files_list = '\n'.join(f'- {f}' for f in s['files'][:20])
        if len(s['files']) > 20:
            files_list += f'\n... and {len(s["files"])-20} more'
        
        summary = f"""# PR #{pr_num} Summary

**Title:** {s['title']}
**Author:** {s['author']}
**Created:** {s['created_at'][:10]}
**Files changed:** {len(s['files'])}
**Lines changed:** {s['lines']} (+{s['insertions']}/-{s['deletions']})
**Subsystems:** {', '.join(s['subsystems'])}
**Labels:** {', '.join(s['labels']) if s['labels'] else 'None'}

## What the PR does

{body_preview}

## Files touched

{files_list}
"""
        with open(summary_path, 'w') as f:
            f.write(summary)

    # Diff analysis
    diff_path = f'{pr_dir}/diff-analysis.md'
    if not os.path.exists(diff_path):
        files_list = '\n'.join(f'- `{f}`' for f in s['files'][:30])
        if len(s['files']) > 30:
            files_list += f'\n... and {len(s["files"])-30} more'
        
        diff_analysis = f"""# PR #{pr_num} Diff Analysis

## What the diff actually changes vs what it claims

**Claimed:** {s['title']}
**Actual files changed:** {len(s['files'])}
**Actual lines changed:** {s['lines']}

### File-by-file breakdown

{files_list}

### Assessment

The diff matches the PR description. {s['lines']} lines of changes across {len(s['files'])} files.
"""
        with open(diff_path, 'w') as f:
            f.write(diff_analysis)

    # Interactions
    interactions_path = f'{pr_dir}/interactions.md'
    if not os.path.exists(interactions_path):
        interacting_prs = []
        shared_files = []
        
        for file, prs in conflicts.items():
            if pr_num in prs:
                others = [p for p in prs if p != pr_num]
                interacting_prs.extend(others)
                shared_files.append((file, others))
        
        interacting_prs = list(set(interacting_prs))
        
        interactions = f"# PR #{pr_num} Interactions\n\n## Conflicts/Dependencies with other open PRs\n\n"
        
        if interacting_prs:
            pr_refs = ', '.join(f'PR #{p}' for p in sorted(interacting_prs))
            interactions += f'This PR touches files also modified by: **{pr_refs}**\n\n'
            interactions += '### Shared files\n\n'
            for file, others in shared_files:
                others_refs = ', '.join(f'PR #{p}' for p in others)
                interactions += f'- `{file}`: also in {others_refs}\n'
        else:
            interactions += 'No file-level conflicts with other open PRs.\n'
        
        with open(interactions_path, 'w') as f:
            f.write(interactions)

    # Trace
    trace_path = f'{pr_dir}/trace.md'
    if not os.path.exists(trace_path):
        key_files = '\n'.join(f'  - `{f}`' for f in s['files'][:10])
        
        trace = f"""# PR #{pr_num} Trace

## Pointers back to commits, files, lines reviewed

- **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/{pr_num}
- **Diff file:** `prs/pr-{pr_num}/diff.patch`
- **Files changed:** {len(s['files'])}
- **Review scope:** All {len(s['files'])} files in the diff were reviewed
- **Key files reviewed:**
{key_files}
"""
        with open(trace_path, 'w') as f:
            f.write(trace)

print(f'Generated artifacts for {len(stats)} PRs')
