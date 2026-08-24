# TR-001 DECISIONS

Every judgment call made during implementation, per the covenant. Protocol
thresholds themselves are untouched; entries here only resolve ambiguity,
always toward the interpretation that makes H1 harder to pass.

## D1. Repo layout and pre-registration
Protocol files copied verbatim to repo root (diff-verified identical to the
original import, which stays untracked under `AN2BLabs/`). Pre-registration
commit `7b7262d` (2026-08-24) contains protocols + CLAUDE.md only, no results
machinery, pushed to github.com/jcools1977/an2b-labs before any Phase 0 code.

The **root copies are canonical**; the nested `AN2BLabs/` import on disk is
dead, kept only as the original download, untracked, diff-verified identical
at the time of the pre-registration commit. Nothing reads from it.

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

**Revision, 2026-08-24, before any Phase 2 code:** legion measures 16 GB
RAM, and bf16 B is ~16 GB of weights alone, so the paragraph above cannot
hold as written. Model B therefore runs **quantized for training and eval
alike**: one quantization level, chosen at environment build as the largest
that leaves training headroom (measure, do not assume), then used for every
condition C1-C4 and every control, so all comparisons share the same ruler.
Gradients still traverse the frozen quantized B to reach the adapter. The
chosen level, and the measured peak memory of the first training config,
get recorded here.

This is QLoRA's training configuration (Dettmers et al., 2023): gradients
through a frozen quantized base into full-precision adapter weights, one of
the most replicated recipes in the fine-tuning literature. The revision is
method, not concession. Two explicit corollaries: the **adapter itself
stays full precision** (fp32 or bf16; it is tiny, and it is the one
component whose gradients matter), and the same-ruler clause above is what
protects the science: a quantized B is a slightly different animal than
bf16, but every TR-001 comparison is internal, so the animal only has to be
the same one everywhere.

## D7. Pooling is a sweep dimension inside the 20-config cap
The protocol allows last-4-layer concat as an alternative to final-layer
mean pooling. Allocation, fixed now: **linear/final-layer 6 configs,
linear/last-4-concat 4, MLP/final-layer 6, MLP/last-4-concat 4 = 20 total.**
Escalation order per protocol: linear before MLP; within each architecture,
final-layer before concat. Every config tried is appended to
`results/sweep_log.jsonl` regardless of outcome.

Stated plainly: the entire cap is spent on this pre-declared grid, so there
is **zero slack for reactive fixes**. If something looks almost-working at
config 4 of 6, the declared escalation order finishes or the run stops on a
PASS. There is no config 21. A near-miss is a FAIL.

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

## D9a. Leakage normalization is punctuation-aggressive
SQuAD contains cosmetically edited near-duplicate passages, so the D5
normalization is: lowercase, replace every non-alphanumeric character with a
space, collapse whitespace, strip, then SHA-256. A twin differing only in
case, whitespace, hyphenation, or punctuation hashes identically and trips
the check. The overlap fixture exercises exactly this. `normalize()` lives
in `checks/check_leakage.py` and the split builder imports it, so the
builder and the checker cannot drift apart.

## D10. Answer scoring uses official SQuAD normalization, max over golds
EM and F1 use the official SQuAD evaluation normalization (lowercase, strip
articles a/an/the, strip punctuation, collapse whitespace), and **both EM
and F1 are taken as the max over the full gold answer set**, never against
the first gold only. Single-reference scoring would understate every
condition unevenly: paraphrase-prone conditions (C2's summary-mediated
answers especially) lose more than extraction-faithful ones, which would
silently move the C3-minus-C2 gap. eval.jsonl carries the full gold list
(D11) precisely so the scorer can do this; a scorer found reading only
`answers[0]` is a bug, not a choice. This keeps the numbers comparable to
the literature and slightly affects where the 5-point margin lands, which
is why it is fixed here, before any numbers exist.

## D11. Data provenance and split construction
- Training pairs come from SQuAD v1.1 `train-v1.1.json`; eval pairs come
  from `dev-v1.1.json`. Train and dev are built from disjoint Wikipedia
  articles, so passage disjointness holds at the article level, the harder
  construction; the hash-overlap check still runs as code on the built
  files, and the builder additionally drops any train passage whose
  normalized hash appears in the eval set (defense in depth).
- Within each side, passages are deduplicated by normalized hash, and at
  most **2 questions per passage** are kept, so no single passage dominates
  either set.
- Eval rows keep the full gold answer list (dev has multiple annotations);
  train rows keep the first answer.
- Split seed is 7 (D8), fixed across both experiment seeds.
- Raw file URLs, SHA-256 checksums, tokenizer identity (repo plus vocab
  hash), and final counts are recorded in `data/MANIFEST.json`.
- Tokenizer for length accounting (D4) is loaded from an ungated mirror of
  Llama 3.1 8B Instruct; Phase 2 must verify the production Model B build's
  tokenizer has the same vocab hash before any C2/C3 numbers are produced.
