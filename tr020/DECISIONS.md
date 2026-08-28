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

**Selection criteria, committed 2026-08-27, before any candidate is
named** (criteria-then-names, the committed-sweep-grid move applied to
sampling, because "measured dead fraction in real agent systems"
invites exactly one attack: that the systems were picked to be
bloated):
1. Popularity: a widely used open-source agent framework or template,
   evidenced by stars/downloads, so the sample reflects what builders
   actually deploy.
2. Runnable against a local OpenAI-compatible endpoint with the
   default configuration untouched.
3. The four span distinct architecture families (e.g. RAG pipeline,
   tool-calling agent, multi-agent crew, planner-executor), no two
   from the same family.
4. Default configurations as shipped: the audit measures what the
   repo hands a new user, not a tuned variant.

**Observational freeze:** the wild audit runs the seeded phase's
configuration unchanged: probe counts, neutral mask placeholders, the
pinned judge, canonical families, thresholds, and per-item seeding all
inherit as committed. Zero knobs. Anything a wild system needs adapted
merely to run (endpoint wiring, prompt plumbing) is logged in this
file as plumbing, never as tuning.

**The wild four, committed 2026-08-27 on DeVere's ratification, before
any wild audit, stars pulled from the GitHub API at commit time:**
1. **LangChain ReAct tool agent** (langchain-ai/langchain, 145,138
   stars) - tool-calling agent family
2. **LlamaIndex starter RAG** (run-llama/llama_index, 51,894 stars) -
   RAG pipeline family
3. **CrewAI default crew** (crewAIInc/crewAI, 57,680 stars) -
   multi-agent crew family
4. **AutoGen planner-executor group chat** (microsoft/autogen, 60,654
   stars) - planner-executor family

Alternates if a candidate fails the runnable-with-defaults test at
wiring time (swap logged here with the failure reason, never silently):
smolagents (tool-calling), MetaGPT (planner-executor).

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
outlier-detection package for the slug.

**Ratified by DeVere, 2026-08-26.** The tool is `deadwood-audit` /
`deadwood`.

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
  final answers): `number` (full sequence of parseable numerics, s3),
  `list` (separator-normalized split on commas, semicolons, and "and";
  per-element case/whitespace normalized, s5), `span` (SQuAD-style
  normalization: lowercase, strip articles and punctuation, collapse
  whitespace; s2, s7), `text` (lowercase, collapse whitespace; s1, s4,
  s6). Under per-item seeding and greedy decoding, a truly unread
  component's mask leaves the final answer byte-identical, so `text`
  can afford to be strict.
- **Family rules, ratified 2026-08-26:** text is strict and span is
  normalized BY DESIGN: maximum text sensitivity costs nothing on true
  deads (bytes identical under greedy determinism) while making every
  dead verdict harder to earn, which is the direction the headline
  number should be conservative in. Lists are ordered: the list-family
  tasks are alphabetize-style, so order is the task and reordering is a
  wrong answer.
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

## D17. Ratification corrections 36, 48, 59
The first exercise of the D13 gate caught three labels that were code
artifacts enshrined as ground truth, flagged by a second reader and
conceded by the author: #36 ("12 + 1" vs "12" is a CHANGE to a human;
first-number extraction said otherwise), #48 and #59 (semicolon and
"and" as list separators read identically to a human; the comma-only
parser said otherwise). Labels and code were corrected together
(canon_number compares the full number sequence; canon_list splits on
commas, semicolons, and "and"), machine consistency re-verified 80/80
on the corrected pair, and ratification bound to the corrected hashes.
Three verdicts changed, seventy-seven held.

