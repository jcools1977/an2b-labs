"""mlx-lm 0.31.3 gemma-2 batched attention fix (DECISIONS D13).

In gemma2.Attention, grouped-query heads reshape scores to five
dimensions (B, kv_heads, repeats, L, L) while the batched mask from
create_attention_mask arrives as (B, 1, L, L); the broadcast fails and
batch_generate dies (surfacing as a ZeroDivisionError in its stats).
Single-prompt generation is unaffected. This wrapper inserts the
missing axis so the mask reads (B, 1, 1, L, L). Certified by
tests/test_gemma_batch.py: batched greedy outputs must equal
sequential greedy outputs token for token, or the patch is not used.
"""
import mlx.core as mx
from mlx_lm.models import gemma2

_orig = gemma2.Attention.__call__


def _patched(self, x, mask=None, cache=None):
    if mask is not None and getattr(mask, "ndim", 0) == 4 and getattr(self, "repeats", 1) > 1:
        mask = mx.expand_dims(mask, 2)
    return _orig(self, x, mask=mask, cache=cache)


def apply():
    gemma2.Attention.__call__ = _patched
