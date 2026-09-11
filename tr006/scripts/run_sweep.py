#!/usr/bin/env python3
"""TR-006 sweep orchestrator: the frozen grid and nothing outside it.
Per seed (41 first, fully, then 43; D15): main grid (S x F), single
baselines (three models), unlimited log (each F), then the three
controls at F=1 across S. Resumable per configuration and per item:
results/raw/<seed>/<config>.jsonl, one line per item.
Usage: run_sweep.py [--limit N] [--only main|baselines|controls]
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tasks import hotpot, puzzles  # noqa: E402
from workspace.council import Seats, run_config  # noqa: E402

TR = Path(__file__).resolve().parents[1]
S_GRID = [1, 2, 4, 8, 16, 32]
F_GRID = [1, 2, 4]
R = 4
SEEDS = [41, 43]


def plan():
    cfgs = []
    for S in S_GRID:
        for F in F_GRID:
            cfgs.append(("main", dict(S=S, F=F, mode="main")))
    for m in ("llama", "qwen", "gemma"):
        cfgs.append(("baselines", dict(S=1, F=1, mode="single", single_model=m)))
    for F in F_GRID:
        cfgs.append(("baselines", dict(S=1, F=F, mode="unlimited")))
    for mode in ("random_salience", "frozen", "role_shuffle"):
        for S in S_GRID:
            cfgs.append(("controls", dict(S=S, F=1, mode=mode)))
    return cfgs


def cfg_name(c):
    return f"{c['mode']}_S{c['S']}_F{c['F']}" + (f"_{c['single_model']}" if c.get("single_model") else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--only", default=None)
    ap.add_argument("--seeds", default="41,43")
    ap.add_argument("--tasks-dir", default=str(TR / "data"))
    ap.add_argument("--raw-dir", default=str(TR / "results" / "raw"))
    ap.add_argument("--R", type=int, default=R)
    ap.add_argument("--max-resident", type=int, default=3)
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--block", default="8", help="items per lockstep block, or all")
    a = ap.parse_args()
    seats = Seats(max_resident=a.max_resident)
    t_start = time.time()
    print(f"sweep settings: R={a.R} max_resident={a.max_resident} cache={not a.no_cache} block={a.block}", flush=True)
    for seed in [int(s) for s in a.seeds.split(",")]:
        tasks = json.load(open(Path(a.tasks_dir) / f"tasks_{seed}.json"))
        for stage, c in plan():
            if a.only and stage != a.only:
                continue
            for fam in ("hotpot", "puzzles"):
                items = tasks["families"][fam]["scored"]
                if a.limit:
                    items = items[:a.limit]
                out = Path(a.raw_dir) / str(seed) / f"{fam}__{cfg_name(c)}.jsonl"
                out.parent.mkdir(parents=True, exist_ok=True)
                done = set()
                if out.exists():
                    done = {json.loads(l)["id"] for l in open(out) if l.strip()}
                todo = [it for it in items if it["id"] not in done]
                if not todo:
                    continue
                t0 = time.time()
                blk = len(todo) if a.block == "all" else int(a.block)
                recs = run_config(seats, todo, S=c["S"], F=c["F"], R=a.R, mode=c["mode"], seed=seed,
                                  single_model=c.get("single_model"), block=max(1, blk), use_cache=not a.no_cache)
                with open(out, "a") as fh:
                    for it, r in zip(todo, recs):
                        r["correct"] = bool(puzzles.score(r["answer"], it) if fam == "puzzles" else hotpot.score(r["answer"], it))
                        r["seed"], r["config"], r["stage"] = seed, cfg_name(c), stage
                        fh.write(json.dumps(r) + "\n")
                acc = sum(r["correct"] for r in recs) / len(recs)
                print(f"[{time.strftime('%H:%M:%S')}] seed {seed} {stage:9} {fam:7} {cfg_name(c):28} "
                      f"n={len(todo)} acc={acc:.3f} {time.time()-t0:.0f}s (elapsed {(time.time()-t_start)/3600:.2f}h)", flush=True)
    print("SWEEP_DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
