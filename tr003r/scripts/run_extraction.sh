#!/usr/bin/env bash
# Extraction chain for all six spaces, resumable per space; writes
# extract.log. Encoders first (minutes), then the 4-bit decoders.
cd "$(dirname "$0")/.."
V=$HOME/an2b-labs/tr020/wild/.venv/bin/python
for s in bge e5 minilm qwen4 llama4 gemma4; do
  $V -u scripts/extract.py $s || { echo "FAILED $s"; exit 1; }
done
echo ALL_SPACES_DONE
