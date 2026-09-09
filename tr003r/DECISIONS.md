# TR-003r DECISIONS

Every judgment call, logged before the numbers it could bend toward.
Protocol thresholds untouched once stamped; ambiguity resolves toward
the reading that makes H1 harder to pass. The CREDO firewall applies:
nothing here cites product value.

## D1. FRONTIER consultation (standing macro-check clause)
Dated 2026-09-08: FRONTIER-002 consulted at this kickoff. It is the
scan that reshaped this experiment: it found TR-003's original
anchor-retrieval question partially answered (zero-shot stitching via
shared anchors established; refinement active, arXiv:2605.30596 and
arXiv:2505.10354) and named the sharper rescope, what survives
translation, with TR-002r's skylines as priors. FRONTIER-002 is
same-day fresh and names this kickoff explicitly, satisfying the
fresh-entry requirement as TR-002r's D1 did with FRONTIER-001.
CORRECTED 2026-09-08, same day: this entry first recorded the
reviewer's countersignature as not landed, and the PI's explicit
override of the hold (RATIFICATION_WAVE3.md) as the basis for
opening. That was a stale-channel error on the builder's side: the
reviewer had countersigned FRONTIER-002 in their own channel before
the kickoff, with the citations spot-checked (arXiv:2510.02348
fetched and verified against the source; an independent search
finding no desk-scale or quantized translation test), and the PI
relayed it after the kickoff. TR-003r's frontier basis is verified,
not open; the override stands in history as what was spoken, now
moot in effect. No exposure remains on this line. Sensing only; no
threshold derives from it.

## D2. Door and mechanics
Door (a) per the PI's Word 1 slate. The rescope lands as a NEW frozen
revision in drafts/ until stamped, then moves to the repository root
with the freeze manifest reissued in the same commit (the stamp is
the approval through a channel other than this seat, per ARENA rule
7). The original TR003 file is untouched. Oracle seals follow the
stamp, before Phase 0 closes.

## D3. Primary pair chosen for the harder honest reading
bge-small <-> all-MiniLM-L6-v2 rather than TR-002r's encoder-decoder
primary. Reason: the gate measures a LOSS PROFILE relative to native
recall, which is only interpretable where paired-anchor alignment is
known to work; TR-002r's encoder-decoder skylines (0.40 to 0.64
identity retrieval) would make the primary's FAIL a foregone
instrument limit rather than a finding about memory. Among encoder
pairs the MiniLM pairs were the hardest in TR-002r (skyline cosine
under 0.80 on both). Decoder pairs are the boundary map. The PI and
reviewer may amend the pair at the stamp; whichever pair is stamped
is the pair.

## D4. Gate on random anchors, not medoids
The original protocol offered two selection strategies. Reading the
gate on the strategy that involves no fitting or selection at all is
the harder reading and the one that cannot be tuned per pair.
Medoids are reported as the boundary map.

## D5. Queries are deterministic sub-spans, not model-generated
No LLM writes queries: Q1 is the middle 60 words of the target, Q2
the first 60 words of the following chunk. This keeps the experiment
free of a generator's bias and of API cost, at the price of lexical
overlap between Q1 and its target, which is exactly why the native
sanity floor (control 5) must be high and why the verdict is about
RETENTION relative to native rather than absolute recall.

## D6. What is inherited from TR-002r, byte-identified at Phase 0
The chunk registry and splits (hash-identified), the six space
snapshots (manifest hashes), and the Procrustes skyline code
(certified in TR-002r D11). Anything reused is named with its hash in
this log before the first extraction; anything rewritten passes an
exam first.

## D7. Stamp received 2026-09-08 with three conditions; how each landed
Condition one (confident-wrong floor tied to a mechanism): the native
confident-wrong rate is pre-registered as the baseline companion, and
the excess over it is reported for every configuration. The stamp
allowed either a delta gate or the absolute 0.05; the absolute bar is
kept because it is the harder reading (native is never below zero, so
"excess <= 0.05" can only be looser), and the excess is reported so
the number has its denominator. Condition two (KILL legible): the
clause was complete in the draft and is unchanged; the chat summary
had truncated it. Condition three (mismatched-anchor behavior
frozen): the collapse criterion is now explicit in the control's own
text (within 0.05 Recall@5 of C2 at every anchor count, retention
under 0.25 of native, disjoint pool halves) rather than by reference
to control 1. The file moved from drafts/ to the root and the freeze
manifest was reissued in this commit, the stamp being the approval
through a channel other than this seat.

## D6 (executed). Inherited assets, byte-identified 2026-09-08
Protocol frozen at commit 05d156e, file sha256 1d957068d911ee31...;
freeze manifest reissued in that commit (22 files).
Corpus (legion, tr002r/corpus_store): chunk_registry.json sha256
74956edab65226ab..., splits.json d37c551927a4db5b.... Space snapshots
(HuggingFace hub commits on legion): bge-small-en-v1.5 5c38ec7c;
e5-small-v2 ffb93f3b; all-MiniLM-L6-v2 1110a243;
Meta-Llama-3.1-8B-Instruct-4bit 241a666d; Qwen3-1.7B-4bit 3b1b1768;
gemma-2-9b-it-4bit ff12eb39. The 8-bit Llama and Qwen3-8B snapshots
are present but outside this protocol's six spaces and are not used.
TR-002r's embedding sidecars (bge, e5, minilm, llama4, qwen4, gemma4
over A, B, eval, ood) cover the 200-word chunks but not this
experiment's 60-word queries; extraction reruns for every text with
TR-002r's extractor, whose file hash is logged at first use.

