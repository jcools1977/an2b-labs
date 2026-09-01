#!/usr/bin/env python3
"""TR-004 negative controls (protocol; D9). The checker consumes every
stratum it is given (the TR-015 D21 lesson): all shuffle entries, all
synonym entries, all projection ranks; absence of any block is itself
a violation.

Schema (results/controls.json):
{
  "label_shuffle": {"<estimator>": {"delta": f, "ci": [lo, hi]}, ...},
  "synonym": {"<estimator>": {"delta": f, "ci": [lo, hi]}, ...},
  "random_subspace": {"orig_delta": f,
                       "projected": {"<rank>": f, ...}}
}
"""
import json
import sys

SYN_POINT = 0.1
PROJ_TOL = 0.05


def check(path):
    d = json.load(open(path))
    v = []
    ls = d.get("label_shuffle")
    if not ls:
        v.append("control 1 (label shuffle) missing")
    else:
        for est, e in sorted(ls.items()):
            if not (e["ci"][0] <= 0 <= e["ci"][1]):
                v.append(f"control 1 ({est}): shuffled delta CI {e['ci']} "
                         f"excludes zero; the pipeline manufactures effect")
    syn = d.get("synonym")
    if not syn:
        v.append("control 2 (synonym) missing")
    else:
        for est, e in sorted(syn.items()):
            if not (e["ci"][0] <= 0 <= e["ci"][1]) or abs(e["delta"]) >= SYN_POINT:
                v.append(f"control 2 ({est}): literal-vs-literal delta "
                         f"{e['delta']} CI {e['ci']} not near zero (D9)")
    rs = d.get("random_subspace")
    if not rs or not rs.get("projected"):
        v.append("control 3 (random subspace) missing")
    else:
        for rank, pd in sorted(rs["projected"].items()):
            if pd > rs["orig_delta"] + PROJ_TOL:
                v.append(f"control 3: effect strengthens under rank-{rank} "
                         f"random projection ({pd} > {rs['orig_delta']} + "
                         f"{PROJ_TOL}); ambient-dimension artifact")
    return v


def main():
    if len(sys.argv) != 2:
        return 2
    vs = check(sys.argv[1])
    for x in vs:
        print(f"VIOLATION [{sys.argv[1]}]: {x}")
    if not vs:
        print(f"controls hold: {sys.argv[1]}")
    return 1 if vs else 0


if __name__ == "__main__":
    sys.exit(main())
