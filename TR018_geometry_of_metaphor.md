# TR-018: The Geometry of Metaphor
**Track D: Art, Voice, and Perception** | Status: Blocked pending TR-004 (uses its curvature toolkit)

## Question
Does analogy and metaphor comprehension correspond to parallel transport on the curved embedding manifold, and does curvature-aware analogy beat flat vector arithmetic exactly where TR-004 says the space bends?

## Hypothesis
**H1:** For analogy tasks stratified by the local curvature of their region (per TR-004 estimators), curvature-aware transport (tangent-space mapping via local PCA frames, discrete parallel transport along k-NN geodesics) beats flat offset arithmetic (a - b + c) by >= 8 points in high-curvature strata while matching it in flat strata.
**H0:** Flat arithmetic is as good as it gets everywhere; curvature measured in TR-004 is real but computationally irrelevant to semantic operations.

## Background
Word2vec analogy arithmetic works eerily well for king/queen and fails quietly for figurative relations. If TR-004 confirms metaphor lives in curved regions, the natural hypothesis is that the arithmetic fails *because* it is flat: transporting a relation vector across curved space without correction accumulates error, exactly like naive vector addition on a sphere. The localization prediction (gains only where curvature is high) is what makes this a theory test rather than a method benchmark.

## Design
- **Task sets:** standard analogy benchmarks (BATS, Google) plus a constructed figurative-analogy set (metaphorical relations: "time is to river as memory is to ___", ~500 items, human-validated answer sets)
- **Stratification:** each item assigned a curvature stratum from TR-004 maps (flat / moderate / high) based on its source region
- **Methods compared:**
  - M1: flat offset (baseline)
  - M2: local-frame transport: express the relation in the tangent frame at (a, b), re-express in the frame at c
  - M3: discrete parallel transport along the k-NN geodesic from b to c (Schild's ladder approximation)
  - M4: 3CosMul (strong non-geometric baseline, to ensure gains are not just better scoring)
- **Evaluation:** accuracy@1 and @5 per method per stratum, per embedding model (two models)

## Metrics
- Interaction effect: (M2/M3 - M1) in high-curvature strata minus same difference in flat strata
- Overall accuracy per method; agreement across the two embedding models

## Pass/Fail (frozen before data)
- **PASS:** transport methods beat M1 by >= 8 points in high-curvature strata with CI excluding zero, advantage in flat strata <= 2 points (localization), pattern replicated in both embedding models, and M4 does not explain the gain.
- **FAIL:** no stratified advantage, or gains uniform (then it is a better scorer, not geometry).
- **KILL:** TR-004 returned FAIL (no reliable curvature map exists; this experiment is dissolved and its budget released).

## Negative Controls
1. **Shuffled strata:** permute curvature labels across items; interaction effect must vanish.
2. **Random frames:** M2 with randomly rotated local frames must fall to or below M1 (frames must earn their keep).
3. **Answer-set leakage check:** constructed figurative items validated by annotators blind to method outputs.

## Cost and Time
$0. Est. 2-3 sessions after TR-004.

## Deliverables
- `tr018/` repo including the transport library; stratified-gain figure; 6-8 page report; the figurative-analogy dataset released publicly.

## Dependencies
**Hard-gated on TR-004 PASS** (needs its curvature maps and estimators).
