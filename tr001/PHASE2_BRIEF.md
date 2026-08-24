# TR-001 Phase 2 brief (for the legion session)

Phase 2 is the model plumbing: Model A extraction, Model B soft-prompt
injection, and the caching layer. It runs on legion and nowhere else.
Read the protocol (`../TR001_latent_corpus_callosum.md`) and `DECISIONS.md`
first; nothing here overrides either.

## Scope

1. Environment build from `requirements.txt` (record any forced pin change
   in DECISIONS D9 before producing anything).
2. Model A (Qwen 3 8B, MLX): forward pass over a passage, mean-pooled
   final-layer hidden states, cached to disk for all 2,500 passages in one
   pass. Extraction config (model revision, quantization, pooling) recorded
   with the cache per D6; any later change invalidates the cache wholesale.
3. Model B (Llama 3.1 8B Instruct, MLX, unquantized bf16 for training):
   embedding-level injection path that prepends M soft vectors to the token
   embeddings.
4. Generation and answer extraction wiring, shared by all four conditions.

## Hard gate: tokenizer verification is an assert, not a manual check

The extraction/eval scripts must assert, before doing anything else, that
the production Model B build's tokenizer vocab hash equals
`data/MANIFEST.json -> tokenizer.vocab_sha256` (hash of the sorted vocab
JSON, same recipe as `scripts/build_split.py`). On mismatch the script
exits nonzero: the 200-400 filter was measured with the wrong ruler and the
split rebuilds (cheap, deterministic, seed 7). A mismatch is never excused
or worked around.

## Red-then-green for Phase 2 itself: the injection identity test

Before any adapter exists, write the test that proves the injection path is
wired to the right nerves:

- Take a short text prompt. Look up its actual token embeddings from B's
  embedding table. Feed those through the soft-prompt injection path (as if
  they were adapter output). Greedy-generate.
- Assert the output is identical to greedy generation over the normal
  tokenized path for the same prompt.

If injecting real token embeddings does not reproduce normal behavior, the
plumbing is broken, and the alternative is discovering that as a mysterious
C3 floor collapse three phases later. Run it red first (e.g. against a
deliberately mis-wired injection, offset by one position or wrong dtype) to
prove the test can fail, then green. Wire it into `verify.sh` alongside the
existing checks.

## Memory evidence

bf16 Llama 8B plus adapter gradients and activations on 32-vector prefixes
over short sequences should fit comfortably, but capture the actual peak
memory in the first training config's log, so the D6 note about a
quantization fallback is evidence-based either way, used or not.

## What Phase 2 does not do

No adapter training, no sweep, no condition numbers. Those are Phases 3-5,
and the sweep budget (D7, 20 configs, no config 21) does not start until
the plumbing passes the identity test.