## D8. Phase 0 CLOSED 2026-09-08: seals of record
Single-seat oracle of record sealed at ca801ab (plaintext sha256
045718d4f3e8..., oracle/sealed/TR003r.sha256), one tool use, the
forecast never in the builder's context. Panel sealed at e4bdb00 as
the pilot's first subject, against protocol commit 05d156e and
prompt sha c81363cfba68, policy d6c5b4968f66 with the DENY control
of 15:54:56Z: oracle-anthropic (served anthropic/claude-fable-5.1
via Anthropic) c0c66f9f5fd53e5a...; oracle-openai (served
openai/gpt-6-astra via OpenAI) 1bf886000344e9be...; oracle-xai
(served x-ai/grok-4.6 via xAI) 947a72befe6fe4ec.... Zero schema
errors, zero tool calls, first attempt each; panel cost $0.27, ledger
$1.24 of $10. Every hash is pushed; the seals become seals when the
reviewer's channel fetches them, which is their act, not this
seat's. The reviewer's context-rich forecast seals through their
channel. No implementation code exists at this commit.

## D9. Store spans many works: 250 contiguous chunks per work, pool 128 per work
The first build (whole works, seeded order) produced a seed-41 store
from six long novels. With so few works, work-level provenance
survival is nearly guaranteed by chance and the clause stops
discriminating. Capping each work at its first 250 contiguous chunks
puts at least twenty works in every store (harder for clause (ii),
sequence edges intact within each run); capping the anchor pool at
128 per work gives anchors that span at least sixteen works, which
is what a memory system's anchor set would look like and what makes
the mismatched-anchor collapse meaningful. Logged before any
embedding exists; the rebuilt manifest is the one that counts.

## D10. C4 ceiling rank rule, fixed before any real number
The paired-anchor Procrustes ceiling centers each side on its anchor
mean and reduces each side by PCA fit on the ANCHORS THEMSELVES to
rank r = min(d_src, d_tgt, k), then fits the orthogonal map on the
anchors. Reason: in the scenario the reader side owns nothing but its
anchors and its queries, so fitting a PCA on a store it does not have
would be an instrument the memory system could not build. At k = 64
the ceiling is rank-limited to 64; that is the honest ceiling at 64
anchors. C2 uses raw vectors and a seeded random map only where
dimensions differ; control 3 uses independent seeded projections of
rank k on each side.

## D11. The anchor exam caught its own world before certifying the library
First run: C3 and C4 at chance on the "recoverable" world while every
collapse leg passed. The world was wrong, not the library: query rows
were drawn from points outside the store, so no correct answer
existed. Fixed (queries are noisy copies of store points) and a
native-sanity leg added so the world proves itself on both sides.
Second run: certified, 9 of 9 legs. Logged because a green exam on a
broken world would have certified nothing.

## D12. Smoke world and the scrambled-anchor arm
The plumbing smoke runs the whole chain (grid, assembler, three
checkers) on a synthetic two-space world before any real embedding.
Its first run failed control 1 on the recoverable world: under an
exact rotation ANY consistently paired anchors translate perfectly,
so scrambled anchors cannot collapse there. Real nonsense strings do
not embed consistently across models, so the smoke world models
scrambled anchors as unpaired random vectors. Stated plainly: whether
real scrambled anchors collapse C3 is the empirical question control
1 pre-registers, and if they do NOT collapse on real spaces that is a
reported violation with its mechanism named, not an excuse. The
smoke certifies the path, not the physics.

## D13. Extraction supervision
Chain nohup'd on legion with a 15-minute staleness supervisor
(checkpoints every 500 texts; a healthy decoder forward never goes
silent that long). Extraction order: encoders first, then Qwen3-1.7B,
Llama-3.1-8B, gemma-2-9b, all 4-bit and already cached.

## D14. Grid run on the three encoders first; decoders join the boundary map as they land
The protocol's cost line estimated "under an hour per 4-bit decoder."
Wrong: on legion (16 GB, 2.7 GB of swap in use during the Llama pass)
the 8B decoder runs at about 45 texts per minute, five hours for the
pass, with gemma-2-9b behind it. The gate reads on bge and MiniLM,
which were done, and the decoders only fill the boundary map, so the
grid ran on the encoders (492 configurations, one minute) and the
gates were read cold before any decoder space existed. The grid is
keyed per configuration and resumable; decoder pairs append without
touching any encoder line. Nothing about the gate depends on the
order, and the order is recorded here.

