#!/usr/bin/env python3
"""TR-002r embedding extraction, one space per invocation (D7).

Usage: extract_spaces.py <space> [--splits A,B,eval,ood]
Spaces: bge | e5 | minilm | llama4 | llama8 | qwen4 | gemma4

Resumable: checkpoints every 2,000 chunks per split. All outputs
L2-normalized float16 in corpus_store/embeddings/<space>__<split>.npz
with hash sidecars in data/.
"""
import hashlib
import json
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
STORE = TR_ROOT / "corpus_store"
CKPT_EVERY = 500
N_CAP = {"A": 16000, "B": 16000, "eval": None, "ood": None}

ENCODERS = {
    "bge": ("BAAI/bge-small-en-v1.5", "cls", ""),
    "e5": ("intfloat/e5-small-v2", "mean", "passage: "),
    "minilm": ("sentence-transformers/all-MiniLM-L6-v2", "mean", ""),
}
DECODERS = {
    "llama4": ("mlx-community/Meta-Llama-3.1-8B-Instruct-4bit",
               "241a666dad6cb93c8ff213d39a7f34a36bf26db4"),
    "llama8": ("mlx-community/Meta-Llama-3.1-8B-Instruct-8bit", None),
    "qwen4": ("mlx-community/Qwen3-1.7B-4bit",
              "3b1b1768f8f8cf8351c712464f906e86c2b8269e"),
    "gemma4": ("mlx-community/gemma-2-9b-it-4bit", None),
}


def load_split_ids(split):
    sp = json.load(open(STORE / "splits.json"))["splits"][split]
    cap = N_CAP.get(split)
    return sp[:cap] if cap else sp


def texts_for(ids):
    for cid in ids:
        yield cid, (STORE / "chunks" / f"{cid}.txt").read_text()


def run_split(space, split, embed_fn):
    import numpy as np
    out = STORE / "embeddings"
    out.mkdir(exist_ok=True)
    final = out / f"{space}__{split}.npz"
    ckpt = out / f"{space}__{split}.ckpt.npz"
    ids = load_split_ids(split)
    done_ids, vecs = [], []
    if final.exists():
        print(f"{space}/{split}: already complete", flush=True)
        return
    if ckpt.exists():
        d = np.load(ckpt, allow_pickle=True)
        done_ids = [str(x) for x in d["ids"]]
        vecs = list(d["X"])
        print(f"{space}/{split}: resuming at {len(done_ids)}", flush=True)
    todo = ids[len(done_ids):]
    for i, (cid, text) in enumerate(texts_for(todo)):
        v = embed_fn(text)
        v = v / (np.linalg.norm(v) + 1e-12)
        vecs.append(v.astype(np.float16))
        done_ids.append(cid)
        if (len(done_ids) % CKPT_EVERY) == 0:
            np.savez(ckpt, ids=np.array(done_ids), X=np.array(vecs))
            print(f"{space}/{split}: {len(done_ids)}/{len(ids)}", flush=True)
    X = np.array(vecs)
    np.savez(final, ids=np.array(done_ids), X=X)
    ckpt.unlink(missing_ok=True)
    (TR_ROOT / "data").mkdir(exist_ok=True)
    side = {"space": space, "split": split, "n": len(done_ids),
            "dim": int(X.shape[1]),
            "sha256": hashlib.sha256(X.tobytes()).hexdigest()}
    json.dump(side, open(TR_ROOT / "data" /
                         f"emb_{space}_{split}.json", "w"), indent=2)
    print(f"{space}/{split}: DONE {side}", flush=True)


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
    model, tok = load(name, revision=rev) if rev else load(name)
    calls = [0]

    def fn(text):
        ids = tok.encode(text)[:512]
        h = model.model.embed_tokens(mx.array([ids]))
        for layer in model.model.layers:
            h = layer(h, mask="causal" if h.shape[1] > 1 else None)
        h = model.model.norm(h)
        out = np.array(h[0], dtype=np.float32).mean(axis=0)
        calls[0] += 1
        if calls[0] % 100 == 0:
            mx.clear_cache()  # metal buffer cache bloats over long loops
        return out
    return fn


def main():
    space = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2].isdigit():
        N_CAP["A"] = N_CAP["B"] = int(sys.argv[2])
    splits = (sys.argv[3].split(",") if len(sys.argv) > 3
              else ["eval", "ood", "A", "B"])
    fn = encoder_fn(space) if space in ENCODERS else decoder_fn(space)
    for split in splits:
        run_split(space, split, fn)
    return 0


if __name__ == "__main__":
    sys.exit(main())
