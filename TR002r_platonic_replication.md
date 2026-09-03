# TR-002r: Platonic Convergence at Desk Scale
**Track A: Latent Geometry and Model Coupling** | Status: Protocol
revision r1 DRAFT, 2026-09-03 — door (a) of the TR-002 kickoff gate
(TR002_KICKOFF_GATE.md), failure-boundary reporting included.
**Frozen upon reviewer stamp; the original TR002 file stands
untouched as the pre-registration of record for what was planned.**

## Question
vec2vec-class results (arXiv:2505.12540, 2510.02348) demonstrate
unsupervised translation between text embedding spaces at full scale.
Do those claims SURVIVE desk scale: 4-bit quantized small models,
small training corpora, consumer hardware? And where exactly do they
break?

## Hypothesis
**H1:** unsupervised embedding-space translation of the vec2vec class
(no paired data, no anchors) achieves usable fidelity between at
least one cross-family pair of desk-scale embedding spaces at the
largest pre-registered corpus size, replicated across seeds, with a
supervised skyline confirming the instruments.
**H0:** the universal-geometry claim does not survive quantization
and small n; unsupervised translation collapses at desk scale even
where supervised alignment succeeds.
Either verdict is a finding: the field has the existence proof at
macro scale and no published test of this regime.

## Design
- **Embedding spaces (5-6, pinned at kickoff with the FRONTIER
  consultation):** 3 small sentence encoders of distinct lineages
  (bge-small-en-v1.5, e5-small-v2, all-MiniLM-class) plus 2-3
  4-bit decoder LLMs as mean-pooled embedders (the lab's pinned
  Llama-3.1-8B-4bit; Qwen3-1.7B-4bit; one further family), snapshots
  pinned before extraction.
- **Corpus:** public-domain prose via the TR-015 builder machinery;
  UNPAIRED training halves (hash-disjoint document splits per D-line;
  model A's training half never contains model B's documents), held
  out eval set disjoint from both.
- **Translator:** vec2vec-class small adapter (shared-latent MLP with
  unsupervised alignment objectives; architecture and losses pinned
  at Phase 0 in the decision log, sized to train in minutes-to-hours
  on M-series).
- **Skyline:** supervised orthogonal Procrustes on paired anchors,
  same pairs, same eval set. The skyline is the instrument
  certification: unsupervised claims are only interpretable where
  supervised alignment demonstrably works.
- **Failure-boundary grid (REPORTED, never gated):** fidelity curves
  over corpus size n in {2k, 8k, 32k} chunks, over precision (4-bit
  vs 8-bit vs the encoders' native fp), same-family vs cross-family
  pairs; a break point is fidelity below half the skyline's.
- **Convergence measurement retained from the original protocol:**
  CKA and Procrustes distance between spaces, reported, correlated
  against achieved translation fidelity.

## Metrics
- Translation fidelity: mean cosine of translated to ground-truth
  embeddings on held-out documents; top-1 retrieval accuracy in a
  1,000-document gallery.
- Skyline fidelity: same metrics for supervised Procrustes.
- Boundary curves per the grid; CKA/Procrustes convergence table.

## Pass/Fail (frozen upon stamp, before any data)
- **PASS:** at least one CROSS-FAMILY pair reaches mean cosine >=
  0.70 AND top-1 >= 0.30 (1,000-document gallery, chance 0.001)
  unsupervised, at the largest pre-registered n, at BOTH seeds (41,
  43), while the skyline on that pair reaches cosine >= 0.80.
- **FAIL:** no cross-family pair reaches the bar while the skyline
  passes on at least half the pairs: the vec2vec-class claim does
  not survive this regime. A near-miss is a FAIL.
- **KILL:** the supervised skyline itself fails (cosine < 0.80 on
  more than half of all pairs): the instruments cannot see alignment
  even with paired data, so no unsupervised claim is tested; publish
  the instrument-failure result.

## Negative Controls
1. **Shuffled-target control:** the translator trained against a
   permuted target space must collapse (top-1 within noise of
   chance); if it does not, the pipeline manufactures alignment.
2. **Disjointness check as code:** hash overlap between the unpaired
   training halves, and between train and eval, must be zero.
3. **Domain-shift stress (reported, never gated):** translation
   fidelity on an out-of-domain probe set; graceful degradation vs
   collapse.

## Cost and Time
$0 cash. Downloads: new model snapshots estimated 15-25 GB;
**approved budget 40 GB total** on the PI's word of 2026-09-03;
anything projecting past 40 GB stops for a fresh word. Est. 3-4
sessions; translator training is minutes-to-hours per pair on
M-series.

## Deliverables
- `tr002r/` repo: extraction and translator code, skyline, boundary
  grid, verify.sh with red-then-green checkers; 6-8 page report; the
  desk-scale boundary map as the headline figure.
- Oracle re-seal against this text after the reviewer's stamp,
  before Phase 0 closes (protocol-only oracle; reviewer's
  context-rich forecast per their practice).

## Dependencies
None. TR-003's flagged rescope (what survives translation) inherits
whatever this experiment learns about translation fidelity.
