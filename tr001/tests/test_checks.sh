#!/usr/bin/env bash
# Negative controls for the checkers themselves. A check that only reports
# success is worthless, so each violating fixture must make its check exit
# nonzero, and each healthy fixture must pass. Written and run before any
# mechanism existed.
set -u
cd "$(dirname "$0")/.."
bad=0

expect_fail() {
  desc="$1"; shift
  if "$@" >/dev/null 2>&1; then
    echo "CHECKER BROKEN: accepted $desc"
    bad=1
  else
    echo "ok: rejected $desc"
  fi
}

expect_pass() {
  desc="$1"; shift
  if "$@" >/dev/null 2>&1; then
    echo "ok: accepted $desc"
  else
    echo "CHECKER BROKEN: rejected $desc"
    bad=1
  fi
}

expect_fail "leaking random adapter" \
  python3 checks/check_controls.py tests/fixtures/controls_bad_random.json
expect_fail "generic-instruction shuffled pairing" \
  python3 checks/check_controls.py tests/fixtures/controls_bad_shuffled.json
expect_fail "dead-code ablation" \
  python3 checks/check_controls.py tests/fixtures/controls_bad_ablation.json
expect_fail "compute mismatch M>K" \
  python3 checks/check_controls.py tests/fixtures/controls_bad_compute.json
expect_pass "healthy controls fixture" \
  python3 checks/check_controls.py tests/fixtures/controls_good.json

expect_fail "train/eval passage overlap (case and whitespace varied)" \
  python3 checks/check_leakage.py tests/fixtures/leak_overlap/train.jsonl tests/fixtures/leak_overlap/eval.jsonl
expect_pass "disjoint train/eval sets" \
  python3 checks/check_leakage.py tests/fixtures/leak_clean/train.jsonl tests/fixtures/leak_clean/eval.jsonl
expect_fail "leakage check over an empty eval set" \
  python3 checks/check_leakage.py tests/fixtures/leak_clean/train.jsonl /dev/null

exit $bad
