#!/usr/bin/env python3
"""TR-006 task-set gate (D10). Schema (data/TASK_MANIFEST.json):
{"raw_hotpot_sha256": str, "screening_rule": "at most one of three single agents correct",
 "seeds": {"41": {"hotpot": {"scored": 200, "screened_pool": int, "screen_disjoint": true},
                  "puzzles": {"scored": 200, "unique_solutions": true, "screened_pool": int}}, "43": {...}},
 "cross_seed_overlap": 0, "families": 2}
"""
import json
import sys


def check(path):
    d = json.load(open(path))
    v = []
    if d.get("families") != 2:
        v.append("two task families required")
    if not d.get("raw_hotpot_sha256"):
        v.append("raw data hash absent")
    if d.get("screening_rule") != "at most one of three single agents correct":
        v.append("screening rule is not the frozen D10 rule")
    for s in ("41", "43"):
        seed = d.get("seeds", {}).get(s, {})
        for f in ("hotpot", "puzzles"):
            c = seed.get(f, {})
            if c.get("scored") != 200:
                v.append(f"seed {s} {f}: {c.get('scored')} scored items, protocol says 200")
            if c.get("screened_pool", 0) < 200:
                v.append(f"seed {s} {f}: screened pool smaller than the scored set")
        if seed.get("hotpot", {}).get("screen_disjoint") is not True:
            v.append(f"seed {s}: hotpot screening not disjoint from scoring by hash")
        if seed.get("puzzles", {}).get("unique_solutions") is not True:
            v.append(f"seed {s}: puzzles without verified unique solutions")
    if d.get("cross_seed_overlap", 1) != 0:
        v.append(f"scored items overlap across seeds: {d.get('cross_seed_overlap')}")
    return v


def main():
    vs = check(sys.argv[1])
    for x in vs:
        print(f"VIOLATION [{sys.argv[1]}]: {x}")
    if not vs:
        print(f"task sets hold: {sys.argv[1]}")
    return 1 if vs else 0


if __name__ == "__main__":
    sys.exit(main())
