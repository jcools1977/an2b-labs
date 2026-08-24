# TR-020: Zero-Callers for Cognition
**Track E: Provenance and Verification** | Status: Protocol draft v0.1 | **Ship first: immediate utility**

## Question
In multi-agent and multi-tool systems, which components run but never causally matter, and can an automated ablation audit find these dead modules cheaply and reliably?

## Hypothesis
**H1:** Systematic component ablation (mask one agent/tool/retrieval source at a time, measure output delta across a probe set) identifies dead modules with high agreement against ground truth in seeded systems, real popular agent configurations contain a nontrivial dead fraction (point estimate reported), and a cheap surrogate (attention-free textual influence tracing) predicts full-ablation results well enough for continuous monitoring.
**H0:** Causal influence is too entangled for one-at-a-time ablation to be meaningful (interaction effects dominate), or every component in reasonable systems genuinely matters.

## Background
The zero-callers lesson: code that exists but is never invoked is indistinguishable from working code until you check invocation. Agent systems have a worse version: components that *are* invoked, produce output, burn tokens, and never causally affect any final answer. Nobody audits for this. The deliverable is a harness any builder can point at their agent stack, and the headline number (the measured dead fraction in common configurations) is the kind of finding that travels.

## Design
- **Ground-truth phase:** construct 6 seeded systems (3-6 components each) with known-dead modules planted (an agent whose outputs are appended but never read downstream; a retrieval source of only irrelevant documents; a redundant duplicate tool); verify the auditor recovers the plant list
- **Ablation protocol:** for each component, mask its outputs (replace with neutral placeholder, preserving structure) over a 150-item probe set matched to the system's task; deltas measured as answer-change rate and judged-quality change
- **Dead criterion (frozen):** answer-change rate < 5% AND quality delta CI includes zero over the probe set
- **Interaction check:** pairwise ablations on a sample to bound how much one-at-a-time misses (masking A and B together vs separately)
- **Wild phase:** audit 4 real open-source agent configurations (popular repo defaults) and report their dead fractions
- **Surrogate:** textual influence tracing (does any downstream context ever contain or reference the component's output, by span matching and embedding similarity); measure agreement with full ablation

## Metrics
- Recovery rate on seeded plants (precision/recall)
- Dead fraction per wild system with CIs; token cost attributable to dead components
- Surrogate-vs-ablation agreement (kappa); interaction-effect bound from pairwise sample

## Pass/Fail (frozen before data)
- **PASS:** seeded recovery precision and recall both >= 0.9; wild-phase dead fractions reported with CIs (any value is a finding); surrogate kappa >= 0.7; pairwise interaction bound reported.
- **FAIL:** seeded recovery below 0.9 (the auditor cannot be trusted on the wild systems, so no wild claims are made).
- **KILL:** interaction effects dominate on seeded systems (one-at-a-time masking flags live components as dead beyond tolerance); publish the entanglement result instead.

## Negative Controls
1. **All-live seeded system:** a system with no planted dead modules must yield zero flags (false-positive floor).
2. **Placebo mask:** replacing a component's output with a *paraphrase* of itself must produce near-zero delta (the masking operation itself must be inert).
3. **Probe-set split:** dead verdicts must replicate across two disjoint probe halves.

## Cost and Time
$0. Est. 3 sessions. The least glamorous experiment and possibly the most cited.

## Deliverables
- `tr020/` repo: the audit harness as an installable tool; seeded-system benchmark released; wild-phase findings table; 6-8 page report.

## Dependencies
None. Recommended first ship alongside TR-001.
