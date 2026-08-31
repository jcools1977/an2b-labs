#!/usr/bin/env python3
"""Embed every corpus chunk (D2): BAAI/bge-small-en-v1.5, each chunk
sliced into 400-token windows, one embedding per window, mean-pooled
across windows, L2-normalized. intfloat/e5-small-v2 runs the same way
as the NON-GATED replication ("passage: " prefix per its model card;
judgment call logged in DECISIONS.md). Writes one .npz per model to
corpus_store/embeddings/ with ids aligned to the chunk registry, plus
a committed hash sidecar in data/.

Usage: run_embed.py [bge|e5]
"""
import hashlib
import json
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
STORE = TR_ROOT / "corpus_store"
WINDOW = 400

MODELS = {
    "bge": ("BAAI/bge-small-en-v1.5", ""),
    "e5": ("intfloat/e5-small-v2", "passage: "),
}


def main():
    import numpy as np
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from transformers import AutoTokenizer

    which = sys.argv[1] if len(sys.argv) > 1 else "bge"
    model_name, prefix = MODELS[which]
    embedder = HuggingFaceEmbedding(model_name=model_name)
    tok = AutoTokenizer.from_pretrained(model_name)

    registry = json.load(open(STORE / "chunk_registry.json"))
    ids = sorted(registry)
    vecs = []
    for i, cid in enumerate(ids):
        text = (STORE / "chunks" / f"{cid}.txt").read_text()
        token_ids = tok.encode(text, add_special_tokens=False)
        windows = [tok.decode(token_ids[j:j + WINDOW])
                   for j in range(0, len(token_ids), WINDOW)] or [text]
        w = np.array([embedder.get_text_embedding(prefix + win)
                      for win in windows])
        v = w.mean(0)
        vecs.append(v / np.linalg.norm(v))
        if (i + 1) % 200 == 0:
            print(f"{i + 1}/{len(ids)}", flush=True)

    X = np.array(vecs, dtype=np.float32)
    out = STORE / "embeddings"
    out.mkdir(exist_ok=True)
    np.savez(out / f"{which}.npz", ids=np.array(ids), X=X)
    sidecar = {
        "model": model_name, "window_tokens": WINDOW,
        "pooling": "mean over windows, L2-normalized",
        "prefix": prefix, "n_chunks": len(ids), "dim": int(X.shape[1]),
        "sha256": hashlib.sha256(X.tobytes()).hexdigest(),
    }
    (TR_ROOT / "data").mkdir(exist_ok=True)
    json.dump(sidecar, open(TR_ROOT / "data" / f"embeddings_{which}.json", "w"),
              indent=2)
    print(json.dumps(sidecar, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
