#!/usr/bin/env python3
"""TR-011 negative controls (protocol; DECISIONS D1, D3).

Reads results/controls.json:
1. Shuffled sentences must MOVE the sequential features (acl, lowfreq)
   by |delta| >= 0.3 across documents; if shuffling is invisible the
   features are bags of words in disguise.
2. Topic transplant: topic-label prediction from entropy features must
   sit at chance (accuracy CI includes the chance rate).
3. Same-text re-scoring: duplicates must have byte-identical series
   (D3: tolerance zero).

Schema:
{
  "shuffle": {"acl_delta": f, "lowfreq_delta": f},
  "topic": {"accuracy_ci": [lo, hi], "chance": f},
  "duplicates": {"byte_identical": bool}
}
"""
import json
import sys

SHUFFLE_GATE = 0.3


def check(path):
    d = json.load(open(path))
    violations = []

    sh = d.get("shuffle", {})
    for feat in ("acl_delta", "lowfreq_delta"):
        v = sh.get(feat)
        if v is None:
            violations.append(f"shuffle control missing {feat}")
        elif abs(v) < SHUFFLE_GATE:
            violations.append(
                f"control 1 (shuffle): {feat} moved only {v} "
                f"(gate {SHUFFLE_GATE}); the sequential features are bags "
                f"of words in disguise"
            )

    t = d.get("topic", {})
    ci, chance = t.get("accuracy_ci"), t.get("chance")
    if not ci or chance is None:
        violations.append("topic control missing")
    elif not (ci[0] <= chance <= ci[1]):
        violations.append(
            f"control 2 (topic): accuracy CI {ci} excludes chance {chance}; "
            f"the classifier is a topic sorter"
        )

    if not d.get("duplicates", {}).get("byte_identical", False):
        violations.append(
            "control 3 (duplicates): re-scored duplicates not byte-identical "
            "(D3 tolerance is zero); pipeline determinism is broken"
        )
    return violations


def main():
    if len(sys.argv) != 2:
        print("usage: check_controls.py <controls.json>", file=sys.stderr)
        return 2
    violations = check(sys.argv[1])
    for v in violations:
        print(f"VIOLATION [{sys.argv[1]}]: {v}")
    if not violations:
        print(f"controls hold: {sys.argv[1]}")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
