#!/usr/bin/env bash
# Reproduces the integration-smoke BATS failure that's poisoning 72 of 75 PR CI runs.
#
# Test file:  dream-server/tests/bats-tests/docker-phase.bats
# Test name:  "_docker_cmd_arr: returns sudo docker when DOCKER_CMD is sudo docker"
# Test line:  100
#
# Failure mode: the test asserts that `_docker_cmd_arr` produces two lines
# (sudo \n docker), but the function uses `echo "sudo" "docker"` which produces
# one line (`sudo docker\n`).
#
# This script reproduces the assertion failure outside of BATS so the bug is
# obvious without a CI runner.
#
# Usage:
#   bash testing/reproductions/repro-bats-docker-cmd-arr.sh

set -euo pipefail

DOCKER_CMD="sudo docker"
_docker_cmd_arr() {
    case "${DOCKER_CMD:-docker}" in
        "sudo docker") echo "sudo" "docker" ;;
        *)             echo "docker" ;;
    esac
}

actual=$(_docker_cmd_arr)
expected=$'sudo\ndocker'

echo "actual:   '$actual'"
echo "expected: '$(printf '%s' "$expected")'"
echo

if [[ "$actual" == "$expected" ]]; then
    echo "PASS — bug is fixed (or you ran this on a system where echo behaves differently)."
    exit 0
else
    echo "FAIL — assertion mismatch reproduced."
    echo "  actual is one line, expected is two lines."
    echo
    echo "Two valid fixes (pick one):"
    echo "  1. Change the function to:    printf '%s\\n' \"sudo\" \"docker\""
    echo "  2. Change the assertion to:   assert_output \"sudo docker\""
    exit 1
fi
