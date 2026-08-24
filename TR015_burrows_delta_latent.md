# TR-015: Burrows Delta in Latent Space
**Track D: Art, Voice, and Perception** | Status: Protocol draft v0.1

## Question
Does an author's voice occupy a stable low-dimensional manifold in embedding space, and can voice drift across a multi-book series be measured geometrically and distinguished from topic drift?

## Hypothesis
**H1:** Author identity is linearly recoverable from a low-rank subspace (rank <= 10) of chunk embeddings with accuracy >= 90% on held-out chunks after topic residualization, and within-author drift across sequential works is measurably smaller than between-author distance, with drift direction consistent across chunk sizes.
**H0:** Apparent voice signal is topic and period residue; after residualization, authors are not separable in low rank, and classical function-word Burrows Delta is not improved upon.

## Background
Burrows Delta established authorship attribution on function-word frequencies. Modern embeddings promise richer voice representations, but conflate voice with topic. The residualization step is the actual contribution: voice as what remains after content is projected out. Applied longitudinally to a series in progress (Epoch I vs Epoch II drafts), it turns "am I keeping the voice consistent" from a feeling into a coordinate.

## Design
- **Corpus:** 12+ authors x 2+ works each (public domain), chunked at 500 and 1,500 words; plus the in-house series (Epoch I published, Epoch II drafts) as the longitudinal case study
- **Pipeline:** sentence embeddings per chunk; topic residualization by regressing out topic-model factors (and separately, an LLM-paraphrase control where chunks are content-preserving rewrites); PCA/LDA to find the voice subspace
- **Baselines:** classical Burrows Delta on function words; full-dimensional embedding classifier
- **Drift measurement:** per-author centroid trajectory across sequential works; drift magnitude vs between-author distances; bootstrap over chunks

## Metrics
- Held-out attribution accuracy: low-rank residualized vs Burrows baseline vs full-dim
- Drift ratio: within-author sequential drift / mean between-author distance
- Rank curve: accuracy vs subspace rank

## Pass/Fail (frozen before data)
- **PASS:** rank <= 10 residualized subspace achieves >= 90% attribution, beats or matches Burrows Delta, and drift ratio < 0.5 for >= 80% of authors with consistent drift direction across both chunk sizes.
- **FAIL:** residualization destroys separability (voice was topic), or Burrows Delta wins (embeddings add nothing).
- **KILL:** paraphrase control fails: if content-preserving rewrites of author A land in author B's region, the "voice" subspace is not voice.

## Negative Controls
1. **Shuffled authorship labels:** attribution must fall to chance.
2. **Topic-only classifier:** a classifier on topic factors alone quantifies the leak the residualization must close.
3. **Translation stress test:** translated works of one author must degrade gracefully, not catastrophically flip identity (robustness bound, reported not gated).

## Cost and Time
$0. Est. 2-3 sessions. Extends the existing voice-fingerprinting tooling.

## Deliverables
- `tr015/` repo; the voice-manifold plot with the series trajectory drawn on it (headline figure); 6-8 page report; if PASS, a voice-drift meter for the editing pipeline.

## Dependencies
None. Pairs with TR-011 for a two-instrument craft toolkit.
