#!/usr/bin/env python3
"""Embed the valid D8 paraphrases with the gated embedder, exactly the
D2 procedure (bge, 400-token windows, mean-pooled, L2-normalized).
Writes corpus_store/embeddings/para_bge.npz.
"""
import json
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
STORE = TR_ROOT / "corpus_store"
WINDOW = 400


def main():
    import numpy as np
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from transformers import AutoTokenizer

    model_name = "BAAI/bge-small-en-v1.5"
    embedder = HuggingFaceEmbedding(model_name=model_name)
    tok = AutoTokenizer.from_pretrained(model_name)
    files = sorted((STORE / "paraphrases").glob("*.txt"))
    ids, vecs = [], []
    for f in files:
        text = f.read_text()
        token_ids = tok.encode(text, add_special_tokens=False)
        windows = [tok.decode(token_ids[j:j + WINDOW])
                   for j in range(0, len(token_ids), WINDOW)] or [text]
        w = np.array([embedder.get_text_embedding(win) for win in windows])
        v = w.mean(0)
        ids.append(f.stem)
        vecs.append(v / np.linalg.norm(v))
    X = np.array(vecs, dtype=np.float32)
    np.savez(STORE / "embeddings" / "para_bge.npz",
             ids=np.array(ids), X=X)
    print(f"embedded {len(ids)} paraphrases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
