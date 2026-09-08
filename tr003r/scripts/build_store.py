#!/usr/bin/env python3
"""TR-003r store builder (protocol Design; DECISIONS D5, D9).

Per seed: a 5,000-chunk graph-shaped store drawn as WHOLE WORKS from
TR-002r's chunk registry (so sequence edges are intact), 500 Q1 cued-
recall queries (middle 60 words of a store chunk), 500 Q2 neighbor
queries (first 60 words of the chunk FOLLOWING a store chunk), an
anchor pool of 2,048 chunks from anchor-eligible works, random anchor
draws at 64/256/1,024, k-means medoids come later from embeddings,
scrambled anchors (seeded random-word strings of matched length), and
the mismatched halves. Works are partitioned GLOBALLY into store-
eligible and anchor-eligible by sha256 of the work id, so no seed's
anchors can overlap another seed's queries (the harder reading of
control 4). Every disjointness flag in the manifest is COMPUTED from
sha256 sets.

Usage: build_store.py  (runs both seeds)
"""
import hashlib
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

TR = Path(__file__).resolve().parents[1]
SRC = TR.parent / "tr002r" / "corpus_store"
OUT = TR / "corpus_store"
DATA = TR / "data"
SEEDS = [41, 43]
STORE_N, Q_N, POOL_N = 5000, 500, 2048
ANCHOR_COUNTS = [64, 256, 1024]
QWORDS = 60


def sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def anchor_eligible(work: str) -> bool:
    # ~25% of works by hash: the first hex digit in 0..3.
    return sha("tr003r-partition:" + work)[0] in "0123"


def load_registry():
    reg = json.load(open(SRC / "chunk_registry.json"))
    by_work = defaultdict(list)
    for cid, meta in reg.items():
        work, pos = cid.rsplit("__", 1)
        by_work[work].append((int(pos), cid, meta["sha256"]))
    for w in by_work:
        by_work[w].sort()
    return reg, by_work


def text(cid):
    return (SRC / "chunks" / f"{cid}.txt").read_text()


def words(s):
    return s.split()


