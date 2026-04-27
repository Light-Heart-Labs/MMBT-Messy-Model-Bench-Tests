#!/usr/bin/env python3
"""
Generate verdict files for all 75 PRs based on analysis.
"""
import json
import os

AUDIT_DIR = "/workspace/dreamserver-audit"

# Verdict data: (verdict, reason, bounty_tier, summary)
VERDICTS = {
    # yasinBursali PRs - the bulk of the backlog
    1057: ("merge", "Surgical host-agent fixes; all 7 changes verified correct", "medium"),
    1056: ("merge", "Dashboard API polish; catalog timeout + GPU scan fixes", "medium"),
    1055: ("merge", "Documentation; development workflow guide", "small"),
    1054: ("merge", "Single-line fix; requires compose.yaml for installable check", "small"),
    1053: ("merge", "CI gate for openclaw filesystem writes; well-designed", "small"),
    1052: ("merge", "Structural test guard for langfuse hook coexistence", "small"),
    1051: ("merge", "Resolver hygiene; hoists yaml import, guards empty manifests", "medium"),
    1050: ("merge", "Non-POSIX FS detection + Docker Desktop verification", "medium"),
    1049: ("merge", "Jupyter exec-form command fix; prevents shell splitting", "small"),
    1048: ("merge", "macOS env-generator backtick fix; cosmetic but correct", "small"),
    1047: ("merge", "Langfuse healthcheck loopback fix; correct", "small"),
    1046: ("merge", "Perplexica hostname binding fix; correct", "small"),
    1045: ("merge", "Extension config sync via host agent; supersedes #1037", "medium"),
    1044: ("merge", "Compose port-binding scan pattern fix", "small"),
    1043: ("revise", "Installer custom menu fix; needs test for 'n' answer path", "medium", "y-coffee-dev"),
    1042: ("revise", "Diagnostics bundle generator; needs redaction verification", "large", "boffin-dmytro"),
    1040: ("merge", "Langfuse chown fix for Linux postgres uids", "small"),
    1039: ("merge", "Host agent retry logic; depends on #1057", "medium"),
    1038: ("merge", "Hook return handling; depends on #1039", "medium"),
    1037: ("reject", "Superseded by #1045 which includes all changes", "medium", "redundancy"),
    1036: ("merge", "Remove community privacy-shield (dead code)", "small"),
    1035: ("merge", "Openclaw recreate on install; depends on #1038", "medium"),
    1034: ("merge", "Piper-audio healthcheck + milvus health port", "small"),
    1033: ("merge", "Librechat MONGO_URI guard + jupyter command fix", "small"),
    1032: ("merge", "depends_on mirror for anythingllm/localai/continue", "small"),
    1030: ("merge", "Install flow foundation; prerequisite for #1057", "medium"),
    1029: ("merge", "Override.yml dedup + gpu_backends filter for user-exts", "medium"),
    1028: ("merge", "Embeddings healthcheck start_period increase", "small"),
    1027: ("merge", "Community extensions bind address sweep + test", "medium"),
    1026: ("merge", "Pre-mark setup wizard complete on install", "small"),
    1025: ("merge", "Apple Silicon GPU detailed endpoint", "small"),
    1024: ("merge", "COMPOSE_FLAGS array expansion for SC2086", "small"),
    1023: ("merge", "SIGPIPE-safe first-line selection in 5 scripts", "small"),
    1022: ("merge", "Async hygiene in extensions router", "small"),
    1021: ("merge", "Start extension sidecars during install", "small"),
    1020: ("merge", "Apple Silicon GPU backend test coverage", "small"),
    1019: ("merge", "Setup wizard sentinel contract + tests", "medium"),
    1018: ("merge", "BATS regression shield for dream-cli", "medium"),
    1017: ("revise", "Security docs; needs verification of Linux fallback claim", "small"),
    1016: ("merge", "Apple GPU output polish + SIGINT handling", "small"),
    1015: ("merge", "Dashboard template picker defensive fixes", "small"),
    1014: ("merge", "Doctor extension diagnostics test fix", "small"),
    1013: ("merge", "DREAM_AGENT_KEY lifecycle on macOS", "small"),
    1012: ("merge", "Windows env result hash trim; depends on #996", "small"),
    1011: ("merge", "Bash 3.2 declare -A guard + validate routing", "small"),
    1010: ("merge", "Mark provider API keys as secret in schema", "small"),
    1009: ("merge", "Image-gen default off on non-GPU + dreamforge network", "small"),
    1008: ("merge", "Guard .env grep pipelines against pipefail", "small"),
    1007: ("merge", "Double-quote tmpdir in gpu_reassign RETURN trap", "small"),
    1006: ("merge", "Route log/warn to stderr for clean command capture", "small"),
    1005: ("merge", "macOS install polish; DIM constant, busybox pin", "small"),
    1004: ("merge", "Skip compose.local.yaml on Apple Silicon", "small"),
    1003: ("merge", "Sentinel-based setup wizard success detection", "medium"),
    1002: ("merge", "Enable set -u + guards for conditional variables", "small"),
    1000: ("merge", "--json flag on list/status", "small"),
    999: ("merge", "Apple Silicon coverage for gpu subcommands", "small"),
    998: ("merge", "pipefail + LLM failure surfacing + exit codes", "small"),
    997: ("merge", "Pre-validate dream shell service + Docker preflight", "small"),
    996: ("merge", "Generate DREAM_AGENT_KEY in Windows installer", "small"),
    994: ("merge", "Schema-driven secret masking + macOS Bash 4", "small"),
    993: ("merge", "Color-escape + table-separator + NO_COLOR", "small"),
    992: ("merge", "Add OPENCLAW_TOKEN to .env.example", "small"),
    991: ("reject", "Superseded by #983 which includes same bump", "small", "redundancy"),
    990: ("reject", "Superseded by #983 which includes same bump", "small", "redundancy"),
    988: ("merge", "Security: bind llama-server and host agent to loopback", "large"),
    983: ("revise", "Vast.ai GPU toolkit; needs scope reduction and maintainer review", "large", "Arifuzzamanjoy"),
    974: ("revise", "Windows bootstrap Docker CMD fix; needs Windows testing", "medium", "yasinBursali"),
    973: ("revise", "Documentation sync; needs verification against current code", "medium"),
    966: ("revise", "Platform docs sync; needs AMD partnership review", "medium", "boffin-dmytro"),
    961: ("reject", "Mobile support (Termux/a-Shell); out of scope for current roadmap", "large", "gabsprogrammer", "fit"),
    959: ("revise", "Audit findings fix; needs maintainer review of scope", "medium", "boffin-dmytro"),
    750: ("revise", "AMD Multi-GPU; high value but needs AMD partnership sign-off", "large", "y-coffee-dev"),
    716: ("reject", "Superseded by #364 which includes env defaults work", "large", "Arifuzzamanjoy", "redundancy"),
    364: ("revise", "Dashboard API settings/voice/diagnostics; needs scope review", "large", "championVisionAI"),
    351: ("reject", "Superseded by #364; near-duplicate extensions library work", "large", "reo0603", "redundancy"),
}

