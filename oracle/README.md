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

## Panel seals (pilot, amended 2026-09-08 per review A7)

From Word 1 of the Wave 3 ratification, the ledger gains a second
mechanism beside the single-seat oracle: a three-seat, three-vendor
panel run on legion under ClawTex's Warden. Its spec is
`PANEL_SPEC.md`; its runner and decision log are in `panel/`. This
section states what a valid panel seal is, so the constitution and the
mechanics agree.

A panel seal for TR-xxx and seat S is valid when all of the following
hold:

1. `oracle/sealed/TR-xxx.S.sha256` is committed and PUSHED, and the
   reviewer's channel has fetched it, before closeout work begins.
   Commit timestamps alone evidence nothing.
2. `oracle/panel/seals/TR-xxx.S.json` records: the seat; the engine as
   resolved (routing alias, canonical slug, gateway creation date,
   gateway cutoff field) and as SERVED (model and provider the gateway
   returned); the self-reported cutoff; sampling requested and sent;
   `request_had_tools: false` and zero tool calls in the response; the
   protocol file, its sha256 and the commit; the prompt template hash
   and the assembled prompt hash; the Warden policy path and sha256 in
   force; a reference to a passing DENY control for that policy hash;
   the plaintext sha256; and the gateway's usage accounting.
3. The freeze manifest was green and the policy matched its committed
   blob at seal time (the runner refuses otherwise).
4. One forecast per seat per seal. A superseded forecast stays beside,
   labeled, and is never selected.

Scoring is engine-stratified: a seat's Brier series is reported per
served engine and never aggregated across an engine change. The
always-FAIL baseline is a standing line in every score. The
mean-probability consensus is reported only and is never the headline.
The reviewer's context-rich forecast remains the ledger's separate
column. The retro-calibration exam each seat sits before duty is a
mechanics exam; its calibration numbers are RETRO and carry no
foresight weight.

Isolation, restated for the panel: Warden's deny-all policy makes a
seat's outbound actions structurally impossible and is watched denying
before first duty; the input path is evidenced by the prompt hash; and
forecast plaintext never transits the builder's context because the
runner prints hashes only. The single-seat procedure above remains the
fallback when the gateway is down, with the missing panel seal recorded
as absent, never backfilled.
