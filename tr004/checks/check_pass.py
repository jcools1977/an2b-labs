#!/usr/bin/env python3
"""TR-004 PASS gates (protocol; D6, D7).

Schema (results/analysis.json):
{
  "estimators_direction_agree": bool,
  "pr": {"delta": f, "ci": [lo, hi]},
  "mle": {"delta": f, "ci": [lo, hi]},
  "after_controls": {"pr": {"delta": f, "ci": [lo, hi]},
                      "mle": {"delta": f, "ci": [lo, hi]}},
  "seeds_replicate": bool
}
"""
import json
import sys

DELTA_GATE = 0.2


def _gate(name, d, v):
    if d is None:
        v.append(f"{name} missing")
        return
    delta, ci = d.get("delta"), d.get("ci")
    if delta is None or ci is None:
        v.append(f"{name} missing delta or CI")
    else:
        if delta < DELTA_GATE:
            v.append(f"{name}: Cliff's delta {delta} < {DELTA_GATE}")
        if ci[0] <= 0 <= ci[1]:
            v.append(f"{name}: CI {ci} includes zero")


def check(path):
    d = json.load(open(path))
    v = []
    if not d.get("estimators_direction_agree"):
        v.append("LID estimators disagree on direction (FAIL clause)")
    _gate("pr", d.get("pr"), v)
    _gate("mle", d.get("mle"), v)
    ac = d.get("after_controls") or {}
    _gate("after-controls pr (D7)", ac.get("pr"), v)
    _gate("after-controls mle (D7)", ac.get("mle"), v)
    if not d.get("seeds_replicate"):
        v.append("gates do not hold at both bootstrap seeds (D6)")
    return v


def main():
    if len(sys.argv) != 2:
        return 2
    vs = check(sys.argv[1])
    for x in vs:
        print(f"VIOLATION [{sys.argv[1]}]: {x}")
    if not vs:
        print(f"PASS gates hold: {sys.argv[1]}")
    return 1 if vs else 0


if __name__ == "__main__":
    sys.exit(main())
