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

**Measured evidence, 2026-08-24 (Phase 2 probes on legion, Apple M4 16 GB):**
- Extraction (Qwen 3 8B 4-bit, full 1,252-passage pass): peak 4.69 GB,
  ~215 tok/s, swap untouched.
- B generation (Llama 4-bit, identity test): peak 4.35 GB.
- One adapter training step at Phase 4 shapes (seq 94, M=32). The linear
  adapter is itself 537M parameters, which drove the outcome:
  - 8-bit B + fp32 adapter: **19.95 GB peak, swap engaged, 14.8 s/step.
    Rejected by the headroom rule.**
  - 4-bit B + fp32 adapter: 16.32 GB peak. Still over the 13.6 GB (85%)
    line. Rejected.
  - 4-bit B + bf16 adapter: **12.21 GB peak, 1.93 s/step, swap flat.
    Accepted.**
- Resolution: B runs `mlx-community/Meta-Llama-3.1-8B-Instruct-4bit`
  @ 241a666d (MANIFEST pin) for every condition and control; the adapter
  trains in bf16 (full fp32 exponent range; the two-seed replication
  criterion doubles as the stability check). Gradient-flow negative
  control held in every configuration: nonzero finite adapter gradients
  with the soft prefix in the loss, exactly 0.0 without it.
- Note for Phase 4 planning: 1.93 s/step at batch 1 means ~65 min per
  epoch over 2,000 pairs; batching or truncated epochs will matter, and
  sweep checkpoints (per CLAUDE.md resumability) are mandatory.

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

## D12. Model A pools raw passage tokens, no chat template
Qwen 3's chat template prepends role tokens and can inject thinking-mode
scaffolding; any of that wrapping would pollute the mean-pooled state with
template tokens that have nothing to do with the passage. Model A never
generates (it only reads), so extraction uses the plain tokenizer-encode
path, stated as a requirement because it is exactly the default a helpful
library applies silently. The asymmetry is chosen: Model B's text
conditions (C1, C2, C4) do use the instruct chat template, because B is
answering questions and that is the model's operating mode.

## D13. Model revisions pinned by HF commit hash
mlx-community repos are updated in place (requantized, tokenizer tweaks,
config fixes), so a bare repo name is a moving target over the months this
program runs. The HF commit hash of each downloaded snapshot is recorded in
`data/MANIFEST.json` under `models`, next to the vocab hash
(`scripts/record_model_revisions.py`). Same logic as D6's cache-invalidation
rule, applied to the models themselves: a future re-download that silently
pulls a requantized build is caught by hash, not by confusion. All
experiment loads pin these revisions.

## D14. Identity-test sabotage modes: offset and mean-collapse, not scale
The first red run of the injection identity test used a uniform 0.9 scale
as one sabotage and it was NOT detected: Llama's first per-block operation
is RMSNorm, which erases uniform magnitude changes, so scale is invisible
by construction and proves nothing about the wiring. The mode was replaced
with mean-collapse (every position becomes the sequence mean: realistic
magnitudes, content destroyed), which is the failure shape of a dead
adapter. Recorded because it is a live example of why sabotage fixtures
must themselves be watched failing: a plausible-looking red case can be
structurally unable to go red. Corollary for later phases: any control
that perturbs only vector magnitudes is suspect under RMSNorm.

## D15. Scorer proves parity with the official SQuAD script
The scorer (`lib/scoring.py`) gets its own red-then-green: on a synthetic
prediction set with deliberately varied answers (exact matches,
paraphrases, article and punctuation variants, empty and partial answers),
its aggregate EM and F1 must equal the vendored official evaluate-v1.1.py
output, and deliberately broken scorer variants (no article stripping,
first-gold-only) must be caught by the same parity check. D10 pinned the
rules; parity with the reference implementation proves the code obeys
them. The official script is vendored with recorded provenance and SHA-256.

