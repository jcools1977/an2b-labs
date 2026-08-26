# TR-020 DECISIONS

Every judgment call, logged before the numbers it could bend toward.
Protocol thresholds are untouched; entries resolve ambiguity, always
toward the interpretation that makes H1 harder to pass.

## D1. Three-verdict taxonomy: dead, redundant, live
Decided before any system is built, because the redundant-duplicate
plant collides with a binary dead criterion: masking either duplicate
alone shows no delta, so both flag, but neither is dead in the
appended-never-read sense, and masking both together shows a live
effect. Semantics, frozen:

- **dead**: individually maskable with no measurable effect, AND no
  effect in pairwise masking either. The plant archetypes
  "appended-but-never-read" and "irrelevant-only retrieval" are dead.
- **redundant**: no measurable effect alone, measurable effect when
  masked jointly with its partner(s). The duplicate-tool archetype is
  redundant, and the seal marks BOTH duplicates as correctly flagged
  under this definition.
- **live**: measurable effect alone.

The pairwise sample is the instrument that separates dead from
redundant. The protocol's recovery gate (precision and recall >= 0.9)
is scored on the flagged set (dead union redundant) against the planted
set; class-exact agreement is additionally reported. Without this
decision, recovery scoring on the duplicate archetype is undefined and
the 0.9 gate would measure against a seal that does not know its own
answer.

## D2. Interaction KILL, quantified
The protocol's KILL ("one-at-a-time masking flags live components as
dead beyond tolerance") gets its number now: on the seeded systems,
if more than **10% of planted-live components** are verdicted dead or
redundant after the pairwise correction, one-at-a-time ablation is
untrustworthy and the entanglement result is published instead.

## D3. The measurement layer proves itself before it measures (red first)
TR-020 audits for components that run but never matter; its own judge
and canonicalizer must not be examples.

- **Judge gate:** the fixed quality judge (a local model, greedy,
  disjoint from the actor model) must score planted degradations
  (truncated answers, wrong-entity substitutions, off-topic responses)
  at least **1.0 point worse on its 1-10 scale** than intact answers,
  per degradation class, on a committed fixture set, before any seeded
  number counts.
- **Canonicalizer gate:** a committed fixture file per task family with
  hand-labeled change/no-change pairs; the canonicalizer must match
  **100%** (n >= 20 per family) before any answer-change rate counts.

## D4. Placebo violation semantics, pre-registered
The placebo control (paraphrase of a component's own output must be
inert: answer-change rate < 5% and quality-delta CI including zero) can
only bite in the wild phase, because a never-read plant paraphrased is
still never read. If a wild system fails placebo, that system is
wording-brittle and the verdict is **"unauditable by this method,
reported as such."** Never a tolerance adjustment. Written now, when
there is no wild system to be tempted by.

## D5. Wild-phase guards
Two, both structural: the wild-phase runner refuses to execute unless a
committed seeded-phase result shows the 0.9 recovery gate passed (the
protocol's own FAIL rule, enforced in code), and the list of four wild
configurations is committed to this file BEFORE any of them is audited,
so the wild sample cannot be cherry-picked after seeing dead fractions.
The list slot is reserved here, empty until Phase 5 planning:
- (wild-four list: to be committed before first wild audit)

## D6. Sealed ground truth
Plant lists live in `seed_systems/GROUND_TRUTH.sealed.json`, with its
SHA-256 committed in `seed_systems/SEAL.sha256`. The auditor package
(`auditor/`) may not reference the sealed file; verify.sh greps for it
and fails on any mention. Recovery scoring joins auditor verdicts with
the seal OUTSIDE the auditor. Finding the plants is an act of
measurement, not file access.

## D7. Replication control, hardest reading
"Dead verdicts must replicate across two disjoint probe halves" is read
as: the full three-class verdict is **identical on both halves for
every component**. A near-boundary flip is a control failure, not noise
to average over.

## D8. Tool name
Candidate: `deadwood` (short, blunt, zero-callers lineage; reads well
as `deadwood audit ./my-agent`). PyPI check 2026-08-26: **`deadwood` is
taken** (an outlier-detection package, v0.9.0); `deadwood-audit` is
free. Options: publish as `deadwood-audit` with `deadwood` as the CLI
entry point (collides only if both packages are co-installed), or a
different name. DeVere holds the final word; nothing ships under any
name until he gives it.

## D9. Scheduling on shared hardware
Adopted from TR-001's D6 lesson, applied as scheduling: phases 0-2 are
pure Python and run anywhere, alongside anything. Model-resident phases
(3-5) run on legion with a headroom check before each window; if the
co-resident Clutch process plus the actor model crowds the 85% line,
Clutch pauses for that window rather than fighting swap. Contention
threatens speed, not validity: all inference is greedy, seeded, and
deterministic, so a loaded machine produces identical numbers slower.

## D10. Dependency pins
`requirements.txt` pins what each phase actually uses, added as phases
land (numpy now; actor/judge model stack at Phase 2 with versions
recorded here). No unpinned installs on the experiment path.
