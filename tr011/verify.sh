#!/usr/bin/env bash
# TR-011 verify: exits nonzero unless the checkers can fail, the KILL
# instrument is certified, the memorization audit ran before analysis,
# and every gate holds on real results.
set -u
cd "$(dirname "$0")"
fail=0

echo "== 0. Checker self-test: violating fixtures must be rejected =="
bash tests/test_checks.sh || fail=1

echo
echo "== 0b. Residualizer bite-proof: planted signals behave (D5) =="
python3 tests/test_residualizer.py || fail=1

echo
echo "== 1. Corpora integrity: manifests, dedup, splits committed (D9) =="
if [ -f data/CORPUS_MANIFEST.json ]; then
  python3 checks/check_corpora.py data/CORPUS_MANIFEST.json || fail=1
else
  echo "MISSING: data/CORPUS_MANIFEST.json"; fail=1
fi

echo
echo "== 2. Memorization audit: ran, before analysis (D7) =="
if [ -f results/memorization_audit.json ]; then
  echo "audit present"
else
  echo "MISSING: results/memorization_audit.json"; fail=1
fi

echo
echo "== 3. PASS gates: qualified features, sign agreement, AUC (D2, D6, D7) =="
if [ -f results/analysis.json ]; then
  python3 checks/check_pass.py results/analysis.json || fail=1
else
  echo "MISSING: results/analysis.json"; fail=1
fi

echo
echo "== 4. Negative controls: shuffle, topic, duplicates (D1, D3) =="
if [ -f results/controls.json ]; then
  python3 checks/check_controls.py results/controls.json || fail=1
else
  echo "MISSING: results/controls.json"; fail=1
fi

echo
echo "== 5. KILL: certified residualizer, length control (D4, D5) =="
if [ -f results/kill.json ]; then
  python3 checks/check_kill.py results/kill.json || fail=1
else
  echo "MISSING: results/kill.json"; fail=1
fi

echo
if [ "$fail" -ne 0 ]; then
  echo "VERIFY: FAIL"
  exit 1
fi
echo "VERIFY: PASS"
