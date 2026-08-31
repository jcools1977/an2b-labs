#!/usr/bin/env python3
"""TR-015 PASS gates (protocol; D3, D4, D10).

Schema (results/analysis.json):
{
  "accuracy_resid": f, "rank_used": int, "accuracy_burrows": f,
  "accuracy_fulldim": f,
  "drift": {"fraction_satisfying": f, "n_authors": int},
  "chunk_sizes_gated": [500, 1500]
}
"""
import json
import sys

ACC_GATE, RANK_MAX, DRIFT_FRACTION = 0.90, 10, 0.80


def check(path):
    d = json.load(open(path))
    v = []
    if d.get("rank_used", 99) > RANK_MAX:
        v.append(f"rank {d.get('rank_used')} exceeds {RANK_MAX}")
    acc = d.get("accuracy_resid")
    if acc is None or acc < ACC_GATE:
        v.append(f"residualized attribution {acc} < {ACC_GATE}")
    if acc is not None and d.get("accuracy_burrows") is not None \
            and acc < d["accuracy_burrows"]:
        v.append(f"Burrows Delta wins ({d['accuracy_burrows']} > {acc}): "
                 f"embeddings add nothing, per the protocol's FAIL clause")
    fr = d.get("drift", {}).get("fraction_satisfying")
    if fr is None or fr < DRIFT_FRACTION:
        v.append(f"drift+direction satisfied by {fr} of authors "
                 f"(gate {DRIFT_FRACTION}, both chunk sizes per D10)")
    if sorted(d.get("chunk_sizes_gated", [])) != [500, 1500]:
        v.append("both chunk sizes (500, 1500) must be gated (D4)")
    return v


def main():
    if len(sys.argv) != 2:
        return 2
    vs = check(sys.argv[1])
    for x in vs:
        print(f"VIOLATION [{sys.argv[1]}]: {x}")
    if not vs:
        print(f"PASS gates hold: {sys.argv[1]}")
    return 1 if vs else 0


if __name__ == "__main__":
    sys.exit(main())
