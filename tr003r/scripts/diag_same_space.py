#!/usr/bin/env python3
"""DIAGNOSTIC, reported only, never a gate (DECISIONS D15).
1. Same-space relative representations: store and queries in ONE
   model, both expressed against the same anchors. If this retrieves
   near native, the zero-fit machinery is sound within a model and
   any cross-model loss is the translation, not the coordinates.
2. Anchor-mean-centered variant of the same, to expose anisotropy.
3. Mean pairwise cosine among store vectors (anisotropy index).
Usage: diag_same_space.py [--seed 41] [--spaces bge,minilm,e5]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

TR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TR))
from analysis.anchors import relative, unit  # noqa: E402
from analysis.retrieval import metrics, topk  # noqa: E402
from scripts.run_grid import Space  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=41)
    ap.add_argument("--spaces", default="bge,minilm,e5")
    a = ap.parse_args()
    root = TR / "corpus_store"
    st = json.load(open(root / f"store_{a.seed}.json"))
    store = st["store"]
    sw = np.array([st["store_meta"][c]["work"] for c in store])
    sidx = {c: i for i, c in enumerate(store)}
    qs = st["q1"]
    qids = [q["qid"] for q in qs]
    tg = np.array([sidx[q["target"]] for q in qs])
    tw = np.array([q["work"] for q in qs])
    out = {}
    for name in a.spaces.split(","):
        sp = Space(root, name)
        S, Q = sp.rows(store), sp.rows(qids)
        U = unit(S[:2000])
        aniso = float((U @ U.T).mean())
        out[name] = {"anisotropy_mean_cos": aniso, "k": {}}
        for k in (64, 256, 1024):
            anc = sp.rows(st["anchors_random"][str(k)])
            idx, sc = topk(relative(Q, anc), relative(S, anc))
            m = metrics(idx, sc, tg, sw, tw)
            mu = anc.mean(0)
            idx2, sc2 = topk(relative(Q - mu, anc - mu), relative(S - mu, anc - mu))
            m2 = metrics(idx2, sc2, tg, sw, tw)
            out[name]["k"][str(k)] = {"same_space_relative_r5": m["r5"], "centered_r5": m2["r5"]}
            print(f"  {name:7} k={k:5} same-space relative r5={m['r5']:.3f}   "
                  f"anchor-mean-centered r5={m2['r5']:.3f}")
        print(f"  {name:7} anisotropy (mean pairwise cosine, store) = {aniso:.3f}")
    (TR / "results").mkdir(exist_ok=True)
    json.dump(out, open(TR / "results" / f"diag_same_space_{a.seed}.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
