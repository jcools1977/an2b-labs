#!/usr/bin/env bash
# Wait until the given local time (HHMM, default 1700), then run the
# full pipeline under caffeinate (no idle or display sleep) with nohup,
# logging to sweep.log. Screening first, then the sweep, then the gates.
cd "$(dirname "$0")/.."
AT="${1:-1700}"
while [ "$(date +%H%M)" -lt "$AT" ]; do sleep 60; done
echo "launch $(date)" >> sweep.log
nohup caffeinate -is bash -c '
  .venv/bin/python -u scripts/screen.py && \
  .venv/bin/python -u scripts/run_sweep.py && \
  .venv/bin/python -u scripts/assemble_gates.py && echo PIPELINE_DONE' >> sweep.log 2>&1 &
echo "launched pid $! $(date)" >> sweep.log
