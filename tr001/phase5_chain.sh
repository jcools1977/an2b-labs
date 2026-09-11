#!/bin/bash
# Phase 5: waits for the seed-2 retrain, writes the D26-inherited
# selection record, then runs each seed single post-selection eval batch
# (C3 headline + controls), then full verify.
cd ~/an2b-labs/tr001
while kill -0 26796 2>/dev/null; do sleep 120; done
echo "seed-2 chain done: $(tail -2 seed2.log | head -1)"
.venv/bin/python - <<PY
import json
dev = json.load(open("results/dev_M15_seed2.json"))
sel = {"seed": 2, "config_id": "M15", "dev_f1": dev["f1"],
       "inherited_from_seed": 1,
       "note": "config inherited from seed-1 selection per D26; retrained from scratch at seed 2"}
json.dump(sel, open("results/selection_seed2.json", "w"), indent=2)
print("selection_seed2:", sel)
PY
.venv/bin/python scripts/eval_config.py --config-id M15 --seed 1 --split eval && \
.venv/bin/python scripts/run_controls.py --seed 1 && \
.venv/bin/python scripts/eval_config.py --config-id M15 --seed 2 --split eval && \
.venv/bin/python scripts/run_controls.py --seed 2 && \
bash verify.sh; echo "FINAL VERIFY EXIT: $?"
echo PHASE5_DONE
