#!/usr/bin/env python3
"""TR-004 corpus gate (D2).

Schema (data/CORPUS_MANIFEST.json):
{
  "source": "VUAMC" | "TroFi",
  "n_lemmas": int, "min_instances_per_side": int,
  "excluded_lemmas_counted": bool,
  "frequency_length_recorded": bool,
  "dedup_overlaps": int,
  "seeds": {"bootstrap": [41, 43], "shuffle": 41, "projection": 47}
}
"""
import json
import sys


def check(path):
    d = json.load(open(path))
    v = []
    if d.get("source") not in ("VUAMC", "TroFi"):
        v.append(f"source {d.get('source')} not a pre-registered corpus (D2)")
    if d.get("n_lemmas", 0) < 20:
        v.append(f"n_lemmas {d.get('n_lemmas')} < 20 (D2: stop for PI "
                 f"adjudication, do not run underpowered)")
    if d.get("min_instances_per_side", 0) < 10:
        v.append("a lemma entered with fewer than 10 instances per side (D2)")
    if not d.get("excluded_lemmas_counted"):
        v.append("exclusions not counted in the manifest (D2)")
    if not d.get("frequency_length_recorded"):
        v.append("frequency/length confounds not recorded per instance (D7)")
    if d.get("dedup_overlaps", 1) != 0:
        v.append("dedup overlaps present")
    s = d.get("seeds", {})
    if s.get("bootstrap") != [41, 43] or s.get("shuffle") != 41 \
            or s.get("projection") != 47:
        v.append("seeds are not the frozen D10 set")
    return v


def main():
    if len(sys.argv) != 2:
        return 2
    vs = check(sys.argv[1])
    for x in vs:
        print(f"VIOLATION [{sys.argv[1]}]: {x}")
    if not vs:
        print(f"corpus integrity holds: {sys.argv[1]}")
    return 1 if vs else 0


if __name__ == "__main__":
    sys.exit(main())
