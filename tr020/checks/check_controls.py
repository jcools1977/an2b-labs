#!/usr/bin/env python3
"""Negative controls 1-3 for TR-020 (protocol; DECISIONS D4, D7).

Reads results/seeded_controls.json and exits nonzero on any violation:
1. All-live system: zero components flagged (false-positive floor).
2. Placebo mask: paraphrasing a component's own output is inert
   (answer-change rate < 5%, quality-delta CI includes zero).
3. Probe-half replication: three-class verdict identical on both
   disjoint halves for every component (agreement == 1.0, D7).

Schema:
{
  "all_live_flags": int,
  "placebo": {"answer_change_rate": float, "quality_ci": [lo, hi]},
  "replication_agreement": float
}
"""
import json
import sys

PLACEBO_RATE_MAX = 0.05


def check(path):
    violations = []
    d = json.load(open(path))

    flags = d.get("all_live_flags")
    if not isinstance(flags, int):
        violations.append("all_live_flags missing")
    elif flags != 0:
        violations.append(
            f"control 1 (all-live): {flags} component(s) flagged in a system "
            f"with no plants; the false-positive floor is not zero"
        )

    p = d.get("placebo", {})
    rate, ci = p.get("answer_change_rate"), p.get("quality_ci")
    if rate is None or not ci or len(ci) != 2:
        violations.append("placebo results missing or malformed")
    else:
        if rate >= PLACEBO_RATE_MAX:
            violations.append(
                f"control 2 (placebo): paraphrase changed {rate:.1%} of answers "
                f"(limit {PLACEBO_RATE_MAX:.0%}); the masking operation is not inert"
            )
        if not (ci[0] <= 0.0 <= ci[1]):
            violations.append(
                f"control 2 (placebo): quality-delta CI {ci} excludes zero; "
                f"the masking operation is not inert"
            )

    agr = d.get("replication_agreement")
    if agr is None:
        violations.append("replication_agreement missing")
    elif agr != 1.0:
        violations.append(
            f"control 3 (replication): verdict agreement across probe halves "
            f"is {agr:.3f}, not 1.0 (D7: identical on both halves, per component)"
        )
    return violations


def main():
    if len(sys.argv) != 2:
        print("usage: check_controls.py <seeded_controls.json>", file=sys.stderr)
        return 2
    violations = check(sys.argv[1])
    for v in violations:
        print(f"VIOLATION [{sys.argv[1]}]: {v}")
    if not violations:
        print(f"controls hold: {sys.argv[1]}")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
