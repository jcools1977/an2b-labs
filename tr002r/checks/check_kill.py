#!/usr/bin/env python3
"""TR-002r KILL gate: the skyline itself fails on more than half of
all pairs (instruments cannot see alignment even with paired data).

Schema (results/kill.json):
{"skyline_pairs": {"<pair>": cosine, ...}, "killed": bool}
"""
import json
import sys

SKY_GATE = 0.80


def check(path):
    d = json.load(open(path))
    v = []
    pairs = d.get("skyline_pairs")
    if not pairs or d.get("killed") is None:
        v.append("kill results incomplete")
        return v
    failing = sum(1 for c in pairs.values() if c < SKY_GATE)
    should_kill = failing > len(pairs) / 2
    if bool(d["killed"]) != should_kill:
        v.append(f"killed flag {d['killed']} inconsistent "
                 f"({failing}/{len(pairs)} skylines below {SKY_GATE})")
    if should_kill:
        v.append(f"KILL: the supervised skyline fails on {failing} of "
                 f"{len(pairs)} pairs; instruments cannot see alignment, "
                 f"no unsupervised claim is tested")
    return v


def main():
    if len(sys.argv) != 2:
        return 2
    vs = check(sys.argv[1])
    for x in vs:
        print(f"VIOLATION [{sys.argv[1]}]: {x}")
    if not vs:
        print(f"KILL gate holds: {sys.argv[1]}")
    return 1 if vs else 0


if __name__ == "__main__":
    sys.exit(main())
