# AN2B Labs Research Program
## Twenty Falsifiable Experiments in Machine Cognition, Geometry, and Verification

**Version:** 1.0
**Principal Investigator:** J. DeVere Cooley
**Imprint:** AN2B Labs, a research imprint of AN2B LLC
**Method discipline:** BB4C (Breath Before Code). Every experiment pre-registers its hypothesis, pass/fail thresholds, and negative controls before data collection. A near-miss is a FAIL. Failed hypotheses are published, not buried.

---

## 1. Mission

AN2B Labs exists to run small, honest, falsifiable experiments at the intersection of AI architecture, geometry, physics, verification, and art, on commodity hardware, and to publish every result, positive or negative, as public technical reports.

Three commitments:

1. **Falsifiability first.** Every experiment has a way to die cleanly. Kill criteria are frozen before data.
2. **Negative controls always.** Every claimed mechanism must be shown to break when ablated (the zero-callers covenant).
3. **Public disclosure.** Every finished report ships publicly (Dev.to / arXiv), doubling as prior-art disclosure for downstream IP.

## 2. Core thesis under test

The program orbits one central bet: **generality emerges from integration, not from any single component.** If cognition-like behavior is an echo between coupled subsystems (global workspace theory), then the connective tissue between models (shared latent spaces, broadcast dynamics, provenance-verified synthesis) matters more than the intelligence of any one model. The experiments attack this thesis from five directions and are designed so that if the thesis is wrong, the program will say so.

## 3. Research tracks

| Track | Theme | Reports |
|---|---|---|
| A | Latent Geometry and Model Coupling | TR-001 to TR-005 |
| B | Echo and Workspace Dynamics | TR-006 to TR-010 |
| C | Physics of Language Systems | TR-011 to TR-014 |
| D | Art, Voice, and Perception | TR-015 to TR-018 |
| E | Provenance and Verification | TR-019 to TR-020 |

## 4. The twenty experiments

### Track A: Latent Geometry and Model Coupling

**TR-001. Latent Corpus Callosum.** Learn a small adapter mapping one model's hidden states into another model's embedding space; test whether latent handoff beats text handoff on QA at matched compute. *The gating experiment for the entire coupling thesis.*

**TR-002. Platonic Convergence Audit.** Measure representational similarity (CKA, Procrustes) across 5-6 open models of increasing scale; test whether geometric convergence predicts coupling cost.

**TR-003. Anchor-Point Translation.** Use relative representations (anchor-set embeddings) to test whether memories written in one model's space can be consumed by another with zero retraining. Direct input to Eidetic cross-model portability.

**TR-004. Curvature of Meaning.** Estimate intrinsic dimension and local curvature of embedding space around concrete, abstract, and figurative language. Hypothesis: metaphor lives in higher-curvature regions.

**TR-005. FSA Postmortem, Inverted.** The FSA experiment showed imposed geometry destroys signal. Test the converse: a task-learned contrastive projection, measuring whether locality and discriminability can coexist when geometry is learned rather than chosen.

### Track B: Echo and Workspace Dynamics

**TR-006. Minimum Viable Workspace.** Three small local models sharing a bounded broadcast buffer with slot competition. Vary buffer size and broadcast frequency; look for phase transitions in task performance.

**TR-007. Committee Memos vs Corpus Callosum.** Same council, two coupling media: text conclusions vs pooled hidden states through a learned adapter, at matched compute. The echo hypothesis, tested directly. *Unlocked by TR-001 PASS.*

**TR-008. Interruption as Cognition.** Polling vs event-driven broadcast in a multi-agent loop; measure latency to correct an injected error. Tests the active-broadcast claim from Global Workspace Agents literature.

**TR-009. Resonance Detection.** Run councils on ambiguous prompts; measure agreement dynamics over iterations (converge, oscillate, bifurcate). Test whether the *dynamic* predicts correctness better than the answer itself.

**TR-010. Asymmetric Hemispheres.** Couple a precision-tuned model with an association-tuned model; test whether heterogeneous pairs beat homogeneous pairs of equal total parameter count.

### Track C: Physics of Language Systems

**TR-011. Semantic Thermodynamics.** Define token-distribution entropy over a document processed sequentially; test whether published prose shows characteristic entropy signatures vs drafts and slush.

**TR-012. Ising Model of Consensus.** Model council agents as coupled spins; predict deadlock vs convergence from mean-field theory, then verify empirically.

**TR-013. Critical Slowing Down in Dialogue.** Test whether variance in model outputs rises before conversational collapse (repetition, mode-locking), analogous to critical slowing before phase transitions. Deliverable: an early-warning signal.

**TR-014. Renormalization of Summaries.** Iteratively summarize at fixed compression ratio; identify which semantic features are fixed points of the coarse-graining flow.

### Track D: Art, Voice, and Perception

**TR-015. Burrows Delta in Latent Space.** Test whether authorial voice occupies a stable low-dimensional manifold in embedding space, and measure voice drift geometrically across a multi-book series.

**TR-016. Payoff Density as Signal Processing.** Fourier-analyze narrative payoff density across published novels vs unpublished drafts; test for a characteristic frequency band readers tolerate.

**TR-017. Synesthetic Embeddings.** Deterministically sonify text embeddings; test whether humans can distinguish coherent from incoherent documents by ear alone.

**TR-018. The Geometry of Metaphor.** Upgrade analogy arithmetic from flat vector offsets to parallel transport on the curved manifold measured in TR-004.

### Track E: Provenance and Verification

**TR-019. Cryptographic Attention.** Merkle commitment over which models and retrieved spans contributed to a composite answer, yielding a verifiable provenance tree for multi-model synthesis. *Product candidate, not just a paper.*

**TR-020. Zero-Callers for Cognition.** Automated dead-module detection in agentic systems: ablate each component and measure causal delta on final answers, flagging components that run but never matter.

## 5. Dependency graph and recommended order

```
TR-001 (gate) ──> TR-007 ──> TR-006, TR-008, TR-009, TR-010
TR-002, TR-003 (parallel, independent)
TR-004 ──> TR-018
TR-020 (independent, ship first for immediate utility)
TR-011, TR-015, TR-016 (reuse existing loomlint / stylometry tooling)
TR-019 (extends AEGIS primitives)
```

**Wave 1 (start now):** TR-001, TR-020, TR-011
**Wave 2:** TR-002, TR-004, TR-015
**Wave 3:** TR-007 (if 001 passes), TR-006, TR-013
**Wave 4:** remainder, ordered by what Waves 1-3 taught.

## 6. Lab operations

- **Hardware:** existing Mac fleet. No experiment may require rented GPU clusters; if it does, it is misdesigned for this lab.
- **Repos:** one repo per TR (`tr001`, `tr002`, ...), each with `verify.sh` asserting negative controls hold, red-then-green fixtures, pinned environments, logged seeds.
- **Reports:** 4-8 pages each, numbered technical reports, published regardless of outcome. FAIL reports include a postmortem on why.
- **Cadence target:** one report per focused work block; no report left in draft more than two weeks after data collection ends.
- **IP posture:** publication is the disclosure event; anything with product legs (TR-019 especially) gets evaluated for provisional filing before the writeup ships.

## 7. Definition of "official"

AN2B Labs is official when TR-001 ships with a result. Everything before that is letterhead. Everything after is a research agency.

*Trust. Walk. Build.*
