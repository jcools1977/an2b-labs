# TR-010: Asymmetric Hemispheres
**Track B: Echo and Workspace Dynamics** | Status: Protocol draft v0.1

## Question
Does a coupled pair of *differently specialized* models (one precision-tuned, one association-tuned) outperform a homogeneous pair of equal total parameter count?

## Hypothesis
**H1:** Heterogeneous pairs beat homogeneous pairs of matched total size on tasks requiring both rigor and lateral generation (creative constraint satisfaction, insight puzzles, essay-with-proof tasks), with the advantage localized to mixed-demand tasks and absent on pure-precision or pure-association tasks.
**H0:** Total capacity determines performance; specialization mix is irrelevant once compute is matched.

## Background
The split-brain literature suggests functional asymmetry is not an accident but a design: two differently biased processors coupled densely. The operational question for AI councils is whether diversity of *bias* (not just diversity of random seed) buys performance. The localization clause in H1 matters: if heterogeneity helps everywhere, it is probably just ensemble variance reduction wearing a costume.

## Design
- **Hemispheres:** one base 7B model, two LoRA fine-tunes: L-precise (code, math, structured extraction data, low temperature) and L-associative (poetry, analogy, brainstorm data, higher temperature)
- **Pairs compared at matched total compute:**
  - HET: L-precise + L-associative
  - HOM-P: two L-precise (different seeds)
  - HOM-A: two L-associative (different seeds)
  - MONO: single model with double inference budget (self-consistency)
- **Coupling:** fixed 4-round text exchange (identical protocol for all pairs)
- **Tasks:** three families x 150 items: precision-only, association-only, mixed-demand

## Metrics
- Accuracy/judged-quality per pair per task family (blind LLM-judge with human spot-audit of 10%)
- Interaction effect: (HET advantage on mixed) minus (HET advantage on pure tasks)

## Pass/Fail (frozen before data)
- **PASS:** HET > best HOM by >= 5 points on mixed-demand tasks with CI excluding zero, AND HET advantage on pure tasks < 2 points (localization confirmed).
- **FAIL:** no mixed-task advantage, or advantage uniform across families (variance reduction verdict).
- **KILL:** judge and human spot-audit disagree beyond kappa 0.6 (measurement invalid; fix judging before claiming anything).

## Negative Controls
1. **Seed-only diversity:** HOM pairs with different seeds establish how much "diversity" is free; HET must beat this, not just MONO.
2. **Swapped roles:** force L-associative to answer precision items solo (and vice versa) to verify the LoRAs actually specialized; if solo profiles are flat, the hemispheres were never different.
3. **Judge blinding:** judge never sees which condition produced an answer; condition labels stripped and order randomized.

## Cost and Time
LoRA training on the fleet, $0 incremental. Est. 4 sessions including fine-tuning.

## Deliverables
- `tr010/` repo including both LoRAs (published); interaction plot as headline figure; 6-8 page report.

## Dependencies
None hard. Pairs naturally with TR-007 if latent coupling passes.
