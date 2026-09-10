"""Prefix KV caching for the council (DECISIONS D17).

Every one of an item's thirteen generations per model shares the same
leading text (the task context and question). That prefix is
prefilled ONCE per item and model into a KV cache; each generation
then passes only its suffix tokens with the cache. batch_generate
documents that prompt caches are not mutated in place, so one cache
serves every generation. The tokenization boundary is verified per
prompt: the prefix's tokens must be an exact prefix of the full
prompt's tokens, otherwise that prompt runs uncached (identical
behavior, slower). Certified by tests/test_prefix_cache.py: cached
greedy output must equal uncached greedy output token for token.
"""
import mlx.core as mx
from mlx_lm.models.cache import make_prompt_cache


def split_tokens(tok, prefix_text, full_text):
    """Token ids for the prefix and the suffix such that prefix+suffix
    equals the full prompt's tokenization; None if the boundary does
    not align."""
    full = tok.encode(full_text, add_special_tokens=False)
    pre = tok.encode(prefix_text, add_special_tokens=False)
    if full[:len(pre)] != pre:
        return None, full
    return pre, full[len(pre):]


def prefill(model, prefix_ids):
    cache = make_prompt_cache(model)
    model(mx.array(prefix_ids)[None], cache=cache)
    mx.eval([c.state for c in cache])
    return cache
