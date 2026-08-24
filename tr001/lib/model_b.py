"""Model B (answerer) loading, soft-prompt injection, and deterministic
greedy generation.

Injection uses mlx-lm's native input_embeddings path: the given vectors
replace the embedding lookup for the prefill, then generation continues
token-by-token through the same KV cache. tests/test_injection_identity.py
is the proof this is wired correctly; it gates the D7 sweep clock.
"""
import mlx.core as mx
from mlx_lm import load as _mlx_load
from mlx_lm.models.cache import make_prompt_cache

from .gates import B_REPO, assert_b_tokenizer, pinned_snapshot


def load_b():
    snap, pin = pinned_snapshot(B_REPO)
    model, tokenizer = _mlx_load(str(snap))
    assert_b_tokenizer(tokenizer)
    return model, tokenizer


def _eos_ids(tokenizer):
    ids = getattr(tokenizer, "eos_token_ids", None)
    if ids is None:
        ids = {tokenizer.eos_token_id}
    return set(ids)


def _greedy_continue(model, logits, cache, max_tokens, eos_ids):
    out = []
    y = mx.argmax(logits[:, -1, :], axis=-1)
    for _ in range(max_tokens):
        t = int(y.item())
        out.append(t)
        if t in eos_ids:
            break
        logits = model(y[None], cache=cache)
        y = mx.argmax(logits[:, -1, :], axis=-1)
    return out


def greedy_from_ids(model, tokenizer, ids, max_tokens=32):
    """Standard path: prefill from token ids, then greedy decode."""
    cache = make_prompt_cache(model)
    logits = model(mx.array(ids)[None], cache=cache)
    return _greedy_continue(model, logits, cache, max_tokens, _eos_ids(tokenizer))


def greedy_from_embeddings(model, tokenizer, embeds, max_tokens=32):
    """Injection path: prefill from embedding-space vectors (soft prompt
    and/or real token embeddings), then greedy decode. The inputs array is
    a dummy; input_embeddings replaces the lookup entirely."""
    cache = make_prompt_cache(model)
    dummy = mx.zeros((1, embeds.shape[1]), dtype=mx.int32)
    logits = model(dummy, cache=cache, input_embeddings=embeds)
    return _greedy_continue(model, logits, cache, max_tokens, _eos_ids(tokenizer))
