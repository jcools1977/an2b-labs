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
3. Model B (Llama 3.1 8B Instruct, MLX, quantized per the D6 revision:
   legion has 16 GB RAM, bf16 does not fit): embedding-level injection path
   that prepends M soft vectors to the token embeddings.
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

Legion has 16 GB RAM (measured 2026-08-24), which rules out bf16 B; the D6
revision moves B to a single quantization level for all conditions. At
environment build, start from the largest level that plausibly fits (8-bit
is ~8.5 GB of weights) and **measure**: capture peak memory for one
extraction pass, one training step, and one generation, and record the
chosen level plus measured peaks in DECISIONS D6. If 8-bit training does
not leave headroom, drop to 4-bit rather than fighting swap; a run that
thrashes proves nothing about the mechanism.

## What Phase 2 does not do

No adapter training, no sweep, no condition numbers. Those are Phases 3-5,
and the sweep budget (D7, 20 configs, no config 21) does not start until
the plumbing passes the identity test.
