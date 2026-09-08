#!/usr/bin/env python3
"""TR-003r store gate (protocol Design + control 4, D5).

Reads data/CORPUS_MANIFEST.json. Every disjointness flag below is
COMPUTED by the builder from sha256 sets, never asserted by hand; this
checker refuses a manifest whose flags or counts miss the frozen text.
"""
import json
import sys

FROZEN = {"store_size": 5000, "queries_per_kind": 500, "chunk_words": 200,
          "query_words": 60, "anchor_counts": [64, 256, 1024],
          "seeds": [41, 43], "spaces": 6,
          "primary_pair": ["bge", "minilm"]}


def check(path):
    d = json.load(open(path))
    v = []
    for k in ("store_size", "queries_per_kind", "chunk_words", "query_words",
              "anchor_counts", "seeds", "spaces", "primary_pair"):
        if d.get(k) != FROZEN[k]:
            v.append(f"{k} is {d.get(k)!r}, frozen {FROZEN[k]!r}")
    if d.get("gate_anchor_selection") != "random":
        v.append("gate anchor selection is not RANDOM (D4)")
    if d.get("anchor_pool_min", 0) < 2048:
        v.append("anchor pool under 2,048 (mismatched control needs disjoint halves of 1,024)")
    flags = d.get("disjointness", {})
    for f in ("store_vs_anchor_pool", "query_sources_vs_anchor_pool",
              "anchors_vs_queries_all_seed_pairs", "works_partition_global"):
        if flags.get(f) is not True:
            v.append(f"disjointness flag {f} is {flags.get(f)!r}, must be computed True")
    if flags.get("overlap_counts") and any(flags["overlap_counts"].values()):
        v.append(f"nonzero overlap counts {flags['overlap_counts']}")
    for s in FROZEN["seeds"]:
        ss = d.get("per_seed", {}).get(str(s), {})
        if ss.get("store_chunks") != FROZEN["store_size"]:
            v.append(f"seed {s} store has {ss.get('store_chunks')} chunks")
        if ss.get("q1") != 500 or ss.get("q2") != 500:
            v.append(f"seed {s} queries {ss.get('q1')}/{ss.get('q2')}")
        if ss.get("sequence_edges", 0) < 4000:
            v.append(f"seed {s} store has only {ss.get('sequence_edges')} sequence edges; not graph-shaped")
    return v


def main():
    if len(sys.argv) != 2:
        return 2
    vs = check(sys.argv[1])
    for x in vs:
        print(f"VIOLATION [{sys.argv[1]}]: {x}")
    if not vs:
        print(f"store integrity holds: {sys.argv[1]}")
    return 1 if vs else 0


if __name__ == "__main__":
    sys.exit(main())
