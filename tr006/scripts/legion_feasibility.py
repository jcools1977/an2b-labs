#!/usr/bin/env python3
"""Legion feasibility measurement (D19): one model resident at a time,
no prefix cache, all items in lockstep; time 16 real items per family
through the full council (S=4, F=1, R=4, main) and report seconds per
item, loads, and load seconds. No scored data is written.
Usage: legion_feasibility.py [--n 16] [--R 4]"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mlx.core as mx  # noqa: E402
from tasks import hotpot, puzzles  # noqa: E402
from workspace.council import Seats, run_config  # noqa: E402

TR = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=16)
    ap.add_argument("--R", type=int, default=4)
    a = ap.parse_args()
    seats = Seats(max_resident=1)
    d = json.load(open(TR / "data" / "tasks_41.json"))
    out = {}
    for fam in ("hotpot", "puzzles"):
        items = d["families"][fam]["scored"][:a.n]
        seats.n_loads, seats.load_seconds = 0, 0.0
        mx.reset_peak_memory()
        t0 = time.time()
        recs = run_config(seats, items, S=4, F=1, R=a.R, mode="main", seed=41, block=len(items), use_cache=False)
        dt = time.time() - t0
        gens = sum(r["n_items_submitted"] for r in recs) + len(items)
        acc = sum((puzzles.score(r["answer"], {"answer": r["gold"]}) if fam == "puzzles" else hotpot.exact_match(r["answer"], r["gold"])) for r in recs) / len(items)
        out[fam] = {"n": len(items), "R": a.R, "seconds": dt, "per_item": dt / len(items), "per_generation": dt / gens,
                    "loads": seats.n_loads, "load_seconds": seats.load_seconds, "peak_gb": mx.get_peak_memory() / 1e9, "acc": acc,
                    "parse_fail": sum(r["n_parse_fail"] for r in recs)}
        print(f"{fam:7} n={len(items)} R={a.R}: {dt:.0f}s = {dt/len(items):.1f}s/item, {dt/gens:.2f}s/gen; "
              f"{seats.n_loads} loads {seats.load_seconds:.0f}s; peak {mx.get_peak_memory()/1e9:.1f} GB; acc {acc:.2f}", flush=True)
    per_point_h = (out["hotpot"]["per_item"] + out["puzzles"]["per_item"]) * 200 / 3600
    out["projection"] = {"hours_per_SF_point": per_point_h, "hours_main_grid_per_seed": per_point_h * 18,
                         "hours_per_seed_all_stages": per_point_h * (18 + 18) + per_point_h * 6 * 0.6}
    print("projection:", json.dumps(out["projection"]), flush=True)
    (TR / "results").mkdir(exist_ok=True)
    json.dump(out, open(TR / "results" / f"legion_feasibility_R{a.R}.json", "w"), indent=1)
    print("FEASIBILITY_DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
