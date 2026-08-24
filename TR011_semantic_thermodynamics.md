# TR-011: Semantic Thermodynamics
**Track C: Physics of Language Systems** | Status: Protocol draft v0.1

## Question
Processed sequentially through a language model, does polished published prose exhibit characteristic token-entropy signatures that distinguish it from drafts and slush, and are those signatures stable enough to serve as an editing instrument?

## Hypothesis
**H1:** Published prose shows (a) lower mean per-token entropy, (b) higher entropy *variance* structure (controlled spikes at reveals and turns), and (c) characteristic autocorrelation length in the entropy series, versus earlier drafts of the same work and versus rejected slush, with effect sizes stable across two scoring models.
**H0:** Entropy series of published and unpublished prose are statistically indistinguishable once topic and length are controlled.

## Background
A language model's per-token predictive distribution is a free thermometer: every sentence has a measurable temperature. Craft intuitions ("this drags", "this surprises too often") may correspond to measurable statistical signatures. With draft-vs-published pairs of the same book available in-house, the confound that kills most stylometry studies (different authors, different topics) is controlled by construction.

## Design
- **Corpora:**
  - A: published Epoch I text vs its own earlier drafts (paired, same author, same story)
  - B: 20 published novels (public domain plus licensed samples) vs 20 unpublished/slush samples, topic-matched where possible
- **Scoring models:** two open models of different families compute per-token negative log-likelihood and full-distribution entropy over each document with a sliding context window
- **Series features:** mean, variance, spectral density, autocorrelation length, spike rate above threshold, entropy at paragraph boundaries vs interiors
- **Analysis:** paired tests for corpus A; classifier (logistic on features) for corpus B with author-disjoint splits

## Metrics
- Effect sizes per feature (paired, corpus A); classifier AUC (corpus B)
- Cross-model agreement (features must correlate rho >= 0.7 between scoring models)

## Pass/Fail (frozen before data)
- **PASS:** at least two features show |Cliff's delta| >= 0.3 in corpus A with the same sign in corpus B, AUC >= 0.7 with author-disjoint splits, and cross-model agreement holds.
- **FAIL:** features unstable across scoring models, or AUC < 0.7, or corpus A and B disagree in sign.
- **KILL:** signal disappears when controlling for sentence length distribution (then it was a length detector).

## Negative Controls
1. **Shuffled sentences:** within-document sentence shuffles must *change* the sequential features (autocorrelation, spectra); if not, the features are bags of words in disguise.
2. **Topic transplant:** classifier trained on corpus B must not sort documents by topic labels above chance (checked with topic classifier residualization).
3. **Same-text re-scoring:** duplicate documents inserted under different filenames must receive near-identical features (pipeline determinism check).

## Cost and Time
$0. Est. 2-3 sessions. Integrates directly with the existing prose-linting toolchain.

## Deliverables
- `tr011/` repo; an "entropy trace" visualization tool for any manuscript; 6-8 page report; if PASS, a new lint dimension for the editing pipeline.

## Dependencies
None.
