#!/usr/bin/env bash
# Checker self-test: every checker must REJECT its red fixtures and ACCEPT its green one.
set -u
cd "$(dirname "$0")/.."
bad=0
expect_fail() { desc="$1"; shift; if "$@" >/dev/null 2>&1; then echo "CHECKER BROKEN: accepted $desc"; bad=1; else echo "ok: rejected $desc"; fi; }
expect_pass() { desc="$1"; shift; if "$@" >/dev/null 2>&1; then echo "ok: accepted $desc"; else echo "CHECKER BROKEN: rejected $desc"; bad=1; fi; }
expect_fail "AIC margin 9.9 in one family (near-miss)"   python3 checks/check_pass.py tests/fixtures/pass_bad_margin_near_miss.json
expect_fail "unlimited log equal to best bounded"       python3 checks/check_pass.py tests/fixtures/pass_bad_unlimited_best.json
expect_fail "seed 43 missing"                           python3 checks/check_pass.py tests/fixtures/pass_bad_seed_missing.json
expect_fail "seeds disagree (43 shows no regime)"       python3 checks/check_pass.py tests/fixtures/pass_bad_seed_disagree.json
expect_pass "healthy pass gates"                        python3 checks/check_pass.py tests/fixtures/pass_good.json
expect_fail "KILL firing (breakpoints two steps apart)" python3 checks/check_kill.py tests/fixtures/kill_bad_fires.json
expect_fail "killed flag inconsistent"                  python3 checks/check_kill.py tests/fixtures/kill_bad_inconsistent.json
expect_pass "breakpoints within one step"               python3 checks/check_kill.py tests/fixtures/kill_good.json
expect_pass "no regime in one family: KILL not evaluated" python3 checks/check_kill.py tests/fixtures/kill_good_no_regime_one_family.json
expect_fail "regime persists under random salience"     python3 checks/check_controls.py tests/fixtures/controls_bad_random_salience.json
expect_fail "frozen buffer far above single agent"      python3 checks/check_controls.py tests/fixtures/controls_bad_frozen_buffer.json
expect_fail "role shuffle leaves accuracy unchanged"    python3 checks/check_controls.py tests/fixtures/controls_bad_role_shuffle.json
expect_fail "control arm missing"                       python3 checks/check_controls.py tests/fixtures/controls_bad_missing_arm.json
expect_pass "healthy controls"                          python3 checks/check_controls.py tests/fixtures/controls_good.json
expect_fail "150 scored items"                          python3 checks/check_tasks.py tests/fixtures/tasks_bad_count.json
expect_fail "screening rule swapped"                    python3 checks/check_tasks.py tests/fixtures/tasks_bad_screen.json
expect_fail "scored items overlap across seeds"         python3 checks/check_tasks.py tests/fixtures/tasks_bad_overlap.json
expect_fail "puzzles without unique solutions"          python3 checks/check_tasks.py tests/fixtures/tasks_bad_nonunique.json
expect_pass "healthy task manifest"                     python3 checks/check_tasks.py tests/fixtures/tasks_good.json
exit $bad
