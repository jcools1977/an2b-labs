#!/usr/bin/env python3
"""TR-006 PASS gate (frozen text): regime model beats smooth monotone
fit by AIC >= 10 on BOTH task families, AND the unlimited-log
baseline underperforms the best bounded configuration, in each
family, at BOTH seeds. Schema (results/analysis.json):
{"seeds": {"41": {"hotpot": {"aic_smooth":..,"aic_regime":..,"aic_margin":..,
   "breakpoint_S":.., "best_bounded_acc":.., "best_bounded": {"S":..,"F":..},
   "unlimited_log_best_acc":.., "single_best_acc":..}, "puzzles": {...}}, "43": {...}}}
"""
import json
import sys

FAMILIES = ("hotpot", "puzzles")
SEEDS = ("41", "43")


def check(path):
    d = json.load(open(path))
    v = []
    for s in SEEDS:
        seed = d.get("seeds", {}).get(s)
        if seed is None:
            v.append(f"seed {s} missing")
            continue
        for f in FAMILIES:
            c = seed.get(f)
            if c is None:
                v.append(f"seed {s}: family {f} missing")
                continue
            if c.get("aic_margin", -1e9) < 10:
                v.append(f"seed {s} {f}: AIC margin {c.get('aic_margin')} < 10 (regime does not beat smooth)")
            if c.get("unlimited_log_best_acc", 1.0) >= c.get("best_bounded_acc", 0.0):
                v.append(f"seed {s} {f}: unlimited log {c.get('unlimited_log_best_acc')} >= best bounded {c.get('best_bounded_acc')} (bottleneck does not help)")
            for k in ("aic_smooth", "aic_regime", "breakpoint_S", "single_best_acc"):
                if k not in c:
                    v.append(f"seed {s} {f}: {k} absent")
    return v


def main():
    vs = check(sys.argv[1])
    for x in vs:
        print(f"VIOLATION [{sys.argv[1]}]: {x}")
    if not vs:
        print(f"PASS gates hold: {sys.argv[1]}")
    return 1 if vs else 0


if __name__ == "__main__":
    sys.exit(main())
