#!/usr/bin/env python3
"""TR-002r frozen run grid (D7, D13, D15, D17). Resumable: appends
one JSON line per run to results/grid.jsonl, skips runs already
recorded, runs only pairs whose embeddings exist, and reports what
remains. Gate files are assembled separately by assemble_gates.py
once the grid is complete.
"""
import json
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TR_ROOT))

from scripts.run_pair import eval_pair, wrong_model_top1  # noqa: E402

STORE = TR_ROOT / "corpus_store"
OUT = TR_ROOT / "results" / "grid.jsonl"
SPACES = ["bge", "e5", "minilm", "llama4", "qwen4", "gemma4"]
PRIMARY = ("bge", "llama4")


def build_runs():
    runs = []
    a, b = PRIMARY
    for direction in ((a, b), (b, a)):
        for n in (2000, 8000):
            runs.append({"a": direction[0], "b": direction[1], "n": n,
                         "seed": 41, "kind": "primary_curve"})
        for seed in (41, 43):
            runs.append({"a": direction[0], "b": direction[1], "n": 16000,
                         "seed": seed, "kind": "primary_gate"})
    for i, x in enumerate(SPACES):
        for y in SPACES[i + 1:]:
            if {x, y} == set(PRIMARY):
                continue
            runs.append({"a": x, "b": y, "n": 8000, "seed": 41,
                         "kind": "boundary"})
    runs.append({"a": "bge", "b": "llama8", "n": 8000, "seed": 41,
                 "kind": "precision_arm"})
    runs.append({"a": a, "b": b, "n": 16000, "seed": 41,
                 "kind": "shuffled_target", "shuffle": True})
    runs.append({"a": a, "b": b, "n": 16000, "seed": 41,
                 "kind": "wrong_model"})
    return runs


def have(space):
    return all((STORE / "embeddings" / f"{space}__{s}.npz").exists()
               for s in ("A", "B", "eval"))


def key(r):
    return (r["a"], r["b"], r["n"], r["seed"], r["kind"])


def main():
    OUT.parent.mkdir(exist_ok=True)
    done = set()
    if OUT.exists():
        for line in OUT.read_text().splitlines():
            d = json.loads(line)
            done.add((d["a"], d["b"], d["n"], d["seed"], d["kind"]))
    runs = build_runs()
    remaining = []
    for r in runs:
        if key(r) in done:
            continue
        if not (have(r["a"]) and have(r["b"])):
            remaining.append(r)
            continue
        print(f"running {r['kind']}: {r['a']}->{r['b']} n={r['n']} "
              f"seed={r['seed']}", flush=True)
        if r["kind"] == "wrong_model":
            res, T = eval_pair(r["a"], r["b"], r["n"], r["seed"])
            wm = wrong_model_top1(T, "e5", r["b"])
            rec = {**r, **res, "wrong_model_top1": wm}
        else:
            res, _ = eval_pair(r["a"], r["b"], r["n"], r["seed"],
                               shuffle_target=r.get("shuffle", False))
            rec = {**r, **res}
        with open(OUT, "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(f"  -> cosine {res['cosine']} top1 {res['top1']} "
              f"(sky {res['skyline_cosine']}/{res['skyline_top1']})",
              flush=True)
    if remaining:
        print(f"\nWAITING on embeddings for {len(remaining)} runs:",
              sorted({(r['a'], r['b']) for r in remaining}))
    else:
        print("\nGRID COMPLETE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
