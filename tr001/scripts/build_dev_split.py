#!/usr/bin/env python3
"""Carve the config-selection dev split out of train.jsonl (DECISIONS D19).

Passage-level: whole passages move to dev, never individual QA pairs.
Deterministic under seed 11. Writes data/dev.jsonl and data/train_core.jsonl,
updates MANIFEST (preserving foreign keys), and hard-fails if the two sides
share a normalized passage hash.
"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from checks.check_leakage import passage_hash  # noqa: E402
from lib.gates import TR_ROOT  # noqa: E402

DEV_SEED = 11
DEV_TARGET_PAIRS = 250


def main():
    rows = [json.loads(l) for l in open(TR_ROOT / "data" / "train.jsonl")]
    by_passage = {}
    for row in rows:
        by_passage.setdefault(passage_hash(row["passage"]), []).append(row)

    hashes = sorted(by_passage)
    random.Random(DEV_SEED).shuffle(hashes)

    dev_hashes, n_dev = set(), 0
    for h in hashes:
        if n_dev >= DEV_TARGET_PAIRS:
            break
        dev_hashes.add(h)
        n_dev += len(by_passage[h])

    dev = [r for h in sorted(dev_hashes) for r in by_passage[h]]
    core = [r for h in sorted(set(hashes) - dev_hashes) for r in by_passage[h]]

    core_hashes = {passage_hash(r["passage"]) for r in core}
    if core_hashes & dev_hashes:
        raise SystemExit("FATAL: dev/train-core share a passage hash")

    with open(TR_ROOT / "data" / "dev.jsonl", "w") as fh:
        for r in dev:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(TR_ROOT / "data" / "train_core.jsonl", "w") as fh:
        for r in core:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    manifest_path = TR_ROOT / "data" / "MANIFEST.json"
    manifest = json.load(open(manifest_path))
    manifest["dev_split"] = {
        "seed": DEV_SEED,
        "dev_pairs": len(dev),
        "dev_unique_passages": len(dev_hashes),
        "train_core_pairs": len(core),
        "train_core_unique_passages": len(core_hashes),
    }
    with open(manifest_path, "w") as fh:
        json.dump(manifest, fh, indent=2)

    print(json.dumps(manifest["dev_split"], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
