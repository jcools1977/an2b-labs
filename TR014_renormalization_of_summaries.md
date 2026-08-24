# TR-014: Renormalization of Summaries
**Track C: Physics of Language Systems** | Status: Protocol draft v0.1

## Question
Under repeated 2:1 summarization, which semantic features of a text survive iteration (fixed points of the coarse-graining flow), which decay, and are the survival laws consistent across texts and models?

## Hypothesis
**H1:** Iterated summarization exhibits reproducible flow structure: (a) feature survival is ordered (causal skeleton and protagonist-goal structure outlive descriptive texture, affect, and style), (b) survival curves per feature class follow consistent decay shapes across documents, and (c) different summarizer models flow the same document toward measurably similar fixed points.
**H0:** Survival is idiosyncratic per document and per model; there is no lawful flow, only lossy paraphrase.

## Background
Renormalization group thinking asks what remains when you coarse-grain repeatedly; the invariants define the system's universality class. Summarization is literal semantic coarse-graining. If the flow is lawful, it yields both theory (a principled answer to "what is the meaning that survives compression") and practice (knowing what chain-of-summaries memory architectures structurally forget, which is a direct design input for hierarchical memory systems). The art angle: run the flow on scripture, on published fiction, and on technical prose, and compare their invariants.

## Design
- **Documents:** 60 texts x 3 classes (narrative fiction including own-manuscript excerpts, scripture/wisdom literature, technical prose), 2,000-4,000 words each
- **Flow:** summarize at 2:1 ratio, 6-8 iterations, until ~30 words; two summarizer models independently
- **Feature tracking per iteration:** presence/absence of tagged atomic claims (pre-extracted, ~40 per document, classed as causal-event, character-goal, descriptive, affective, stylistic); embedding drift per step; named-entity survival
- **Fixed-point comparison:** cross-model similarity of final summaries per document vs cross-document baseline

## Metrics
- Survival curves per feature class with CIs; ordering test (causal > descriptive > stylistic survival)
- Cross-model fixed-point similarity ratio (same-doc across models vs different-doc)
- Per-class decay-shape consistency (curve family fit)

## Pass/Fail (frozen before data)
- **PASS:** feature-class survival ordering holds with pairwise CIs excluding overlap on 2 of 3 document classes, and same-document cross-model fixed-point similarity exceeds cross-document baseline by >= 0.15 cosine.
- **FAIL:** ordering inconsistent, or fixed points model-specific.
- **KILL:** atomic-claim tagging fails audit (below 85% human agreement on a 10% sample), invalidating the measurement layer.

## Negative Controls
1. **Shuffled-paragraph input:** scrambled documents must flow to *less* stable fixed points (structure must matter, or the flow is generic compression).
2. **Claim-tag placebo:** insert decoy claims never present in the text; their "survival" must be ~0 (guards against tagger hallucination).
3. **Ratio control:** a 4:1 flow reaching the same final length must preserve the ordering result (findings must be about the flow, not one ratio).

## Cost and Time
$0. Est. 2-3 sessions; iteration chains run unattended.

## Deliverables
- `tr014/` repo; survival-curve atlas; side-by-side fixed points of fiction vs scripture vs technical prose; 6-8 page report.

## Dependencies
None.
