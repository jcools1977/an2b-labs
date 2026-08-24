# TR-016: Payoff Density as Signal Processing
**Track D: Art, Voice, and Perception** | Status: Protocol draft v0.1

## Question
Treating narrative payoff events as a signal over story time, do published novels occupy a characteristic spectral band of payoff density that unpublished drafts and slush measurably violate?

## Hypothesis
**H1:** Payoff-density series of published novels concentrate spectral energy in a shared band (regular-but-not-periodic reward pacing), maintain a bounded maximum inter-payoff gap relative to book length, and these two features separate published from unpublished manuscripts with AUC >= 0.7 on author-disjoint splits.
**H0:** Payoff pacing shows no cross-book regularity; pacing craft does not reduce to measurable spectral structure.

## Background
The observed 7,488-word payoff desert in a draft (flagged by a human reader as "too wordy" before any instrument existed) is a single data point suggesting readers track reward pacing. Signal processing gives the natural formalism: payoffs as events, pacing as spectrum, deserts as gap statistics. If a tolerable band exists, editing gains a quantitative pacing instrument, and narrative theory gains a falsifiable claim about reader physiology-adjacent constraints.

## Design
- **Payoff operationalization (the load-bearing step):** an LLM tagger labels payoff events (revelation, reversal, goal completion, question answered, emotional release) per 250-word window, with a written rubric; human audit on 10% must reach kappa >= 0.65 before proceeding
- **Corpus:** 40 published novels (public domain, mixed genre) and 25 unpublished manuscripts/drafts (in-house drafts plus openly licensed amateur fiction), all length-normalized to story-time coordinates
- **Series analysis:** payoff density per normalized window; Lomb-Scargle spectra (uneven safety), max-gap statistics, burstiness index (Fano factor)
- **Classifier:** logistic on {band energy ratio, max normalized gap, burstiness}, author-disjoint cross-validation
- **Case study:** the Epoch I published text vs its draft, with the known desert as a marked exhibit

## Metrics
- Spectral band consistency across published corpus (overlap of top-energy bands)
- AUC of the 3-feature classifier; per-genre breakdown
- Desert census: distribution of max gaps, published vs not

## Pass/Fail (frozen before data)
- **PASS:** published books share a top-energy band (majority overlap), classifier AUC >= 0.7 author-disjoint, and max-gap distributions differ with Cliff's delta >= 0.3.
- **FAIL:** no shared band, or AUC < 0.7, or gaps indistinguishable.
- **KILL:** tagger audit below kappa 0.65 after one rubric revision (measurement layer invalid; publish the tagging difficulty as the finding instead).

## Negative Controls
1. **Chapter-shuffled novels:** shuffling published chapters must degrade spectral regularity (the signal must live in sequence, not genre vocabulary).
2. **Genre residualization:** classifier must survive genre as a covariate (not just detecting that slush skews to certain genres).
3. **Tagger placebo:** run the tagger on procedurally generated neutral text; payoff rate must be near zero (hallucinated payoffs check).

## Cost and Time
$0 beyond modest tagging inference. Est. 3 sessions.

## Deliverables
- `tr016/` repo; the payoff spectrogram tool for any manuscript; the published-band figure; 6-8 page report.

## Dependencies
None. Natural companion to TR-011 and TR-015 in a craft-instrumentation trilogy.
