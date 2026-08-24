# TR-009: Resonance Detection
**Track B: Echo and Workspace Dynamics** | Status: Protocol draft v0.1

## Question
When a council iterates on an ambiguous problem, does the *dynamic* of inter-model agreement (convergent, oscillating, bifurcating) predict answer correctness better than the final answer's confidence does?

## Hypothesis
**H1:** Trajectory features of pairwise agreement over iterations (convergence rate, oscillation amplitude, bifurcation onset) predict correctness with AUC >= 0.75, beating final-answer self-reported confidence and majority-vote margin.
**H0:** Agreement dynamics carry no predictive signal beyond the final vote; the echo's shape is noise.

## Background
If cognition-like behavior is an echo between subsystems, the echo's waveform should carry information: healthy resonance vs pathological ringing. Practically, a dynamics-based correctness predictor is a calibration tool no vote-counting ensemble provides, and it is computed from signals every council already emits for free.

## Design
- **Council:** 3 and 5 member councils of local models, iterating R = 8 rounds per problem with visible mutual critique
- **Problems:** 400 items spanning verifiable-but-ambiguous questions (underspecified math, contested factual framing, adversarial trivia) with ground truth
- **Signals per round:** pairwise embedding cosine of answers; edit distance of numeric/structured answers; stance labels from a cheap classifier
- **Features:** convergence half-life, spectral energy of agreement series (oscillation), variance trajectory, time-to-lock
- **Predictor:** logistic regression and gradient-boosted trees on trajectory features (deliberately simple; the claim is about the signal, not the model)

## Metrics
- AUC of dynamics-based predictor vs (a) final confidence, (b) vote margin, (c) both combined
- Calibration curves; feature importances

## Pass/Fail (frozen before data)
- **PASS:** dynamics AUC >= 0.75 and exceeds vote-margin AUC by >= 0.05 on held-out problems, stable across 3 and 5 member councils.
- **FAIL:** dynamics add < 0.05 AUC over vote margin, or fall below 0.75.
- **KILL:** signal present only for one problem family (then it is a family detector, not a resonance detector, and is reported as such).

## Negative Controls
1. **Round-shuffled trajectories:** permute round order within each problem; predictive power must drop sharply (order is the claim).
2. **Cross-problem transplant:** pair problem i's trajectory with problem j's label; AUC must fall to ~0.5.
3. **Single-model self-consistency:** same features computed over one model's resampled answers; if it matches council AUC, the effect is sampling variance, not inter-model resonance.

## Cost and Time
$0. Est. 3 sessions (heavy inference, overnight-friendly).

## Deliverables
- `tr009/` repo; trajectory zoo figures (convergent vs oscillating vs bifurcating examples); 6-8 page report; a drop-in council confidence estimator if PASS.

## Dependencies
TR-006 harness recommended, not required.