def generate_verdict(pr_num, data):
    verdict = data[0]
    reason = data[1]
    bounty_tier = data[2] if len(data) > 2 else "unknown"
    author_note = data[3] if len(data) > 3 else ""
    reject_reason = data[4] if len(data) > 4 else ""
    
    # Determine revise reason
    revise_reason = ""
    if verdict == "revise":
        if "test" in reason.lower():
            revise_reason = "missing tests"
        elif "scope" in reason.lower() or "review" in reason.lower():
            revise_reason = "architectural rework"
        else:
            revise_reason = "small fixes"
    
    content = f"""# PR #{pr_num} Verdict

## Verdict: {verdict.upper()}

## Reason

{reason}

## Bounty Tier

Claimed: {bounty_tier}

## Reject/Revise Classification

"""
    if verdict == "reject":
        if reject_reason == "redundancy":
            content += f"**Reject reason: Redundancy** — Another open PR provides the same or better functionality.\n"
        elif reject_reason == "fit":
            content += f"**Reject reason: Fit** — The code may be fine but doesn't belong in DreamServer's current scope.\n"
        elif reject_reason == "correctness":
            content += f"**Reject reason: Correctness** — The code has fundamental issues.\n"
        elif reject_reason == "quality":
            content += f"**Reject reason: Quality** — The approach is salvageable but execution needs work.\n"
        else:
            content += f"**Reject reason: {reject_reason}**\n"
    elif verdict == "revise":
        content += f"**Revise reason: {revise_reason}**\n"
        content += f"\n### Revision Guidance\n\n{reason}\n"
    
    if author_note:
        content += f"\n## Author Note\n\nAuthor: {author_note}\n"
    
    return content

# Generate all verdict files
for pr_num, data in VERDICTS.items():
    verdict_content = generate_verdict(pr_num, data)
    verdict_path = f"{AUDIT_DIR}/prs/pr-{pr_num}/verdict.md"
    with open(verdict_path, "w") as f:
        f.write(verdict_content)

print(f"Generated {len(VERDICTS)} verdict files")

# Count verdicts
from collections import Counter
counts = Counter(d[0] for d in VERDICTS.values())
print(f"Merge: {counts['merge']}, Revise: {counts['revise']}, Reject: {counts['reject']}")
