#!/usr/bin/env python3
"""TR-003r retrieval grid: resumable, one JSON line per configuration
in results/grid.jsonl. Every configuration in the protocol's grid and
nothing outside it (sweep budget = the grid as written).

Usage: run_grid.py [--root corpus_store] [--spaces bge,e5,...] [--out results/grid.jsonl]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans

TR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TR))
from analysis.anchors import (naive_map, procrustes_map, random_projection_pair,  # noqa: E402
                              relative)
from analysis.retrieval import metrics, topk  # noqa: E402

KS = [64, 256, 1024]
SEEDS = [41, 43]
QKINDS = ["q1", "q2"]
DEFAULT_SPACES = ["bge", "e5", "minilm", "llama4", "qwen4", "gemma4"]


class Space:
    def __init__(self, root, name):
        d = np.load(root / "emb" / f"{name}.npz", allow_pickle=True)
        self.name = name
        self.ids = [str(x) for x in d["ids"]]
        self.row = {t: i for i, t in enumerate(self.ids)}
        self.X = np.asarray(d["X"], dtype=np.float32)
        self.dim = self.X.shape[1]

    def rows(self, ids):
        return self.X[[self.row[t] for t in ids]]


def medoid_ids(space, pool_ids, k, seed, cache):
    key = (space.name, k, seed)
    if key not in cache:
        P = space.rows(pool_ids)
        km = KMeans(n_clusters=k, random_state=seed, n_init=2).fit(P)
        picked = []
        for c in km.cluster_centers_:
            d = np.linalg.norm(P - c, axis=1)
            for j in np.argsort(d):
                if j not in picked:
                    picked.append(int(j))
                    break
        cache[key] = [pool_ids[j] for j in picked]
    return cache[key]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(TR / "corpus_store"))
    ap.add_argument("--spaces", default=",".join(DEFAULT_SPACES))
    ap.add_argument("--out", default=str(TR / "results" / "grid.jsonl"))
    a = ap.parse_args()
    root = Path(a.root)
    names = a.spaces.split(",")
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out.exists():
        for ln in out.read_text().splitlines():
            if ln.strip():
                done.add(json.loads(ln)["key"])
    fh = open(out, "a")

    def emit(rec):
        if rec["key"] in done:
            return
        fh.write(json.dumps(rec) + "\n")
        fh.flush()
        done.add(rec["key"])

    spaces = {n: Space(root, n) for n in names}
    med_cache = {}
    for seed in SEEDS:
        st = json.load(open(root / f"store_{seed}.json"))
        store_ids = st["store"]
        store_work = np.array([st["store_meta"][c]["work"] for c in store_ids])
        sidx = {c: i for i, c in enumerate(store_ids)}
        for qk in QKINDS:
            qs = st[qk]
            qids = [q["qid"] for q in qs]
            targets = np.array([sidx[q["target"]] for q in qs])
            tworks = np.array([q["work"] for q in qs])
            # natives per space (C1)
            native = {}
            for n, sp in spaces.items():
                idx, sc = topk(sp.rows(qids), sp.rows(store_ids))
                m = metrics(idx, sc, targets, store_work, tworks)
                native[n] = {"m": m, "top": idx, "margin": m["median_margin"]}
                emit({"key": f"{seed}|{qk}|{n}|C1", "seed": seed, "qkind": qk,
                      "space": n, "condition": "C1", **m})
            for A in names:
                for B in names:
                    if A == B:
                        continue
                    spA, spB = spaces[A], spaces[B]
                    S_A, Q_B = spA.rows(store_ids), spB.rows(qids)
                    ref = native[B]
                    base = {"seed": seed, "qkind": qk, "pair": f"{A}->{B}",
                            "native_r5": ref["m"]["r5"],
                            "native_confident_wrong": ref["m"]["confident_wrong"]}

                    def run(S, Q, cond, k=None, sel=None, arm=None):
                        key = f"{seed}|{qk}|{A}->{B}|{cond}|{k}|{sel}|{arm}"
                        if key in done:
                            return
                        idx, sc = topk(Q, S)
                        m = metrics(idx, sc, targets, store_work, tworks,
                                    native_top_idx=ref["top"], native_median_margin=ref["margin"])
                        m["retention"] = m["r5"] / max(ref["m"]["r5"], 1e-9)
                        m["excess_confident_wrong"] = m["confident_wrong"] - ref["m"]["confident_wrong"]
                        emit({"key": key, "condition": cond, "anchors": k, "selection": sel,
                              "arm": arm, **base, **m})

                    run(naive_map(S_A, spB.dim, seed), Q_B, "C2")
                    for k in KS:
                        for sel in ("random", "medoid"):
                            ids = (st["anchors_random"][str(k)] if sel == "random"
                                   else medoid_ids(spA, st["anchor_pool"], k, seed, med_cache))
                            anc_A, anc_B = spA.rows(ids), spB.rows(ids)
                            run(relative(S_A, anc_A), relative(Q_B, anc_B), "C3", k, sel)
                            f_src, f_tgt = procrustes_map(anc_A, anc_B)
                            run(f_src(S_A), f_tgt(Q_B), "C4", k, sel)
                        # controls (random selection frame)
                        scr = st["anchors_scrambled"][str(k)]
                        run(relative(S_A, spA.rows(scr)), relative(Q_B, spB.rows(scr)),
                            "C3", k, "random", "scrambled")
                        mm = st["anchors_mismatched"][str(k)]
                        run(relative(S_A, spA.rows(mm["A"])), relative(Q_B, spB.rows(mm["B"])),
                            "C3", k, "random", "mismatched")
                    Ra, Rb = random_projection_pair(spA.dim, spB.dim, 1024, seed)
                    run(S_A @ Ra, Q_B @ Rb, "RP", 1024, "random", "random_projection")
                    print(f"seed {seed} {qk} {A}->{B} done", flush=True)
    fh.close()
    print("GRID_DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
