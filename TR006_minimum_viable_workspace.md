# TR-006: Minimum Viable Workspace
**Track B: Echo and Workspace Dynamics** | Status: Protocol draft v0.1

## Question
In a small multi-model system with a bounded shared broadcast buffer, how do buffer capacity and broadcast frequency affect task performance, and is there a phase transition or merely a smooth curve?

## Hypothesis
**H1:** Task performance as a function of workspace capacity shows a non-linear regime change: below a critical capacity the council performs at single-model level; above it, performance jumps rather than climbs smoothly.
**H0:** Performance is monotonic and smooth in capacity; the workspace is just a bigger scratchpad, with no emergent regime.

## Background
Global Workspace Theory's core structural claim is a *limited-capacity* broadcast bottleneck: consciousness-like integration comes from competition for scarce broadcast slots, not from unlimited sharing. If the bottleneck is doing real computational work, artificial workspaces should show capacity-dependent regime changes. If capacity just monotonically helps, the GWT-flavored story is decoration on ordinary shared memory.

## Design
- **Agents:** three 7B-class local models with distinct roles (proposer, critic, synthesizer)
- **Workspace:** shared buffer of S slots; each round, agents submit candidate items with self-assessed salience; top-S survive and are broadcast to all
- **Sweep:** S in {1, 2, 4, 8, 16, 32}; broadcast every {1, 2, 4} rounds
- **Tasks:** multi-step reasoning sets where no single agent solves reliably alone (multi-hop QA, constraint puzzles), 200 items per configuration
- **Baselines:** single best agent; three agents with *unlimited* shared log (no competition)

## Metrics
- Accuracy vs S curves per broadcast frequency
- Second-difference test for regime change vs smooth fit (compare piecewise vs monotone spline via AIC)
- Slot-competition statistics: how often the eventual answer's ancestor items barely survived the cut

## Pass/Fail (frozen before data)
- **PASS:** piecewise/regime model beats smooth monotone fit by AIC >= 10 on two task families, with the unlimited-log baseline underperforming the best bounded configuration (bottleneck helps, not just hurts less).
- **FAIL:** smooth fit wins, or unlimited log is best everywhere.
- **KILL:** regime location not stable across the two task families.

## Negative Controls
1. **Random salience:** replace self-assessed salience with random scores; any regime structure must weaken or vanish.
2. **Frozen buffer:** broadcast the round-1 buffer forever; performance must fall to near single-agent, proving live broadcast (not initial sharing) carries the effect.
3. **Role shuffle:** randomize role prompts; if performance is unchanged, roles are dead weight and claims about specialization are withdrawn.

## Cost and Time
$0, but inference-heavy: est. 3-4 sessions with overnight sweeps.

## Deliverables
- `tr006/` workspace harness (reused by TR-008, TR-009, TR-010); capacity curves; 6-8 page report.

## Dependencies
None hard; harness becomes Track B infrastructure.
