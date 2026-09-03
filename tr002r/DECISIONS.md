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

## D6. Oracle seal superseded; ledger complete; exposure disclosed
2026-09-03, after D2. Commit c82b994 (AutoBot channel, per the
provenance line in oracle/tr002r_reviewer_forecast.sha256.md)
replaced the protocol-only oracle of record: hash 3750e42f...,
plaintext consistent on this machine. This session's earlier seal
(D2, d89674bd...) is SUPERSEDED: preserved in git history at 78d2e78
and verified byte-identical on legion today. Rules fixed now, before
any fidelity number exists:
- At closeout, the repo's current seal (3750e42f...) is scored as
  THE protocol-only oracle. The superseded forecast is reported
  beside it, labeled superseded, and is never selected post hoc for
  a friendlier Brier. No multiplicity enters the meta-ledger.
- Disclosed: the of-record plaintext transited THIS builder's
  context on 2026-09-03 (a file-change notice surfaced it), so both
  protocol-only seals share the TR-004-class transit limitation
  toward this seat. Mitigation unchanged: gates frozen, checkers
  committed, every remaining operationalization logged here before
  its number.
- Ledger complete for TR-002r: protocol-only oracle (3750e42f...)
  and the reviewer's context-rich forecast (a98fb8fd..., plaintext
  held by the PI), both sealed against protocol commit 11b914d,
  before Phase 0 closed.

## D7. Extraction scope and representation, pinned before extraction
- Representation: every space L2-normalized. Encoders use their
  model-card pooling (bge: CLS; e5: mean with "passage: " prefix;
  MiniLM: mean); decoders use mean-pooled final-layer states per the
  protocol.
- Compute scoping, frozen: the PRIMARY pair embeds both training
  halves to the full 32k grid ceiling. Non-primary pairs enter the
  boundary map at the n=8k grid point only; the 8-bit precision arm
  runs at n=8k only. Every space embeds the full eval (2,269),
  gallery (1,000 within eval), and OOD (6,522) sets. These are
  reported-leg economies; the gate's inputs are untouched.
- Runs are resumable (checkpoint per 2,000 chunks) per house rules;
  each single run stays under the 8-hour ask line, the long pole
  being the pinned Llama-4bit at ~64k chunks.
- Third decoder family: gemma-2-9b-it-4bit downloaded (D5 candidate
  one); snapshot hash logged here at extraction launch.

## D8. Downloaded snapshots, pinned at extraction launch
gemma-2-9b-it-4bit @ ff12eb39 (D5 candidate one, now the third
decoder family); Meta-Llama-3.1-8B-Instruct-8bit @ 142d4280
(precision arm); all-MiniLM-L6-v2 @ 1110a243. Budget spent ~14 GB of
the approved 40; legion at 328Gi free. Extraction queue order:
encoders (bge full, e5/minilm at the 8k economy), then llama4 full
(the primary's long pole), then qwen4/gemma4/llama8 at 8k.

## D9. Extraction stall and fix; revised long-pole estimate surfaced
2026-09-03: the llama4 pass stalled mid-OOD (checkpoint frozen 32
minutes, worker at ~1% CPU) with the signature of MLX metal-buffer
bloat in a long single-process loop. Fix: mx.clear_cache() every 100
chunks in the decoder path; chain killed and relaunched, resuming
from checkpoints (nothing recomputed, no number touched). Separately,
the measured decoder rate (~0.9s/chunk pre-stall) revises the llama4
invocation estimate to ~17h, past the 8-hour ask line the launch
estimate sat under; the PI was pinged and the run continues
checkpointed pending the word.

## D10. Ride, with the fallback pre-authorized
2026-09-03, the PI's word on the revised estimate, carrying the
reviewer's condition: the llama4 long pole rides to the full 32k
grid if the D9 cure holds. If the stall returns, the experiment
falls back to a 16k largest grid point, logged here as a D-line
BEFORE any gate is read; in that event the PASS gate's "largest
pre-registered n" reads 16k, by this pre-authorized contingency and
not by any post-hoc choice. The 2k and 8k grid points are unchanged
either way.
