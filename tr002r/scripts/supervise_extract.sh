#!/usr/bin/env bash
# D15 staleness supervisor: run the extraction chain; if no output
# file (log or any checkpoint) has been touched for 10 minutes, kill
# and relaunch — checkpoints make the restart lose at most one
# interval. Exits when the chain prints ALL_SPACES_DONE.
cd "$(dirname "$0")/.."
V=../tr020/wild/.venv/bin/python
while ! grep -q ALL_SPACES_DONE extract.log 2>/dev/null; do
  if ! pgrep -f extract_spaces > /dev/null; then
    nohup sh -c "
$V -u scripts/extract_spaces.py bge && \
$V -u scripts/extract_spaces.py e5 8000 && \
$V -u scripts/extract_spaces.py minilm 8000 && \
$V -u scripts/extract_spaces.py llama4 16000 && \
$V -u scripts/extract_spaces.py qwen4 8000 && \
$V -u scripts/extract_spaces.py gemma4 8000 && \
$V -u scripts/extract_spaces.py llama8 8000 && \
echo ALL_SPACES_DONE" >> extract.log 2>&1 &
    echo "supervisor: (re)launched chain at $(date)" >> supervise.log
    sleep 120
  fi
  newest=$(find corpus_store/embeddings extract.log -newer /tmp/.sup_mark 2>/dev/null | head -1)
  touch -t "$(date -v-10M +%Y%m%d%H%M)" /tmp/.sup_mark 2>/dev/null || touch /tmp/.sup_mark
  latest=$(stat -f %m extract.log 2>/dev/null || echo 0)
  ck=$(ls -t corpus_store/embeddings/*.ckpt.npz 2>/dev/null | head -1)
  [ -n "$ck" ] && ckm=$(stat -f %m "$ck") || ckm=0
  now=$(date +%s)
  recent=$(( latest > ckm ? latest : ckm ))
  if [ $((now - recent)) -gt 600 ]; then
    echo "supervisor: stale $((now-recent))s, killing at $(date)" >> supervise.log
    pkill -f extract_spaces
    sleep 5
  fi
  sleep 60
done
echo "supervisor: chain complete at $(date)" >> supervise.log