## D16. C2 summary generation: A generates, so A's chat template applies
Extraction raw-encodes because A only reads (D12); C2 is the first place
A generates, so it uses its instruct chat template, with Qwen 3's thinking
mode explicitly disabled (enable_thinking=False): a hidden reasoning block
would burn generation budget and is not part of the summary channel.
Summaries are question-blind, matching the latent channel, which is also
question-blind. The K-token budget is enforced as a **hard cap in Model
B's tokens** (the pricing ruler C3's M=32 vectors are matched against):
A generates with a generous cap, and the summary is truncated to exactly
K=32 tokens of B's tokenizer. Truncation-after-generation is the harder
reading: a mid-sentence cut costs C2 nothing relative to C3, which gets
exactly 32 vectors with no grace either.

## D17. Deterministic decoding everywhere in eval
Greedy (argmax) decoding for A's summaries and B's answers in every
condition and control. Eval-time generation has no entropy to replicate;
the experiment seeds govern data splitting and adapter training only.
Consequence, logged rather than hidden: C1, C2, and C4 involve no
training and no sampling, so they are identical across the two protocol
seeds and are computed once, entering both seeds' results tables as the
same numbers. Only C3 and the controls vary by seed.

## D18. Expectation bands, stated before any numbers exist
Sanity alarms, not criteria; they trigger investigation of the harness,
never iteration on the mechanism. An 8B instruct model reading the
passage (C1) should land roughly 65-90 F1 on SQuAD-style extraction; the
no-context floor (C4) should be low but nonzero, roughly 3-30 F1, since
some questions leak their answers. C1 below 60 or C4 above 35 is a
plumbing alarm: halt, diagnose the harness, and record what was found.
Written now so a broken harness cannot be rationalized as a finding.

## D19. Config selection happens on a dev split, never on the held-out 500
The protocol caps the sweep at 20 configs but does not say what data
selects among them. Scoring each config on the held-out 500 would use the
eval set 20 times as a selection signal and inflate the winner's margin by
selection bias, in exactly the direction that fakes a PASS. Therefore: a
**dev split of ~250 pairs is carved from the 2,000 training pairs at the
passage level** (same normalize()-hash discipline, split seed 11, logged
in MANIFEST), leaving ~1,750 train-core pairs. Configs are selected on
dev F1; the held-out 500 is touched **exactly once per experiment seed**,
by the selected config, for the final answer. The eval script refuses to
run on the held-out split unless a committed selection record names the
config it is running (structural guard, not a convention). This protects
the frozen criteria rather than altering them: the protocol's thresholds
apply to the held-out result, which stays unconsumed until the end.

## D20. Uniform training budget, fixed before config 1
Every config trains **exactly 2 epochs over train-core, batch 1, Adam,
bf16 adapter, final checkpoint only**. No early stopping, no within-config
checkpoint selection (picking the best epoch per config would be a second
sweep hiding inside the first), no per-config budget adjustments. Dev F1
is computed once per config, on the final checkpoint. The full 20-config
grid (architecture, pooling, learning rate per D7 tiers) is enumerated in
`configs/sweep.json`, committed before the first config trains. Measured
basis: 1.93 s/step means one config is ~1.9 h of training plus ~10 min of
dev eval; tier 1 (6 configs) is one overnight. Loss is cross-entropy over
the answer tokens plus EOS (the adapter must teach B to stop, not only to
answer), and the C3 prompt frame is identical to C4's, so the soft prefix
is the only channel that differs from the floor condition.

## D21. Stop semantics: no mid-sweep PASS exists to stop on
With selection moved to dev (D19), the held-out set is untouched during
the sweep, so a protocol PASS is not observable mid-sweep and nothing
stops on "success". What ends a tier early is nothing; what prevents
later tiers is the protocol's own escalation rule: tiers 2-4 run only if
every earlier tier FAILS the **dev bar** (best dev C3 F1 at least 5 over
dev C2 F1 and at least 15 over dev C4 F1, the frozen margins applied to
dev as an operational trigger only, never as the verdict). If tier 1
clears the dev bar, tiers 2-4 do not run, which is the protocol's
"escalate only if linear fails" as written, evaluated without peeking at
the held-out set. This supersedes the D7 phrasing "or the run stops on a
PASS": under D19 there is no PASS to see until selection is over.
