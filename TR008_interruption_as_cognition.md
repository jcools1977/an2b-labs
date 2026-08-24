# TR-008: Interruption as Cognition
**Track B: Echo and Workspace Dynamics** | Status: Protocol draft v0.1

## Question
Does event-driven broadcast (agents are pushed new state and can interrupt) beat passive polling (agents check shared state on their turn) for error detection and correction speed in multi-agent systems?

## Hypothesis
**H1:** Event-driven councils detect and correct injected errors in fewer downstream tokens and fewer wall-clock rounds than polling councils of identical membership, and the advantage widens as error injection gets rarer.
**H0:** Turn-based polling matches event-driven correction; interruption machinery is engineering overhead without cognitive payoff.

## Background
The Global Workspace Agents literature argues that passive blackboard architectures bottleneck autonomy: nothing can spontaneously initiate or interrupt. That is an architectural claim with a cheap test. Error-correction latency is the right probe because interruption should matter most exactly when something is going wrong off-turn.

## Design
- **Agents:** three local models: worker (executes a multi-step task), monitor (watches for contradictions), coordinator
- **Conditions:**
  - C1: polling; agents act in fixed rotation, reading the shared log on their turn
  - C2: event-driven; every write is pushed to all agents, and the monitor may preempt the rotation when it flags an issue
- **Error injection:** corrupted facts inserted into working state at controlled rates (1 per 10, 50, 200 steps) across coding-style and reasoning-style tasks
- **Matched budget:** total inference calls per episode capped equally in both conditions

## Metrics
- Detection latency (steps between injection and flag); correction latency; end-task accuracy
- False-interrupt rate in C2 (the cost of the machinery)

## Pass/Fail (frozen before data)
- **PASS:** C2 detection latency <= half of C1 at the rare-error setting with CI excluding parity, end-task accuracy >= C1, and false-interrupt rate under 20%.
- **FAIL:** latency parity, or C2 accuracy pays for its speed, or false interrupts exceed 20%.
- **KILL:** result reverses between the two task styles.

## Negative Controls
1. **Blind monitor:** monitor receives pushes but with the injected span masked; C2 advantage must vanish, proving the channel (not extra turns) carries the effect.
2. **Random interrupts:** replace monitor logic with random preemption at matched rate; must not reproduce C2 gains.
3. **No-injection episodes:** both conditions must perform equally when nothing is wrong (interruption must be free when unneeded).

## Cost and Time
$0. Est. 2-3 sessions on the TR-006 harness.

## Deliverables
- `tr008/` repo with the event bus module (reusable in any production agent system); latency distributions; 5-7 page report.

## Dependencies
TR-006 harness. Independent of Track A.
