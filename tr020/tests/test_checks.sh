#!/usr/bin/env bash
# Negative controls for TR-020's checkers: every violating fixture must be
# rejected and every healthy one accepted, before any mechanism exists.
set -u
cd "$(dirname "$0")/.."
bad=0

expect_fail() {
  desc="$1"; shift
  if "$@" >/dev/null 2>&1; then echo "CHECKER BROKEN: accepted $desc"; bad=1
  else echo "ok: rejected $desc"; fi
}
expect_pass() {
  desc="$1"; shift
  if "$@" >/dev/null 2>&1; then echo "ok: accepted $desc"
  else echo "CHECKER BROKEN: rejected $desc"; bad=1; fi
}

expect_fail "recovery below the 0.9 gate" \
  python3 checks/check_recovery.py tests/fixtures/recovery_bad_gate.json
expect_fail "interaction KILL (12.5% live falsely flagged)" \
  python3 checks/check_recovery.py tests/fixtures/recovery_bad_kill.json
expect_pass "clean recovery with redundant duplicates correctly flagged" \
  python3 checks/check_recovery.py tests/fixtures/recovery_good.json

expect_fail "flags on the all-live system" \
  python3 checks/check_controls.py tests/fixtures/controls_bad_alllive.json
expect_fail "non-inert placebo mask" \
  python3 checks/check_controls.py tests/fixtures/controls_bad_placebo.json
expect_fail "verdicts flipping between probe halves" \
  python3 checks/check_controls.py tests/fixtures/controls_bad_replication.json
expect_pass "healthy controls" \
  python3 checks/check_controls.py tests/fixtures/controls_good.json

expect_fail "judge blind to wrong-entity damage" \
  python3 checks/check_measurement_gates.py tests/fixtures/gates_bad_judge.json
expect_fail "canonicalizer missing hand-labeled pairs" \
  python3 checks/check_measurement_gates.py tests/fixtures/gates_bad_canon.json
expect_pass "healthy measurement gates" \
  python3 checks/check_measurement_gates.py tests/fixtures/gates_good.json

exit $bad
