# TR-003r: What Survives Translation
**Track A: Latent Geometry and Model Coupling** | Status: Protocol
revision r1, STAMPED 2026-09-08 with three conditions (confident-wrong
rate given its native baseline; KILL and mismatched-anchor clauses
confirmed legible as pre-registered), door (a) of the TR-003 kickoff
gate (TR003_KICKOFF_GATE.md), opened on the PI's explicit override of
the FRONTIER-002 countersignature clause. **FROZEN as of this commit;
the original TR003 file stands untouched as the pre-registration of
record for what was planned.**

## Question
Zero-shot stitching of embedding spaces through shared anchors is
established in the literature, and TR-002r measured at desk scale
that paired-anchor alignment works while unsupervised alignment does
not. The open question is not whether a memory store can cross
models but what a MEMORY SYSTEM keeps and loses when it does: recall,
provenance, ranking, and the shape of its failures, as a function of
how many anchors it carries, on consumer hardware.

## Hypothesis
**H1:** a memory store written in one desk-scale embedding space and
read from another through relative representations against a shared
anchor set (Moschella-class: each side expressed as cosines to the
anchor texts, no fitted transform) retains most of its native recall
and keeps its provenance intact at the largest pre-registered anchor
count, on the hardest encoder pair, in both directions, at both
seeds.
**H0:** recall, provenance, or failure safety degrades past the frozen
bars even where paired-anchor alignment demonstrably works: the
store crosses, but what arrives is not the memory that left.
Either verdict is a finding: the loss profile of a translated memory
store has not been published at this scale.

## Design
- **Embedding spaces (6, all already pinned and cached from TR-002r;
  no downloads):** bge-small-en-v1.5, e5-small-v2, all-MiniLM-L6-v2
  (three sentence encoders of distinct lineages); Llama-3.1-8B-
  Instruct-4bit, Qwen3-1.7B-4bit, gemma-2-9b-it-4bit as mean-pooled
  embedders. Snapshot hashes logged at Phase 0 from the TR-002r
  manifest.
- **The store (graph-shaped, desk scale):** 5,000 memory chunks of
  200 words drawn from TR-002r's chunk registry (public-domain prose,
  154 works), each carrying provenance (work, position in work) and
  sequence edges to its neighbors within the work. Seeds 41 and 43
  draw two independent stores.
- **Queries (500 per store, two kinds, deterministic, no model
  generates them):**
  - Q1 cued recall: the middle 60 words of a target chunk; the
    correct memory is that chunk.
  - Q2 neighbor recall: the first 60 words of the chunk that FOLLOWS
    a target within the same work; the correct memory is the target
    (the memory that precedes the cue, reached through a sequence
    edge). Reported, never gated.
  Query sources are held out from anchor selection by hash.
- **Anchors:** 64, 256, and 1,024 anchor texts from a pool of
  held-out chunks disjoint from the store and the queries. Two
  selection strategies: random (seeded) and k-means medoids of the
  pool in the store model's space. **The gate reads on RANDOM
  anchors only**; medoids are the boundary map. Per-pair anchor
  tuning of any kind is a FAIL by definition (retraining by another
  name).
- **Conditions per ordered model pair (A writes the store, B asks):**
  - C1 native: store and query both in A (ceiling), and both in B.
  - C2 naive cross-model: raw vectors, through a seeded random
    orthogonal map where dimensions differ (floor).
  - C3 relative representations (PRIMARY, zero-fit): store and query
    each expressed as cosine-to-anchor coordinates in their own
    space; retrieval by cosine in anchor coordinates.
  - C4 paired-anchor Procrustes (the TR-002r skyline instrument,
    already certified): orthogonal map fit on the same anchors. The
    ceiling for what any anchor method could recover; reported, and
    the KILL reads on it.
- **Primary pair, frozen:** bge-small-en-v1.5 <-> all-MiniLM-L6-v2,
  the hardest ENCODER pair in the slate (TR-002r's skyline cosine
  fell short of 0.80 on both MiniLM pairs while retrieval held), and
  the realistic model-swap scenario for a memory index. The gate
  reads on this pair alone, both directions, both seeds. Every other
  pair is the boundary map, class-stratified per TR-002r (encoder-
  encoder, decoder-decoder, encoder-decoder); a decoder pair clearing
  what the primary misses is a scoped finding, never a PASS.

## Metrics (per pair, direction, anchor count, selection, seed, query kind)
- Recall@1, Recall@5, MRR against the 5,000-chunk store.
- **Retention:** condition Recall@5 divided by native (C1 in the
  query model) Recall@5.
- **Provenance survival:** among a condition's top-1 results, the
  fraction whose source WORK is the true source work (chunk-exact
  survival reported beside).
