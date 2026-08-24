# TR-005: FSA Postmortem, Inverted
**Track A: Latent Geometry and Model Coupling** | Status: Protocol draft v0.1

## Question
FSA showed that imposing an elegant chaotic geometry (Mandelbrot dynamics) on embeddings destroyed task signal. Does the converse hold: can a *learned*, task-driven projection give locality benefits without sacrificing discriminability?

## Hypothesis
**H1:** A contrastively learned low-dimensional projection preserves >= 95% of full-space retrieval F1 while improving a locality objective (neighborhood purity, index speed) by a measurable margin.
**H0:** Any projection that improves locality costs more than 5 points of discriminability: the two objectives are fundamentally opposed at this scale, and the FSA lesson generalizes to learned geometries too.

## Background
The original FSA result was a clean kill: chosen geometry stripped signal. The scientifically honest follow-up asks whether the failure was about *imposing* geometry or about *compressing* at all. Publishing both halves together (imposed geometry fails, learned geometry does or does not succeed) turns a private postmortem into a citable pair of results about the price of structure in embedding spaces.

## Design
- **Base embeddings:** same embedder and eval task used in the original FSA run, for direct comparability
- **Projections compared:**
  - P1: original FSA-style imposed dynamic map (replicated as published baseline)
  - P2: PCA to dimension d
  - P3: contrastive projection (small MLP, InfoNCE on positive pairs from the task) to same d
  - P4: identity (full space) - ceiling
- **d sweep:** 16, 64, 256
- **Tasks:** retrieval F1 (discriminability) and neighborhood purity plus ANN query latency (locality)

## Metrics
- Retention ratio: F1(projection)/F1(full) per method per d
- Locality gain: purity and latency vs full space
- The trade-off frontier plotted per method

## Pass/Fail (frozen before data)
- **PASS:** P3 achieves >= 0.95 retention at some d while beating P4 latency by >= 2x, and dominates P1 and P2 on the frontier.
- **FAIL:** P3 cannot reach 0.95 retention at any swept d, or offers no locality gain over PCA.
- **KILL:** results not reproducible across two seeds of contrastive training.

## Negative Controls
1. **Frozen random MLP:** same architecture as P3, untrained; must land near P2 or worse, proving the training (not the architecture) earns the result.
2. **Label leakage check:** contrastive pairs drawn strictly from a training split disjoint from eval.
3. **Replication of the kill:** P1 must reproduce the original FSA failure; if it does not, the historical result needs re-examination before anything else is claimed.

## Cost and Time
$0. Est. 2 sessions, reusing FSA-era code and data.

## Deliverables
- `tr005/` repo; frontier plots; a two-part report (the kill and the inversion) suitable for publication as a single honest paper.

## Dependencies
Access to original FSA code/data. Otherwise independent.
