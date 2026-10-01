# TR-013 implementation plan (before any code)

Protocol: TR013_critical_slowing_down.md, frozen 2026-08-24 at
7b7262d, unchanged.

1. **Corpus generation** (`tr013/gen/`): long self-dialogues and task
   loops from small local models under collapse-prone settings (low
   temperature, repetitive tasks, long horizons), unattended on the
   cockpit. Models and settings fixed in D3 before generation; every
   run logged with seed, model snapshot, settings. Target: enough runs
   that 300 collapse and 300 matched non-collapsing runs exist.
2. **Auto-labeler** (`tr013/label/`): collapse onset by n-gram loop
   detection plus embedding self-similarity threshold, per protocol;
   the thresholds fixed in D4 before any run is labeled; a 10 percent
   audit sample packaged for the PI (control 3, >= 90 percent
   agreement gates the headline).
3. **Signals** (`tr013/signals/`): per-turn embedding, rolling variance
   and lag-1 autocorrelation of the embedding series, distinct-n token
   diversity; embedding model and reduction fixed in D5 (FRONTIER-003's
   dimensionality caveat).
4. **Perturbation probe**: 50 runs, a fixed off-topic sentence
   injected at controlled points, recovery time measured; its trend
   against turns-to-collapse (rho >= 0.4 clause).
5. **Predictor**: logistic model on indicator slopes over a trailing
   window at a 5-turn horizon, run-level held-out split; evaluated
   against the matched controls; time-reversed and length-matched
   nulls (controls 1 and 2).
6. **Checkers, red first**: check_corpus (300/300, matched lengths,
   audit sample present), check_pass (AUC >= 0.75 and rho >= 0.4),
   check_kill (indicator firing rate in controls at parity),
   check_controls (reversed series loses power; turn index withheld
   and residualized; audit floor); fixtures before mechanisms;
   verify.sh.
7. **Closeout** per the standing word: report, reveal and score,
   v1.0 with the marker, utilization draft, clearance, ledger row,
   notification; the headline withheld until the PI's audit clears
   control 3.
