#!/usr/bin/env python3
"""Measurement-layer gates (DECISIONS D3): the judge and canonicalizer
must prove they can see before anything they measure counts. TR-020
audits for components that run but never matter; its own measurement
layer must not be an example.

Reads results/measurement_gates.json, exits nonzero unless:
- every degradation class scores >= 1.0 point worse than intact
  (judge scale 1-10)
- canonicalizer matches its hand-labeled fixtures 100%, n >= 20 per
  task family

Schema:
{
  "judge": {"intact_mean": float,
            "degraded_means": {"truncated": f, "wrong_entity": f, "off_topic": f}},
  "canonicalizer": {"families": {name: {"match_rate": f, "n": int}}}
}
"""
import json
import sys

JUDGE_MARGIN = 1.0
REQUIRED_DEGRADATIONS = {"truncated", "wrong_entity", "off_topic"}
CANON_MIN_N = 20


def check(path):
    violations = []
    d = json.load(open(path))

    j = d.get("judge", {})
    intact = j.get("intact_mean")
    degraded = j.get("degraded_means", {})
    if intact is None or not REQUIRED_DEGRADATIONS <= set(degraded):
        violations.append(f"judge results missing classes {REQUIRED_DEGRADATIONS - set(degraded)}")
    else:
        for cls in sorted(REQUIRED_DEGRADATIONS):
            sep = intact - degraded[cls]
            if sep < JUDGE_MARGIN:
                violations.append(
                    f"judge gate: '{cls}' degradation separated by only "
                    f"{sep:.2f} points (need >= {JUDGE_MARGIN}); a judge that "
                    f"cannot see planted damage is a dead module in the "
                    f"measurement layer"
                )

    fams = d.get("canonicalizer", {}).get("families", {})
    if not fams:
        violations.append("canonicalizer fixtures missing")
    for name, f in fams.items():
        if f.get("n", 0) < CANON_MIN_N:
            violations.append(
                f"canonicalizer gate: family '{name}' has n={f.get('n')} "
                f"fixtures (need >= {CANON_MIN_N})"
            )
        if f.get("match_rate") != 1.0:
            violations.append(
                f"canonicalizer gate: family '{name}' match rate "
                f"{f.get('match_rate')}, not 1.0 on hand-labeled pairs"
            )
    return violations


def main():
    if len(sys.argv) != 2:
        print("usage: check_measurement_gates.py <measurement_gates.json>", file=sys.stderr)
        return 2
    violations = check(sys.argv[1])
    for v in violations:
        print(f"VIOLATION [{sys.argv[1]}]: {v}")
    if not violations:
        print(f"measurement gates hold: {sys.argv[1]}")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
