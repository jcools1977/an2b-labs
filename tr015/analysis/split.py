"""Held-out-by-works split (D3, seed frozen at 41 per D13).

For each gate-population author, one entire work is held out as test;
training chunks come only from the author's remaining works. No chunk
of a test work ever appears in training, at either chunk size. The
held-out work is drawn per-author with the frozen seed, once, and the
same assignment governs every instrument (Burrows baseline, raw
embeddings, residualized embeddings, subspace projections), so no
instrument can shop for a friendlier split.
"""
import random


def held_out_works(registry, seed=41):
    """Map author -> held-out work id, over gate-population chunks only."""
    by_author = {}
    for meta in registry.values():
        if not meta.get("gate_population", True):
            continue
        by_author.setdefault(meta["author"], set()).add(meta["work"])
    rng = random.Random(seed)
    return {a: rng.choice(sorted(works))
            for a, works in sorted(by_author.items()) if len(works) >= 2}


def split_ids(registry, size, seed=41):
    """(train_ids, test_ids) for one chunk size, gate population only."""
    held = held_out_works(registry, seed)
    train, test = [], []
    for cid, meta in sorted(registry.items()):
        if meta["size"] != size or meta["author"] not in held:
            continue
        (test if meta["work"] == held[meta["author"]] else train).append(cid)
    return train, test
