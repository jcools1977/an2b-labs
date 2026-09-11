#!/usr/bin/env bash
# Staleness supervisor for the legion sweep: relaunch if the process
# dies without SWEEP_DONE, or if sweep.log has been silent for more
# than 6 hours (a configuration on legion at R=2 takes under 4 hours;
# TR-002r D16: never kill a healthy long forward). Resumable per
# configuration. Usage: supervise_sweep.sh "<run_sweep args>"
cd "$(dirname "$0")/.."
ARGS="$1"
while true; do
  grep -q PIPELINE_DONE sweep.log 2>/dev/null && { echo "supervisor: complete $(date)" >> supervise.log; exit 0; }
  if ! pgrep -f "scripts/run_sweep.py" >/dev/null && ! pgrep -f "scripts/assemble_gates.py" >/dev/null; then
    n=$(grep -c "supervisor: (re)launched" supervise.log 2>/dev/null || echo 0)
    [ "$n" -ge 20 ] && { echo "supervisor: giving up after 20 relaunches $(date)" >> supervise.log; exit 1; }
    nohup bash -c ".venv/bin/python -u scripts/run_sweep.py $ARGS && .venv/bin/python -u scripts/assemble_gates.py && echo PIPELINE_DONE" >> sweep.log 2>&1 &
    echo "supervisor: (re)launched $(date)" >> supervise.log
    sleep 300
    continue
  fi
  latest=$(stat -f %m sweep.log 2>/dev/null || echo 0)
  if [ $(( $(date +%s) - latest )) -gt 21600 ]; then
    echo "supervisor: silent >6h, killing $(date)" >> supervise.log
    pkill -f "scripts/run_sweep.py"; sleep 10
  fi
  sleep 600
done
