#!/usr/bin/env bash
# Negative controls for TR-020's checkers: every violating fixture must be
# rejected and every healthy one accepted, before any mechanism exists.
set -u
cd "$(dirname "$0")/.."
bad=0

expect_fail() {
  desc="$1"; shift
  if "$@" >/dev/null 2>&1; then echo "CHECKER BROKEN: accepted $desc"; bad=1
  else echo "ok: rejected $desc"; fi
}
expect_pass() {
  desc="$1"; shift
  if "$@" >/dev/null 2>&1; then echo "ok: accepted $desc"
  else echo "CHECKER BROKEN: rejected $desc"; bad=1; fi
}

expect_fail "recovery below the 0.9 gate" \
  python3 checks/check_recovery.py tests/fixtures/recovery_bad_gate.json
expect_fail "interaction KILL (12.5% live falsely flagged)" \
  python3 checks/check_recovery.py tests/fixtures/recovery_bad_kill.json
expect_pass "clean recovery with redundant duplicates correctly flagged" \
  python3 checks/check_recovery.py tests/fixtures/recovery_good.json

expect_fail "flags on the all-live system" \
  python3 checks/check_controls.py tests/fixtures/controls_bad_alllive.json
expect_fail "non-inert placebo mask" \
  python3 checks/check_controls.py tests/fixtures/controls_bad_placebo.json
expect_fail "verdicts flipping between probe halves" \
  python3 checks/check_controls.py tests/fixtures/controls_bad_replication.json
expect_pass "healthy controls" \
  python3 checks/check_controls.py tests/fixtures/controls_good.json

# Ratification gate (D13): tested against temp copies of the real fixtures.
RATTMP=$(mktemp -d)
cp fixtures/canon_pairs.jsonl fixtures/judge_damage.jsonl "$RATTMP/"
expect_fail "unratified fixtures (no RATIFICATION.json)" \
  python3 checks/check_ratification.py "$RATTMP"
python3 - "$RATTMP" <<'PYEOF'
import hashlib, json, sys
from pathlib import Path
d = Path(sys.argv[1])
json.dump({"ratified_by": "test-human", "date": "2026-01-01", "sha256": {
    n: hashlib.sha256((d / n).read_bytes()).hexdigest()
    for n in ("canon_pairs.jsonl", "judge_damage.jsonl")}},
    open(d / "RATIFICATION.json", "w"))
PYEOF
expect_pass "ratified fixtures with matching hashes" \
  python3 checks/check_ratification.py "$RATTMP"
printf '{"family":"text","a":"x","b":"x","label":"no-change"}\n' >> "$RATTMP/canon_pairs.jsonl"
expect_fail "post-ratification fixture edit (hash mismatch)" \
  python3 checks/check_ratification.py "$RATTMP"
rm -rf "$RATTMP"

expect_fail "judge blind to wrong-entity damage" \
  python3 checks/check_measurement_gates.py tests/fixtures/gates_bad_judge.json
expect_fail "canonicalizer missing hand-labeled pairs" \
  python3 checks/check_measurement_gates.py tests/fixtures/gates_bad_canon.json
expect_pass "healthy measurement gates" \
  python3 checks/check_measurement_gates.py tests/fixtures/gates_good.json

exit $bad
