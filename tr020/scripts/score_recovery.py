#!/usr/bin/env python3
"""Join auditor verdicts with the sealed ground truth (D1, D6).

The ONLY code besides build_seal.py that imports plants. Verifies the
seal hash first, then writes results/seeded_recovery.json in the schema
check_recovery.py enforces.
"""
import hashlib
import json
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TR_ROOT))

from seed_systems.plants import EXPECTED  # noqa: E402


def main():
    sealed = TR_ROOT / "seed_systems" / "GROUND_TRUTH.sealed.json"
    digest = hashlib.sha256(sealed.read_bytes()).hexdigest()
    recorded = (TR_ROOT / "seed_systems" / "SEAL.sha256").read_text().split()[0]
    if digest != recorded:
        raise SystemExit("SEAL BROKEN: refusing to score against a tampered seal")
    truth = json.load(open(sealed))
    assert truth["expected"] == EXPECTED, "plants.py and the seal disagree"

    detail = json.load(open(TR_ROOT / "results" / "seeded_detail.json"))
    rows = []
    for sid, expected in EXPECTED.items():
        verdicts = detail[sid]["verdicts"]
        for comp, exp in expected.items():
            rows.append({"system": sid, "component": comp,
                         "verdict": verdicts[comp], "expected": exp})

    out = {"seal_sha256": digest, "per_component": rows}
    with open(TR_ROOT / "results" / "seeded_recovery.json", "w") as fh:
        json.dump(out, fh, indent=2)

    exact = sum(1 for r in rows if r["verdict"] == r["expected"])
    print(f"scored {len(rows)} components; class-exact {exact}/{len(rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
