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
exit $bad
