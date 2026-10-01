"""Per-turn embeddings with bge-small-en-v1.5 (CLS, L2-normalized),
cached per run as results/emb/<run_id>.npy. The same embedder serves
the labeler (mode-lock test, D4) and the indicators (D5)."""
import hashlib
import json
from pathlib import Path

import numpy as np

TR = Path(__file__).resolve().parents[1]
EMB_DIR = TR / "results" / "emb"
_model = {}


def _load():
    if not _model:
        import torch
        from transformers import AutoModel, AutoTokenizer
        name = "BAAI/bge-small-en-v1.5"
        _model["tok"] = AutoTokenizer.from_pretrained(name)
        _model["m"] = AutoModel.from_pretrained(name).eval()
        _model["torch"] = torch
    return _model


def embed_texts(texts, batch=64):
    m = _load()
    torch = m["torch"]
    out = []
    with torch.no_grad():
        for lo in range(0, len(texts), batch):
            enc = m["tok"](texts[lo:lo + batch], padding=True, truncation=True, max_length=512, return_tensors="pt")
            h = m["m"](**enc).last_hidden_state[:, 0]
            h = torch.nn.functional.normalize(h, dim=-1)
            out.append(h.numpy().astype(np.float32))
    return np.concatenate(out) if out else np.zeros((0, 384), np.float32)


def run_embeddings(run_id, texts):
    EMB_DIR.mkdir(parents=True, exist_ok=True)
    p = EMB_DIR / f"{run_id}.npy"
    if p.exists():
        E = np.load(p)
        if len(E) == len(texts):
            return E
    E = embed_texts(texts)
    np.save(p, E)
    return E
