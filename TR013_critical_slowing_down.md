# TR-013: Critical Slowing Down in Dialogue
**Track C: Physics of Language Systems** | Status: Protocol draft v0.1

## Question
Before a long model conversation collapses into repetition or mode-locking, do early-warning signals from dynamical systems theory (rising variance, rising lag-1 autocorrelation, slowed recovery from perturbation) appear in the model's output statistics?

## Hypothesis
**H1:** In conversations that later collapse, output-embedding variance and lag-1 autocorrelation rise significantly in the W turns preceding collapse, compared to matched non-collapsing conversations, yielding a predictor with AUC >= 0.75 at a 5-turn horizon.
**H0:** Collapse arrives without statistical warning; degradation is a step function invisible to these indicators.

## Background
Physical and ecological systems approaching a critical transition show critical slowing down: perturbations decay slower, variance and autocorrelation climb. Conversational collapse (loops, obsessive phrasing, mode-locking) looks phenomenologically like a transition into an absorbing state. If the classic early-warning indicators transfer, the deliverable is immediately useful: a dashboard light that says "restart this agent soon" before quality craters, valuable for any long-running agentic session.

## Design
- **Collapse corpus:** 300 long self-dialogues and task loops from small local models under collapse-prone settings (low temperature, repetitive tasks, long horizons), auto-labeled for collapse onset (n-gram loop detection plus embedding self-similarity threshold, human-audited on 10%)
- **Matched controls:** 300 same-length non-collapsing runs, same models and tasks
- **Signals per turn:** embedding of each turn; rolling variance and lag-1 autocorrelation of the embedding series; distinct-n token diversity
- **Perturbation probe (subset, 50 runs):** inject a fixed off-topic sentence at controlled points; measure recovery time (turns to return to pre-perturbation trajectory); test whether recovery time lengthens approaching collapse
- **Predictor:** logistic model on indicator slopes over a trailing window, evaluated at 5-turn warning horizon

## Metrics
- AUC and precision/recall at 5-turn horizon; lead-time distribution
- Recovery-time trend vs turns-to-collapse (perturbation subset)

## Pass/Fail (frozen before data)
- **PASS:** AUC >= 0.75 at 5-turn horizon on held-out runs, and perturbation recovery time shows positive trend approaching collapse (rho >= 0.4).
- **FAIL:** AUC < 0.75, or recovery times flat.
- **KILL:** indicators fire equally often in matched non-collapsing controls (false-alarm parity means no signal, just drift).

## Negative Controls
1. **Time-reversed series:** indicators computed on reversed sequences must lose predictive power (directionality check).
2. **Length-matched null:** predictor must not achieve its AUC from turn-count alone (turn index withheld and residualized).
3. **Label-audit floor:** human audit of auto-labels must exceed 90% agreement before any headline number is computed.

## Cost and Time
$0; corpus generation runs unattended overnight. Est. 3 sessions.

## Deliverables
- `tr013/` repo; early-warning monitor module usable in production agent loops; indicator-trace figures; 6-8 page report.

## Dependencies
None.
