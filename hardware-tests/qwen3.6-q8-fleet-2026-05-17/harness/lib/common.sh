#!/usr/bin/env bash
# Shared helpers for bench-fleet scripts. Source, don't exec.
# Pattern adapted from ~/dream-fleet-test/lib/common.sh.

BENCH_FLEET_ROOT="${BENCH_FLEET_ROOT:-$HOME/bench-fleet}"
TARGETS_JSON="$BENCH_FLEET_ROOT/targets.json"

log()   { printf '[%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*"; }
warn()  { printf '[%s] WARN: %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >&2; }
err()   { printf '[%s] ERROR: %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >&2; }
die()   { err "$@"; exit 1; }

# Print a JSON field from targets.json for a host. Usage: target_field <host> <field>
target_field() {
    local host="$1" field="$2"
    jq -r --arg h "$host" --arg f "$field" \
        '.hosts[] | select(.name == $h) | .[$f] // empty' \
        "$TARGETS_JSON"
}

# Print a JSON array/object field from targets.json for a host (raw JSON).
# Usage: target_field_json <host> <field>
target_field_json() {
    local host="$1" field="$2"
    jq -c --arg h "$host" --arg f "$field" \
        '.hosts[] | select(.name == $h) | .[$f]' \
        "$TARGETS_JSON"
}

# List all host names. Usage: target_names
target_names() {
    jq -r '.hosts[].name' "$TARGETS_JSON"
}

# List backends for a host as space-separated. Usage: target_backends <host>
target_backends() {
    local host="$1"
    jq -r --arg h "$host" \
        '.hosts[] | select(.name == $h) | .backends[]' \
        "$TARGETS_JSON" | tr '\n' ' '
}

# Read a study-level field. Usage: study_field <jq-path>  (e.g. .llama_cpp_sha)
study_field() {
    local path="$1"
    jq -r ".study${path} // empty" "$TARGETS_JSON"
}

# Per-process SSH ControlMaster dir so repeated host_exec / host_cp calls on the
# same host multiplex over one TCP+auth handshake. Cleaned up at script exit.
BENCH_FLEET_SSH_CTRL="${BENCH_FLEET_SSH_CTRL:-/tmp/bench-fleet-ssh-$$}"
mkdir -p "$BENCH_FLEET_SSH_CTRL" 2>/dev/null
trap 'rm -rf "$BENCH_FLEET_SSH_CTRL" 2>/dev/null' EXIT

_ssh_opts=(
    -o BatchMode=yes
    -o ConnectTimeout=10
    -o ServerAliveInterval=30
    -o ControlMaster=auto
    -o "ControlPath=$BENCH_FLEET_SSH_CTRL/%C"
    -o ControlPersist=600
)

# Run a shell command on a host. Local hosts use bash directly; remote hosts via ssh.
# Streams stdout+stderr combined. Returns the command's exit code.
# Usage: host_exec <host> <bash_command_string>
host_exec() {
    local host="$1"; shift
    local cmd="$*"
    local is_local; is_local="$(target_field "$host" local)"
    if [[ "$is_local" == "true" ]]; then
        bash -lc "$cmd" 2>&1
    else
        local alias; alias="$(target_field "$host" ssh_alias)"
        [[ -z "$alias" ]] && die "host $host is not local and has no ssh_alias"
        ssh "${_ssh_opts[@]}" "$alias" "bash -lc $(printf %q "$cmd")" 2>&1
    fi
}

# Copy a file to a host. Local hosts use cp; remote hosts use rsync over the
# ControlMaster connection. Usage: host_cp <host> <src> <dest_path_on_host>
host_cp() {
    local host="$1" src="$2" dest="$3"
    local is_local; is_local="$(target_field "$host" local)"
    if [[ "$is_local" == "true" ]]; then
        mkdir -p "$(dirname "$dest")"
        cp -f "$src" "$dest"
    else
        local alias; alias="$(target_field "$host" ssh_alias)"
        [[ -z "$alias" ]] && die "host $host is not local and has no ssh_alias"
        # Ensure remote dir exists, then rsync (multiplexed over ControlMaster)
        ssh "${_ssh_opts[@]}" "$alias" "mkdir -p $(printf %q "$(dirname "$dest")")"
        rsync -aP \
            -e "ssh ${_ssh_opts[*]}" \
            "$src" "$alias:$dest"
    fi
}

# Compute SHA256 of a file on a host (uses sha256sum on linux, shasum -a 256 on macos).
# Usage: host_sha256 <host> <path_on_host>
host_sha256() {
    local host="$1" path="$2"
    local os; os="$(target_field "$host" os)"
    if [[ "$os" == "macos" ]]; then
        host_exec "$host" "shasum -a 256 $(printf %q "$path") | awk '{print \$1}'"
    else
        host_exec "$host" "sha256sum $(printf %q "$path") | awk '{print \$1}'"
    fi
}
