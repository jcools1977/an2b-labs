# The Oracle Ledger

A standing mechanism, stood up 2026-09-01 on the PI's word: before
each experiment's Phase 0 closes, a fresh model instance with no repo
access receives the frozen protocol text ONLY and commits a sealed
prediction. The question the ledger answers over time: could the
model's priors have known these results in advance, or does the lab
keep finding things the priors get wrong?

## Procedure (per TR)

1. **At kickoff, before Phase 0 closes:** a fresh instance (no tools,
   no web, no repo; the protocol text pasted inline; model id
   recorded) returns a prediction in the fixed schema below.
2. **Sealing:** the prediction JSON's sha256 is committed to
   `oracle/sealed/TRxxx.sha256` at kickoff; the plaintext stays out
   of the repo (held locally, gitignored) until closeout, when it is
   committed beside its hash and scored.
3. **Scoring at closeout:** multiclass Brier score on the verdict
   distribution against the published verdict; directional calls
   graded true/false/unresolvable with one line of justification
   each, referencing published numbers only.

## Prediction schema

```json
{
  "verdict_probabilities": {"PASS": 0.0, "FAIL": 0.0,
                             "SPLIT": 0.0, "KILL": 0.0},
  "key_effect_directions": [
    {"claim": "a directional statement tied to the protocol's own metrics",
     "probability": 0.0}
  ],
  "rationale": "short paragraph"
}
```

Verdict classes: PASS = all frozen gates met. FAIL = gates missed.
SPLIT = the protocol's own legs divide (some pass, some fail, per its
structure). KILL = the pre-registered kill criterion fired as the
primary outcome. Brier = sum over classes of (p - outcome)^2; lower
is better; a uniform forecast scores 0.75.

## Isolation, honestly stated

The oracle instance runs as a subagent instructed to use no tools and
answer from the pasted text alone; isolation is instruction-level in
this harness, not structural. Two mitigations: the instance's
transcript is the prompt and the JSON (auditable), and the published
results postdate every available model's training cutoff, so priors
cannot contain the outcomes. A structurally sandboxed runner is an
open improvement.

## Retro-calibration anchor (Wave 1 + TR-015)

The four closed experiments were retro-predicted 2026-09-01 by the
same procedure (fresh instance, protocol text only). Retro sealing is
moot, so these are labeled RETRO and serve only as the calibration
anchor; they carry no evidential weight about foresight. Results in
`retro_calibration.json`. First live subject: TR-004.
