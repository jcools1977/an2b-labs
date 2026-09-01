#!/usr/bin/env bash
# TR-004 verify: exits nonzero on any violation or missing leg.
set -u
cd "$(dirname "$0")"
fail=0

echo "== 0. Checker self-test =="
bash tests/test_checks.sh || fail=1

echo
echo "== 0b. Estimator certification (D5) =="
python3 tests/test_estimators.py || fail=1

echo
echo "== 1. Corpus integrity (D2, D10) =="
if [ -f data/CORPUS_MANIFEST.json ]; then
  python3 checks/check_corpus.py data/CORPUS_MANIFEST.json || fail=1
else
  echo "MISSING: data/CORPUS_MANIFEST.json"; fail=1
fi

echo
echo "== 2. PASS gates (D6, D7) =="
if [ -f results/analysis.json ]; then
  python3 checks/check_pass.py results/analysis.json || fail=1
else
  echo "MISSING: results/analysis.json"; fail=1
fi

echo
echo "== 3. Controls (D9) =="
if [ -f results/controls.json ]; then
  python3 checks/check_controls.py results/controls.json || fail=1
else
  echo "MISSING: results/controls.json"; fail=1
fi

echo
echo "== 4. KILL (D8) =="
if [ -f results/kill.json ]; then
  python3 checks/check_kill.py results/kill.json || fail=1
else
  echo "MISSING: results/kill.json"; fail=1
fi

echo
if [ $fail -eq 0 ]; then echo "VERIFY: PASS"; else echo "VERIFY: FAIL"; fi
exit $fail
