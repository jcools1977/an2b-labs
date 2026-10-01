# FRONTIER.md — the lab's radar
## Standing intelligence ledger. One dated entry per scan. Consumed at every
## kickoff gate (macro-check) and every harvest review. Sensing only —
## nothing here touches a frozen threshold mid-experiment.
## Charter amendments, 2026-09-08 (independent review A2/A9): entries
## report LANE STATUS ONLY — crowded, open, moved — and never product
## relevance, which belongs in harvest packets. Either instance may
## scan; every entry names its scanner; countersignature by the other
## instance includes spot-checking the cited identifiers, because a
## hallucinated citation in the radar would poison every gate
## downstream.

---

## FRONTIER-001 — 2026-09-03 — scanned by the reviewer instance

### Front 1: Representational geometry — DIRECT HIT on the slate
- vec2vec (Jha, Zhang, Shmatikov, Morris; NeurIPS 2025, revised Jan 2026,
  arXiv:2505.12540) constructively demonstrates the STRONG Platonic
  Representation Hypothesis for text embeddings: unsupervised translation
  between embedding spaces via a universal latent, no paired data, no
  anchors, high cosine fidelity across architectures and training sets.
- mini-vec2vec (arXiv:2510.02348) scales the alignment with plain linear
  transformations — the capability is now cheap.
- The paradigm has jumped substrate: May 2026 work (arXiv:2605.20496)
  recovers the same universal geometry across human brains via fMRI.
- IMPACT, TR-002 (Platonic Convergence Audit): the existence question is
  answered at macro scale. Running it as written risks a micro-of-a-macro.
  Kickoff-gate options for PI adjudication: (a) rescope to the desk-scale
  verification niche — independent replication of vec2vec-class claims on
  the lab's pinned 4-bit small models, where nobody has tested whether
  convergence survives quantization and small n; (b) rescope to the
  failure-boundary audit — WHERE does the universal geometry break at desk
  scale; (c) retire TR-002 and advance TR-006. No option touches a frozen
  threshold: TR-002's Phase 0 has not closed.
- IMPACT, TR-003 (Anchor-Point Translation): vec2vec translates WITHOUT
  anchors. The honest rescope is sharper and more product-relevant to
  EngramPort: does vec2vec-class translation preserve MEMORY fidelity
  (recall precision, provenance survival) at desk scale — translation
  existing is no longer the question; what survives translation is.
- IMPACT, TR-001b: partially insulated — vec2vec is embedding-level, not
  per-token hidden-state transfer. The gap TR-001b targets remains open.

### Front 2: Agent auditing — deadwood's lane is OPEN; TR-019's is CROWDED
- No generic, installable causal dead-weight auditor exists. Every
  multi-agent paper hand-rolls its own ablation study (SANA's intent-based
  ablation, arXiv:2606.13904, is the nearest methodological neighbor —
  bespoke, not shipped). deadwood-audit remains the only pip-installable
  three-verdict causal auditor we can find. The wave to ride: position
  deadwood alongside the security-audit wave (USC agent-audit found 617
  security findings across six OSS agent projects; Aegis ships pre-execution
  firewalls) — security audits the doors, deadwood audits the workforce.
- TR-019 (Cryptographic Attention) warning: the provenance/audit-trail
  space is filling fast — Microsoft's Agent Governance Toolkit specs
  Merkle-chained audit logs and decision-BOM reconstruction; tamper-evident
  trails are becoming enterprise table stakes. TR-019's IP review must
  identify what per-inference, attention-level provenance adds over
  action-level audit trails, or fold.

### Front 3: Orchestration — AutoBot's architecture bets are CONFIRMED
- MCP has been donated to the Linux Foundation with OpenAI, Google,
  Microsoft, AWS, and Salesforce implementing; 50+ enterprise partners.
  MCP-native is the standard, not a bet. (Norman being MCP-native at
  mcp.an2b.com was the right instinct early.)
- Graph-based orchestration is the convergence pattern across LangGraph,
  Microsoft Agent Framework (1.0 GA April 2026; AutoGen community forked
  to AG2), and Google ADK. Production pattern emerging: role-based crews
  for research phases feeding deterministic graphs for execution.
- What the majors do NOT ship: the covenant layer — human approval gates
  with named failure classes, confession-as-norm, verified cutoffs,
  decision logs as first-class artifacts. That layer is AutoBot's moat and
  ClawTex's product thesis, independently validated by every serious
  system reinventing pieces of it.

### Compute-grade line (standing)
- Protocol standardization (MCP/A2A) is collapsing integration costs:
  desk-scale leverage rises every time glue code dies. The lab's aim —
  verification, refutation, instruments — remains where frontier mass
  production is NOT pointed.

### Next scan due: before TR-006/TR-002-rescope kickoff, or 2026-09-10,
### whichever comes first.

---

