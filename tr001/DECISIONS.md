# TR-001 DECISIONS

Every judgment call made during implementation, per the covenant. Protocol
thresholds themselves are untouched; entries here only resolve ambiguity,
always toward the interpretation that makes H1 harder to pass.

## D1. Repo layout and pre-registration
Protocol files copied verbatim to repo root (diff-verified identical to the
original import, which stays untracked under `AN2BLabs/`). Pre-registration
commit `7b7262d` (2026-08-24) contains protocols + CLAUDE.md only, no results
machinery, pushed to github.com/jcools1977/an2b-labs before any Phase 0 code.

## D2. Numeric thresholds for negative controls 1-3
The protocol states controls qualitatively; these numbers are fixed here,
before any results exist, and implemented in `checks/check_controls.py`:

- Controls 1 and 2 ("collapse toward floor"): random-adapter F1 and
  shuffled-pairing F1 must each be within **3.0 F1 points of C4**.
- Control 3 ("delta must equal roughly the full C3-over-C4 margin"):
  read two-sided, the harder interpretation. The ablation delta
  (C3 minus ablated) must be within **max(20% of the margin, 2.0 F1
  points)** of the C3-minus-C4 margin, in both directions.
- Compute match is enforced as a check, not a convention: M > K is a
  hard failure.

## D3. Confidence interval on the primary comparison
The "CI excluding zero" in the pass criterion is computed on the **paired
per-item C3 minus C2 F1 difference** (10,000 bootstrap resamples), not on
two marginal CIs. Paired is harder to game and is the honest reading.

## D4. Token accounting
K tokens for the C2 summary are counted with **Model B's tokenizer** (B is
the consumer, so B's tokenizer prices the text channel). Summaries are
generated with a cap and hard-truncated to exactly K = 32 tokens. Passage
length filtering (200-400 tokens) also uses B's tokenizer.

## D5. Data split at passage level
SQuAD reuses passages across questions, so the train/eval split is made on
**disjoint passage sets**, never QA pairs. The hash-overlap leakage check
(`checks/check_leakage.py`) runs on lowercased, whitespace-collapsed passage
text, SHA-256, and any overlap is a hard failure.

## D6. Quantization consistency for cached latents
Model A extraction may run quantized for memory, but the extraction config
(model revision, quantization, pooling) is fixed **once** and recorded with
the cache. Training and eval latents must come from the same config.
If the extraction config ever changes mid-experiment, the cached latents
are **invalidated wholesale**: delete the entire cache and re-extract
everything. Never patch a cache. Model B is unquantized bf16 during adapter
training (gradients traverse frozen B).

## D7. Pooling is a sweep dimension inside the 20-config cap
The protocol allows last-4-layer concat as an alternative to final-layer
mean pooling. Allocation, fixed now: **linear/final-layer 6 configs,
linear/last-4-concat 4, MLP/final-layer 6, MLP/last-4-concat 4 = 20 total.**
Escalation order per protocol: linear before MLP; within each architecture,
final-layer before concat. Every config tried is appended to
`results/sweep_log.jsonl` regardless of outcome.

## D8. Seeds
The two protocol seeds are **1 and 2**. Seed governs adapter init, training
shuffle, and any sampling; the data split uses its own fixed seed (7),
identical across both runs, so replication tests the mechanism rather than
the split.

## D9. Dependency pins
`requirements.txt` pins the versions current on PyPI at scaffold time
(2026-08-24). If the legion environment build forces a different pin, the
change is recorded here with the reason, and no results produced under the
old pin are mixed with results under the new one.
