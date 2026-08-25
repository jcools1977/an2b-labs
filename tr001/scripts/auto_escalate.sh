#!/bin/bash
# Overnight escalation chain (D21), as armed on legion 2026-08-25.
# Waits for the running tier-3 sweep, records selection, and escalates to
# tier 4 only on select_config exit 2 (tier judged and failed, next tier
# missing). A bar-clear (exit 0) stops here: the held-out touch belongs to
# a session with the Phase 5 controls implemented.
cd "$(dirname "$0")/.."
while kill -0 "${TIER3_PID:?set TIER3_PID to the running tier-3 sweep pid}" 2>/dev/null; do sleep 300; done
echo "tier 3 sweep process ended: $(tail -1 phase4_tier3.log)"
.venv/bin/python scripts/select_config.py --seed 1
rc=$?
echo "select_config exit: $rc"
if [ $rc -eq 2 ]; then
  echo "escalating to tier 4 per D21"
  .venv/bin/python scripts/run_sweep.py --seed 1 --tier 4
  .venv/bin/python scripts/select_config.py --seed 1
  echo "post-tier-4 select exit: $?"
fi
