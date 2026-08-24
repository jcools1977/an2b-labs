#!/usr/bin/env python3
"""Negative control 4 for TR-001: label leakage check (protocol section 8).

Hashes normalized passage text from the adapter training set and the held-out
eval set; any overlap is a hard failure. Also fails on an empty or missing
file, because a leakage check that passes on no data proves nothing.

Both files are JSONL, one object per line, with a "passage" field.
Normalization (DECISIONS.md D5): lowercase, collapse all whitespace runs to
a single space, strip, SHA-256.
"""
import hashlib
import json
import re
import sys


def passage_hashes(path):
    hashes = set()
    with open(path) as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            passage = row.get("passage")
            if not isinstance(passage, str) or not passage.strip():
                raise ValueError(f"{path}:{lineno}: missing or empty 'passage'")
            norm = re.sub(r"\s+", " ", passage.lower()).strip()
            hashes.add(hashlib.sha256(norm.encode("utf-8")).hexdigest())
    return hashes


def main():
    if len(sys.argv) != 3:
        print("usage: check_leakage.py <train.jsonl> <eval.jsonl>", file=sys.stderr)
        return 2

    train_path, eval_path = sys.argv[1], sys.argv[2]
    try:
        train = passage_hashes(train_path)
        evalset = passage_hashes(eval_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"LEAKAGE CHECK UNRUNNABLE: {exc}")
        return 1

    if not train or not evalset:
        print(
            f"LEAKAGE CHECK UNRUNNABLE: empty set "
            f"(train={len(train)}, eval={len(evalset)}); "
            f"a check over nothing proves nothing"
        )
        return 1

    overlap = train & evalset
    if overlap:
        print(
            f"LEAKAGE: {len(overlap)} eval passage(s) present in adapter "
            f"training set (train={len(train)} unique, eval={len(evalset)} unique)"
        )
        return 1

    print(
        f"no leakage: 0 overlapping passages "
        f"(train={len(train)} unique, eval={len(evalset)} unique)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
