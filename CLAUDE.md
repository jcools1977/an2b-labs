# CLAUDE.md - AN2B Labs Research Repository

## What this repo is
Twenty pre-registered experimental protocols (TR-001 to TR-020) for AN2B Labs.
Each TRxxx_*.md file is a frozen protocol: hypothesis, design, pass/fail
thresholds, kill criteria, and negative controls were fixed BEFORE any code
or data. Your job is to implement the protocols faithfully, not to improve
their scientific choices.

## Hard rules (BB4C covenant)
1. NEVER modify pass/fail thresholds, kill criteria, or negative controls in
   any protocol file. If an implementation problem makes a criterion
   impossible as written, STOP and surface it to DeVere. Do not quietly adapt.
2. Every experiment gets its own directory: tr001/, tr002/, etc. Protocol
   file stays at repo root, untouched.
3. Red then green: write the negative-control tests FIRST and watch them fail
   before implementing the mechanism. Every trXXX/ must contain a verify.sh
   that runs all negative controls and exits nonzero on any violation.
4. Determinism: every run logs its seed, model versions, and environment.
   Pin dependencies in trXXX/requirements.txt. No unseeded randomness.
5. Data hygiene: eval sets are held out with hash-overlap checks against
   training data. The leakage check is code, not a promise.
6. A near-miss is a FAIL. Never iterate hyperparameters past the sweep
   budget stated in the protocol. Log every config tried.
7. Results are written to trXXX/results/ as JSON plus figures. The report
   draft goes in trXXX/report/. Negative results get the same care as
   positive ones.

## Execution order
Wave 1: TR-001 (gates Track B latent work), TR-020, TR-011.
TR-007 is blocked until TR-001 passes. TR-018 is blocked until TR-004 passes.
Do not start a gated experiment early, even as scaffolding.

## Environment
- Hardware: Apple Silicon Macs. Use MLX for anything needing hidden-state
  access; llama.cpp acceptable for pure inference. Nothing may require a
  rented GPU cluster; if it seems to, the implementation is wrong, stop
  and reconsider.
- Prefer small models (1B-9B class) named in each protocol.
- Long sweeps should be resumable (checkpoint per configuration) so
  overnight runs survive interruption.

## Working style
- Plan before code on each experiment: restate the protocol as a task list,
  confirm the negative controls are testable, then build.
- Small commits, one logical step each.
- When a protocol is ambiguous, choose the interpretation that makes the
  hypothesis HARDER to pass, and note the choice in trXXX/DECISIONS.md.
- Ask before: downloading datasets over 2 GB, running anything estimated
  over 8 hours, or installing system-level dependencies.

## Definition of done (per experiment)
[ ] verify.sh passes (all negative controls hold)
[ ] Both seeds run; results replicate per protocol
[ ] results/ contains machine-readable outputs and figures
[ ] report/ contains a draft with the pass/fail verdict stated plainly
[ ] DECISIONS.md lists every judgment call made during implementation

## Utilization and harvest
CREDO.md binds every session alongside this file: solutions first, value as
byproduct. Product pressure never enters an experiment in flight; every TR
closes with a utilization verdict (product-now / feeds-product-X /
credibility-asset) drafted for PI ratification; harvest reviews happen at
wave boundaries and are the PI's call. Never cite commercial value in
DECISIONS, protocol readings, or threshold interpretations.

## Estate hygiene (standing closeout rule)
Every TR closeout records a disk line: what the experiment leaves on
each machine (model snapshots, entropy/latent caches, corpus stores,
venvs, adapters, checkpoints), sized with du, and what may be swept.
Wave boundaries include an estate audit; deletions of experiment
artifacts happen only on the PI's word, recorded in the closing TR's
decision log. Transient tarballs and scratch venvs are swept without
ceremony.

