#!/usr/bin/env python3
"""Surrogate gate (protocol PASS line; D23).

Exits nonzero unless the re-run certificate is green (byte-identical
passes, persisted change rates exactly reproduced) AND the primary
kappa (dead-vs-not, thresholds frozen in D23) is >= 0.7. A kappa miss
is the pre-registered SPLIT verdict: ablation certified, surrogate not
validated, and this leg red for that stated reason.

Usage: check_surrogate.py <surrogate.json> <surrogate_cert.json>
"""
import json
import sys

KAPPA_GATE = 0.7


def check(surrogate_path, cert_path):
    violations = []
    cert = json.load(open(cert_path))
    if not cert.get("byte_identical"):
        violations.append("re-run certificate: passes not byte-identical (D23)")
    for sid, v in cert.get("per_system", {}).items():
        if not v.get("match"):
            violations.append(
                f"re-run certificate: {sid}/{v.get('component')} change rate "
                f"{v.get('recomputed')} != persisted {v.get('persisted')} (D23)"
            )
    s = json.load(open(surrogate_path))
    k = s.get("kappa_primary_dead_vs_not")
    if not isinstance(k, (int, float)):
        violations.append("kappa_primary missing")
    elif k < KAPPA_GATE:
        violations.append(
            f"surrogate kappa {k} < {KAPPA_GATE}: per D23 the verdict is a "
            f"SPLIT (ablation certified, surrogate not validated); this leg "
            f"is red for that pre-registered reason"
        )
    return violations


def main():
    if len(sys.argv) != 3:
        print("usage: check_surrogate.py <surrogate.json> <surrogate_cert.json>",
              file=sys.stderr)
        return 2
    violations = check(sys.argv[1], sys.argv[2])
    for v in violations:
        print(f"VIOLATION: {v}")
    if not violations:
        s = json.load(open(sys.argv[1]))
        print(f"surrogate gate holds: kappa {s['kappa_primary_dead_vs_not']} "
              f">= {KAPPA_GATE}, certificate green")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
