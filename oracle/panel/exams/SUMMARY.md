# Retro-calibration exam: panel seats, 2026-09-08

**RETRO. Zero foresight weight. Mechanics are the bar (DECISIONS D6);
the calibration numbers below are the anchor for each seat under the
engine it was served on today.** Six closed TRs, identical prompt
(template sha in each record), one attempt per item, no re-roll.
Spend $0.9684 of the $10 cap across 21 calls.

| Seat | Served engine (gateway) | Mechanics | Mean Brier | Modal hits | Params sent | Self-reported cutoff |
|---|---|---|---|---|---|---|
| oracle-anthropic | anthropic/claude-fable-5.1 via Anthropic | PASS 6/6 | 0.4885 | 4 of 6 | none | 2025-01 |
| oracle-openai | openai/gpt-6-astra via OpenAI | PASS 6/6 | 0.6274 | 3 of 6 | seed | 2024-08 |
| oracle-xai | x-ai/grok-4.6 via xAI | PASS 6/6 | 0.5014 | 4 of 6 | temperature, top_p, seed | 2023-12 |
| consensus (reported only) | mean probability | | 0.5158 | 4 of 6 | | |

Baselines: uniform 0.75; always-FAIL 0.3333 on this battery (five FAIL,
one SPLIT). The 2026-09-01 single-seat anchor scored 0.6607 on its
four-TR battery. No seat beats always-FAIL, as no forecaster has yet.

## Per item (published verdict in brackets)

| TR | anthropic | openai | xai | consensus |
|---|---|---|---|---|
| TR-001 [FAIL] | 0.548 KILL | 1.205 KILL | 1.023 KILL | 0.899 KILL |
| TR-020 [SPLIT] | 0.765 PASS | 1.083 FAIL | 0.727 PASS | 0.839 FAIL |
| TR-011 [FAIL] | 0.485 FAIL | 0.214 FAIL | 0.366 FAIL | 0.332 FAIL |
| TR-015 [FAIL] | 0.452 FAIL | 0.684 KILL | 0.407 FAIL | 0.474 FAIL |
| TR-004 [FAIL] | 0.484 FAIL | 0.385 FAIL | 0.366 FAIL | 0.391 FAIL |
| TR-002r [FAIL] | 0.198 FAIL | 0.195 FAIL | 0.121 FAIL | 0.161 FAIL |

## Reading, RETRO

- **Cross-vendor error is correlated on the two hard items.** All three
  vendors called TR-001 KILL (it was FAIL) and none called TR-020 SPLIT
  (the one SPLIT in the battery). This is the panel's first
  pre-registered question (PANEL_SPEC procedure 4) answered on retro
  data: the uniformity blind spot the ledger named in Wave 2 looks
  frontier-wide, not a vendor artifact. Live seals will say whether
  that holds with foresight.
- **All three converge on TR-002r FAIL with confidence** (0.63 to
  0.70), the best item for every seat, consistent with the ledger's
  of-record oracle (0.2718) on the same protocol.
- **Contamination flags are CLEAR on every item, but the flag rests on
  self-report.** The gateway's cutoff field is null for all three
  engines; the self-reported cutoffs (2023-12 to 2025-01) precede
  every publication date, and a model created in 2026 reporting a
  2024 cutoff should be read with the usual doubt. Recorded as the
  rule requires; not a certification of cleanliness.
- **Sampling actually sent differs per seat** and is in each record:
  the Anthropic engine accepted no sampling parameter, OpenAI took
  seed only, xAI took all three. The determinism exception is now
  concrete per engine.

## What this certifies

Each seat is certified for panel duty under the engine it was served
on today. A different served engine at a live seal starts a new
engine-stratified series for that seat, with no exam carried over.
