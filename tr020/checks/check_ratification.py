#!/usr/bin/env python3
"""Human-ratification gate for measurement fixtures (DECISIONS D13).

The D3 gate is armed only when fixtures/RATIFICATION.json exists, names
a human ratifier, and carries SHA-256 hashes matching the committed
fixture files. Any post-ratification edit breaks the hashes and disarms
the gate. Exits nonzero when unratified.

Usage: check_ratification.py [fixtures_dir]   (default: ../fixtures)
"""
import hashlib
import json
import sys
from pathlib import Path

REQUIRED = ["canon_pairs.jsonl", "judge_damage.jsonl"]


def check(fix_dir):
    fix_dir = Path(fix_dir)
    rat_path = fix_dir / "RATIFICATION.json"
    if not rat_path.exists():
        return [f"UNRATIFIED: {rat_path} absent; the D3 gate is not armed (D13)"]
    rat = json.load(open(rat_path))
    violations = []
    if not rat.get("ratified_by"):
        violations.append("RATIFICATION.json names no human ratifier")
    hashes = rat.get("sha256", {})
    for name in REQUIRED:
        f = fix_dir / name
        if not f.exists():
            violations.append(f"fixture {name} missing")
            continue
        actual = hashlib.sha256(f.read_bytes()).hexdigest()
        if hashes.get(name) != actual:
            violations.append(
                f"fixture {name} does not match its ratified hash; "
                f"post-ratification edit disarms the gate (D13)"
            )
    return violations


def main():
    fix_dir = sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "fixtures"
    violations = check(fix_dir)
    for v in violations:
        print(f"VIOLATION [{fix_dir}]: {v}")
    if not violations:
        rat = json.load(open(Path(fix_dir) / "RATIFICATION.json"))
        print(f"fixtures ratified by {rat['ratified_by']} on {rat.get('date', '?')}; hashes match")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
