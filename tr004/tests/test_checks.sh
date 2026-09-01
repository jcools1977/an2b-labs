#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/.."
bad=0
expect_fail() { desc="$1"; shift; if "$@" >/dev/null 2>&1; then echo "CHECKER BROKEN: accepted $desc"; bad=1; else echo "ok: rejected $desc"; fi; }
expect_pass() { desc="$1"; shift; if "$@" >/dev/null 2>&1; then echo "ok: accepted $desc"; else echo "CHECKER BROKEN: rejected $desc"; bad=1; fi; }

expect_fail "delta below 0.2" python3 checks/check_pass.py tests/fixtures/pass_bad_delta.json
expect_fail "estimator direction disagreement" python3 checks/check_pass.py tests/fixtures/pass_bad_direction.json
expect_fail "effect dying under controls" python3 checks/check_pass.py tests/fixtures/pass_bad_controls.json
expect_fail "seed non-replication" python3 checks/check_pass.py tests/fixtures/pass_bad_seeds.json
expect_pass "healthy pass gates" python3 checks/check_pass.py tests/fixtures/pass_good.json

expect_fail "KILL firing (model artifact)" python3 checks/check_kill.py tests/fixtures/kill_bad_fires.json
expect_fail "killed flag inconsistent with D8" python3 checks/check_kill.py tests/fixtures/kill_bad_inconsistent.json
expect_pass "effect present in both models" python3 checks/check_kill.py tests/fixtures/kill_good.json

expect_fail "shuffled labels retaining effect" python3 checks/check_controls.py tests/fixtures/controls_bad_shuffle.json
expect_fail "synonym control manufacturing effect" python3 checks/check_controls.py tests/fixtures/controls_bad_synonym.json
expect_fail "effect strengthening under random projection" python3 checks/check_controls.py tests/fixtures/controls_bad_projection.json
expect_fail "missing control block (D21 lesson)" python3 checks/check_controls.py tests/fixtures/controls_bad_missing_block.json
expect_pass "healthy controls" python3 checks/check_controls.py tests/fixtures/controls_good.json

expect_fail "too few lemmas" python3 checks/check_corpus.py tests/fixtures/corpus_bad_lemmas.json
expect_fail "wrong frozen seeds" python3 checks/check_corpus.py tests/fixtures/corpus_bad_seeds.json
expect_pass "healthy corpus" python3 checks/check_corpus.py tests/fixtures/corpus_good.json
exit $bad
