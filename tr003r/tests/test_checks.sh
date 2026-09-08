#!/usr/bin/env bash
# Checker self-test: every checker must REJECT its red fixtures and
# ACCEPT its green one. Extended leg by leg as checkers land.
set -u
cd "$(dirname "$0")/.."
bad=0
expect_fail() { desc="$1"; shift; if "$@" >/dev/null 2>&1; then echo "CHECKER BROKEN: accepted $desc"; bad=1; else echo "ok: rejected $desc"; fi; }
expect_pass() { desc="$1"; shift; if "$@" >/dev/null 2>&1; then echo "ok: accepted $desc"; else echo "CHECKER BROKEN: rejected $desc"; bad=1; fi; }

expect_fail "store/anchor overlap"                 python3 checks/check_corpus.py tests/fixtures/corpus_bad_overlap.json
expect_fail "gate read on medoid anchors (D4)"     python3 checks/check_corpus.py tests/fixtures/corpus_bad_medoid_gate.json
expect_fail "anchor grid not the frozen 64/256/1024" python3 checks/check_corpus.py tests/fixtures/corpus_bad_anchor_grid.json
expect_fail "store without sequence edges"         python3 checks/check_corpus.py tests/fixtures/corpus_bad_no_edges.json
expect_fail "primary pair not bge<->minilm"        python3 checks/check_corpus.py tests/fixtures/corpus_bad_pair.json
expect_pass "healthy store manifest"               python3 checks/check_corpus.py tests/fixtures/corpus_good.json

expect_fail "retention 0.79 in one direction (clause i)"   python3 checks/check_pass.py tests/fixtures/pass_bad_retention.json
expect_fail "provenance 0.89 (clause ii)"                  python3 checks/check_pass.py tests/fixtures/pass_bad_provenance.json
expect_fail "confident-wrong 0.06 (clause iii)"            python3 checks/check_pass.py tests/fixtures/pass_bad_confident_wrong.json
expect_fail "gate read on medoid anchors"                  python3 checks/check_pass.py tests/fixtures/pass_bad_medoid.json
expect_fail "gate read at 256 anchors"                     python3 checks/check_pass.py tests/fixtures/pass_bad_anchors.json
expect_fail "gate read on C4 instead of C3"                python3 checks/check_pass.py tests/fixtures/pass_bad_condition.json
expect_fail "seed 43 missing"                              python3 checks/check_pass.py tests/fixtures/pass_bad_seed_missing.json
expect_fail "native confident-wrong baseline absent"       python3 checks/check_pass.py tests/fixtures/pass_bad_no_baseline.json
expect_pass "healthy pass gates"                           python3 checks/check_pass.py tests/fixtures/pass_good.json

expect_fail "KILL firing (C4 retention 0.49)"              python3 checks/check_kill.py tests/fixtures/kill_bad_fires.json
expect_fail "killed flag inconsistent"                     python3 checks/check_kill.py tests/fixtures/kill_bad_inconsistent.json
expect_pass "instrument healthy"                           python3 checks/check_kill.py tests/fixtures/kill_good.json

expect_fail "scrambled anchors retaining retrieval"        python3 checks/check_controls.py tests/fixtures/controls_bad_scrambled.json
expect_fail "mismatched anchors not collapsing"            python3 checks/check_controls.py tests/fixtures/controls_bad_mismatched.json
expect_fail "random projection matching C3"                python3 checks/check_controls.py tests/fixtures/controls_bad_random_projection.json
expect_fail "disjointness not established"                 python3 checks/check_controls.py tests/fixtures/controls_bad_disjoint.json
expect_fail "primary space under the native floor"         python3 checks/check_controls.py tests/fixtures/controls_bad_native_floor.json
expect_fail "control arm missing"                          python3 checks/check_controls.py tests/fixtures/controls_bad_missing_arm.json
expect_pass "healthy controls"                             python3 checks/check_controls.py tests/fixtures/controls_good.json
exit $bad
