# TR-006 forecast scoring

Published verdict: **FAIL** (H0 shape; KILL did not fire), 2026-09-27
on the PI's standing word (D22). Brier baselines: uniform 0.75,
always-FAIL 0.0 on this outcome.

## Oracle of record (single seat, sealed 0f475c0 before Phase 0
closed; hash 27de79260aae... verified on legion; plaintext committed
beside)

Verdict forecast: PASS 0.10 / FAIL 0.55 / SPLIT 0.12 / KILL 0.23.
**Brier 0.2798. Modal call FAIL: HIT.**

| Claim | p | Graded | Why |
|---|---|---|---|
| Unlimited log matches or exceeds the best bounded configuration on at least one family | 0.65 | TRUE | ties on three of four cells |
| Regime fails AIC >= 10 on at least one family | 0.80 | TRUE | fails on all four cells |
| Frozen buffer within 3 points of the single best agent on both families | 0.70 | FALSE | 5 points under (41 puzzles), 6 points over (43 puzzles); QA within 2 |

Two of three on the correct side. The rationale priced the noise
correctly (a three-point standard error against any plausible gain)
and gave KILL real weight; no regime appeared for the KILL to locate.

## Panel (second live cycle; all three plaintexts MATCH their hashes)

| Seat | Served engine | PASS/FAIL/SPLIT/KILL | Brier | Modal |
|---|---|---|---|---|
| oracle-anthropic | anthropic/claude-fable-5.1 via Anthropic | 0.08 / 0.72 / 0.05 / 0.15 | 0.1098 | FAIL, HIT |
| oracle-openai | openai/gpt-6-astra via OpenAI | 0.07 / 0.51 / 0.07 / 0.35 | 0.3724 | FAIL, HIT |
| oracle-xai | x-ai/grok-4.6 via xAI | 0.10 / 0.50 / 0.25 / 0.15 | 0.3450 | FAIL, HIT |
| consensus (reported only) | mean probability | 0.08 / 0.58 / 0.12 / 0.22 | 0.2483 | FAIL |

oracle-anthropic
| Claim | p | Graded | Why |
|---|---|---|---|
| Smooth fits at least as well as piecewise on at least one family | 0.80 | TRUE | all four cells |
| Unlimited log matches or exceeds best bounded on at least one family | 0.65 | TRUE | three of four cells |
| Random-salience curves indistinguishable from self-assessed at most S | 0.60 | TRUE | within noise at every S |

oracle-openai
| Claim | p | Graded | Why |
|---|---|---|---|
| Accuracy at S=8 or 16 exceeds S=1 on average | 0.80 | TRUE | +1.8 and +3.8 (41), -1.0 and +3.5 (43): higher on average |
| Best bounded beats the unlimited log | 0.57 | FALSE | ties in three cells, +0.5 in one |
| Regime fails AIC >= 10 on both families | 0.83 | TRUE | all cells |

oracle-xai
| Claim | p | Graded | Why |
|---|---|---|---|
| Regime beats smooth on both families | 0.18 | FALSE | correct side |
| Best bounded beats the unlimited log | 0.28 | FALSE | correct side |
| Accuracy rises from near single-agent at S=1 to substantially higher by S>=8 on both families | 0.72 | FALSE | rises 2 to 4 points; falls on seed 43 QA |

## Reading

Four forecasters, four FAIL calls, and this time nobody over-priced
PASS (0.07 to 0.10). The spread was on KILL: the openai seat put 0.35
on an unstable breakpoint and paid for it; the anthropic seat's 0.72
on FAIL is the ledger's second-best live score. The shared miss was
mechanical rather than directional: every seat expected a gentle rise
with capacity, and the rise was two to four points where it existed
at all. Nobody, including the builder, anticipated that S could not
bind above six candidates at R = 2; the traces did. Engine-stratified
series now hold two live points per engine.
