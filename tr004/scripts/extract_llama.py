#!/usr/bin/env python3
"""Extract Llama-3.1-8B hidden states for every instance (D3, D16).

One forward pass per sentence, capturing the target token's
post-block residual state at layers 8, 16, and 24. Unnormalized,
stored float16. Writes corpus_store/embeddings/llama.npz and a hash
sidecar in data/.
"""
import hashlib
import json
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
STORE = TR_ROOT / "corpus_store"
MODEL = "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"
REVISION = "241a666dad6cb93c8ff213d39a7f34a36bf26db4"
LAYERS = (8, 16, 24)


def hidden_at_layers(model, ids, mx):
    h = model.model.embed_tokens(mx.array([ids]))
    out = {}
    for i, layer in enumerate(model.model.layers):
        h = layer(h, mask="causal" if h.shape[1] > 1 else None)
        if i + 1 in LAYERS:
            out[i + 1] = h
        if i + 1 >= max(LAYERS):
            break
    return out


def main():
    import mlx.core as mx
    import numpy as np
    from mlx_lm import load

    model, tok = load(MODEL, revision=REVISION)
    data = json.load(open(STORE / "instances.json"))
    rows = []
    for lemma, v in sorted(data["lemmas"].items()):
        for label in ("lit", "met"):
            for j, r in enumerate(v[label]):
                rows.append((f"{lemma}::{label}::{j:03d}", r))

    ids_out, vecs = [], {L: [] for L in LAYERS}
    for n, (rid, r) in enumerate(rows):
        toks = r["sentence"].split()
        prefix = " ".join(toks[: r["tok_index"]])
        pre_ids = tok.encode(prefix) if prefix else tok.encode("")
        full_ids = tok.encode(r["sentence"])
        pos = min(len(pre_ids), len(full_ids) - 1)
        hs = hidden_at_layers(model, full_ids, mx)
        for L in LAYERS:
            vecs[L].append(np.array(hs[L][0, pos], dtype=np.float16))
        ids_out.append(rid)
        if (n + 1) % 250 == 0:
            print(f"{n + 1}/{len(rows)}", flush=True)

    out = STORE / "embeddings"
    out.mkdir(exist_ok=True)
    arrays = {f"X_l{L}": np.array(vecs[L]) for L in LAYERS}
    np.savez(out / "llama.npz", ids=np.array(ids_out), **arrays)
    sidecar = {"model": MODEL, "revision": REVISION,
               "layers": list(LAYERS), "n": len(ids_out),
               "dim": int(arrays["X_l16"].shape[1]), "dtype": "float16",
               "sha256": hashlib.sha256(
                   arrays["X_l16"].tobytes()).hexdigest()}
    (TR_ROOT / "data").mkdir(exist_ok=True)
    json.dump(sidecar, open(TR_ROOT / "data" / "embeddings_llama.json", "w"),
              indent=2)
    print(json.dumps(sidecar, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
