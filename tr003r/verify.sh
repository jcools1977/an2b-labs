#!/usr/bin/env bash
# TR-003r verify: exits nonzero on any violation or missing leg.
set -u
cd "$(dirname "$0")"
PY="${PANEL_PY:-python3}"
fail=0
echo "== 0. Checker self-test (25 red-then-green legs) =="
bash tests/test_checks.sh || fail=1
echo; echo "== 0b. Anchor library certification (D11) =="
$PY tests/test_anchors.py || fail=1
echo; echo "== 0c. Grid plumbing smoke on a synthetic two-space corpus =="
$PY tests/test_grid_smoke.py || fail=1
echo; echo "== 1. Store integrity (control 4) =="
[ -f data/CORPUS_MANIFEST.json ] && $PY checks/check_corpus.py data/CORPUS_MANIFEST.json || { echo "MISSING manifest"; fail=1; }
echo; echo "== 2. PASS gates (three clauses, primary pair) =="
[ -f results/analysis.json ] && $PY checks/check_pass.py results/analysis.json || { echo "MISSING results/analysis.json"; fail=1; }
echo; echo "== 3. Controls 1-5 =="
[ -f results/controls.json ] && $PY checks/check_controls.py results/controls.json || { echo "MISSING results/controls.json"; fail=1; }
echo; echo "== 4. KILL (instrument sees the translation) =="
[ -f results/kill.json ] && $PY checks/check_kill.py results/kill.json || { echo "MISSING results/kill.json"; fail=1; }
echo; [ $fail -eq 0 ] && echo "VERIFY: all legs green" || echo "VERIFY: FAILING (exit 1)"
exit $fail
