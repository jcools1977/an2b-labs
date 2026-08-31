#!/usr/bin/env python3
"""LDA topic factors (D5): k=20, seed 37, content-word counts with the
frozen D7 list removed from the vocabulary, one document per chunk.
One model per chunk size (chunk length changes count scale). Fit over
all chunks of that size, gate and non-gate alike: topics learned from
more text residualize harder, which leans against H1. Factors written
to corpus_store/topics_{size}.npz aligned to sorted chunk ids.
"""
import json
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
STORE = TR_ROOT / "corpus_store"


def main():
    import numpy as np
    from sklearn.decomposition import LatentDirichletAllocation
    from sklearn.feature_extraction.text import CountVectorizer

    frozen = (TR_ROOT / "data" / "function_words.txt").read_text().split()
    registry = json.load(open(STORE / "chunk_registry.json"))
    for size in (500, 1500):
        ids = sorted(c for c, m in registry.items() if m["size"] == size)
        texts = [(STORE / "chunks" / f"{c}.txt").read_text() for c in ids]
        vec = CountVectorizer(lowercase=True, token_pattern=r"[a-z']+",
                              stop_words=frozen, max_features=5000, min_df=5)
        counts = vec.fit_transform(texts)
        lda = LatentDirichletAllocation(n_components=20, random_state=37,
                                        max_iter=30)
        T = lda.fit_transform(counts)
        np.savez(STORE / f"topics_{size}.npz", ids=np.array(ids),
                 T=T.astype(np.float32))
        import joblib
        joblib.dump({"vectorizer": vec, "lda": lda},
                    STORE / f"topic_model_{size}.joblib")
        print(f"size {size}: {len(ids)} chunks, vocab {counts.shape[1]}, "
              f"perplexity {lda.perplexity(counts):.0f}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
