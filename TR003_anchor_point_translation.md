# TR-003: Anchor-Point Translation
**Track A: Latent Geometry and Model Coupling** | Status: Protocol draft v0.1

## Question
Can memories embedded in one model's space be consumed by a different model with zero retraining, using relative representations against a shared anchor set?

## Hypothesis
**H1:** Re-expressing embeddings as cosine similarities to a fixed anchor set (Moschella et al., relative representations) yields retrieval accuracy in a *foreign* model's space within 10 F1 points of native-space retrieval.
**H0:** Cross-model retrieval via anchors degrades by more than 10 points, making anchor translation impractical.

## Background
Every memory system built on embeddings is silently married to one embedding model. Swap the model and the store is garbage. If anchor-relative coordinates are model-invariant enough, memory becomes portable across models and across time, which is the single largest architectural risk in any long-lived memory substrate. This is the experiment with the most direct product consequence for a graph-RAG memory layer.

## Design
- **Embedding models (3):** two local sentence embedders of different families plus one API embedder (nomic-embed, bge, text-embedding class)
- **Corpus:** 5,000 memory-like chunks (mix of synthetic facts and real project notes, scrubbed)
- **Anchors:** 256 and 512 anchor texts, two selection strategies: random sample vs k-means medoids of the corpus
- **Conditions:**
  - C1: native retrieval (query and store in same model) - ceiling
  - C2: naive cross-model (query in model X, store in model Y, raw vectors) - expected floor
  - C3: anchor-relative cross-model (both sides projected to anchor coordinates)
- **Task:** top-k retrieval of the known-correct chunk for 500 held-out queries

## Metrics
- Recall@1, Recall@5, MRR per condition per model pair
- Sensitivity to anchor count and anchor selection strategy

## Pass/Fail (frozen before data)
- **PASS:** C3 within 10 F1/recall points of C1 for at least 2 of 3 model pairs at 512 anchors.
- **FAIL:** C3 misses the margin, or only works with per-pair anchor tuning (that is retraining by another name).
- **KILL:** C2 floor and C3 statistically indistinguishable across pairs.

## Negative Controls
1. **Scrambled anchors:** replace anchor texts with random strings; C3 must collapse toward C2.
2. **Anchor overlap check:** zero overlap between anchors and eval queries (hash check).
3. **Dimension-matched random projection:** project both spaces through random matrices of the same rank as the anchor map; must underperform C3, proving anchors carry semantic alignment, not just dimensionality.

## Cost and Time
$0 beyond trivial API embedding costs. Est. 2 sessions.

## Deliverables
- `tr003/` repo with anchor projection library (reusable as a product component)
- Report with portability table and anchor-count curves
- If PASS: a migration path for any embedding-locked memory store

## Dependencies
None. Runs independently of TR-001/002.
