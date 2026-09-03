# TR-002r: Platonic Convergence at Desk Scale
**Track A: Latent Geometry and Model Coupling** | Status: Protocol
revision r1, STAMPED 2026-09-03 with three reviewer amendments
(primary pair named, wrong-model control added, method class frozen)
— door (a) of the TR-002 kickoff gate (TR002_KICKOFF_GATE.md),
failure-boundary reporting included. **FROZEN as of this commit; the
original TR002 file stands untouched as the pre-registration of
record for what was planned.**

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
- **Translator, method class FROZEN (amendment three):** the PRIMARY
  method is mini-vec2vec-style linear alignment (unsupervised linear
  mapping to a shared structure; what the frontier reports as
  sufficient, and what this hardware runs well). An adversarial
  vec2vec-style MLP variant is pre-registered as SECONDARY, run if
  compute allows, reported beside the primary, and never substituted
  post hoc if the primary disappoints. Exact objective and
  optimization settings for the primary are pinned at Phase 0 in the
  decision log before any fidelity number exists.
- **Primary pair, FROZEN (amendment one):** bge-small-en-v1.5
  against the pinned Llama-3.1-8B-Instruct-4bit (mean-pooled), the
  most architecturally distant pairing in the slate (encoder vs
  quantized decoder, 110M vs 8B, different tokenizers). The PASS
  gate reads on this pair alone, in BOTH translation directions, at
  both seeds. Every other pair is the boundary map: if the primary
  fails and another pair clears, that is a scoped finding for the
  failure-boundary section, never a PASS.
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
- **PASS:** the FROZEN PRIMARY PAIR (bge-small <-> Llama-3.1-8B-4bit)
  reaches mean cosine >= 0.70 AND top-1 >= 0.30 (1,000-document
  gallery, chance 0.001) unsupervised, in BOTH directions, at the
  largest pre-registered n, at BOTH seeds (41, 43), while the
  skyline on that pair reaches cosine >= 0.80. One pair, one gate:
  no multiplicity.
- **FAIL:** the primary pair misses the bar while the skyline passes
  on at least half of all pairs: the vec2vec-class claim does not
  survive this regime on the hardest honest pairing. A near-miss is
  a FAIL; another pair clearing is a boundary-map finding, never a
  PASS.
- **KILL:** the supervised skyline itself fails (cosine < 0.80 on
  more than half of all pairs): the instruments cannot see alignment
  even with paired data, so no unsupervised claim is tested; publish
  the instrument-failure result.

## Negative Controls
1. **Shuffled-target control:** the translator trained against a
   permuted target space must collapse (top-1 within noise of
   chance); if it does not, the pipeline manufactures alignment.
2. **Wrong-model control (amendment two, the house catcher):** feed
   the trained primary translator embeddings from a THIRD model,
   frozen now as e5-small-v2 (dimension-compatible with bge's input
   side). Retrieval through the wrong model must collapse: top-1
   below one-tenth of the genuine pair's top-1 AND below 0.05
   absolute. If C-through-A->B retrieves near the real pair's
   fidelity, the "translation" is exploiting degenerate gallery
   geometry (hubness, anisotropy), not performing model-specific
   alignment — the fake-margin class TR-001's shuffled-pairing
   control caught. Red-then-green in the checker suite like its
   ancestors.
3. **Disjointness check as code:** hash overlap between the unpaired
   training halves, and between train and eval, must be zero.
4. **Domain-shift stress (reported, never gated):** translation
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
