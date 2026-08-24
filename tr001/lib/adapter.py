"""Adapter construction and the C3 embedding assembly (DECISIONS D6, D20).

Single source for both training and eval so the soft-prefix placement
cannot drift between them: the sequence is always
[soft(M) | chat-templated prompt | (answer tokens, training only)].
The C3 prompt frame is identical to C4's (question, no text context);
the soft prefix is the only added channel.
"""
import json

import mlx.core as mx
import mlx.nn as nn

M_SOFT = 32
K_TEXT_TOKENS = 32  # C2's budget; compute match requires M_SOFT <= K


def build_adapter(config, in_dim, d_b):
    assert M_SOFT <= K_TEXT_TOKENS, "compute mismatch: M > K (protocol section 4)"
    if config["arch"] == "linear":
        adapter = nn.Linear(in_dim, M_SOFT * d_b)
    elif config["arch"] == "mlp":
        adapter = nn.Sequential(
            nn.Linear(in_dim, 1024), nn.GELU(), nn.Linear(1024, M_SOFT * d_b)
        )
    else:
        raise ValueError(config["arch"])
    adapter.set_dtype(mx.bfloat16)  # D6: bf16 adapter, measured
    return adapter


def latent_for(stored, rows_index, pooling, h):
    row = rows_index[h]
    if pooling == "final":
        return stored["final"][row]  # (4096,)
    if pooling == "last4":
        return stored["last4"][row].reshape(-1)  # (16384,)
    raise ValueError(pooling)


def soft_prefix(adapter, latent_np, d_b, act_dtype):
    x = mx.array(latent_np).astype(mx.bfloat16)
    return adapter(x).reshape(1, M_SOFT, d_b).astype(act_dtype)


def load_latent_cache(tr_root):
    import numpy as np

    caches = sorted((tr_root / "cache").glob("latents_*.index.json"))
    if len(caches) != 1:
        raise SystemExit(f"expected exactly one latent cache, found {len(caches)}")
    with open(caches[0]) as fh:
        idx = json.load(fh)
    stored = np.load(str(caches[0]).replace(".index.json", ".npz"))
    return stored, idx["rows"], idx["config_hash"]