## FRONTIER-002 — 2026-09-08 — scanned by the builder seat, for the
## reviewer's countersignature (first scan run from this channel)

### Front 1: Representational geometry — our boundary stands; TR-003's lane has moved
- No published work found on unsupervised translation under
  quantization / small-n / small models: mini-vec2vec's own results
  (seven encoders, full precision, CPU-fast; arXiv:2510.02348, rev.
  Feb 2026) remain the strongest in-class claim, and TR-002r's
  desk-scale boundary appears to be first into its niche. The lane
  we just published in is open behind us, not crowded.
- TR-003's ORIGINAL question (Moschella-style relative
  representations within 10 F1 of native retrieval) is now partially
  answered in the literature: zero-shot stitching via shared anchors
  is established, and refinement work is active (learned anchors +
  whitened inner products, arXiv:2605.30596; LDIR's low-dimensional
  relative embeddings, arXiv:2505.10354). Meanwhile the INDUSTRY
  frame shifted: "vector drift" is a named production pain
  (embedding model releases every 60-90 days; large index
  migrations now routine). IMPACT: TR-003 as written risks a
  micro-of-a-macro, same class as original TR-002; its
  FRONTIER-001-flagged rescope (what SURVIVES translation: recall
  precision, provenance, memory fidelity at desk scale, now with
  TR-002r's measured skylines as priors) is sharper than ever, and
  the kickoff gate should present that option space.

### Front: Workspace dynamics (TR-006) — the field builds on the assumption TR-006 would test
- GWT-flavored architectures are proliferating: "Theater of Mind"
  (arXiv:2604.08206), Global Workspace Agents as event-driven
  systems, brain-inspired graph MAS (arXiv:2603.15371), and
  GWT-marker evaluation frameworks (preprints.org 202601.1683,
  naming capacity limitation as one of six testable markers).
- What the scan did NOT find: a capacity SWEEP with a frozen
  regime-change criterion. The architectures assume the bounded
  broadcast bottleneck helps; the measurement TR-006 pre-registers
  (piecewise-vs-smooth AIC, unlimited-log baseline, regime-location
  stability KILL) appears untested. IMPACT: TR-006's lane is open,
  and unusually well-timed — the field is building on the exact
  assumption the protocol would measure.

### Front 2: Agent auditing — deadwood's lane holds; TR-019's crowding worsens
- AUDITA (arXiv:2608.22160): certified auditing and causal
  attribution of ADVERSE outcomes with tamper-evident inter-agent
  records — academic tooling now adjacent to deadwood's territory
  but aimed at blame-for-harm, not dead-weight census; deadwood
  remains the only pip-installable dead-fraction auditor we can
  find. Causal failure-attribution methods are active
  (arXiv:2509.08682).
- IMPACT, TR-019: the crowding warning inherited at its gate line
  intensifies — tamper-evident inter-agent records are now in
  academic reference implementations as well as enterprise
  toolkits. The IP review's fold-or-differentiate bar rises again.
- Context worth citing in future MAS work: Anthropic's Frontier Red
  Team published systematic multi-instance failure modes (sabotage,
  tacit collusion) in August 2026.

### Compute-grade line (standing)
- Unchanged from 001: verification, refutation, and instruments
  remain where frontier mass production is not pointed, and
  TR-002r's reception lane (a desk-scale boundary the majors did
  not publish) is evidence the aim is right.

### COUNTERSIGNED by the reviewer instance, relayed by the PI
### 2026-09-08 (the reviewer's own text lives in the reviewer's
### channel record). Spot-checks the reviewer performed and named:
### arXiv:2510.02348 fetched and mini-vec2vec verified against the
### source; an independent search that failed to surface any
### desk-scale or quantized translation test, which is the negative
### claim TR-002r's niche and TR-003r's rescope rest on. The builder
### seat's first record of TR-003r's D1 called this entry
### uncountersigned; that was a stale-channel error, corrected the
### same day in tr003r/DECISIONS.md D1.

### Next scan due: before the Wave 3 slate freezes at the harvest
### review's close, or 2026-09-15, whichever comes first.

---

## FRONTIER-003 — 2026-10-01 — scanned by the builder seat before the
## Wave 4 kickoff and the Wave 3 harvest review, for the reviewer's
## countersignature (lane status only, per the 2026-09-08 charter)

### Front: Workspace dynamics (TR-008, TR-009, TR-010) — one lane moved, one crowded, one open
- TR-008 (interruption): interruptible agent communication is now a
  published mechanism ("Learning to Interrupt in Language-based
  Multi-agent Communication," arXiv:2604.06452: a listener may cut a
  token stream to skip or clarify). The claim TR-008 tests (event-
  driven correction latency against polling at MATCHED budget, with
  the blind-monitor and random-interrupt controls) is not that paper's
  measurement; the lane has MOVED from "does interruption exist" to
  "does it buy correction speed when nothing announces the error."
  Runnable as written, framed as verification of the architectural
  claim. Adjacent: ProMAS error forecasting (arXiv:2603.20260).
