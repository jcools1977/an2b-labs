#!/usr/bin/env bash
# Staleness supervisor for the extraction chain (TR-002r D16 lesson:
# checkpoint every 500 texts, kill only after 15 minutes of silence,
# never on a healthy long forward). Relaunches run_extraction.sh,
# which resumes per space from its checkpoint. Exits on ALL_SPACES_DONE
# or on a FAILED line.
cd "$(dirname "$0")/.."
LOG=extract.log
while true; do
  grep -q ALL_SPACES_DONE $LOG 2>/dev/null && { echo "supervisor: complete $(date)" >> supervise.log; exit 0; }
  grep -q '^FAILED' $LOG 2>/dev/null && { echo "supervisor: chain FAILED $(date)" >> supervise.log; exit 1; }
  if ! pgrep -f "scripts/extract.py" >/dev/null; then
    nohup bash scripts/run_extraction.sh >> $LOG 2>&1 &
    echo "supervisor: (re)launched $(date)" >> supervise.log
    sleep 120
    continue
  fi
  latest=$(stat -f %m $LOG 2>/dev/null || echo 0)
  ck=$(ls -t corpus_store/emb/*.ckpt.npz 2>/dev/null | head -1)
  [ -n "$ck" ] && ckm=$(stat -f %m "$ck") || ckm=0
  recent=$(( latest > ckm ? latest : ckm ))
  if [ $(( $(date +%s) - recent )) -gt 900 ]; then
    echo "supervisor: stale >15 min, killing $(date)" >> supervise.log
    pkill -f "scripts/extract.py"; sleep 5
  fi
  sleep 60
done
