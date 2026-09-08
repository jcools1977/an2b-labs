# ARENA.md — the lab as an arena of engine-agnostic seats
**Direction document, drafted 2026-09-08 on the PI's word ("a fleet
of bots should not be LLM-confined"). This is a roadmap, not a
protocol: nothing here is frozen, nothing here touches an experiment
in flight, and the Wave 3 slate decision at the harvest review is
where any of it becomes work.**

## The principle

A seat is a persistent identity with duties, a policy, and a track
record. An engine is whatever currently animates it: a frontier API
model behind OpenRouter, a pinned local model, frozen deterministic
code, or a human. Engines swap by editing a description; seats
persist. The lab's governance (sealing, decision logs, Warden
policies, audit trails) attaches to SEATS, so swapping an engine
never resets accountability.

This is not aspiration; it is a description of the estate slightly
ahead of itself:

| Lab role today | Already a seat? | Engine today |
|---|---|---|
| Builder | yes (this session) | Anthropic frontier |
| Reviewer | yes (chat channel) | Anthropic frontier |
| Protocol-only oracle | yes (sealed per TR) | Anthropic frontier |
| Checkers / verify legs | in effect | frozen code (deterministic) |
| Extractors / runners | in effect | pinned local models |
| PI | the root seat | human |

The checkers are the proof that the arena was never LLM-confined:
the lab's most trusted seats are deterministic code, and every
verdict already flows through them.

## What ClawTex/EngramPort supplies (investigated 2026-09-08)

- Fleet manifests declare model per seat; the bus
  (api.engramport.com) admits any HTTP-plus-key process as a
  first-class seat; cross-vendor panels are a coded example
  pattern; a single OpenRouter key resolves "all vendors."
- Warden gives ALLOW/DENY/REVIEW per tool call with an audit log:
  seat policies become STRUCTURAL. The oracle's deny-all-tools
  policy upgrades the ledger's isolation from instruction-level to
  policy-enforced.

## Design rules the lab imposes on the arena (to pre-register when built)

1. **Seat and engine are both recorded on every act.** The oracle
   ledger's calibration history attaches to the seat, with the
   engine noted per seal, so an engine swap is visible in the Brier
   series rather than silently laundered through it.
2. **Engine currency by live lookup, never memory.** What "latest"
   resolves to is read at swap time and logged (the MODELS.md rule,
   applied to seat descriptions).
3. **Frozen thresholds never live in an LLM seat.** Gates read
   through code-engine seats only; reasoning seats propose, code
   seats decide. This is already the lab's law; the arena inherits
   it structurally.
4. **Every new seat passes an exam before real duty** (the
   certification-exam pattern: estimators, translators, and
   watchdogs all earned their posts; so do seats).
5. **Two-channel truth generalizes to n-channel truth**: the bus and
   the repo are the shared record; no seat's context is
   authoritative.

## The road there

- **Wave 3 (the de-risking wave, if the review so slates it):**
  TR-003's rescope measures what survives cross-model memory
  translation on the bus's own substrate question; TR-006 measures
  the shared-workspace capacity regime the arena's bus embodies.
  First engine-agnostic duty: the three-vendor oracle panel,
  ClawTex-run, Warden-sealed (harvest candidate 5).
- **Waves 4-5 (through TR-020's close):** reviewer-seat diversity
  piloted as forecast columns before any second reviewer gets a
  pen; extraction and analysis runners enrolled as fleet seats so
  the estate's compute discipline (supervisors, checkpoints,
  budgets) becomes seat policy instead of session craft.
- **The next batch:** experiments authored, forecast, executed, and
  adjudicated by the arena on EngramPort, engines chosen per duty
  from whatever the frontier then holds, under the same covenant
  machinery that ran the first twenty. The lab's published results
  already constrain the design: cross-model memory rides paired
  anchors (TR-002r), and the workspace's capacity curve will have
  been measured (TR-006) rather than assumed.

*The PI decides at each gate. Sessions prepare; the arena will too.*
