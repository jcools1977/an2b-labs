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

## D11. Translator certification exam, red before the instrument
Committed while extraction runs, before any real embedding meets the
translator: on synthetic spaces with a known orthogonal relation,
trained unpaired, the D3 procedure must recover top-1 >= 0.9 (the
easiest world; failure means broken code); against an independent
cloud with no shared geometry it must not beat 10x chance (alignment
manufactured from nothing). The exam is the D5-estimator pattern
applied to the translator; verify will carry it as its own leg.
D11 addendum: the exam's first recoverable-structure world drew
GAUSSIAN latents, under which unsupervised alignment is
information-theoretically unrecoverable up to axis signs (the
distribution is rotation-symmetric; no moment carries sign
information). That is not an easiest world but an impossible one, an
exam-design error corrected before any real data: the synthetic
latents are now skewed (centered gamma), the fair analogue of real
embedding clouds, which are strongly non-gaussian. The no-structure
leg is untouched. Also logged: the exam already earned its keep
twice, refuting the sorted-profile initialization (no discriminative
structure) before the PCA-sign initialization replaced it.
D11 second addendum: the skewed-iid world is STILL ill-posed — iid
latents carry an m!-fold permutation symmetry that is distributionally
undetectable, so pointwise recovery is impossible for any unsupervised
method even in principle. A fair easiest world must be identifiable:
latent variances made distinct (decaying spectrum, the realistic
analogue of power-law embedding spectra) alongside the skew. The
no-structure leg remains untouched throughout. The exam has now
refuted two implementations and two of its own worlds; each refutation
is logged, and the gates never moved.
D11 third addendum: the faithful published implementation (fetched
pseudo-code, QAP centroid matching, ensembled relative
representations, smoothed ICP, single cluster correction) ALSO fails
the unimodal world, and the paper says why: the method's stage 1
conjectures that "clusters represent recurring themes" consistent
across datasets. A unimodal cloud has no clusters to anchor on. The
exam world gains mixture structure (24 latent clusters), the analogue
of topics in real text. The three world corrections now form a
pre-registered PRECONDITION LIST for the method class: identifiable
spectrum, non-gaussian moments, and multi-modal cluster structure.
Mechanistic prediction, logged before any real number: pairs whose
embedding clouds lack clean cluster structure should sit on the
failure side of the boundary map for stage-1 reasons.

## D12. Translator certified; the exam's full kill list
The D11 exam went green only on the sixth implementation, having
refuted, in order: (1) sorted-profile centroid matching (no
discriminative structure), (2) sign-matched PCA alignment (defeated
by spectrum degeneracy), (3) multi-restart centroid ICP (local
search cannot find a global rotation), (4) canonical ICA (component
correspondence scrambles under near-tied mixing norms), and (5) the
FAITHFUL published pipeline with scipy's FAQ solver, which returned
QAP objectives of 38-51 against the known-true permutation's 72.45
on an instance where k-means had recovered both halves' clusters at
ARI 1.0. The certified version is the published mini-vec2vec
pipeline (fetched pseudo-code) with one substitution: seeded greedy
structural growth replaces FAQ for centroid matching, recovering the
true permutation 24/24 at the true objective. Along the way the exam
also forced three world corrections, each an identifiability
argument now standing as the method class's pre-registered
precondition list (D11 addenda). Exam final state: top-1 1.000 on
the recoverable world, 0.004 on the no-structure world, both legs
frozen throughout; no gate or bar moved at any point.

## D13. Gates-runner operationalizations, before any real fidelity number
- Skyline anchors: the 1,269 eval chunks OUTSIDE the gallery are the
  paired anchors (every space embeds eval); supervised Procrustes
  fits on them in the comparison frame and is evaluated on the
  gallery, so skyline and unsupervised numbers share the same eval
  geometry and never touch training halves.
- Shuffled-target control operationalized: for unpaired training,
  permuting sample order is a no-op, so the destruction is per-row
  coordinate permutation of the target half (seed 41), which erases
  the space's shared geometry while preserving marginals; the
  translator trained against it must retrieve at chance.
- Boundary-map economies: non-primary pairs run one direction, seed
  41, n=8k (per D7); the precision arm is llama8<->bge at 8k. The
  primary pair runs the full grid, both directions, both seeds.
- Declared now: one SMOKE TEST of the runner mechanics on bge<->e5
  at n=2k before the primary's embeddings exist; its numbers are
  quarantined (not boundary-map material; the map re-runs from the
  frozen grid) and the smoke test is recorded here either way.

