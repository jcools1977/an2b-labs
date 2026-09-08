#!/usr/bin/env python3
"""TR-003r KILL: C4 at 1,024 anchors retains < 0.50 of native Recall@5
on the primary pair in either direction, either seed. Schema
(results/kill.json): {"primary_pair":..., "anchors": 1024, "condition": "C4",
 "cells": {"41": {"bge->minilm": retention, ...}, "43": {...}}, "killed": bool}
Exit nonzero if the KILL fires or the flag disagrees with the cells.
"""
import json
import sys


def check(path):
    d = json.load(open(path))
    v = []
    if d.get("condition") != "C4" or d.get("anchors") != 1024:
        v.append("KILL must read on C4 at 1,024 anchors")
    fires = False
    for s in ("41", "43"):
        for dr, r in d.get("cells", {}).get(s, {}).items():
            if r < 0.50:
                fires = True
                v.append(f"KILL: seed {s} {dr} C4 retention {r} < 0.50; instrument cannot see the translation")
    if bool(d.get("killed")) != fires:
        v.append(f"killed flag {d.get('killed')} inconsistent with cells (fires={fires})")
    return v


def main():
    vs = check(sys.argv[1])
    for x in vs:
        print(f"VIOLATION [{sys.argv[1]}]: {x}")
    if not vs:
        print(f"KILL did not fire: {sys.argv[1]}")
    return 1 if vs else 0


if __name__ == "__main__":
    sys.exit(main())
