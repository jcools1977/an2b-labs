# TR-007: Committee Memos vs Corpus Callosum
**Track B: Echo and Workspace Dynamics** | Status: Blocked pending TR-001 PASS

## Question
When a council of models collaborates on a task, does coupling them through learned latent adapters outperform coupling them through exchanged text, at strictly matched compute?

## Hypothesis
**H1:** Latent-coupled councils outperform text-coupled councils of identical membership and compute budget on multi-step tasks, and the advantage grows with the number of exchange rounds (text loses information per hop; latents lose less).
**H0:** Text coupling equals or beats latent coupling; natural language is already a near-optimal inter-model bus at this scale.

## Background
This is the echo hypothesis made operational. The brain's subsystems share dense state, not memos. TR-001 tests one directed handoff; TR-007 tests the full conversational loop, where per-hop loss compounds. If H1 holds and grows with rounds, the corpus-callosum architecture is not a curiosity but a scaling law for councils.

## Design
- **Council:** the TR-006 trio (proposer, critic, synthesizer), fixed membership
- **Conditions:**
  - C1: text exchange, K tokens per message
  - C2: latent exchange, M soft vectors per message via TR-001 adapters trained for each directed pair (6 adapters)
  - C3: hybrid (text plus a small latent side-channel), exploratory
- **Compute matching:** M <= K; total rounds fixed at R in {1, 2, 4, 8}
- **Tasks:** the TR-006 task suite plus a long-context synthesis task where compounding loss should bite hardest

## Metrics
- Accuracy per condition per R; slope of (C2 - C1) vs R
- Information proxy: probe classifier accuracy on intermediate representations (what survives each hop)

## Pass/Fail (frozen before data)
- **PASS:** C2 > C1 by >= 5 points at R = 4 with CI excluding zero, and positive (C2 - C1) slope in R.
- **FAIL:** no significant gap at any R, or gap shrinks with R.
- **KILL:** C2 wins only when M > K, or adapters fail to transfer from TR-001's task to this suite without full retraining (fragility verdict).

## Negative Controls
1. **Random adapters:** C2 with untrained adapters must collapse below C1.
2. **Crossed adapters:** route pair (A to B) traffic through the (A to C) adapter; must degrade sharply, proving pair-specific alignment is real.
3. **Single-agent latent loop:** one model talking to itself through an adapter must not match council performance (guards against the adapter itself doing the reasoning).

## Cost and Time
$0. Est. 3-4 sessions after TR-001 machinery exists.

## Deliverables
- `tr007/` repo; the (C2 - C1) vs R curve is the headline figure; 6-8 page report.

## Dependencies
**Hard-gated on TR-001 PASS.** Uses TR-006 harness.