## D14. STOP surfaced: the cosine bars' frame is ambiguous, and it decides the KILL
Found by the declared D13 smoke test before any gate number exists.
The certified translator (like the published pipeline's own
preprocessing) works in a CENTERED, sphered comparison frame. The
frozen bars (PASS cosine >= 0.70, skyline floor 0.80) were calibrated
against the literature's RAW-cosine reporting scale. Measured on the
easiest pair (bge<->e5, supervised skyline, gallery top-1 = 1.000 in
BOTH frames): raw cosine 0.888, centered cosine 0.637. The identical,
demonstrably perfect alignment passes the skyline floor in one frame
and fails it in the other; bge<->minilm reads 0.779 raw / 0.618
centered at top-1 0.943-0.999. As written, the centered reading would
fire the instrument-failure KILL against instruments retrieving
perfectly, a hollow death by unit choice; the raw reading matches the
scale the bars were frozen against. Per BB4C rule 1 this seat
adjudicates neither: the question goes to the PI and reviewer. Top-1,
frame-robust in every measurement above, is unaffected either way.
Also recorded, quarantined per D13: the smoke test's unsupervised leg
read zero at n=2k on bge<->e5 (no interpretation attached; the frozen
grid will speak). Extraction and non-gate machinery continue; no gate
is read until the frame ruling lands.

## D15. D10 fallback executed: largest grid point is 16k
2026-09-03, 17:20 EDT: the MLX stall recurred mid-half-A (checkpoint
frozen 33 minutes, worker ~0%CPU, ~3h process uptime; the D9
periodic cache clear delays but does not eliminate the wedge). Per
the PI's pre-authorized D10 contingency, the experiment falls back
to a 16k largest grid point, executed now, before any gate number
exists: the PASS gate's "largest pre-registered n" reads 16k; the
2k and 8k points are unchanged; checkers and fixtures amended
accordingly under the pre-authorization (the only threshold-adjacent
edit, made on the PI's prior word, not this seat's judgment). The
remaining extraction runs under a staleness supervisor (kill and
resume from checkpoint when the checkpoint ages past 10 minutes),
which costs at most one checkpoint interval per stall.

## D16. The supervisor failed its own missing negative control
Overnight 2026-09-03/04: 62 restarts, llama4 half A pinned at chunk
4,000. Mechanism: the D15 supervisor's 10-minute staleness threshold
is SHORTER than llama4's ~33-minute natural silence between 2,000-
chunk checkpoints, so it killed healthy runs all night, each cycle
losing sub-checkpoint progress. A watchdog whose failure mode is
killing healthy work, shipped without testing the healthy-slow case:
the lab's own negative-control rule, violated by its plumbing and
logged as such. Fix, both sides of the race: decoder checkpoints
every 500 chunks (~9-minute heartbeat) and the staleness threshold
raised to 15 minutes. No experiment number was touched; the cost was
one night of wall-clock.

## D17. The D14 ruling: raw frame for both bars; resolution, not adjustment
Ruled by the PI 2026-09-04: RAW cosine is the frame for both frozen
bars (PASS 0.70, skyline floor 0.80), matching the literature scale
they were calibrated against; the centered reading is reported as
companion beside every raw number; the wrong-model control reads in
the same raw frame. Logged as a RESOLUTION of a frame the
pre-registration left unnamed, not an adjustment of any bar: no
threshold value changed, and the ambiguity was surfaced (D14) before
any gate number existed.
Readout operationalization, pinned now: the translator works in its
certified comparison frame; raw-frame readout inverts the frame
chain with the target space's stored statistics (comparison vector
times the mean centered norm, plus the center; PCA back-projection
for wide spaces) and compares against the stored raw embeddings.
One mechanism, applied uniformly to the unsupervised prediction, the
skyline, and the wrong-model control. Declared: one skyline-only
readout verification on bge<->e5 (mechanics, no unsupervised
number) to confirm the inverse chain reproduces the D14 diagnostic's
raw reading before the grid runs.
D17 addendum: the pinned inverse-chain readout reads 0.940 where the
D14 diagnostic's direct-raw Procrustes fit read 0.888, on the same
alignment (top-1 = 1.000 under both; the restored mean inflates
cosine). The uniform mechanism is kept: skyline and translator read
through the SAME chain, so their comparison and the KILL stay fair,
but the absolute cosine scale is ~0.05 more generous than the
numbers the ruling was calibrated on. Surfaced to the PI and
reviewer before any gate number exists; a veto swaps the readout for
direct-raw-anchor fitting on both sides. Centered companions are
reported beside every raw number regardless.

## D18. Gemma mask crash; decoder forward unified
gemma-2's attention requires an array mask where llama/qwen accepted
the string "causal"; the hand-rolled layer loop crashed at gemma's
first block. Fix: the decoder extractor now calls each model's own
inner forward (model.model), inheriting the family's mask logic and
final norm. For the families already extracted (llama4, qwen4) this
is mathematically identical to the loop that ran, verified by the
module structure (the inner model applies the same blocks and norm);
no re-extraction. Logged before gemma produces a single vector.
