#!/usr/bin/env python3
"""The thermometers (D8, D18): per-token full-vocabulary entropy and NLL
for every corpus document and its seeded sentence-shuffled twin, both
scoring models, sequential residency.

Cache: corpus_store/entropy/<config_hash>/<model>/<doc_id>.npz
(entropy series, nll series, paragraph-boundary token indices).
Wholesale invalidation on any config change (TR-001 D6 pattern).
Resumable per (model, doc).
"""
import hashlib
import json
import re
import sys
import time
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
DOCS = TR_ROOT / "corpus_store" / "docs"

CONFIG = {
    "models": {
        "qwen": ("mlx-community/Qwen3-1.7B-4bit",
                 "3b1b1768f8f8cf8351c712464f906e86c2b8269e"),
        "llama": ("mlx-community/Meta-Llama-3.1-8B-Instruct-4bit",
                  "241a666dad6cb93c8ff213d39a7f34a36bf26db4"),
    },
    "window": 2048, "stride": 1024, "min_context": 1024,
    "shuffle": "sentence split on terminal punctuation + whitespace, "
               "seeded Fisher-Yates per doc id, single-space rejoin (D18)",
}
CONFIG_HASH = hashlib.sha256(
    json.dumps(CONFIG, sort_keys=True).encode()).hexdigest()[:16]


def shuffled_text(doc_id, text):
    import random
    sents = re.split(r"(?<=[.!?])\s+", text.replace("\n", " "))
    sents = [s for s in sents if s.strip()]
    rng = random.Random(int(hashlib.sha256(
        f"shuffle:{doc_id}".encode()).hexdigest()[:12], 16))
    rng.shuffle(sents)
    return " ".join(sents)


def paragraph_boundaries(text, tok):
    enc = tok(text, add_special_tokens=False, return_offsets_mapping=True)
    offsets = enc["offset_mapping"]
    starts = [m.end() + 2 for m in re.finditer(r"\n\n", text)]
    bounds, j = [], 0
    for s in starts:
        while j < len(offsets) and offsets[j][0] < s:
            j += 1
        if j < len(offsets):
            bounds.append(j)
    return bounds


def score_series(model, ids):
    """Entropy (nats) + NLL per position, strided windows, positions with
    >= min_context context only. Returns (positions, entropy, nll)."""
    import mlx.core as mx
    import numpy as np

    W, S, C = CONFIG["window"], CONFIG["stride"], CONFIG["min_context"]
    pos_out, ent_out, nll_out = [], [], []
    recorded = -1
    start = 0
    while start < len(ids) - 1:
        chunk = ids[start:start + W]
        logits = model(mx.array(chunk)[None])[0]  # [T, V]
        logp = logits - mx.logsumexp(logits, axis=-1, keepdims=True)
        p = mx.exp(logp)
        ent = -(p * logp).sum(axis=-1)  # [T]
        ent = np.array(ent.astype(mx.float32))
        logp_np = None
        for t in range(len(chunk) - 1):
            gpos = start + t + 1  # predicting token at gpos
            if gpos <= recorded or (t + 1) < C and start > 0:
                continue
            if gpos < C:  # never score tokens with under min_context
                continue
            if logp_np is None:
                logp_np = np.array(logp.astype(mx.float32))
            pos_out.append(gpos)
            ent_out.append(float(ent[t]))
            nll_out.append(float(-logp_np[t, ids[gpos]]))
            recorded = gpos
        if start + W >= len(ids):
            break
        start += S
    return pos_out, ent_out, nll_out


def main():
    import numpy as np
    from mlx_lm import load as mlx_load

    cache = TR_ROOT / "corpus_store" / "entropy" / CONFIG_HASH
    manifest = json.load(open(TR_ROOT / "data" / "CORPUS_MANIFEST.json"))
    doc_ids = sorted(manifest["documents"])
    jobs = [(d, False) for d in doc_ids] + [(d, True) for d in doc_ids]

    (cache / "_config.json").parent.mkdir(parents=True, exist_ok=True)
    json.dump(CONFIG, open(cache / "_config.json", "w"), indent=2)

    for mkey, (repo, pin) in CONFIG["models"].items():
        out_dir = cache / mkey
        out_dir.mkdir(exist_ok=True)
        todo = [(d, sh) for d, sh in jobs
                if not (out_dir / f"{d}{'__shuffled' if sh else ''}.npz").exists()]
        if not todo:
            print(f"[{mkey}] complete")
            continue
        snap = (Path.home() / ".cache/huggingface/hub" /
                ("models--" + repo.replace("/", "--")) / "snapshots" / pin)
        print(f"[{mkey}] loading @ {pin[:12]}; {len(todo)} series to score",
              flush=True)
        model, tok = mlx_load(str(snap))
        hf_tok = getattr(tok, "_tokenizer", tok)
        t0 = time.time()
        for n, (did, sh) in enumerate(todo, 1):
            text = (DOCS / f"{did}.txt").read_text()
            if sh:
                text = shuffled_text(did, text)
            ids = tok.encode(text)
            bounds = paragraph_boundaries(text, hf_tok)
            pos, ent, nll = score_series(model, ids)
            np.savez_compressed(
                out_dir / f"{did}{'__shuffled' if sh else ''}.npz",
                positions=np.array(pos, dtype=np.int32),
                entropy=np.array(ent, dtype=np.float32),
                nll=np.array(nll, dtype=np.float32),
                boundaries=np.array(bounds, dtype=np.int32),
                n_tokens=len(ids),
            )
            if n % 20 == 0 or n == len(todo):
                print(f"  [{mkey}] {n}/{len(todo)} "
                      f"({(time.time()-t0)/n:.1f} s/series)", flush=True)
        del model
    print(f"scoring complete, cache {CONFIG_HASH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
