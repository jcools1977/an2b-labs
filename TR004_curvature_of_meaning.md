# TR-004: Curvature of Meaning
**Track A: Latent Geometry and Model Coupling** | Status: Protocol draft v0.1

## Question
Does figurative language occupy measurably different geometry (higher local curvature, higher intrinsic dimension) than literal language in embedding space?

## Hypothesis
**H1:** Local intrinsic dimension (LID) and curvature proxies around metaphorical usages are significantly higher than around literal usages of the *same* target words.
**H0:** No consistent geometric difference between literal and figurative neighborhoods.

## Background
Word-vector arithmetic treats meaning as flat. But if abstraction and metaphor bend the space, flat operations fail exactly where language gets interesting, and that failure is measurable. This experiment produces the curvature map that TR-018 (Geometry of Metaphor) needs, and it is pure mathematics on embeddings: no training, no GPUs, just careful estimation.

## Design
- **Data:** VU Amsterdam Metaphor Corpus (VUAMC) or equivalent, giving literal/metaphorical labels for identical lemmas in context; supplement with matched sentence pairs (literal vs figurative use of the same verb)
- **Embeddings:** contextual token embeddings from one mid-size open model, plus one sentence embedder for robustness
- **Estimators:**
  - LID: Two-NN estimator (Facco et al.) and MLE estimator (Levina-Bickel), both, to guard against estimator artifacts
  - Curvature proxy: geodesic-vs-chordal distance ratio in k-NN graphs; PCA residual spectrum decay rate
- **Analysis:** paired comparison (same lemma, literal vs metaphorical context), controlling for frequency and sentence length

## Metrics
- Median LID (literal) vs median LID (figurative), paired effect size (Cliff's delta)
- Curvature proxy distributions with bootstrap CIs
- Per-POS breakdown (verbs vs nouns vs adjectives)

## Pass/Fail (frozen before data)
- **PASS:** both LID estimators agree on direction, Cliff's delta >= 0.2, CI excluding zero, and effect survives frequency/length controls.
- **FAIL:** estimators disagree, or effect vanishes under controls.
- **KILL:** effect present in one embedding model but absent in the other (model artifact, not a property of meaning).

## Negative Controls
1. **Shuffled labels:** permute literal/figurative labels; effect must vanish.
2. **Synonym control:** literal words matched to *different* literal words of similar frequency must show near-zero delta (the pipeline should not manufacture differences).
3. **Random subspace:** repeat in a random low-rank projection; if the effect strengthens under random projection, it is an artifact of ambient dimension, not structure.

## Cost and Time
$0. Est. 2 sessions. Heaviest step is careful statistics, not compute.

## Deliverables
- `tr004/` repo: LID/curvature estimation toolkit (reusable)
- Curvature atlas figures; 5-7 page report
- Feeds TR-018 directly

## Dependencies
None. Independent, and one of the cheapest experiments in the program.
