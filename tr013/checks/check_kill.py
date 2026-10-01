#!/usr/bin/env python3
"""TR-013 KILL: indicators fire equally often in matched controls
(false-alarm parity, D5: within 0.05 for all three indicators).
Schema (results/kill.json): {"firing": {"variance": {"collapse": r, "control": r},
 "lag1_autocorr": {...}, "distinct2": {...}}, "killed": bool}"""
import json
import sys


def check(path):
    d = json.load(open(path))
    v = []
    f = d.get("firing", {})
    parity = []
    for ind in ("variance", "lag1_autocorr", "distinct2"):
        c = f.get(ind)
        if c is None:
            v.append(f"firing rates for {ind} missing")
            continue
        parity.append(abs(c["collapse"] - c["control"]) <= 0.05)
    fires = bool(parity) and all(parity)
    if fires:
        v.append("KILL: every indicator fires at parity in matched controls; no signal, just drift")
    if bool(d.get("killed")) != fires:
        v.append(f"killed flag {d.get('killed')} inconsistent with rates (fires={fires})")
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
