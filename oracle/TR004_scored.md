# TR-004 forecast scoring (first live subjects of the ledger)

Published verdict: **FAIL** (near-miss; KILL did not fire).
Scored 2026-09-02 at closeout. Brier baselines: uniform 0.75,
always-FAIL 0.0 on this outcome.

## Protocol-only oracle (sealed before Phase 0; hash verified
4b6776a8..., plaintext revealed beside its seal at closeout)

Verdict forecast: PASS 0.22 / FAIL 0.40 / SPLIT 0.10 / KILL 0.28.
**Brier 0.497. Modal call FAIL: HIT** (the isolated oracle's first
modal hit in five subjects, after 1-of-4 on the retro anchor).

| Claim | p | Graded | Why |
|---|---|---|---|
| Metaphorical LID higher under both estimators (token model) | 0.65 | TRUE | +0.181 / +0.133, both positive |
| Delta >= 0.2, CI excl. zero, survives controls | 0.35 | FALSE | PR 0.193 max, MLE loses point |
| Sentence embedder reproduces direction; KILL avoided | 0.55 | TRUE | bge +0.253/+0.337; kill leg green |

All three sub-claims on the correct side of 0.5.

## Context-rich reviewer forecast (PROVISIONAL: scored against the
relay text per tr004 D19; authoritative scoring requires the PI's
held plaintext verified against hash 2329d28e...)

Verdict forecast: FAIL 0.55 / SPLIT 0.25 / PASS 0.20.
**Brier 0.305 (provisional). Modal call FAIL: HIT.**

| Sub-claim | p | Graded | Why |
|---|---|---|---|
| 1. ID-delta gate clears | 0.35 | FALSE | near-miss, gate red |
| 2. Curvature-delta gate clears | 0.30 | FALSE | curvature delta 0.000 |
| 3. KILL fires | 0.20 | FALSE | model-2 effect stronger, kill green |
| 4. Direction: metaphorical HIGHER (conditional) | 0.75 | TRUE | everywhere measured |
| 5. Raw effect survives rogue-dimension control | 0.55 | TRUE | +0.169 of +0.181 retained, CI excl. zero (checker fired only for gate-level reasons) |
| 6. A substitute estimator passes the frozen noisy exam | 0.65 | TRUE | PR, first attempt, every leg |
| 7. Layer-8/24 direction replicates at both depths | 0.50 | MIXED | PR yes at both; MLE only at 24 |

Six of seven on the correct side of 0.5 (one mixed). The mechanism
note named the modal failure path as controls cutting an
anisotropy-carried delta; the measured path was gentler (the effect
survives its controls numerically and was simply born under-gate),
so the FAIL prediction was right with the mechanism half-right.

## Reading

Context beat isolation, as it should: 0.305 vs 0.497, sharper
sub-claims, same modal verdict. The ledger's live question, whether
the lab keeps finding what priors miss, now has its first nuanced
answer: both forecasters called this FAIL, and both under-priced the
direction being real everywhere while the magnitude missed
everything. The standing pattern to watch across Wave 2.
