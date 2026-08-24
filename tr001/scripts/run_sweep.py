#!/usr/bin/env python3
"""Sweep orchestrator (DECISIONS D19-D21): trains and dev-evaluates every
config in one tier, in declared order, one subprocess per step so model
memory is fully released between configs. Skips work that is already done
(sweep_log entry + adapter file for training; dev result file for eval),
so re-running after an interruption resumes cleanly.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.gates import TR_ROOT  # noqa: E402


def trained(config_id, seed):
    log = TR_ROOT / "results" / "sweep_log.jsonl"
    if not log.exists():
        return False
    done = any(
        (e["config_id"], e["seed"]) == (config_id, seed)
        for e in map(json.loads, open(log))
    )
    return done and (TR_ROOT / "adapters" / f"{config_id}_seed{seed}.safetensors").exists()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--tier", type=int, required=True)
    args = ap.parse_args()

    sweep = json.load(open(TR_ROOT / "configs" / "sweep.json"))
    configs = [c for c in sweep["configs"] if c["tier"] == args.tier]
    if not configs:
        raise SystemExit(f"no configs in tier {args.tier}")

    for c in configs:
        tag = f"{c['id']}_seed{args.seed}"
        if not trained(c["id"], args.seed):
            print(f"=== training {tag} ===", flush=True)
            subprocess.run(
                [sys.executable, str(TR_ROOT / "scripts" / "train_adapter.py"),
                 "--config-id", c["id"], "--seed", str(args.seed)],
                check=True,
            )
        else:
            print(f"=== {tag} already trained ===", flush=True)
        dev_result = TR_ROOT / "results" / f"dev_{c['id']}_seed{args.seed}.json"
        if not dev_result.exists():
            print(f"=== dev eval {tag} ===", flush=True)
            subprocess.run(
                [sys.executable, str(TR_ROOT / "scripts" / "eval_config.py"),
                 "--config-id", c["id"], "--seed", str(args.seed), "--split", "dev"],
                check=True,
            )

    print(f"tier {args.tier} complete for seed {args.seed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
