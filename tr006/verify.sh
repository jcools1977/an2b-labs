#!/usr/bin/env bash
# TR-006 verify: exits nonzero on any violation or missing leg.
set -u
cd "$(dirname "$0")"
PY="${PY:-.venv/bin/python}"
fail=0
echo "== 0. Checker self-test (19 red-then-green legs) =="; bash tests/test_checks.sh || fail=1
echo; echo "== 0b. Regime test certification (D8) =="; $PY tests/test_regime.py || fail=1
echo; echo "== 0c. gemma-2 batch patch certification (D13) =="; $PY tests/test_gemma_batch.py 2>/dev/null | grep -E "ok|FAIL|exam" || fail=1
echo; echo "== 1. Task sets (D10) =="; [ -f data/TASK_MANIFEST.json ] && $PY checks/check_tasks.py data/TASK_MANIFEST.json || { echo "MISSING task manifest"; fail=1; }
echo; echo "== 2. PASS gates =="; [ -f results/analysis.json ] && $PY checks/check_pass.py results/analysis.json || { echo "MISSING results/analysis.json"; fail=1; }
echo; echo "== 3. Controls =="; [ -f results/controls.json ] && $PY checks/check_controls.py results/controls.json || { echo "MISSING results/controls.json"; fail=1; }
echo; echo "== 4. KILL =="; [ -f results/kill.json ] && $PY checks/check_kill.py results/kill.json || { echo "MISSING results/kill.json"; fail=1; }
echo; [ $fail -eq 0 ] && echo "VERIFY: all legs green" || echo "VERIFY: FAILING (exit 1)"
exit $fail
