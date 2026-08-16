#!/usr/bin/env bash
# Stage the Qwen3.6-27B Q8_0 GGUF for the quant crossover pilot
# (PREREGISTRATION.md section 7; configs/quant-pilot.json models.q36_q8).
#
# WRITTEN, NOT RUN, at build time (2026-08-16). The operator runs this on
# Tower2 BEFORE the pilot window opens. run_quant_pilot.sh preflight refuses
# to open the window until this file exists with the pinned size + sha256.
#
# Artifact identity, fetched via the HF API on 2026-08-16 and pinned:
#   repo:      unsloth/Qwen3.6-27B-GGUF
#   revision:  82d411acf4a06cfb8d9b073a5211bf410bfc29bf  (same revision the
#              local UD-Q4_K_XL artifact traces to; revision-pinned URL below)
#   file:      Qwen3.6-27B-Q8_0.gguf   (repo root)
#   size:      28595763424 bytes
#   sha256:    f93f517f38e696d35a1a7df2c0e3155a64f4c4dcd662107a146ae263f7fb14ce
#              (HF LFS oid, sha256-verified after download below)
#
# Destination follows the campaign staging convention already used for the
# Qwen3.8 Q8_0 artifact (/mnt/bulk/models/qwen3.8-27b-q8_0/):
#   /mnt/bulk/models/qwen3.6-27b-q8_0/Qwen3.6-27B-Q8_0.gguf
#
# Behavior: idempotent; resumes partial downloads; downloads to a .part file
# and only moves it into place after BOTH the byte size and the full sha256
# verify. Never deletes or overwrites an existing verified artifact.

set -euo pipefail

REPO="unsloth/Qwen3.6-27B-GGUF"
REVISION="82d411acf4a06cfb8d9b073a5211bf410bfc29bf"
FILE="Qwen3.6-27B-Q8_0.gguf"
URL="https://huggingface.co/${REPO}/resolve/${REVISION}/${FILE}"
EXPECTED_SIZE=28595763424
EXPECTED_SHA256=f93f517f38e696d35a1a7df2c0e3155a64f4c4dcd662107a146ae263f7fb14ce

DEST_DIR=/mnt/bulk/models/qwen3.6-27b-q8_0
DEST="$DEST_DIR/$FILE"
PART="$DEST.part"
MAX_ATTEMPTS=8

log() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*"; }
die() { log "ERROR: $*" >&2; exit 1; }

verify() { # path -> 0 iff size + sha256 both match the pins
  local path="$1" size sha
  size="$(stat -c %s "$path")"
  if [ "$size" != "$EXPECTED_SIZE" ]; then
    log "size mismatch on $path: got $size, want $EXPECTED_SIZE"
    return 1
  fi
  log "hashing $path ($size bytes)..."
  sha="$(sha256sum "$path" | awk '{print $1}')"
  if [ "$sha" != "$EXPECTED_SHA256" ]; then
    log "sha256 mismatch on $path: got $sha, want $EXPECTED_SHA256"
    return 1
  fi
  return 0
}

# Idempotence: an existing verified artifact is left untouched.
if [ -f "$DEST" ]; then
  if verify "$DEST"; then
    log "already staged and verified: $DEST"
    exit 0
  fi
  die "$DEST exists but does NOT match the pinned identity — refusing to touch it; inspect manually"
fi

# Free-space check (need the remainder of the file + 1 GiB margin).
have_part=0
[ -f "$PART" ] && have_part="$(stat -c %s "$PART")"
need=$(( EXPECTED_SIZE - have_part + 1073741824 ))
avail="$(df -B1 --output=avail /mnt/bulk | tail -1 | tr -d ' ')"
[ "$avail" -gt "$need" ] || die "insufficient space on /mnt/bulk: have $avail bytes, need $need"

mkdir -p "$DEST_DIR"

attempt=0
while [ "$attempt" -lt "$MAX_ATTEMPTS" ]; do
  attempt=$((attempt + 1))
  resume=0
  [ -f "$PART" ] && resume="$(stat -c %s "$PART")"
  log "attempt $attempt/$MAX_ATTEMPTS: $FILE resume@$resume (expected $EXPECTED_SIZE)"
  if curl -fL --retry 5 --retry-delay 10 --connect-timeout 30 \
       -C - -o "$PART" "$URL"; then
    break
  fi
  log "curl exited nonzero; will resume"
  sleep 15
done

[ -f "$PART" ] || die "download produced no file after $MAX_ATTEMPTS attempts"

if ! verify "$PART"; then
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  mv "$PART" "$PART.badsha.$stamp"
  die "downloaded bytes failed verification; quarantined at $PART.badsha.$stamp (re-run to download fresh)"
fi

mv "$PART" "$DEST"
chmod 644 "$DEST"
log "staged + verified: $DEST"
log "sha256=$EXPECTED_SHA256 size=$EXPECTED_SIZE url=$URL"
log "next: record this artifact in the study manifest/ pins before the pilot window opens"
