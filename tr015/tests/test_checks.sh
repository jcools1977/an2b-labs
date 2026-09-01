#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/.."
bad=0
expect_fail() { desc="$1"; shift; if "$@" >/dev/null 2>&1; then echo "CHECKER BROKEN: accepted $desc"; bad=1; else echo "ok: rejected $desc"; fi; }
expect_pass() { desc="$1"; shift; if "$@" >/dev/null 2>&1; then echo "ok: accepted $desc"; else echo "CHECKER BROKEN: rejected $desc"; bad=1; fi; }

expect_fail "accuracy below 0.90" python3 checks/check_pass.py tests/fixtures/pass_bad_acc.json
expect_fail "Burrows Delta winning" python3 checks/check_pass.py tests/fixtures/pass_bad_burrows.json
expect_fail "drift gate missed" python3 checks/check_pass.py tests/fixtures/pass_bad_drift.json
expect_fail "rank above 10" python3 checks/check_pass.py tests/fixtures/pass_bad_rank.json
expect_pass "healthy pass gates" python3 checks/check_pass.py tests/fixtures/pass_good.json

expect_fail "paraphrase KILL (voice was content)" python3 checks/check_kill.py tests/fixtures/kill_bad_paraphrase.json
expect_fail "residualizer under-corrects" python3 checks/check_kill.py tests/fixtures/kill_bad_undercorrect.json
expect_fail "residualizer over-corrects" python3 checks/check_kill.py tests/fixtures/kill_bad_overcorrect.json
expect_pass "certified residualizer, no kill" python3 checks/check_kill.py tests/fixtures/kill_good.json

expect_fail "label-shuffle above chance" python3 checks/check_controls.py tests/fixtures/controls_bad_shuffle.json
expect_fail "label-shuffle leak hidden in one size (D21)" python3 checks/check_controls.py tests/fixtures/controls_bad_hidden_size.json
expect_fail "per-size CIs absent (D21)" python3 checks/check_controls.py tests/fixtures/controls_bad_no_sizes.json
expect_fail "topic leak unreported" python3 checks/check_controls.py tests/fixtures/controls_bad_topic.json
expect_fail "translation stress unreported" python3 checks/check_controls.py tests/fixtures/controls_bad_translation.json
expect_pass "healthy controls" python3 checks/check_controls.py tests/fixtures/controls_good.json
exit $bad
