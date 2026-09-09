#!/usr/bin/env python3
"""TR-006 screening (D10, D14): one-shot single-agent pass of each
model over seeded candidate items; an item is scored only if at most
one of the three models answers it correctly. 200 per family per
seed, disjoint across seeds by hash. Writes data/tasks_<seed>.json
and data/TASK_MANIFEST.json. Resumable per seed.
"""
import hashlib
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tasks import hotpot, puzzles  # noqa: E402
from workspace.council import Seats, run_config  # noqa: E402

TR = Path(__file__).resolve().parents[1]
SEEDS = [41, 43]
N_SCORED = 200
N_CAND = {"hotpot": 600, "puzzles": 400}


def one_shot(seats, items):
    """Each model alone, R=1, no buffer: the screening pass."""
    correct = {}
    for m in ("llama", "qwen", "gemma"):
        recs = run_config(seats, items, S=1, F=1, R=1, mode="single", seed=0, single_model=m)
        for it, r in zip(items, recs):
            ok = (puzzles.score(r["answer"], it) if it["family"] == "puzzles" else hotpot.score(r["answer"], it))
            correct.setdefault(it["id"], []).append(bool(ok))
    return correct


def main():
    seats = Seats()
    rows = hotpot.load()
    raw_sha = hashlib.sha256((TR / "data" / "raw" / "hotpot_distractor_validation.parquet").read_bytes()).hexdigest()
    used = set()
    manifest = {"raw_hotpot_sha256": raw_sha, "screening_rule": "at most one of three single agents correct",
                "families": 2, "seeds": {}, "cross_seed_overlap": 0}
    for seed in SEEDS:
        out = TR / "data" / f"tasks_{seed}.json"
        if out.exists():
            d = json.load(open(out))
            print(f"seed {seed}: screening already done", flush=True)
        else:
            rng = random.Random(f"screen:{seed}")
            idx = rng.sample(range(len(rows)), N_CAND["hotpot"])
            hot = [hotpot.format_item(rows[i], seed) for i in idx]
            hot = [h for h in hot if h["sha"] not in used]
            puz = [puzzles.generate(seed, i) for i in range(N_CAND["puzzles"])]
            part = TR / "data" / f"tasks_{seed}.partial.json"
            d = json.load(open(part)) if part.exists() else {"seed": seed, "families": {}}
            for fam, cands in (("hotpot", hot), ("puzzles", puz)):
                if fam in d["families"]:
                    print(f"seed {seed} {fam}: screening already done (partial checkpoint)", flush=True)
                    continue
                corr = one_shot(seats, cands)
                keep = [c for c in cands if sum(corr[c["id"]]) <= 1]
                scored = keep[:N_SCORED]
                d["families"][fam] = {"scored": scored, "screened_pool": len(cands), "kept": len(keep),
                                      "single_shot_correct": {c["id"]: corr[c["id"]] for c in cands}}
                print(f"seed {seed} {fam}: {len(cands)} candidates, {len(keep)} pass the screen, {len(scored)} scored", flush=True)
                json.dump(d, open(part, "w"))
            json.dump(d, open(out, "w"))
            part.unlink(missing_ok=True)
        for fam in ("hotpot", "puzzles"):
            for c in d["families"][fam]["scored"]:
                used.add(c["sha"])
        manifest["seeds"][str(seed)] = {
            "hotpot": {"scored": len(d["families"]["hotpot"]["scored"]), "screened_pool": d["families"]["hotpot"]["screened_pool"],
                       "screen_disjoint": True},
            "puzzles": {"scored": len(d["families"]["puzzles"]["scored"]), "screened_pool": d["families"]["puzzles"]["screened_pool"],
                        "unique_solutions": all(c.get("unique") for c in d["families"]["puzzles"]["scored"])}}
    a = {c["sha"] for f in json.load(open(TR / "data" / "tasks_41.json"))["families"].values() for c in f["scored"]}
    b = {c["sha"] for f in json.load(open(TR / "data" / "tasks_43.json"))["families"].values() for c in f["scored"]}
    manifest["cross_seed_overlap"] = len(a & b)
    json.dump(manifest, open(TR / "data" / "TASK_MANIFEST.json", "w"), indent=1)
    print("manifest written", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
