#!/usr/bin/env python3
"""Burrows Delta baseline (protocol leg, D7 frozen function-word list).

Classic Delta: relative frequencies of the frozen function words per
chunk, z-scored against the training population, author profile = mean
train z-vector, attribution = argmin mean absolute z-difference. Split
is held-out-by-works (D3, seed 41), identical to the split every latent
instrument uses. Run per chunk size (D4). Writes
results/burrows_baseline.json.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TR_ROOT))
import numpy as np  # noqa: E402

from analysis.split import held_out_works, split_ids  # noqa: E402

STORE = TR_ROOT / "corpus_store"
WORDS = (TR_ROOT / "data" / "function_words.txt").read_text().split()


def features(text):
    toks = re.findall(r"[a-z']+", text.lower())
    n = max(len(toks), 1)
    c = Counter(toks)
    return np.array([c[w] / n for w in WORDS])


def run(registry, size):
    train, test = split_ids(registry, size)
    Xtr = np.array([features((STORE / "chunks" / f"{c}.txt").read_text())
                    for c in train])
    Xte = np.array([features((STORE / "chunks" / f"{c}.txt").read_text())
                    for c in test])
    ytr = np.array([registry[c]["author"] for c in train])
    yte = np.array([registry[c]["author"] for c in test])
    mu, sd = Xtr.mean(0), Xtr.std(0)
    sd[sd == 0] = 1.0
    Ztr, Zte = (Xtr - mu) / sd, (Xte - mu) / sd
    authors = sorted(set(ytr))
    profiles = np.array([Ztr[ytr == a].mean(0) for a in authors])
    pred = [authors[int(np.argmin(np.abs(profiles - z).mean(1)))] for z in Zte]
    acc = float((np.array(pred) == yte).mean())
    per_author = {a: float((np.array(pred)[yte == a] == a).mean())
                  for a in authors}
    return {"size": size, "accuracy": acc, "n_train": len(train),
            "n_test": len(test), "n_authors": len(authors),
            "chance": 1 / len(authors), "per_author": per_author}


def main():
    registry = json.load(open(STORE / "chunk_registry.json"))
    out = {"function_words": len(WORDS),
           "held_out_works": held_out_works(registry),
           "runs": [run(registry, s) for s in (500, 1500)]}
    (TR_ROOT / "results").mkdir(exist_ok=True)
    json.dump(out, open(TR_ROOT / "results" / "burrows_baseline.json", "w"),
              indent=2)
    for r in out["runs"]:
        print(f"size {r['size']}: acc {r['accuracy']:.3f} "
              f"({r['n_authors']} authors, chance {r['chance']:.3f}, "
              f"test n={r['n_test']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