## D18. Standing ratification mechanism: cross-instance review, PI witness
Recorded on DeVere's ruling, 2026-08-26. This lab's ratification
mechanism is **cross-instance adversarial review with PI witness**: the
author instance and the reviewer instance are separate model contexts;
disagreements are adjudicated on the record, in front of the human PI,
who carries artifacts between contexts, witnesses the adjudication, and
holds override on every ruling. Ratification means the PI, having
witnessed the argument, affirms the outcome matches his judgment; it
never means re-deriving the work. Two instances of the same model
family have real but partial independence (different contexts and
roles, demonstrated by this gate's first exercise catching three real
defects; shared training lineage, so correlated blind spots remain
possible on judgment calls, which is why the PI witness and the
public record stay in the loop). The PI's name goes on the seal
because it is free and stronger in the report. The pre-registration
commits, sealed ground truths, and public FAIL discipline are not
thinned by this mechanism and never will be: they are what make
autonomy legible to outsiders.

## D19. Placebo scoping: the failure mode is directionally asymmetric
DRAFTED 2026-08-27 on the reviewer's adjudication; **RATIFIED by
DeVere, 2026-08-27**, as amended after the 8B-paraphraser supplementary
run.

The seeded placebo measured 34% aggregate answer-change: near-zero on
span/number/list systems, 36-98% on text-family generative systems,
with quality CIs including zero throughout. The scoping rests on this
load-bearing argument, stated verbatim because it is what separates
scoping from rationalizing: **the placebo failure mode is directionally
asymmetric. Under greedy cascades, paraphrasing a live component's
output can only add answer-change; nothing about wording perturbation
can make a live component look byte-invariant. So the failure can
inflate change-rates on live components but cannot manufacture false
deads, and every verdict the tool actually claims (dead and redundant,
both defined by exact invariance under masking) sits on the side of the
asymmetry the failure cannot reach.** That is why recovery was perfect
through six wording-brittle systems: deadness showed up as invariance,
and cascades only ever push away from invariance.

AMENDED 2026-08-27 after the supplementary 8B-paraphraser run: the
draft's original sentence "quality CIs including zero throughout" was
FALSIFIED by the clean data and is replaced, with the falsification
left on the record (that a frozen interpretation could be falsified is
what makes its surviving core credible rather than convenient). The
clean table: change rates indistinguishable between weak and strong
paraphrasers on every text system (cascade physics, not paraphrase
sloppiness); span and number families near-inert (0.3->2.3 and 0->1.3
upticks, one report sentence, no scoping change; s3's original 7%
dissolved entirely as paraphrase artifact); and **quality deltas in
text systems nonzero in BOTH directions** (s4 -0.3; s5 +0.4 to +1.0;
s6 +0.1 to +0.7).

Ruling, once ratified: the placebo's two arms are reported separately
and per-family; the change-arm is diagnostic for extractive, numeric,
and list answers and is recorded as structurally unsatisfiable for
live components of text-family systems under greedy determinism; the
placebo leg's red is the pre-registered-reason red, per the TR-001 D28
pattern. check_controls.py stays frozen byte-for-byte.

Methodological findings, claimed rather than buried:
1. Placebo controls for agent-system audits must split
   wording-inertness from quality-inertness, because generative
   cascades make the former structurally unsatisfiable for live
   components.
2. **Paraphrase provenance moves quality.** A stronger model
   paraphrasing a weaker system's intermediates is an intervention,
   not a placebo: upgrade the planner's prose and answers improve,
   upgrade the aggregator's and they dip. The placebo paraphraser must
   be capability-matched to the system under audit or the control
   measures the paraphraser. Discovered by the lab's own honesty
   mechanism (the pre-committed draft meeting clean data) doing its
   job, and the paper says so in exactly those terms.

## D20. D4 refined, not repealed
DRAFTED 2026-08-27, AMENDED same day after the supplementary run,
**RATIFIED by DeVere, 2026-08-27**. D4's protective purpose survives with the
arm that is actually diagnostic: a wild system is **"unauditable,
reported as such" if the placebo's QUALITY arm fails**, with the
tripwire carrying BOTH clauses:
1. **Capability-matched paraphraser**: the placebo is generated by a
   model of the same capability class as the system under audit,
   fixing the causal confound the supplementary run demonstrated
   (paraphrase provenance moves quality in both directions).
