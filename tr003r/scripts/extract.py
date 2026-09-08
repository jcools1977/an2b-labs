#!/usr/bin/env python3
"""TR-003r embedding extraction, one space per invocation.

Embeds every text id listed in corpus_store/store_{seed}.json
(store chunks, anchor pool, Q1/Q2 queries, scrambled anchors) for
both seeds. The encoder and decoder functions are TR-002r's
(scripts/extract_spaces.py, sha256 3939a56a1f24f723... at commit
d7aaccf), copied verbatim below with one change: float32 output
instead of float16, so score margins are not quantized. Resumable:
checkpoint every 500 texts. Outputs corpus_store/emb/<space>.npz
(ids, X) with a hash sidecar in data/.

Usage: extract.py <space>   (bge | e5 | minilm | llama4 | qwen4 | gemma4)
"""
import hashlib
import json
import sys
from pathlib import Path

TR = Path(__file__).resolve().parents[1]
STORE = TR / "corpus_store"
CKPT_EVERY = 500

ENCODERS = {
    "bge": ("BAAI/bge-small-en-v1.5", "cls", ""),
    "e5": ("intfloat/e5-small-v2", "mean", "passage: "),
    "minilm": ("sentence-transformers/all-MiniLM-L6-v2", "mean", ""),
}
DECODERS = {
    "llama4": ("mlx-community/Meta-Llama-3.1-8B-Instruct-4bit",
               "241a666dad6cb93c8ff213d39a7f34a36bf26db4"),
    "qwen4": ("mlx-community/Qwen3-1.7B-4bit",
              "3b1b1768f8f8cf8351c712464f906e86c2b8269e"),
    "gemma4": ("mlx-community/gemma-2-9b-it-4bit",
               "ff12eb39da2cd9b3b0f4b4f9ffb274603f05bb29"),
}


def all_text_ids():
    ids = set()
    for p in sorted(STORE.glob("store_*.json")):
        ids.update(json.load(open(p))["text_ids"])
    return sorted(ids)


def encoder_fn(space):
    import numpy as np
    import torch
    from transformers import AutoModel, AutoTokenizer
    name, pool, prefix = ENCODERS[space]
    tok = AutoTokenizer.from_pretrained(name)
    model = AutoModel.from_pretrained(name)
    model.eval()

    def fn(text):
        with torch.no_grad():
            enc = tok(prefix + text, truncation=True, max_length=512,
                      return_tensors="pt")
            h = model(**enc).last_hidden_state[0]
            v = h[0] if pool == "cls" else h.mean(0)
            return v.numpy().astype(np.float32)
    return fn


def decoder_fn(space):
    import mlx.core as mx
    import numpy as np
    from mlx_lm import load
    name, rev = DECODERS[space]
    model, tok = load(name, revision=rev)
    calls = [0]

    def fn(text):
        ids = tok.encode(text)[:512]
        h = model.model(mx.array([ids]))
        out = np.array(h[0].astype(mx.float32)).mean(axis=0)
        calls[0] += 1
        if calls[0] % 100 == 0:
            mx.clear_cache()
        return out
    return fn


def main():
    import numpy as np
    space = sys.argv[1]
    out = STORE / "emb"
    out.mkdir(exist_ok=True)
    final = out / f"{space}.npz"
    ckpt = out / f"{space}.ckpt.npz"
    if final.exists():
        print(f"{space}: already complete", flush=True)
        return 0
    ids = all_text_ids()
    done_ids, vecs = [], []
    if ckpt.exists():
        d = np.load(ckpt, allow_pickle=True)
        done_ids = [str(x) for x in d["ids"]]
        vecs = list(d["X"])
        print(f"{space}: resuming at {len(done_ids)}", flush=True)
    fn = encoder_fn(space) if space in ENCODERS else decoder_fn(space)
    for tid in ids[len(done_ids):]:
        v = fn((STORE / "texts" / f"{tid}.txt").read_text())
        v = v / (np.linalg.norm(v) + 1e-12)
        vecs.append(v.astype(np.float32))
        done_ids.append(tid)
        if len(done_ids) % CKPT_EVERY == 0:
            np.savez(ckpt, ids=np.array(done_ids), X=np.array(vecs))
            print(f"{space}: {len(done_ids)}/{len(ids)}", flush=True)
    X = np.array(vecs, dtype=np.float32)
    np.savez(final, ids=np.array(done_ids), X=X)
    ckpt.unlink(missing_ok=True)
    (TR / "data").mkdir(exist_ok=True)
    side = {"space": space, "n": len(done_ids), "dim": int(X.shape[1]),
            "model": (ENCODERS.get(space) or DECODERS.get(space))[0],
            "sha256": hashlib.sha256(X.tobytes()).hexdigest()}
    json.dump(side, open(TR / "data" / f"emb_{space}.json", "w"), indent=2)
    print(f"{space}: DONE {side}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
