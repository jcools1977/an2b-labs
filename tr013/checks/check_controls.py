#!/usr/bin/env python3
"""TR-013 controls (D5). Schema (results/controls.json):
{"main_auc": x, "reversed_auc": x, "turn_index_withheld": true, "residualized_on_turn": true,
 "audit": {"agreement": x, "n": int, "auditor": str}}"""
import json
import sys


def check(path):
    d = json.load(open(path))
    v = []
    if d.get("main_auc", 0) - d.get("reversed_auc", 1) < 0.10:
        v.append(f"control 1: time-reversed series keeps predictive power ({d.get('reversed_auc')} vs {d.get('main_auc')})")
    if d.get("turn_index_withheld") is not True or d.get("residualized_on_turn") is not True:
        v.append("control 2: turn index not withheld and residualized")
    a = d.get("audit", {})
    if a.get("agreement", 0) < 0.90:
        v.append(f"control 3: label audit agreement {a.get('agreement')} < 0.90")
    if not a.get("auditor"):
        v.append("control 3: auditor not named")
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
