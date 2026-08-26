#!/usr/bin/env python3
"""Write the sealed ground truth and its hash (DECISIONS D6).

Cross-checks plants.py against the actual system definitions (every
component accounted for, both redundant-pair archetypes present, the
all-live control genuinely plant-free) before sealing. Run once per
change to the seeded systems; verify.sh then holds the hash.
"""
import hashlib
import json
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TR_ROOT))

from seed_systems.plants import EXPECTED, REDUNDANT_PAIRS  # noqa: E402
from seed_systems.systems import build_systems  # noqa: E402


def main():
    systems = build_systems()
    assert set(systems) == set(EXPECTED), "systems and plants disagree on system ids"
    for sid, system in systems.items():
        assert set(system.component_names()) == set(EXPECTED[sid]), \
            f"{sid}: components and expected verdicts disagree"
    assert all(v == "live" for v in EXPECTED["s7_all_live_qa"].values()), \
        "the all-live control has a plant"
    for sid, a, b in REDUNDANT_PAIRS:
        assert EXPECTED[sid][a] == EXPECTED[sid][b] == "redundant"

    counts = {"dead": 0, "redundant": 0, "live": 0}
    for verdicts in EXPECTED.values():
        for v in verdicts.values():
            counts[v] += 1

    truth = {
        "taxonomy": "D1: dead | redundant | live",
        "expected": EXPECTED,
        "redundant_pairs": [list(p) for p in REDUNDANT_PAIRS],
        "census": counts,
    }
    sealed = TR_ROOT / "seed_systems" / "GROUND_TRUTH.sealed.json"
    with open(sealed, "w") as fh:
        json.dump(truth, fh, indent=2, sort_keys=True)

    digest = hashlib.sha256(sealed.read_bytes()).hexdigest()
    with open(TR_ROOT / "seed_systems" / "SEAL.sha256", "w") as fh:
        fh.write(f"{digest}  seed_systems/GROUND_TRUTH.sealed.json\n")
    print(f"sealed: {counts} -> {digest[:16]}...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
