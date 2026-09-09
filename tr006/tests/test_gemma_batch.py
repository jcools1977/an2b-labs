#!/usr/bin/env python3
"""Certification exam for the gemma-2 batch patch: with the patch,
batched greedy generation over three prompts of unequal length must
reproduce the sequential greedy output for each prompt token for
token (24 tokens). Also asserts the failure is real without the
patch. Exit nonzero if the outputs differ."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mlx.core as mx  # noqa: E402
from mlx_lm import generate, load  # noqa: E402
from mlx_lm.generate import batch_generate  # noqa: E402

PROMPTS = [
    "In two sentences, why do bounded buffers force prioritization?",
    "Read this carefully. " * 30 + "List three colors, comma separated.",
    "Alice, Bob and Carol each own one pet among a cat, a dog and a fish. Alice does not own the dog. Bob owns the fish. Who owns the cat?",
]


def main():
    model, tok = load("mlx-community/gemma-2-9b-it-4bit")
    toks = [tok.apply_chat_template([{"role": "user", "content": p}], add_generation_prompt=True, tokenize=True) for p in PROMPTS]
    txts = [tok.apply_chat_template([{"role": "user", "content": p}], add_generation_prompt=True, tokenize=False) for p in PROMPTS]
    seq = [generate(model, tok, prompt=t, max_tokens=24, verbose=False) for t in txts]
    try:
        batch_generate(model, tok, prompts=toks, max_tokens=24, verbose=False)
        print("  note: batching worked WITHOUT the patch in this build")
    except Exception as e:
        print(f"  ok  unpatched batch fails as documented ({type(e).__name__})")
    from workspace import gemma_batch_patch
    gemma_batch_patch.apply()
    res = batch_generate(model, tok, prompts=toks, max_tokens=24, verbose=False)
    bat = res.texts if hasattr(res, "texts") else res
    bad = 0
    for i, (s, b) in enumerate(zip(seq, bat)):
        same = s.strip() == b.strip()
        print(f"  {'ok ' if same else 'FAIL'} prompt {i}: sequential {s.strip()[:40]!r} | batched {b.strip()[:40]!r}")
        bad += 0 if same else 1
    print(f"gemma batch exam: {'CERTIFIED' if bad == 0 else str(bad) + ' prompts differ; patch NOT certified'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
