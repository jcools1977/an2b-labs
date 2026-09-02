#!/usr/bin/env python3
"""Extract bge-small token-level states for every instance (D3, D16):
last_hidden_state of the target token's first wordpiece, located by
fast-tokenizer character offsets. Unnormalized, float16. Writes
corpus_store/embeddings/bge.npz and a hash sidecar.
"""
import hashlib
import json
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
STORE = TR_ROOT / "corpus_store"
MODEL = "BAAI/bge-small-en-v1.5"


def main():
    import numpy as np
    import torch
    from transformers import AutoModel, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModel.from_pretrained(MODEL)
    model.eval()
    data = json.load(open(STORE / "instances.json"))
    rows = []
    for lemma, v in sorted(data["lemmas"].items()):
        for label in ("lit", "met"):
            for j, r in enumerate(v[label]):
                rows.append((f"{lemma}::{label}::{j:03d}", r))

    ids_out, vecs = [], []
    with torch.no_grad():
        for n, (rid, r) in enumerate(rows):
            toks = r["sentence"].split()
            start = len(" ".join(toks[: r["tok_index"]]))
            if r["tok_index"] > 0:
                start += 1
            enc = tok(r["sentence"], return_offsets_mapping=True,
                      truncation=True, max_length=512, return_tensors="pt")
            offsets = enc.pop("offset_mapping")[0].tolist()
            pos = next((i for i, (a, b) in enumerate(offsets)
                        if b > a and a >= start), len(offsets) - 1)
            h = model(**enc).last_hidden_state[0, pos]
            vecs.append(h.numpy().astype(np.float16))
            ids_out.append(rid)
            if (n + 1) % 500 == 0:
                print(f"{n + 1}/{len(rows)}", flush=True)

    out = STORE / "embeddings"
    out.mkdir(exist_ok=True)
    X = np.array(vecs)
    np.savez(out / "bge.npz", ids=np.array(ids_out), X=X)
    sidecar = {"model": MODEL, "n": len(ids_out), "dim": int(X.shape[1]),
               "dtype": "float16",
               "sha256": hashlib.sha256(X.tobytes()).hexdigest()}
    json.dump(sidecar, open(TR_ROOT / "data" / "embeddings_bge.json", "w"),
              indent=2)
    print(json.dumps(sidecar, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
