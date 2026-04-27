# Test Environments

## Environment 1: Code Analysis (Primary)

**Purpose:** Static analysis of all 75 PRs
**Tool:** Python 3.12 + git + bash
**What was tested:**
- Diff extraction and analysis
- File-level conflict detection
- Subsystem classification
- Risk scoring

**Reproduction:**
```bash
cd /workspace/dreamserver-repo
python3 /workspace/dreamserver-audit/analysis/scripts/analyze_prs.py
```

## Environment 2: Docker (Not Used)

**Purpose:** Would be used for live container testing
**Status:** Available via host socket but not used for this audit
**Rationale:** 75 PRs across 15+ subsystems would require days of live testing

## Environment 3: GPU Hardware (Not Used)

**Purpose:** Would be used for GPU code path testing
**Status:** NVIDIA GPU available on host but not configured for DreamServer
**Rationale:** GPU testing requires full DreamServer deployment

## Environment 4: Windows/macOS (Not Available)

**Purpose:** Would be used for platform-specific testing
**Status:** Not available in this environment
**Rationale:** Linux-only VM
