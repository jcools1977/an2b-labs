#!/usr/bin/env bash
# TR-001 verify: exits nonzero unless every negative control (protocol
# section 8) demonstrably holds on real results for both protocol seeds,
# and the checkers themselves pass their own red fixtures.
set -u
cd "$(dirname "$0")"
fail=0

echo "== 0. Checker self-test: violating fixtures must be rejected =="
bash tests/test_checks.sh || fail=1

echo
echo "== 1-3. Adapter controls: random init, shuffled pairing, ablation, compute match =="
for seed in 1 2; do
  f="results/controls_seed${seed}.json"
  if [ ! -f "$f" ]; then
    echo "MISSING: $f (controls must hold on both protocol seeds)"
    fail=1
  else
    python3 checks/check_controls.py "$f" || fail=1
  fi
done

echo
echo "== 4. Label leakage: eval passages absent from adapter training set =="
if [ ! -f data/train.jsonl ] || [ ! -f data/eval.jsonl ]; then
  echo "MISSING: data/train.jsonl and/or data/eval.jsonl"
  fail=1
else
  python3 checks/check_leakage.py data/train.jsonl data/eval.jsonl || fail=1
fi

echo
echo "== 5. Injection identity (Phase 2 gate: sabotage red, clean green) =="
if .venv/bin/python -c "import mlx.core" 2>/dev/null; then
  .venv/bin/python tests/test_injection_identity.py --self-test >/dev/null || {
    echo "INJECTION IDENTITY: FAIL (see results/injection_identity.json)"
    fail=1
  }
  grep -q '"violations": \[\]' results/injection_identity.json 2>/dev/null \
    && echo "injection identity holds (sabotage detected, clean identical)"
else
  echo "MISSING: MLX environment; identity gate can only verify on the experiment machine"
  fail=1
fi

echo
echo "== 6. Scorer parity with official SQuAD script (red variants must be caught) =="
python3 tests/test_scorer_parity.py --self-test || fail=1

echo
if [ "$fail" -ne 0 ]; then
  echo "VERIFY: FAIL"
  exit 1
fi
echo "VERIFY: PASS (all negative controls hold on both seeds)"
