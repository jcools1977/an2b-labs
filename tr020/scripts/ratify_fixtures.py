#!/usr/bin/env python3
"""Record DeVere's ratification of the measurement fixtures (D13).

Run ONLY on DeVere's explicit word, after he has read
fixtures/canon_pairs.jsonl and fixtures/judge_damage.jsonl. Writes
fixtures/RATIFICATION.json with the current file hashes; any later edit
to a fixture disarms the D3 gate until re-ratified.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ["canon_pairs.jsonl", "judge_damage.jsonl"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ratified-by", required=True)
    ap.add_argument("--date", required=True)
    ap.add_argument("--note", default="")
    args = ap.parse_args()

    fix = TR_ROOT / "fixtures"
    record = {
        "ratified_by": args.ratified_by,
        "date": args.date,
        "note": args.note,
        "sha256": {
            name: hashlib.sha256((fix / name).read_bytes()).hexdigest()
            for name in REQUIRED
        },
    }
    with open(fix / "RATIFICATION.json", "w") as fh:
        json.dump(record, fh, indent=2)
    print(json.dumps(record, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
