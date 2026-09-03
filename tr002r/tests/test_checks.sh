#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/.."
bad=0
expect_fail() { desc="$1"; shift; if "$@" >/dev/null 2>&1; then echo "CHECKER BROKEN: accepted $desc"; bad=1; else echo "ok: rejected $desc"; fi; }
expect_pass() { desc="$1"; shift; if "$@" >/dev/null 2>&1; then echo "ok: accepted $desc"; else echo "CHECKER BROKEN: rejected $desc"; bad=1; fi; }

expect_fail "cosine below 0.70 in one direction" python3 checks/check_pass.py tests/fixtures/pass_bad_cosine.json
expect_fail "top-1 below 0.30 in one direction" python3 checks/check_pass.py tests/fixtures/pass_bad_top1.json
expect_fail "gate read on a non-primary pair (amendment one)" python3 checks/check_pass.py tests/fixtures/pass_bad_pair_swap.json
expect_fail "method swapped post hoc (amendment three)" python3 checks/check_pass.py tests/fixtures/pass_bad_method_swap.json
expect_fail "primary skyline below 0.80" python3 checks/check_pass.py tests/fixtures/pass_bad_skyline.json
expect_fail "gate read below the largest n" python3 checks/check_pass.py tests/fixtures/pass_bad_small_n.json
expect_fail "seed non-replication" python3 checks/check_pass.py tests/fixtures/pass_bad_seeds.json
expect_pass "healthy pass gates" python3 checks/check_pass.py tests/fixtures/pass_good.json

expect_fail "KILL firing (skyline dead on most pairs)" python3 checks/check_kill.py tests/fixtures/kill_bad_fires.json
expect_fail "killed flag inconsistent" python3 checks/check_kill.py tests/fixtures/kill_bad_inconsistent.json
expect_pass "skylines healthy" python3 checks/check_kill.py tests/fixtures/kill_good.json

expect_fail "shuffled target retaining retrieval" python3 checks/check_controls.py tests/fixtures/controls_bad_shuffle.json
expect_fail "wrong-model retrieval not collapsing (amendment two)" python3 checks/check_controls.py tests/fixtures/controls_bad_wrongmodel.json
expect_fail "training halves sharing documents" python3 checks/check_controls.py tests/fixtures/controls_bad_overlap.json
expect_fail "wrong-model block absent" python3 checks/check_controls.py tests/fixtures/controls_bad_missing_wrongmodel.json
expect_pass "healthy controls" python3 checks/check_controls.py tests/fixtures/controls_good.json

expect_fail "halves split by chunk not work" python3 checks/check_corpus.py tests/fixtures/corpus_bad_chunk_split.json
expect_fail "primary pair absent from slate" python3 checks/check_corpus.py tests/fixtures/corpus_bad_no_primary.json
expect_pass "healthy corpus" python3 checks/check_corpus.py tests/fixtures/corpus_good.json
exit $bad
