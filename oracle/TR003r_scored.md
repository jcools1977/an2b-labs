# TR-003r forecast scoring

Published verdict pending ratification: **FAIL** (H0 shape; KILL did
not fire). Scored 2026-09-09 at closeout against the cold gate read.
Brier baselines: uniform 0.75, always-FAIL 0.0 on this outcome.

## Oracle of record (single seat, sealed ca801ab before Phase 0
closed; hash 045718d4f3e8... verified; plaintext committed beside)

Verdict forecast: PASS 0.33 / FAIL 0.60 / SPLIT 0.02 / KILL 0.05.
**Brier 0.2718. Modal call FAIL: HIT.** The seal was made with one
tool use (the write) and the forecast never entered the builder's
context until this reveal.

| Claim | p | Graded | Why |
|---|---|---|---|
| C4 retention exceeds C3 retention at 1,024 random anchors in every primary cell | 0.85 | TRUE | 0.69 to 0.89 vs 0.015 to 0.19, all four cells |
| C3 retention clears 0.80 in all four cells | 0.45 | FALSE | 0.19 and 0.015 |
| C3 provenance clears 0.90 in all four cells | 0.40 | FALSE | 0.28 and 0.11 |

All three on the correct side of 0.5. The rationale named, before
any number, the uncentered anchor-coordinate compression in bge, the
trivial pass of the confident-wrong clause, and the scrambled-anchor
control refusing to collapse "because identical nonsense strings
still carry lexical overlap in both spaces." Three mechanisms
predicted, three measured.

## Panel (pilot's first live subject; sealed e4bdb00; all three
plaintexts MATCH their committed hashes and seal records)

| Seat | Served engine | Forecast (PASS/FAIL/SPLIT/KILL) | Brier | Modal |
|---|---|---|---|---|
| oracle-anthropic | anthropic/claude-fable-5.1 via Anthropic | 0.35 / 0.55 / 0.04 / 0.06 | 0.3302 | FAIL, HIT |
| oracle-openai | openai/gpt-6-astra via OpenAI | 0.15 / 0.83 / 0.00 / 0.02 | 0.0518 | FAIL, HIT |
| oracle-xai | x-ai/grok-4.6 via xAI | 0.27 / 0.61 / 0.08 / 0.04 | 0.2330 | FAIL, HIT |
| consensus (reported only) | mean probability | 0.26 / 0.66 / 0.04 / 0.04 | 0.1824 | FAIL |

Sub-claims, graded against published numbers only:

oracle-anthropic
| Claim | p | Graded | Why |
|---|---|---|---|
| C4 retains >= 0.80 in both directions at 1,024, so KILL does not fire | 0.88 | FALSE (number), KILL part TRUE | bge->MiniLM C4 retention 0.69 / 0.79, under 0.80; MiniLM->bge 0.86 / 0.89; KILL quiet |
| C3 rises monotonically 64 < 256 < 1,024 AND exceeds C2 by > 0.20 at 1,024 | 0.90 | FALSE | MiniLM->bge 0.006, 0.005, 0.014 is not monotone; C3 0.19 sits BELOW C2 0.36 to 0.48 |
| C3 confident-wrong <= 0.05 in every cell | 0.75 | TRUE | 0.000 everywhere |

oracle-openai
| Claim | p | Graded | Why |
|---|---|---|---|
| C3 at 1,024 exceeds C2 in both directions, both seeds | 0.97 | FALSE | C2 0.36 to 0.48 beats C3 0.015 to 0.19 in every cell |
| C3 mean Recall@5 increases from 64 to 1,024 anchors | 0.88 | TRUE | 0.050 to 0.100 averaged over directions |
| Scrambled C3 exceeds C2 by > 0.05 in at least one tested configuration | 0.80 | MIXED | never on the primary pair where the control reads (0.45 vs 0.48 at best); true on the map (e5->bge 0.49 to 0.55 vs 0.42 to 0.44) |

oracle-xai
| Claim | p | Graded | Why |
|---|---|---|---|
| C3 retention >= 0.80 in all four cells | 0.42 | FALSE | 0.19 and 0.015 |
| C3 provenance >= 0.90 in all four cells | 0.61 | FALSE | 0.28 and 0.11; the one sub-claim priced on the wrong side |
| C4 retention >= 0.50 both directions, KILL quiet | 0.93 | TRUE | 0.69 to 0.89 |

## Reading

Every forecaster, the oracle of record and all three panel seats,
called FAIL, and every one priced PASS between 0.15 and 0.35 on a
question whose measured outcome was not close. Shared error, stated
plainly: two of four expected C3 to beat the raw-vector floor with
high confidence (0.90 and 0.97), and the floor turned out not to be
one on BERT-family encoders. The openai seat's low Brier came from
committing hardest to FAIL and pricing SPLIT at exactly zero on the
protocol's own text; its sub-claims were the least accurate of the
panel. The two-experiment uniformity blind spot from Wave 2 did not
recur here: outcomes were uniformly red and every seat leaned red.
Engine-stratified series open with these numbers; nothing is
aggregated across engines. The reviewer's context-rich forecast,
sealed through their channel, is scored when its plaintext is
relayed.
