#!/usr/bin/env python3
"""TR-004 KILL gate (protocol; D8).

Schema (results/kill.json):
{
  "model1_present": bool,
  "model2": {"delta_twonn": f, "ci_twonn": [lo, hi],
              "delta_mle": f, "ci_mle": [lo, hi],
              "direction_reversed": bool, "absent": bool},
  "killed": bool
}
"""
import json
import sys


def check(path):
    d = json.load(open(path))
    v = []
    m2 = d.get("model2")
    if d.get("model1_present") is None or m2 is None \
            or d.get("killed") is None:
        v.append("kill results incomplete")
        return v
    # D8: absent = CI includes zero OR direction reversed (per estimator,
    # both estimators must be absent for the model to be absent)
    def est_absent(ci, rev):
        return rev or (ci[0] <= 0 <= ci[1])
    absent = (est_absent(m2["ci_twonn"], m2["direction_reversed"])
              and est_absent(m2["ci_mle"], m2["direction_reversed"]))
    if bool(m2.get("absent")) != absent:
        v.append(f"model2 'absent' flag {m2.get('absent')} inconsistent "
                 f"with D8 rule (computed {absent})")
    should_kill = bool(d["model1_present"]) and absent
    if bool(d["killed"]) != should_kill:
        v.append(f"killed flag {d['killed']} inconsistent with D8 "
                 f"(model1_present={d['model1_present']}, "
                 f"model2_absent={absent})")
    if should_kill:
        v.append("KILL (D8): effect present in model 1 and absent in "
                 "model 2; a model artifact, not a property of meaning")
    return v


def main():
    if len(sys.argv) != 2:
        return 2
    vs = check(sys.argv[1])
    for x in vs:
        print(f"VIOLATION [{sys.argv[1]}]: {x}")
    if not vs:
        print(f"KILL gate holds: {sys.argv[1]}")
    return 1 if vs else 0


if __name__ == "__main__":
    sys.exit(main())
