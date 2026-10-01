#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/.."
bad=0
expect_fail() { desc="$1"; shift; if "$@" >/dev/null 2>&1; then echo "CHECKER BROKEN: accepted $desc"; bad=1; else echo "ok: rejected $desc"; fi; }
expect_pass() { desc="$1"; shift; if "$@" >/dev/null 2>&1; then echo "ok: accepted $desc"; else echo "CHECKER BROKEN: rejected $desc"; bad=1; fi; }
expect_fail "250 collapse runs"                      python3 checks/check_corpus.py tests/fixtures/corpus_bad_count.json
expect_fail "labeler threshold changed"             python3 checks/check_corpus.py tests/fixtures/corpus_bad_labeler.json
expect_fail "controls not matched on length"        python3 checks/check_corpus.py tests/fixtures/corpus_bad_match.json
expect_fail "audit sample under 10 percent"         python3 checks/check_corpus.py tests/fixtures/corpus_bad_audit.json
expect_pass "healthy corpus manifest"               python3 checks/check_corpus.py tests/fixtures/corpus_good.json
expect_fail "AUC 0.749 at one seed (near-miss)"     python3 checks/check_pass.py tests/fixtures/pass_bad_auc_near_miss.json
expect_fail "recovery rho 0.3"                      python3 checks/check_pass.py tests/fixtures/pass_bad_rho.json
expect_fail "headline without cleared audit"        python3 checks/check_pass.py tests/fixtures/pass_bad_no_audit.json
expect_fail "seed 43 missing"                       python3 checks/check_pass.py tests/fixtures/pass_bad_seed_missing.json
expect_pass "healthy pass gates"                    python3 checks/check_pass.py tests/fixtures/pass_good.json
expect_fail "KILL firing (parity on all indicators)" python3 checks/check_kill.py tests/fixtures/kill_bad_fires.json
expect_fail "killed flag inconsistent"              python3 checks/check_kill.py tests/fixtures/kill_bad_inconsistent.json
expect_pass "indicators discriminate"               python3 checks/check_kill.py tests/fixtures/kill_good.json
expect_fail "reversed series keeps power"           python3 checks/check_controls.py tests/fixtures/controls_bad_reversed.json
expect_fail "turn index leaked"                     python3 checks/check_controls.py tests/fixtures/controls_bad_turn_index.json
expect_fail "audit agreement 0.85"                  python3 checks/check_controls.py tests/fixtures/controls_bad_audit.json
expect_fail "auditor unnamed"                       python3 checks/check_controls.py tests/fixtures/controls_bad_auditor.json
expect_pass "healthy controls"                      python3 checks/check_controls.py tests/fixtures/controls_good.json
exit $bad
