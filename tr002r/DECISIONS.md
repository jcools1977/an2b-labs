# TR-002r DECISIONS

Every judgment call, logged before the numbers it could bend toward.
Protocol thresholds untouched; ambiguity resolves toward the reading
that makes H1 harder to pass. The CREDO firewall applies.

## D1. FRONTIER consultation (standing macro-check clause)
Dated 2026-09-03: FRONTIER-001 consulted at this kickoff; it is the
scan that created this experiment (TR-002 rescoped through the
kickoff gate, door (a) with failure-boundary reporting, on the PI's
word and the reviewer's stamp with three amendments). FRONTIER-001
is same-day fresh and names this kickoff explicitly, so it satisfies
the fresh-entry requirement; the next scan is due before TR-006 or
2026-09-10, whichever comes first. Sensing only; no threshold here
derives from it.

## D2. Oracle seal
Sealed 2026-09-03 against the stamped protocol (commit 11b914d),
before Phase 0 closed: sha256 d89674bd13c66bb9... committed in
oracle/sealed/TR002r.sha256, plaintext gitignored until closeout,
zero oracle tool uses verified. The reviewer's context-rich forecast
seals through their channel.

## D3. Primary method, pinned before any fidelity number
Mini-vec2vec-style linear alignment, operationalized:
1. Each space standardized on its own training half (center, per-dim
   scale); the 4096-dim decoder spaces reduced to 384 by PCA fit on
   their own training half only.
2. Initialization: k-means with k=128 (seed 41) on each half;
   cluster centroids matched across spaces by optimal assignment on
   the correlation of centroid-to-centroid distance structure;
   orthogonal Procrustes on matched centroids gives W0.
3. Refinement: T=10 rounds of (nearest-neighbor re-matching of
   training points under the current W, orthogonal Procrustes refit
   on the matched pairs). Deterministic given seeds.
4. Final translator: the round-T orthogonal W (plus the fixed PCA
   and standardization transforms). No paired documents are ever
   used: matching operates across the hash-disjoint halves.
The adversarial secondary, if run, is reported beside this and never
replaces it (protocol amendment three).

## D4. Corpus operationalization
TR-015's Gutenberg builder machinery reused with its cache; the book
list extends (public-domain IDs appended at build, logged in the
manifest) until the largest grid point is coverable: 32,000 training
chunks per half plus a 1,000-document gallery and eval set, chunks
of 200 words, non-overlapping, hash-disjoint halves by DOCUMENT
(work), never by chunk, so no work contributes to both halves. Eval
and gallery works are disjoint from both training halves. Seeds per
protocol (41, 43).

## D5. Third decoder family
The protocol's "one further family" is chosen at extraction from
what the FRONTIER-current mlx-community catalog holds within the
40 GB budget, logged here with its snapshot hash before extraction.
Candidate order fixed now, most-distinct-lineage first: a
Gemma-class, then a Phi-class, then a Mistral-class 4-bit build.
