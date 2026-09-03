#!/usr/bin/env python3
"""TR-002r PASS gates (protocol amendments one and three).

Schema (results/analysis.json):
{
  "primary_pair": "bge-small-en-v1.5<->Llama-3.1-8B-4bit",
  "method": "mini-vec2vec-linear",
  "n_used": 32000,
  "directions": {"bge_to_llama": {"cosine": f, "top1": f},
                  "llama_to_bge": {"cosine": f, "top1": f}},
  "skyline_cosine_primary": f,
  "seeds_replicate": bool
}
"""
import json
import sys

COS_GATE, TOP1_GATE, SKY_GATE, N_MAX = 0.70, 0.30, 0.80, 16000
PAIR = "bge-small-en-v1.5<->Llama-3.1-8B-4bit"
METHOD = "mini-vec2vec-linear"


def check(path):
    d = json.load(open(path))
    v = []
    if d.get("primary_pair") != PAIR:
        v.append(f"gate read on {d.get('primary_pair')}, not the frozen "
                 f"primary pair (amendment one: no multiplicity)")
    if d.get("method") != METHOD:
        v.append(f"method {d.get('method')} is not the frozen primary "
                 f"(amendment three: no method shopping)")
    if d.get("n_used") != N_MAX:
        v.append(f"gate read at n={d.get('n_used')}, not the largest "
                 f"pre-registered n ({N_MAX})")
    dirs = d.get("directions") or {}
    for name in ("bge_to_llama", "llama_to_bge"):
        e = dirs.get(name)
        if not e:
            v.append(f"direction {name} missing (gate reads BOTH)")
            continue
        if e.get("cosine", 0) < COS_GATE:
            v.append(f"{name}: cosine {e.get('cosine')} < {COS_GATE}")
        if e.get("top1", 0) < TOP1_GATE:
            v.append(f"{name}: top-1 {e.get('top1')} < {TOP1_GATE}")
    if d.get("skyline_cosine_primary", 0) < SKY_GATE:
        v.append(f"primary skyline {d.get('skyline_cosine_primary')} < "
                 f"{SKY_GATE}: unsupervised number uninterpretable")
    if not d.get("seeds_replicate"):
        v.append("gate does not hold at both seeds (41, 43)")
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