- **Ranking stability:** Jaccard overlap of the top-10 list against
  the native top-10 for the same query. Reported.
- **Confident-wrong rate:** fraction of queries whose top-1 is the
  wrong chunk AND the wrong work AND whose score margin over rank 2
  exceeds the native median margin: the memory system returning a
  wrong memory with native-grade confidence. **Native baseline
  (stamp condition one):** the same statistic for C1 in the query
  model, on the same queries, is the denominator every confident-
  wrong number is read against; the excess (condition rate minus
  native rate) is reported beside the rate for every configuration.
- **Direction asymmetry:** absolute difference in Recall@5 between
  A->B and B->A. Reported.
- Anchor-count curves for every metric; TR-002r's skyline census
  cited as the class priors (encoder-encoder retrieval near 1.0,
  decoder-decoder 0.80 to 0.94, encoder-decoder 0.40 to 0.64).

## Pass/Fail (frozen upon stamp, before any data)
- **PASS:** on the frozen primary pair, Q1, random anchors at 1,024,
  in BOTH directions, at BOTH seeds, C3 satisfies all three:
  (i) retention >= 0.80 of native Recall@5;
  (ii) work-level provenance survival >= 0.90;
  (iii) confident-wrong rate <= 0.05 absolute, with the native
  baseline and the excess over it reported beside (stamp condition
  one: the absolute bar is the harder of the two readings the stamp
  allowed, since native confident-wrong is never below zero; the
  excess is the mechanism that makes the number legible).
  Three clauses, one pair, one anchor count: no multiplicity across
  the grid.
- **FAIL:** any clause misses on either direction or either seed
  while the KILL does not fire. A near-miss is a FAIL. C3 clearing
  only with medoid anchors, or only at a tuned anchor count, is a
  FAIL. Another pair clearing is a boundary-map finding.
- **KILL:** the paired-anchor instrument itself cannot see the
  translation: C4 at 1,024 anchors retains less than 0.50 of native
  Recall@5 on the primary pair in either direction. Then no zero-fit
  claim is tested; publish the instrument-boundary result.

## Negative Controls
1. **Scrambled anchors:** anchor texts replaced by seeded random-word
   strings of matched length, embedded normally; C3 must collapse to
   within 0.05 Recall@5 of C2 at every anchor count. If it does not,
   the anchor coordinates carry gallery geometry, not alignment.
2. **Mismatched anchors (the house catcher, TR-002r's wrong-model
   lesson; stamp condition three):** side A and side B use DIFFERENT
   anchor texts paired only by index, drawn from disjoint halves of
   the anchor pool. C3 under mismatched anchors must collapse to
   within 0.05 Recall@5 of the C2 floor at EVERY anchor count on the
   primary pair, both directions, both seeds, and its retention must
   fall below 0.25 of native. A store that "survives translation"
   through wrong anchors survived on gallery geometry, not memory
   transfer. Red-then-green with its own fixture before any real
   number counts.
3. **Dimension-matched random projection:** seeded random orthogonal
   projections of the same rank as the anchor map on both sides must
   fall below C3 by at least 0.20 Recall@5 at 1,024 anchors on the
   primary pair, proving anchors carry semantic alignment and not
   only dimensionality.
4. **Disjointness as code:** zero hash overlap among store chunks,
   query sources, and anchor pool; zero overlap between the two
   seeds' anchor draws and their queries. The check is code, run by
   verify.sh, red-then-green.
5. **Native sanity floor:** C1 Recall@5 >= 0.90 on Q1 in every space;
   a space that cannot recall its own memories from a 60-word cue is
   excluded from the boundary map with the number published, and
   the primary pair's spaces must both clear it or the experiment
   STOPS for the PI.

## Cost and Time
$0 cash, zero downloads (every space and the corpus are on the
legion machine from TR-002r). Extraction: roughly 9,000 texts per
space, minutes for encoders and under an hour per 4-bit decoder on
M-series. Retrieval grid is numpy. Est. 2 sessions. Panel forecasts
at seal: under the standing $10 panel cap, a few cents each.

## Deliverables
- `tr003r/` repo: anchor library (relative representations and the
  Procrustes ceiling), store builder with provenance and sequence
  edges, retrieval grid, verify.sh with red-then-green checkers for
  all five controls; results as JSON plus figures; 6-8 page report
  with the survival table and the anchor-count curves as headline.
- Oracle seals against this text after the stamp, before Phase 0
  closes: the standing single-seat protocol-only oracle of record,
  plus the three-seat panel as the pilot's first subject (reported
  beside, never selected); the reviewer's context-rich forecast per
  their practice.

## Dependencies
TR-002r (closed): its corpus store, pinned spaces, certified
Procrustes instrument, and skyline census as class priors. Nothing
else. Runs on legion.