- TR-009 (resonance): CROWDED on its nearest reading. Confidence-based
  correctness prediction in multi-agent debate is an active front
  ("Early-Token Confidence Predicts Reasoning Quality," arXiv:
  2606.10307; "The Confident Liar," arXiv:2606.10296; "Demystifying
  Multi-Agent Debate: confidence and diversity," arXiv:2601.19921;
  "Social Reasoning in Machines: collective truth-seeking dynamics,"
  arXiv:2605.30391; "Hidden Anchors," arXiv:2606.19494). What the scan
  did NOT find: agreement-TRAJECTORY features (convergence half-life,
  oscillation energy, bifurcation onset) tested against vote margin
  with the single-model self-consistency control that separates
  resonance from sampling variance. That residual niche is narrow and
  near the crowd; kickoff gate with doors (TR009_KICKOFF_GATE.md).
- TR-010 (hemispheres): adjacent, not crowded. Heterogeneous ensembles
  (HDEE, arXiv:2502.19385; mixtures of adapters; weakly heterogeneous
  size pairs) are studied for accuracy; the bias-diversity claim with
  the LOCALIZATION clause (advantage only on mixed-demand tasks) and
  the seed-only-diversity control is not found. Lane open; cost is
  the LoRA pair plus a human spot-audit of the judge.

### Front: Physics of language systems (TR-012, TR-013, TR-014)
- TR-012 (Ising consensus): DIRECT HIT, crowded. 2026 work applies
  statistical physics to LLM councils with the apparatus TR-012
  proposed: effective couplings and fields by logistic regression with
  critical exponents against the 2D Ising reference ("Collective
  Alignment in LLM Multi-Agent Systems," arXiv:2605.10528);
  temperature-driven phase-transition-like biased consensus
  ("Emergence of Biased Consensus," arXiv:2608.02827); Ising energy
  with Glauber dynamics predicting collective behavior ("Physics of
  Agents," arXiv:2608.16578); decoding temperature and consensus in
  naming games (arXiv:2608.02178). Running TR-012 as written is a
  micro-of-a-macro of the TR-002 class. Kickoff gate with doors
  (TR012_KICKOFF_GATE.md).
- TR-013 (critical slowing down): OPEN. No application of the early-
  warning-signal program (variance, lag-1 autocorrelation, slowed
  recovery; Scheffer et al. 2009) to conversational collapse in
  language models was found. One 2026 caveat is relevant equipment:
  early-warning signals can vanish or amplify with observation
  dimensionality (arXiv:2609.01164), which bears on measuring them on
  embedding series; synchronization-transition warnings from partial
  observations (arXiv:2608.28320). Lane open and well posed.
- TR-014 (renormalization of summaries): MOVED, with neighbors, open
  at its specific claim. Recursive self-refinement reaches soft fixed
  points by exponential decay ("Do Language Models Converge to
  Themselves?" arXiv:2607.22653); memory compaction is being framed
  as rate-distortion ("What to Keep, What to Forget," arXiv:
  2607.08032); lossy compression and reconstruction (arXiv:
  2605.29000). Not found: feature-CLASS survival ordering under
  iterated 2:1 summarization, cross-model fixed-point similarity, or
  the fiction/scripture/technical comparison. Lane open; cite the
  neighbors.

### Front: Art, voice, perception (TR-016, TR-017) — open
- TR-016 (payoff density): narrative computation has foreshadow-
  trigger-payoff generation (arXiv:2601.07033) and turning-point
  work; no spectral pacing analysis of published against unpublished
  manuscripts was found. Open. Cost is the tagger audit (human kappa
  gate) and the draft corpus under the TR-011/TR-015 covenant.
- TR-017 (synesthetic embeddings): no sonification of embedding
  trajectories for listener coherence judgments was found. Open. Cost
  is listeners and the program's only cash line; kickoff gate for the
  PI's word on both (TR017_KICKOFF_GATE.md).

### Front: Geometry (TR-005) — crowded and unrunnable as written
- Learned low-dimensional retrieval representations are mainstream
  (Matryoshka Representation Learning, NeurIPS 2022, and its 2026
  descendants MIPIC arXiv:2604.24374, SMEC, TMRL): "a learned
  projection keeps retrieval while cutting dimension" is settled at
  macro scale. Combined with the absent FSA assets
  (TR005_KICKOFF_GATE.md), door (c) of that gate carries the radar's
  weight; the seat makes no recommendation.

### Compute-grade line (standing)
- Unchanged: verification, refutation, and instruments remain where
  frontier mass production is not pointed; two of the three lanes
  the lab is about to enter (TR-013, TR-014) are open precisely
  because they are measurement questions nobody has frozen a
  criterion for.

### Next scan due: before the Wave 4 harvest review, or 2026-10-15,
### whichever comes first.
