# TR-019: Cryptographic Attention
**Track E: Provenance and Verification** | Status: Protocol draft v0.1 | **Product candidate**

## Question
Can a multi-model synthesis pipeline emit a compact, verifiable provenance tree, a Merkle commitment binding the final answer to exactly which models, prompts, parameters, and retrieved spans produced it, with negligible overhead and meaningful tamper detection?

## Hypothesis
**H1:** A provenance layer wrapping a council/RAG pipeline can (a) commit to all contributing artifacts (model IDs and weights hashes where available, prompts, sampling params, retrieved span hashes, inter-agent messages) in a Merkle tree whose root accompanies the answer, (b) support selective disclosure proofs ("span 14 of document X contributed, here is the inclusion path") without revealing the full trace, (c) detect 100% of a defined tamper suite, and (d) add < 5% latency and < 10 KB per response.
**H0:** Honest provenance at this granularity is either too heavy for interactive use or too coarse to catch realistic tampering; receipts for synthesis remain impractical.

## Background
Single-model attribution is hard; multi-model synthesis currently has *no* receipts at all. An answer assembled by three models over retrieved documents is an evidentiary black hole, which is disqualifying for regulated, legal, and government contexts. The primitives already exist in-house (hash-chained attestation from prior cryptographic-provenance work); the research contribution is the schema and the tamper-detection evaluation, and the product contribution is obvious. Determinism boundaries are the honest hard part: the commitment proves *what went in and what came out*, not that the stochastic middle is replayable, and the report must say so plainly.

## Design
- **Schema:** canonical leaf encoding for {model descriptor, prompt hash, params, retrieval span hashes with source doc Merkle paths, message log hashes, output hash}; tree root signed; selective-disclosure proof format specified
- **Reference implementation:** wrap the TR-006 council harness and a standard RAG pipeline; measure overhead at 1, 3, 5 agents and 0-50 retrieved spans
- **Tamper suite (the adversarial eval):** 12 defined attacks, including span substitution after commitment, model swap with descriptor kept, prompt edit, message-log reordering, retrieval-source substitution, params change, root reuse across answers; each must be detected by verification
- **Verifier:** standalone script, no access to the pipeline, verifying from {answer, root, disclosed proofs} alone
- **Determinism boundary test:** re-run identical committed inputs; document exactly which leaves reproduce and which (stochastic outputs) are commit-only

## Metrics
- Tamper detection rate over the suite (target 12/12); false-alarm rate on 500 honest runs (target 0)
- Latency and payload overhead vs uninstrumented pipeline
- Proof sizes for selective disclosure

## Pass/Fail (frozen before data)
- **PASS:** 12/12 tamper detection, 0 false alarms on honest runs, < 5% latency overhead, < 10 KB payload, and selective disclosure verified by the standalone verifier.
- **FAIL:** any undetected tamper class, or overhead exceeding bounds.
- **KILL:** a tamper class is found that the schema *cannot* express detection for without re-architecting (documented as the negative result; the schema gap is the finding).

## Negative Controls
1. **Broken-verifier canary:** a deliberately corrupted verifier build must fail the honest suite (tests that tests can fail: the zero-callers covenant applied to cryptography).
2. **Root-collision sanity:** distinct runs must never share roots across 10,000 honest runs.
3. **Blind red team round:** tamper cases applied by a second party (or a scripted adversary unseen by the implementer) after implementation freeze.

## Cost and Time
$0. Est. 4-5 sessions (schema design is the long pole).

## Deliverables
- `tr019/` repo: schema spec, reference implementation, standalone verifier, tamper suite; 8-10 page report. **Evaluate provisional patent filing before public disclosure ships.**
  *Gate note, 2026-09-03 (PI's word; thresholds untouched): the IP
  review inherits FRONTIER-001's crowding warning — Merkle-chained
  audit logs and decision-BOM reconstruction are entering enterprise
  toolkits, so the review must identify what per-inference,
  attention-level provenance adds over action-level audit trails, or
  fold.*

## Dependencies
TR-006 harness convenient, not required. Extends existing attestation primitives.
