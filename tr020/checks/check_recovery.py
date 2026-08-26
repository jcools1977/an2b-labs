#!/usr/bin/env python3
"""Seeded recovery gate (protocol Pass/Fail; DECISIONS D1, D2).

Reads results/seeded_recovery.json and exits nonzero unless:
- flagged-set precision AND recall >= 0.9 against the seal
  (flagged = verdict in {dead, redundant}; planted = expected in same)
- the D2 KILL condition is absent: <= 10% of planted-live components
  verdicted dead or redundant after pairwise correction

Schema:
{
  "seal_sha256": "...",
  "per_component": [
    {"system": s, "component": c,
     "verdict": "dead|redundant|live", "expected": "dead|redundant|live"}
  ]
}
"""
import json
import sys

GATE = 0.9
KILL_FALSE_FLAG_RATE = 0.10
FLAGGED = {"dead", "redundant"}


def check(path):
    violations = []
    data = json.load(open(path))
    rows = data.get("per_component", [])
    if not rows:
        return [f"{path}: no per-component rows; a gate over nothing proves nothing"]
    for r in rows:
        if r.get("verdict") not in {"dead", "redundant", "live"} or \
           r.get("expected") not in {"dead", "redundant", "live"}:
            return [f"{path}: malformed row {r}"]

    flagged = [r for r in rows if r["verdict"] in FLAGGED]
    planted = [r for r in rows if r["expected"] in FLAGGED]
    tp = sum(1 for r in flagged if r["expected"] in FLAGGED)
    precision = tp / len(flagged) if flagged else 1.0
    recall = tp / len(planted) if planted else 1.0

    if precision < GATE or recall < GATE:
        violations.append(
            f"recovery gate: precision {precision:.3f} / recall {recall:.3f} "
            f"(gate {GATE}); the auditor cannot be trusted on wild systems, "
            f"no wild claims may be made"
        )

    live = [r for r in rows if r["expected"] == "live"]
    false_flagged = sum(1 for r in live if r["verdict"] in FLAGGED)
    rate = false_flagged / len(live) if live else 0.0
    if rate > KILL_FALSE_FLAG_RATE:
        violations.append(
            f"KILL (D2): {rate:.1%} of planted-live components flagged "
            f"dead/redundant after pairwise correction (tolerance "
            f"{KILL_FALSE_FLAG_RATE:.0%}); interaction effects dominate, "
            f"publish the entanglement result"
        )
    return violations


def main():
    if len(sys.argv) != 2:
        print("usage: check_recovery.py <seeded_recovery.json>", file=sys.stderr)
        return 2
    violations = check(sys.argv[1])
    for v in violations:
        print(f"VIOLATION [{sys.argv[1]}]: {v}")
    if not violations:
        print(f"recovery gate holds: {sys.argv[1]}")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
