#!/usr/bin/env python3
"""TR-006 negative controls (D9 operationalization), per seed and family.
1 random salience: the control's AIC margin must be <= half the main
  margin or below 10 ("weaken or vanish"); evaluated only where the
  main margin is >= 10, else recorded vacuous.
2 frozen buffer: best accuracy over S at F=1 must be within 0.05 of
  the single best agent ("fall to near single-agent").
3 role shuffle: accuracy at the best bounded configuration must move
  by at least 0.03; if unchanged, specialization claims are WITHDRAWN
  (recorded as a violation so verify.sh shows it).
Schema (results/controls.json):
{"seeds": {"41": {"hotpot": {"main_aic_margin":.., "random_salience_aic_margin":..,
  "frozen_buffer_best_acc":.., "single_best_acc":.., "role_shuffle_acc":..,
  "main_best_bounded_acc":..}, "puzzles": {...}}, "43": {...}}}
"""
import json
import sys


def check(path):
    d = json.load(open(path))
    v = []
    for s in ("41", "43"):
        for f in ("hotpot", "puzzles"):
            c = d.get("seeds", {}).get(s, {}).get(f)
            if c is None:
                v.append(f"seed {s} {f}: control cell missing")
                continue
            for k in ("main_aic_margin", "random_salience_aic_margin", "frozen_buffer_best_acc",
                      "single_best_acc", "role_shuffle_acc", "main_best_bounded_acc"):
                if k not in c:
                    v.append(f"seed {s} {f}: {k} absent")
            if any(k not in c for k in ("main_aic_margin", "random_salience_aic_margin")):
                continue
            if c["main_aic_margin"] >= 10:
                if c["random_salience_aic_margin"] > 0.5 * c["main_aic_margin"] and c["random_salience_aic_margin"] >= 10:
                    v.append(f"seed {s} {f}: control 1: regime persists under random salience ({c['random_salience_aic_margin']} vs main {c['main_aic_margin']})")
            else:
                print(f"note: seed {s} {f}: control 1 vacuous (main margin {c['main_aic_margin']} < 10)")
            if c.get("frozen_buffer_best_acc", 1) > c.get("single_best_acc", 0) + 0.05:
                v.append(f"seed {s} {f}: control 2: frozen buffer {c.get('frozen_buffer_best_acc')} not near single agent {c.get('single_best_acc')}")
            if abs(c.get("role_shuffle_acc", 0) - c.get("main_best_bounded_acc", 0)) < 0.03:
                v.append(f"seed {s} {f}: control 3: role shuffle leaves accuracy unchanged ({c.get('role_shuffle_acc')} vs {c.get('main_best_bounded_acc')}); specialization claims WITHDRAWN")
    return v


def main():
    vs = check(sys.argv[1])
    for x in vs:
        print(f"VIOLATION [{sys.argv[1]}]: {x}")
    if not vs:
        print(f"controls hold: {sys.argv[1]}")
    return 1 if vs else 0


if __name__ == "__main__":
    sys.exit(main())
