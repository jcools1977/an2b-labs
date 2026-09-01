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
    # D21 closure: every chunk size's CI is consumed; which-size is
    # never a choice. Absence of the per-size CIs is itself a violation.
    per = ls.get("per_size_ci")
    if not per:
        v.append("control 1 (label shuffle): per-size CIs absent; the "
                 "checker must see every chunk size (D21)")
    else:
        for size, sci in sorted(per.items()):
            if not (sci[0] <= ch <= sci[1]):
                v.append(f"control 1 (label shuffle): size {size} CI {sci} "
                         f"excludes chance {ch}; the attribution pipeline "
                         f"is leaking (D21: all sizes must pass)")
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