def middle(ws, n):
    start = max(0, (len(ws) - n) // 2)
    return " ".join(ws[start:start + n])


def build_seed(seed, reg, by_work, vocab):
    rng = random.Random(seed)
    store_works = [w for w in by_work if not anchor_eligible(w)]
    anchor_works = [w for w in by_work if anchor_eligible(w)]
    rng.shuffle(store_works)
    rng.shuffle(anchor_works)
    # Store: whole works until 5,000 chunks; the last work is truncated
    # at a position boundary so edges stay contiguous.
    store = []  # (cid, work, pos, sha)
    for w in store_works:
        for pos, cid, h in by_work[w]:
            if len(store) >= STORE_N:
                break
            store.append((cid, w, pos, h))
        if len(store) >= STORE_N:
            break
    store_ids = [s[0] for s in store]
    store_set = set(store_ids)
    pos_index = {cid: (w, pos) for cid, w, pos, _ in store}
    edges = [(cid, f"{w}__{pos+1:04d}") for cid, w, pos, _ in store
             if f"{w}__{pos+1:04d}" in store_set]
    # Q1: 500 store chunks, middle 60 words.
    q1_targets = rng.sample(store_ids, Q_N)
    # Q2: 500 store chunks whose successor exists in the registry (in
    # the store or not); cue = first 60 words of the successor.
    cands = [cid for cid, w, pos, _ in store if f"{w}__{pos+1:04d}" in reg]
    q2_targets = rng.sample(cands, Q_N)
    # Anchor pool: 2,048 chunks from anchor-eligible works, whole works
    # in shuffled order.
    pool = []
    for w in anchor_works:
        for pos, cid, h in by_work[w]:
            if len(pool) >= POOL_N:
                break
            pool.append((cid, h))
        if len(pool) >= POOL_N:
            break
    pool_ids = [p[0] for p in pool]
    draws = {}
    for k in ANCHOR_COUNTS:
        draws[str(k)] = rng.sample(pool_ids, k)
    half_a, half_b = pool_ids[:POOL_N // 2], pool_ids[POOL_N // 2:]
    mismatched = {str(k): {"A": rng.sample(half_a, k), "B": rng.sample(half_b, k)}
                  for k in ANCHOR_COUNTS}
    # Scrambled anchors: random-word strings of matched length.
    scrambled = {}
    for k in ANCHOR_COUNTS:
        scrambled[str(k)] = []
        for cid in draws[str(k)]:
            n = len(words(text(cid)))
            scrambled[str(k)].append(" ".join(rng.choice(vocab) for _ in range(n)))
    # Texts to embed: store chunks, anchor pool, queries, scrambled.
    texts = {}
    for cid in store_ids + pool_ids:
        texts[cid] = text(cid)
    q1 = []
    for t in q1_targets:
        qid = f"q1_{seed}_{t}"
        texts[qid] = middle(words(text(t)), QWORDS)
        q1.append({"qid": qid, "target": t, "work": pos_index[t][0]})
    q2 = []
    for t in q2_targets:
        w, pos = pos_index[t]
        succ = f"{w}__{pos+1:04d}"
        qid = f"q2_{seed}_{t}"
        texts[qid] = " ".join(words(text(succ))[:QWORDS])
        q2.append({"qid": qid, "target": t, "work": w, "cue_source": succ})
    scr_ids = {}
    for k, lst in scrambled.items():
        scr_ids[k] = []
        for i, s in enumerate(lst):
            sid = f"scr_{seed}_{k}_{i:04d}"
            texts[sid] = s
            scr_ids[k].append(sid)
    # Disjointness, computed on content hashes.
    store_sha = {h for _, _, _, h in store}
    pool_sha = {h for _, h in pool}
    qsrc_sha = {reg[t]["sha256"] for t in q1_targets} | {reg[q["cue_source"]]["sha256"] for q in q2}
    return {
        "seed": seed, "store": store_ids, "store_meta": {cid: {"work": w, "pos": pos} for cid, w, pos, _ in store},
        "edges": edges, "q1": q1, "q2": q2, "anchor_pool": pool_ids,
        "anchors_random": draws, "anchors_mismatched": mismatched, "anchors_scrambled": scr_ids,
        "texts": texts,
        "_sets": {"store": store_sha, "pool": pool_sha, "qsrc": qsrc_sha,
                  "anchor_draw": {reg[c]["sha256"] for c in draws["1024"]}},
        "stats": {"store_chunks": len(store_ids), "works_in_store": len({w for _, w, _, _ in store}),
                  "sequence_edges": len(edges), "q1": len(q1), "q2": len(q2),
                  "anchor_pool": len(pool_ids)},
    }


def main():
    reg, by_work = load_registry()
    vocab = sorted({w for cid in list(reg)[:3000] for w in words(text(cid)) if w.isalpha()})
    OUT.mkdir(exist_ok=True)
    (OUT / "texts").mkdir(exist_ok=True)
    DATA.mkdir(exist_ok=True)
    built = {}
    for seed in SEEDS:
        b = build_seed(seed, reg, by_work, vocab)
        for tid, t in b["texts"].items():
            (OUT / "texts" / f"{tid}.txt").write_text(t)
        sets = b.pop("_sets")
        texts = b.pop("texts")
        b["text_ids"] = sorted(texts)
        json.dump(b, open(OUT / f"store_{seed}.json", "w"))
        built[seed] = (b, sets)
        print(f"seed {seed}: {b['stats']}", flush=True)
    overlap = {
        "store_anchor": sum(len(built[s][1]["store"] & built[s][1]["pool"]) for s in SEEDS),
        "query_anchor": sum(len(built[s][1]["qsrc"] & built[s][1]["pool"]) for s in SEEDS),
        "cross_seed": sum(len(built[s][1]["anchor_draw"] & built[t][1]["qsrc"])
                          for s in SEEDS for t in SEEDS),
    }
    manifest = {
        "source": "tr002r chunk_registry (Gutenberg, 200-word chunks)",
        "registry_sha256": hashlib.sha256((SRC / "chunk_registry.json").read_bytes()).hexdigest(),
        "store_size": STORE_N, "queries_per_kind": Q_N, "chunk_words": 200, "query_words": QWORDS,
        "anchor_counts": ANCHOR_COUNTS, "anchor_pool_min": POOL_N, "seeds": SEEDS, "spaces": 6,
        "space_keys": ["bge", "e5", "minilm", "llama4", "qwen4", "gemma4"],
        "primary_pair": ["bge", "minilm"], "gate_anchor_selection": "random",
        "disjointness": {
            "works_partition_global": True,
            "store_vs_anchor_pool": overlap["store_anchor"] == 0,
            "query_sources_vs_anchor_pool": overlap["query_anchor"] == 0,
            "anchors_vs_queries_all_seed_pairs": overlap["cross_seed"] == 0,
            "overlap_counts": overlap},
        "per_seed": {str(s): built[s][0]["stats"] for s in SEEDS},
        "texts_total": len(list((OUT / "texts").glob("*.txt"))),
    }
    json.dump(manifest, open(DATA / "CORPUS_MANIFEST.json", "w"), indent=1)
    print("manifest:", json.dumps(manifest["disjointness"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
