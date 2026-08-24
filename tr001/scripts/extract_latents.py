#!/usr/bin/env python3
"""Model A extraction (Phase 2): mean-pooled hidden states for every unique
passage in the split, cached once, per D6 and D12.

- Raw tokenizer-encode of the passage. Never the chat template (D12).
- Loads the MANIFEST-pinned snapshot only (D13 revision gate).
- Caches BOTH the final-layer (post-norm) pooled state and the last-4-block
  (pre-norm) pooled states, so the D7 concat arm never re-extracts.
- Sequential residency: this process loads Qwen and nothing else.
- Checkpoints every --checkpoint-every passages; a re-run with the same
  extraction config resumes, a re-run with a different config refuses to
  reuse anything (wholesale invalidation, D6).
"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
import mlx.core as mx  # noqa: E402
from mlx_lm import load as mlx_load  # noqa: E402
from mlx_lm.models.base import create_attention_mask  # noqa: E402

from checks.check_leakage import normalize  # noqa: E402
from lib.gates import A_REPO, TR_ROOT, pinned_snapshot  # noqa: E402

POOLING_RECIPE = "mean over sequence; final=post-norm last block; last4=pre-norm block outputs"


def passage_hash(text):
    return hashlib.sha256(normalize(text).encode("utf-8")).hexdigest()


def unique_passages():
    seen = {}
    for name in ("train.jsonl", "eval.jsonl"):
        with open(TR_ROOT / "data" / name) as fh:
            for line in fh:
                row = json.loads(line)
                seen.setdefault(passage_hash(row["passage"]), row["passage"])
    return dict(sorted(seen.items()))  # deterministic order


def pooled_states(model, tokenizer, passage):
    inner = model.model
    ids = tokenizer.encode(passage)  # raw encode, no chat template (D12)
    h = inner.embed_tokens(mx.array(ids)[None])
    mask = create_attention_mask(h, None)
    n = len(inner.layers)
    last4 = []
    for i, layer in enumerate(inner.layers):
        h = layer(h, mask, None)
        if i >= n - 4:
            last4.append(h)
    final = inner.norm(h)

    def pool(a):
        return np.array(a.mean(axis=1)[0].astype(mx.float32))

    return pool(final), np.stack([pool(a) for a in last4], axis=0), len(ids)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="smoke test: first N passages only")
    ap.add_argument("--checkpoint-every", type=int, default=250)
    args = ap.parse_args()

    snap, pin = pinned_snapshot(A_REPO)
    config = {
        "a_repo": A_REPO,
        "hf_commit": pin,
        "quantization": "4bit (as published in pinned snapshot)",
        "pooling": POOLING_RECIPE,
        "chat_template": "none (D12)",
    }
    config_hash = hashlib.sha256(
        json.dumps(config, sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]

    cache_dir = TR_ROOT / "cache"
    cache_dir.mkdir(exist_ok=True)
    npz_path = cache_dir / f"latents_{config_hash}.npz"
    index_path = cache_dir / f"latents_{config_hash}.index.json"

    passages = unique_passages()
    if args.limit:
        passages = dict(list(passages.items())[: args.limit])

    done = {}
    if index_path.exists() and npz_path.exists():
        with open(index_path) as fh:
            idx = json.load(fh)
        if idx["config"] != config:  # same hash but paranoia is free
            raise SystemExit("CACHE CONFLICT: index config mismatch; delete the cache (D6)")
        stored = np.load(npz_path)
        done = {
            h: (stored["final"][i], stored["last4"][i])
            for h, i in idx["rows"].items()
            if h in passages
        }
        print(f"resuming: {len(done)}/{len(passages)} already extracted")

    mx.reset_peak_memory()
    print(f"loading {A_REPO} @ {pin[:12]} (pinned snapshot)")
    model, tokenizer = mlx_load(str(snap))

    order, finals, last4s = [], [], []
    for h in passages:
        if h in done:
            order.append(h)
            finals.append(done[h][0])
            last4s.append(done[h][1])

    def save():
        rows = {h: i for i, h in enumerate(order)}
        np.savez_compressed(
            npz_path, final=np.stack(finals), last4=np.stack(last4s)
        )
        with open(index_path, "w") as fh:
            json.dump({"config": config, "config_hash": config_hash, "rows": rows}, fh)

    todo = [(h, p) for h, p in passages.items() if h not in done]
    t0, tokens_done = time.time(), 0
    for k, (h, passage) in enumerate(todo, 1):
        final, last4, n_tok = pooled_states(model, tokenizer, passage)
        order.append(h)
        finals.append(final)
        last4s.append(last4)
        tokens_done += n_tok
        if k % args.checkpoint_every == 0 or k == len(todo):
            save()
            rate = tokens_done / max(time.time() - t0, 1e-9)
            print(
                f"{len(order)}/{len(passages)} passages; {rate:.0f} tok/s; "
                f"peak {mx.get_peak_memory()/2**30:.2f} GB",
                flush=True,
            )

    if todo:
        save()
    print(
        json.dumps(
            {
                "passages": len(order),
                "final_shape": list(np.stack(finals).shape),
                "last4_shape": list(np.stack(last4s).shape),
                "peak_memory_gb": round(mx.get_peak_memory() / 2**30, 2),
                "cache": str(npz_path.relative_to(TR_ROOT)),
                "config_hash": config_hash,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
