#!/usr/bin/env python3
"""TR-015 negative controls (protocol; D9).

Schema (results/controls.json):
{
  "label_shuffle": {"accuracy_ci": [lo, hi], "chance": f},
  "topic_only": {"accuracy": f, "reported": true},
  "translation": {"reported": bool, "note": str}
}
"""
import json
import sys


def check(path):
    d = json.load(open(path))
    v = []
    ls = d.get("label_shuffle", {})
    ci, ch = ls.get("accuracy_ci"), ls.get("chance")
    if not ci or ch is None:
        v.append("label-shuffle control missing")
    elif not (ci[0] <= ch <= ci[1]):
        v.append(f"control 1 (label shuffle): CI {ci} excludes chance {ch}; "
                 f"the attribution pipeline is leaking")
    if d.get("topic_only", {}).get("accuracy") is None:
        v.append("control 2 (topic-only leak) not reported")
    if not d.get("translation", {}).get("reported"):
        v.append("control 3 (translation stress) not reported (D9: reported, "
                 "never gated; absence is a violation, degradation is not)")
    return v


def main():
    if len(sys.argv) != 2:
        return 2
    vs = check(sys.argv[1])
    for x in vs:
        print(f"VIOLATION [{sys.argv[1]}]: {x}")
    if not vs:
        print(f"controls hold: {sys.argv[1]}")
    return 1 if vs else 0


if __name__ == "__main__":
    sys.exit(main())
