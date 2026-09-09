#!/usr/bin/env python3
"""TR-006 KILL: regime location not stable across the two task
families. Operationalized (D8): evaluated only where both families
show a regime (AIC margin >= 10); the breakpoints must lie within one
grid step (|log2 S_a - log2 S_b| <= 1) at each seed. Schema
(results/kill.json): {"seeds": {"41": {"hotpot": {"aic_margin":..,"breakpoint_S":..},
 "puzzles": {...}}, "43": {...}}, "killed": bool}
"""
import json
import math
import sys


def check(path):
    d = json.load(open(path))
    v = []
    fires = False
    for s in ("41", "43"):
        seed = d.get("seeds", {}).get(s, {})
        h, p = seed.get("hotpot"), seed.get("puzzles")
        if not h or not p:
            v.append(f"seed {s}: family cell missing")
            continue
        if h["aic_margin"] >= 10 and p["aic_margin"] >= 10:
            gap = abs(math.log2(h["breakpoint_S"]) - math.log2(p["breakpoint_S"]))
            if gap > 1:
                fires = True
                v.append(f"KILL: seed {s} breakpoints S={h['breakpoint_S']} (hotpot) vs S={p['breakpoint_S']} (puzzles), {gap:.0f} grid steps apart")
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
