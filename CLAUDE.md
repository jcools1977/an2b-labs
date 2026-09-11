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

## Estate hygiene and bench clearance (standing closeout rule)
Every TR closeout records a disk line: what the experiment leaves on
each machine, sized with du. When the PI ratifies the report, the
session writes trXXX/report/RATIFIED, sets the status line to v1.0,
and clears the bench with estate/bench_clear.py on every machine the
experiment touched: rebuildable bulk (corpus stores, raw data,
caches, checkpoints, venvs, adapters, logs) and model snapshots no
open experiment references are removed, the disk line is appended to
DECISIONS.md, and the entry is committed. Evidence is never touched;
paths in trXXX/KEEP and estate/KEEP are never touched; a snapshot
nothing references is reported, not swept. The tool refuses without
the marker, with uncommitted files, or with HEAD off origin;
estate/verify.sh proves the refusals. Full text: estate/BENCH_CLEAR.md
(drafted 2026-09-11 on the PI's word, for the PI's ratification).
Transient tarballs and scratch venvs are swept without ceremony.


## The macro-check (standing kickoff clause)
FRONTIER.md is the lab's radar: one dated entry per scan, sensing
only. No experiment's Phase 0 closes without a dated FRONTIER
consultation logged in its DECISIONS, and FRONTIER.md receives a
fresh entry before each kickoff and each harvest review. Scans
inform scoping at gates that have not closed; they never touch a
frozen threshold mid-experiment.
