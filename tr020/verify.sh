#!/usr/bin/env bash
# TR-020 verify: exits nonzero unless the checkers can fail, the seal is
# intact and unread by the auditor, the measurement layer has proven it
# can see, the seeded gates hold, and the wild phase ran behind its guard.
set -u
cd "$(dirname "$0")"
fail=0

echo "== 0. Checker self-test: violating fixtures must be rejected =="
bash tests/test_checks.sh || fail=1

echo
echo "== 0b. Substrate determinism: sabotage caught red, traces byte-stable (D11) =="
python3 tests/test_substrate.py || fail=1

echo
echo "== 1. Seal: intact, and never referenced by the auditor (D6) =="
if [ ! -f seed_systems/GROUND_TRUTH.sealed.json ] || [ ! -f seed_systems/SEAL.sha256 ]; then
  echo "MISSING: sealed ground truth and/or SEAL.sha256"
  fail=1
else
  if shasum -a 256 -c seed_systems/SEAL.sha256 >/dev/null 2>&1 || \
     sha256sum -c seed_systems/SEAL.sha256 >/dev/null 2>&1; then
    echo "seal hash verified"
  else
    echo "SEAL BROKEN: GROUND_TRUTH.sealed.json does not match SEAL.sha256"
    fail=1
  fi
fi
if grep -rIl "GROUND_TRUTH" auditor/ deadwood_audit/ 2>/dev/null | grep -q .; then
  echo "SEAL VIOLATION: the audit engine references the sealed ground truth"
  fail=1
else
  echo "audit engine (deadwood_audit and the auditor shim) never references the seal"
fi

echo
echo "== 2. Measurement gates: fixtures human-ratified, judge and canonicalizer sighted (D3, D13) =="
python3 checks/check_ratification.py fixtures || fail=1
if [ -f results/measurement_gates.json ]; then
  python3 checks/check_measurement_gates.py results/measurement_gates.json || fail=1
else
  echo "MISSING: results/measurement_gates.json"; fail=1
fi

echo
echo "== 3. Seeded recovery gate and interaction KILL (D1, D2) =="
if [ -f results/seeded_recovery.json ]; then
  python3 checks/check_recovery.py results/seeded_recovery.json || fail=1
else
  echo "MISSING: results/seeded_recovery.json"; fail=1
fi

echo
echo "== 4. Negative controls: all-live, placebo, replication (D4, D7) =="
if [ -f results/seeded_controls.json ]; then
  python3 checks/check_controls.py results/seeded_controls.json || fail=1
else
  echo "MISSING: results/seeded_controls.json"; fail=1
fi

echo
echo "== 5. Wild phase behind its guard (D5) =="
wild=$(ls results/wild_*.json 2>/dev/null | head -1)
if [ -n "$wild" ]; then
  if python3 checks/check_recovery.py results/seeded_recovery.json >/dev/null 2>&1; then
    echo "wild results present with a passing seeded gate behind them"
  else
    echo "GUARD VIOLATION: wild results exist but the seeded gate does not pass"
    fail=1
  fi
else
  echo "MISSING: no wild-phase results yet"
  fail=1
fi

echo
echo "== 6. Surrogate: re-run certified, kappa gate (D23) =="
if [ -f results/surrogate.json ] && [ -f results/surrogate_cert.json ]; then
  python3 checks/check_surrogate.py results/surrogate.json results/surrogate_cert.json || fail=1
else
  echo "MISSING: results/surrogate.json and/or surrogate_cert.json"; fail=1
fi

echo
if [ "$fail" -ne 0 ]; then
  echo "VERIFY: FAIL"
  exit 1
fi
echo "VERIFY: PASS"
