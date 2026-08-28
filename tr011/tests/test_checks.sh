#!/usr/bin/env bash
# Negative controls for TR-011's checkers: every violating fixture must be
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

expect_fail "one qualifying feature (rho disqualification, D6)" \
  python3 checks/check_pass.py tests/fixtures/pass_bad_features.json
expect_fail "AUC below the 0.7 gate" \
  python3 checks/check_pass.py tests/fixtures/pass_bad_auc.json
expect_fail "PASS claimed over a D7-invalidated corpus B" \
  python3 checks/check_pass.py tests/fixtures/pass_bad_binvalid.json
expect_pass "healthy pass gates" \
  python3 checks/check_pass.py tests/fixtures/pass_good.json

expect_fail "shuffle-invisible sequential features" \
  python3 checks/check_controls.py tests/fixtures/controls_bad_shuffle.json
expect_fail "topic-sorting classifier" \
  python3 checks/check_controls.py tests/fixtures/controls_bad_topic.json
expect_fail "non-identical duplicate re-scoring" \
  python3 checks/check_controls.py tests/fixtures/controls_bad_dupes.json
expect_pass "healthy controls" \
  python3 checks/check_controls.py tests/fixtures/controls_good.json

expect_fail "KILL fired (length detector)" \
  python3 checks/check_kill.py tests/fixtures/kill_bad_killed.json
expect_fail "residualizer over-corrects (can fake a KILL, D5)" \
  python3 checks/check_kill.py tests/fixtures/kill_bad_overcorrect.json
expect_fail "residualizer under-corrects (can fake a pass, D5)" \
  python3 checks/check_kill.py tests/fixtures/kill_bad_undercorrect.json
expect_pass "certified residualizer, no kill" \
  python3 checks/check_kill.py tests/fixtures/kill_good.json

exit $bad
