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
  seat policies become STRUCTURAL for the seat's OUTBOUND actions.
  What Warden does not address (review A6): the input path and
  plaintext custody, which remain governed by ceremony and the
  transit rules; the panel pilot's pass criteria carry that burden.

## Design rules the lab imposes on the arena (to pre-register when built)

1. **Seat and engine are both recorded on every act, and scoring
   is ENGINE-STRATIFIED by rule.** Calibration attaches to the seat;
   Brier series are reported per engine within a seat, never
   aggregated across engine changes; the recorded engine is the
   SERVED backend (provider and model metadata returned by the
   gateway), not the routing alias; each engine's stated training
   cutoff is recorded per seal (review B2/B5).
2. **Engine currency by live lookup, never memory.** What "latest"
   resolves to is read at swap time and logged (the MODELS.md rule,
   applied to seat descriptions).
3. **Frozen thresholds never live in an LLM seat, and neither does
   unreviewed authorship of the code that reads them.** Gates read
   through code-engine seats only; gate-reading code is reviewed by
   a seat other than its author before first duty; frozen protocol
   files carry a hash manifest checked mechanically (a freeze check
   that FAILS on any diff to a frozen TRxxx file), so BB4C rule 1
   has a negative control of its own (review B4).
4. **Every new seat passes an exam before real duty** (the
   certification-exam pattern: estimators, translators, and
   watchdogs all earned their posts; so do seats).
5. **Two-channel truth generalizes to n-channel truth**: the bus and
   the repo are the shared record; no seat's context is
   authoritative.
6. **The PI decides at every gate. This is a rule of the arena, not
   a flourish**: authoring, forecasting, and executing may be seat
   work; ADJUDICATION is never seat work (review A4, resolving the
   earlier draft's contradiction in the covenant's favor).
7. **Constraints are not self-editable.** Fleet manifests and Warden
   policy files live under the same freeze-and-approval discipline
   as protocols: edits are logged, approved through a channel other
   than the seat they constrain, and every seal hashes the policy
   in force (review B4).

## The portfolio, through Voltron (wired 2026-09-08 on the PI's word)

The estate converged on one epistemology twice, independently: the
lab applies preregistration, adversarial controls, and receipts to
SCIENCE; Voltron (products/eidetic/voltron) applies the identical
discipline to ORCHESTRATION — preregistrations with checksummed
results, gated canaries (G1-G6 accepted), 1,026 passing tests dated
2026-09-08, and an authority boundary that currently reads
NOT_AUTHORIZED / NOT_ADMITTED across every consequential workflow.
Voltron's binding rule is this document's rules 6-7 stated as
protocol: "a component may provide signed evidence to the next
stage; it may not silently inherit that stage's authority."

The organ map, per Voltron's own structure: Eidetic supplies memory
EVIDENCE; AEGIS (vendored snapshot inside Voltron) supplies
grounding, abstention, and source precedence; Procura supplies
intake through a read-only adapter; ClawTex supplies execution with
atomic one-use admission; CadenceAuth supplies identity proofs;
EngramPort supplies the collaboration surface. Voltron binds their
proofs before any consequential action.

What this settles for the arena: the seal-receipt provisions this
spec hand-rolled (policy hashing, watched DENYs, non-self-editable
constraints) are not to be rebuilt in the lab; they are Voltron
protocol families (signed actor admission, hash-chained events,
pinned Trust Bundles with rotation) to be ADOPTED through the lab's
exam discipline, component by component, the way every estimator
and translator earned its post. EngramPort's measured impersonation
gap is precisely what signed admission closes. Autonomy grows at
the speed of receipts; Voltron is where the receipts come from.
Standing constraints honored on both sides: Voltron's README states
no EngramPort integration is in its current implementation, and the
lab's AEGIS Gate 2 hold remains blocking until the PI's named word.

## The road there

- **Wave 3 (if the review slates TR-003r and TR-006 on their
  scientific merits, which FRONTIER-002 supports independently):**
  their findings would, as a byproduct, constrain this design;
  that benefit is a harvest observation, never slate rationale
  (review A1). First engine-agnostic duty: the three-vendor oracle
  panel, ClawTex-run, Warden-sealed (harvest candidate 5), as a
  PILOT until its proving cycle completes.
- **Waves 4-5 (through TR-020's close):** reviewer-seat diversity
  piloted as forecast columns before any second reviewer gets a
  pen; extraction and analysis runners enrolled as fleet seats so
  the estate's compute discipline (supervisors, checkpoints,
  budgets) becomes seat policy instead of session craft.
- **The next batch:** experiments authored, forecast, and executed
  by the arena on EngramPort — adjudicated by the PI at every gate,
  per rule 6 — engines chosen per duty
  from whatever the frontier then holds, under the same covenant
  machinery that ran the first twenty. The lab's published results
  already constrain the design: cross-model memory rides paired
  anchors (TR-002r), and the workspace's capacity curve will have
  been measured (TR-006) rather than assumed.

*The PI decides at each gate. Sessions prepare; the arena will too.*