2. **The 1.0-point certified-resolution floor**: a quality delta only
   trips the wire if it reaches the separation the D3 judge gate
   certified the judge to discriminate. Effects below certified
   resolution are noise to the instrument, whatever their sign.

Calibration reading from the seeded set: with both clauses armed, the
seven known-good systems produce exactly zero unauditable flags, which
is correct, because all seven demonstrably were auditable (recovery
was perfect). Even the confounded supplementary effects (-0.3, +0.4,
+0.7) sit below the certified 1.0-point floor. A tripwire that fires
on none of the known-good systems and is armed against both confound
and noise is a tripwire the wild phase can trust. The change-arm is
reported per-family and scoped per D19.

## D21. Wild-phase endpoint and adapter plumbing
The wild systems are served by the pinned actor model
(Qwen3-1.7B-4bit @ 3b1b1768) through a local OpenAI-compatible
endpoint (mlx_lm.server), which keeps $0, keeps everything on-machine,
and makes the D20 capability-matched-paraphraser clause trivially
satisfied: the placebo paraphraser is the same model class the wild
system runs on. Each framework gets a bespoke adapter that exposes its
own named units (retrievers, tools, agents, planner steps) as maskable
components through the trace interface, intercepting at framework
boundaries. Every adapter line is plumbing under D5's observational
freeze: it exists to make the system run and be maskable, never to
change what the system does. Framework versions are pinned in
wild/requirements.txt at install time and recorded here.

Plumbing log (D21, recorded as installed):
- The wild venv runs Homebrew python@3.11 (already present on legion):
  tiktoken ships no Python 3.14 wheel and the machine has no Rust
  toolchain to build one. No new system dependency was installed.
- Framework pins at install time (full freeze in `wild-freeze.txt`):
  langchain 1.3.18, langchain-openai, llama-index 0.14.24, crewai
  1.15.17, autogen-agentchat 0.2.40, openai 2.54.0, tiktoken 0.14.0.
- The endpoint is `mlx_lm server --port 8399 --chat-template-args
  '{"enable_thinking": false}'`; requests name the pinned actor repo
  explicitly. Without the template flag, Qwen3's thinking template
  produces degenerate output through the server path (the D15/D16
  lesson at the server layer); with it, temperature-0 completions are
  clean and deterministic. Verified: "What is the capital of France?"
  -> "Paris".

## D22. Wild adapters: bite-proofs and the plumbing judgment calls
The wild frameworks are foreign plumbing, so interception is not
trusted by construction the way the seeded substrate was. **No
adapter's audit counts until its bite-proof is green**: masking a
component the answer demonstrably depends on must visibly change the
canonicalized output (bite), the same check must fail under a sabotage
mode that computes and discards the mask (red proof that the proof can
fail), and the item's trace must be byte-identical across repeated
runs (D11 on foreign plumbing). The wild runner refuses to audit a
system without its green bite record; the failure this closes is an
adapter that believes it masked while the framework's internals
deliver the original content anyway, which would manufacture false
deads through plumbing, the direction the D19 asymmetry argument
certifies cannot happen through physics.

Plumbing judgment calls, logged:
- Compositions are each framework's canonical tutorial shape (what the
  docs hand a new user): LlamaIndex retriever + response synthesizer
  (low-level composition API), LangChain 1.x create_agent with tools,
  CrewAI researcher->writer sequential tasks, AutoGen AssistantAgent
  planner->executor. Where masking requires an interception point
  between a framework's internal stages (CrewAI between tasks, AutoGen
  between agents), the adapter executes the same sequential flow in
  two framework-native steps with the interception between; same
  information flow, one added seam.
