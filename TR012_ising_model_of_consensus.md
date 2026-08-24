# TR-012: Ising Model of Consensus
**Track C: Physics of Language Systems** | Status: Protocol draft v0.1

## Question
Can council deadlock vs convergence be predicted quantitatively by mapping agents to coupled spins and applying mean-field theory, before running the expensive iterations?

## Hypothesis
**H1:** An Ising-style model, with per-pair coupling constants J_ij estimated from a cheap calibration set of observed agreement frequencies, predicts convergence vs deadlock on held-out problems with accuracy >= 0.75, and the empirically located transition tracks the mean-field critical prediction within 20%.
**H0:** Agreement dynamics are not usefully captured by pairwise couplings; prediction does not beat a majority-baseline heuristic.

## Background
Statistical mechanics earns its keep when macro behavior follows from micro couplings without simulating every step. If council consensus behaves like an Ising system, three practical things follow: deadlock becomes predictable, "temperature" (sampling temperature, literally) becomes a principled control knob, and council design gets a phase diagram instead of vibes.

## Design
- **Spin mapping:** binary or k-state stance per agent per round on decision problems with discrete answer sets
- **Calibration:** 200 problems to estimate J_ij (from pairwise agreement rates) and per-agent fields h_i (from solo answer biases)
- **Prediction targets:** 200 held-out problems; predict (a) converges within R rounds vs deadlocks, (b) final majority state
- **Temperature sweep:** run identical problem sets at sampling temperatures {0.2, 0.7, 1.0, 1.4}; locate the empirical order-disorder transition in consensus rate; compare to mean-field critical temperature from estimated couplings
- **Council sizes:** 3, 5, 7

## Metrics
- Deadlock-prediction accuracy and Brier score vs baselines (majority heuristic, logistic on solo answers)
- Empirical vs predicted critical temperature; consensus-rate-vs-temperature curves

## Pass/Fail (frozen before data)
- **PASS:** prediction accuracy >= 0.75 beating baselines by >= 0.05, and critical temperature within 20% of mean-field prediction at two council sizes.
- **FAIL:** predictions at baseline, or transition location off by > 20% at all sizes.
- **KILL:** estimated J_ij unstable across two disjoint calibration halves (no stable couplings means no model).

## Negative Controls
1. **Shuffled couplings:** permute J_ij assignments among pairs; prediction must degrade toward baseline.
2. **Independent-spin null:** predictions from fields h_i alone (no couplings) quantify how much the interaction terms actually earn.
3. **Synthetic sanity:** pipeline must recover known J on simulated Ising data before touching real councils (red-then-green fixture).

## Cost and Time
$0. Est. 3 sessions; temperature sweeps run overnight.

## Deliverables
- `tr012/` repo; the council phase diagram (consensus rate vs temperature vs size) as headline figure; 6-8 page report.

## Dependencies
Council transcripts from TR-009 are reusable as calibration data.
