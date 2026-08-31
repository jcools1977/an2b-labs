#!/usr/bin/env python3
"""Topic labels for the D19 topic control: k-means (k=4, seed 31) on bge
document embeddings, computed blind to entropy (runs on legion in the
recorded embedding environment). Writes data/topic_labels.json.
"""
import json
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
DOCS = TR_ROOT / "corpus_store" / "docs"


def main():
    import numpy as np
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding

    embedder = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    manifest = json.load(open(TR_ROOT / "data" / "CORPUS_MANIFEST.json"))
    doc_ids = sorted(manifest["documents"])

    vecs = []
    for did in doc_ids:
        text = (DOCS / f"{did}.txt").read_text()
        w = text.split()
        chunks = [" ".join(w[i:i + 400]) for i in range(0, len(w), 400)][:12]
        v = np.mean([np.array(embedder.get_text_embedding(c)) for c in chunks], axis=0)
        vecs.append(v / np.linalg.norm(v))
    X = np.array(vecs)

    # seeded k-means (numpy-only Lloyd's, deterministic)
    rng = np.random.default_rng(31)
    centers = X[rng.choice(len(X), 4, replace=False)]
    for _ in range(50):
        d = ((X[:, None, :] - centers[None]) ** 2).sum(-1)
        lab = d.argmin(1)
        new = np.array([X[lab == k].mean(0) if (lab == k).any() else centers[k]
                        for k in range(4)])
        if np.allclose(new, centers):
            break
        centers = new

    json.dump({did: int(l) for did, l in zip(doc_ids, lab)},
              open(TR_ROOT / "data" / "topic_labels.json", "w"), indent=1)
    counts = {int(k): int((lab == k).sum()) for k in range(4)}
    print("topic clusters:", counts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
