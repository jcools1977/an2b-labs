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
fresh-entry requirement as TR-002r's D1 did with FRONTIER-001. Its
reviewer countersignature has NOT landed; the PI overrode that hold
explicitly on 2026-09-08 (RATIFICATION_WAVE3.md), so this experiment
carries the disclosed exposure that its radar entry was written by
the builder seat and spot-checked by no one else yet. If the
countersignature later finds a cited identifier false, that is
logged here and reported. Sensing only; no threshold derives from it.

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