## D15. Gates read cold 2026-09-08 (encoder grid); what the checkers said and what is reported beside
PASS: red on clause (i) retention (0.19 and 0.19 bge->minilm; 0.015
and 0.015 minilm->bge, seeds 41 and 43) and clause (ii) provenance
(0.28/0.30 and 0.11/0.11) in every cell; clause (iii) confident-wrong
0.000 with the native baseline 0.002 (excess -0.002): passes
trivially because relative coordinates compress margins. KILL did not
fire: C4 retention 0.69 to 0.86 on the primary pair, above 0.50.
Native floor (control 5): bge 0.926, e5 0.972, MiniLM 0.974, all
above 0.90. Disjointness (control 4): zeros by code.
Controls 1 to 3 read literally by the checker and stated here
without adjustment:
- Control 2 (mismatched anchors): C3 at 0.000 everywhere and
  retention 0.000: the collapse the control demands happened. The
  literal clause "within 0.05 Recall@5 of C2" fails because C2 is
  NOT a floor on these pairs: raw 384-dim vectors from these three
  BERT-family encoders retrieve across models at 0.17 to 0.43 R@5
  without any transform. The control presupposed a floor that the
  data did not supply; the checker records the violation and the
  mechanism is stated rather than excused (the TR-002r wrong-model
  precedent, now in the other direction).
- Control 1 (scrambled anchors): the same C2 degeneracy applies to
  the literal clause, but the substantive finding is worse for H1:
  scrambled nonsense anchors do NOT collapse C3 when the store is in
  bge or e5 (at 1,024 anchors, scrambled 0.32 vs real 0.18
  bge->minilm; 0.49 vs 0.24 e5->bge). Nonsense anchors translate
  BETTER than real ones. Per the control's own text, the anchor
  coordinates carry gallery geometry, not semantic alignment.
- Control 3 (random projection): C3 exceeds random projection by
  0.18 on bge->minilm and 0.01 on minilm->bge against a 0.20 bar. A
  near-miss is a FAIL: relative representations barely beat noise on
  the primary pair.
Diagnostic run AFTER the gate read, reported only (D15a, script
committed before running): same-space relative representations
(store and queries in ONE model, both against the same anchors)
retrieve 0.56 (bge), 0.78 (MiniLM), 0.72 (e5) at 1,024 anchors
against natives above 0.92; anchor-mean centering does not help.
Mean pairwise cosine in the stores is 0.64 (bge), 0.33 (MiniLM), 0.83
(e5). The zero-fit coordinates are lossy before any translation, in
proportion to anisotropy, and the cross-model loss sits on top. C3
dies whenever MiniLM is the STORE (0.015 minilm->bge, 0.004
minilm->e5), the least anisotropic space; reported as direction
asymmetry. C4 at 64 anchors returns confidently wrong memories at
0.12 to 0.21 (native 0.002): the fitted ceiling with few anchors is
the memory-safety failure the confident-wrong clause was written to
catch, in the reported column. No threshold, checker, or grid line
was altered after the read; the diagnostic is a separate script and
a separate results file.

## D16. Native floor exclusions and a retention above 1.0
Control 5 as frozen: Qwen3-1.7B-4bit (native Q1 Recall@5 0.294,
confident-wrong 0.21) and Llama-3.1-8B-4bit (0.847) fall under 0.90
and are excluded from the boundary map with their numbers published;
gemma-2-9b (0.942) and the three encoders stay. Class means in the
report are over the twelve retained ordered pairs; the excluded rows
appear in results/summary.json and the report text. C4 "retention"
above 1.0 on gemma->Qwen and Llama->Qwen is arithmetic, not a
finding: a store translated from a healthy space retrieves better
than Qwen's own store does, which is exactly why Qwen is excluded.

## D17. Closeout, 2026-09-09
verify.sh exit code 1 as built: instrument legs green (25 checker
fixtures, anchor exam 9/9, plumbing smoke both worlds, store
integrity), PASS clauses (i) and (ii) red in every cell, controls 1
and 3 red for measured reasons, control 2 red on a degenerate
literal clause with its mechanism satisfied, KILL quiet. Oracle of
record revealed and scored (Brier 0.2718, modal FAIL); panel revealed
(three hashes MATCH) and scored (0.3302 / 0.0518 / 0.2330, every seat
modal FAIL; consensus reported-only 0.1824). Report draft v0.1,
utilization draft (credibility-asset proposed), figures committed.
Panel pilot proving cycle: legs 2 through 7 green on evidence; leg 1
(hashes fetched by the reviewer's channel) is the reviewer's act and
is recorded when they say so. Verdict pending PI ratification.

## D18. Disk line (standing closeout rule)
legion: tr003r 776 MB (corpus_store 774 MB, of which emb 707 MB in
six float32 sidecar-hashed npz files; texts 75 MB); HF cache 23 GB
shared with TR-002r, unchanged; oracle plaintext redundancy 12 KB;
326 GB free. cockpit: tr003r 1.7 MB (results, figures, report).
Sweepable on the PI's word: tr003r/corpus_store on legion (rebuildable
from the committed builder, the TR-002r registry, and the pinned
snapshots in about thirteen hours of extraction).