- LangChain's shipped tutorial tools are cloud SaaS (search APIs),
  which the $0 local envelope cannot run; the adapter substitutes two
  local tools (calculator, fact lookup) preserving the tool-calling
  architecture. Substitution, not tuning.
- All framework clients run temperature 0 (the seeded phase's greedy
  rule, inherited per the observational freeze) and caching is
  disabled where a framework caches (AutoGen cache_seed=None), because
  a response cache fakes determinism and can hide broken masking.
- Wild probe sets: 150 items per system at seed 21, committed with the
  RAG corpus and lookup fact table they reference.
- Dead-token cost share is operationalized as word count of component
  outputs over the first 50 baseline traces, a stated proxy.
- The D20 tripwire operationalization: unauditable iff the placebo
  quality CI excludes zero AND |quality mean| >= the certified
  1.0-point floor, with the paraphraser being the endpoint model
  itself (capability-matched by construction).

## D23. Surrogate phase: thresholds, certificates, and the miss, all frozen first
Committed 2026-08-28 BEFORE the baseline re-run finishes and before any
kappa exists. The tracer's knobs freeze now because tuning them while
watching kappa would fit the surrogate to its own exam; a surrogate
that clears 0.7 with pre-frozen thresholds is a monitoring tool, one
that clears it after threshold search is a curve fit wearing one.

**Tracer specification, frozen:**
- Influence per item: component c's flattened output is INFLUENTIAL if
  any downstream output (transitive readers of c, plus the final
  answer) contains it by span or resembles it by embedding.
- Span: word 3-gram containment >= 0.2 (fraction of c's 3-grams
  appearing in the downstream text); outputs of 5 or fewer words use
  exact-substring containment instead (3-grams degenerate on short
  outputs like numbers and names).
- Embedding: BAAI/bge-small-en-v1.5 (already the wild embedder),
  cosine >= 0.60, computed only for pairs that fail span (embedding
  rescues detection, never vetoes it).
- Component influence rate = mean over the 150 probes. Surrogate
  verdict: DEAD iff influence rate < 0.05, mirroring the ablation
  criterion's 5% arm.
- **Primary kappa (the PASS gate): dead-vs-not-dead** against the
  ablation taxonomy, with redundant counting as not-dead on both
  sides. Rationale: a content tracer cannot express counterfactual
  redundancy (both duplicates' content propagates; which one mattered
  is invisible to content flow), so gating it on the redundant class
  tests the tool against a question it cannot ask. That blindness is
  named as a limitation, and the **secondary kappa (reported, not
  gated): flagged-vs-live** (dead union redundant), which is expected
  to be worse for exactly this reason.

**Re-run certificate:** the seeded runner persisted aggregates, not
per-item answers, an omission this line admits rather than hides. The
certificate is therefore: (1) the trace-persisting baseline runs twice
in independent processes and every trace must be byte-identical; (2)
one masked condition per system is recomputed in full and its
answer-change rate must EXACTLY equal the value persisted in
seeded_detail.json, tying the re-run to the measurements the ablation
verdicts describe. Any drift on either check stops the phase before
the tracer sees a single trace.

**The miss, pre-registered:** the protocol's PASS bundles seeded
recovery (achieved), the wild census (delivered), and surrogate kappa
>= 0.7. If kappa lands below 0.7, the verdict is a SPLIT: the ablation
auditor is certified and its findings stand; the cheap
continuous-monitoring surrogate is not validated, reported as its own
negative sub-finding. Written while kappa is unknown.

**For the report regardless of outcome:** the wild phase stress-tested
the surrogate's core assumption. w4's planner showed total textual
influence with quality below certified resolution, so textual
influence and causal mattering DISSOCIATE in text-family systems: the
tracer would call that planner maximally influential while ablation
calls it live-but-unmeasurable on quality. The seeded set should agree
(plants were invisible both textually and causally); the dissociation
marks the surrogate's wild-phase failure boundary and is the reason
the surrogate is a screening tool, never a verdict-giver.

