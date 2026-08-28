#!/usr/bin/env python3
"""TR-011 KILL gate (protocol; DECISIONS D4, D5).

Reads results/kill.json and exits nonzero if:
- the residualizer bite-proof is not green (a KILL verdict from an
  uncertified residualizer is not a measurement, D5), or
- the KILL fired (PASS conditions do not survive length
  residualization), reported with the pre-registered consequence:
  publish the length-detector result.

Schema:
{
  "residualizer_biteproof": {"length_collapse": bool, "signal_survives": bool},
  "killed": bool,
  "auc_residualized": f,
  "qualifying_features_residualized": int
}
"""
import json
import sys


def check(path):
    d = json.load(open(path))
    violations = []
    bp = d.get("residualizer_biteproof", {})
    if not bp.get("length_collapse", False):
        violations.append(
            "D5 bite-proof: planted pure-length signal did NOT collapse "
            "under residualization; the KILL instrument cannot be trusted"
        )
    if not bp.get("signal_survives", False):
        violations.append(
            "D5 bite-proof: planted orthogonal entropy signal did NOT "
            "survive residualization; the residualizer over-corrects and "
            "can fake a KILL"
        )
    if d.get("killed", None) is None:
        violations.append("killed verdict missing")
    elif d["killed"]:
        violations.append(
            f"KILL (D4): PASS conditions do not survive length "
            f"residualization (residualized AUC {d.get('auc_residualized')}, "
            f"qualifying features {d.get('qualifying_features_residualized')}); "
            f"the signal was a length detector, publish that result"
        )
    return violations


def main():
    if len(sys.argv) != 2:
        print("usage: check_kill.py <kill.json>", file=sys.stderr)
        return 2
    violations = check(sys.argv[1])
    for v in violations:
        print(f"VIOLATION [{sys.argv[1]}]: {v}")
    if not violations:
        print(f"KILL gate holds (instrument certified, no kill): {sys.argv[1]}")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
