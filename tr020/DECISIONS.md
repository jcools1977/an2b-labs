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

Recommendation on the record, 2026-08-26: **package `deadwood-audit`,
CLI command `deadwood`** (`pip install deadwood-audit`, then
`deadwood audit ./my-agent`). Command names do not collide with package
names, so the blunt one-word tool survives without fighting the
outlier-detection package for the slug. Awaiting ratification.

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

## D11. Per-item seeding; traces byte-reproducible in isolation
Determinism sneaks out of multi-agent systems through run-level state,
so the trace runtime seeds **per item, never per run**: every random
draw and every LM call derives its seed from (system_id, item_id,
component), nothing else. Consequence, enforced by test: a probe item's
trace is byte-identical whether run alone, twice, or inside the full
set. This is what makes a wild-phase finding replayable by a skeptic
("here is the exact trace where masking the retriever changed
nothing"); replayable traces turn a dead fraction from a claim into a
receipt. The test is red-then-green: a sabotage mode that draws from
run-level RNG must be caught by the reproducibility check.

## D12. Probe sets are synthetic, committed, and generated at seed 20
150 items per system, matched to each system's task, generated by
`scripts/build_probes.py` (seed 20) and committed as JSONL. Synthetic
keeps $0, keeps every probe inspectable, and makes the leakage question
moot; the generator is deterministic so the committed files are
reproducible from the script alone.

## D13. The hand in "hand-labeled" is human
The judge-damage and canonicalizer fixtures are the ground truth every
downstream CI stands on; if the session both writes and labels them,
the D3 gate is the measurement layer grading its own homework. So: the
fixture files are committed with proposed labels, DeVere spot-ratifies
them by reading, and the ratification is recorded as
`fixtures/RATIFICATION.json` carrying the SHA-256 of each ratified
fixture file. The D3 gate is **not armed** until that record exists and
its hashes match the committed files; any post-ratification edit breaks
the hashes and disarms the gate. Same principle as a human audit floor,
applied to the instrument instead of the corpus.

## D14. Placebo paraphrase sanity bounds
A "placebo" that quietly mangled meaning could masquerade as a
wording-brittleness finding, so every paraphrase is bounds-checked at
generation time and the bounds are frozen now: **length ratio within
[0.5, 2.0]** of the original and **content-word Jaccard overlap >=
0.3**. A paraphrase outside bounds is regenerated once with a stricter
prompt; if it still fails, the placebo run for that item is marked
invalid and reported, never silently used. Every paraphrase's measured
bounds are logged with the run.

## D15. Canonical answer families, judge specification, model choices
- **Canonical families** (answer-change is measured on canonicalized
  final answers): `number` (first parseable numeric, s3), `list`
  (comma-split, per-element case/whitespace normalized, s5), `span`
  (SQuAD-style normalization: lowercase, strip articles and
  punctuation, collapse whitespace; s2, s7), `text` (lowercase,
  collapse whitespace; s1, s4, s6). Under per-item seeding and greedy
  decoding, a truly unread component's mask leaves the final answer
  byte-identical, so `text` can afford to be strict.
- **Judge**: Llama 3.1 8B Instruct 4-bit (the TR-001 pinned build),
  greedy, scoring 1-10 with a fixed rubric prompt, disjoint from the
  actor model. Score parsed as the first integer 1-10 in the output;
  unparseable output is a judge error counted against the run, never
  imputed.
- **Actor**: Qwen3-1.7B-4bit (verified ungated 2026-08-26), thinking
  disabled, greedy. Both models' snapshot commits get pinned into
  `MANIFEST.json` by `scripts/record_model_revisions.py` at the legion
  environment build, TR-001 discipline unchanged (D10).

## D16. Placebo sampling plan
The placebo control paraphrases every output of a component across all
probe items, which is too expensive to run for every component. Sample,
frozen: **2 components per system**, chosen by seeded draw from the
full component list (seed derived per system), across all 7 systems.
The aggregate reported to the checker uses the mean change rate and the
widest quality CI across sampled components, the harder reading.
