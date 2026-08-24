# TR-002: Platonic Convergence Audit
**Track A: Latent Geometry and Model Coupling** | Status: Protocol draft v0.1

## Question
Do open-weight models' internal geometries converge toward a common representational structure as they scale, and does the degree of convergence predict how cheaply two models can be coupled?

## Hypothesis
**H1:** Representational similarity between model pairs (measured by linear CKA and Procrustes distance on matched stimuli) increases with model scale, and pairwise similarity negatively correlates with the training loss of a linear adapter between them (from TR-001 machinery).
**H0:** Similarity is flat or idiosyncratic across scale, or does not predict adapter cost.

## Background
The Platonic Representation Hypothesis (Huh et al., 2024) claims models converge on a shared statistical model of reality as they scale. If true, it is the theoretical license for latent coupling: the corpus callosum is cheap only if the hemispheres already speak near-dialects of one language. This audit tests the claim on models that run on our own fleet, and adds the practical corollary nobody has published: convergence as a *predictor of coupling cost*.

## Design
- **Models (6):** Llama 3.2 1B, Llama 3.1 8B, Qwen 3 4B, Qwen 3 8B, Mistral 7B, Gemma 2 9B (all MLX or llama.cpp with hidden-state export)
- **Stimuli:** 1,000 sentences stratified across domains (news, code, scripture, fiction, technical), identical for all models
- **Measurement:** mean-pooled final-layer states per sentence per model; compute pairwise linear CKA and orthogonal Procrustes distance across all 15 model pairs
- **Coupling cost:** for each pair, train a linear adapter (TR-001 code) for a fixed budget; record final loss
- **Analysis:** correlation between similarity metrics and adapter loss; scale trend across parameter counts

## Metrics
- Pairwise CKA matrix, Procrustes distance matrix
- Spearman correlation: similarity vs adapter final loss
- Scale trend: similarity vs geometric mean of pair parameter counts

## Pass/Fail (frozen before data)
- **PASS:** Spearman |rho| >= 0.6 between CKA and adapter loss across the 15 pairs, with bootstrap CI excluding zero.
- **FAIL:** |rho| < 0.6 or CI includes zero.
- **KILL:** results not stable across two disjoint stimulus halves.

## Negative Controls
1. **Shuffled stimuli:** compute CKA with sentence order permuted per model; must collapse toward chance.
2. **Random-weight model:** include one randomly initialized model; its similarity to all trained models must be near floor.
3. **Domain leave-out:** correlation must hold when any one domain is dropped (guards against one domain driving everything).

## Cost and Time
Existing fleet, $0 incremental. Est. 2-3 sessions (mostly inference sweeps that can run overnight).

## Deliverables
- `tr002/` repo: extraction pipeline, CKA/Procrustes code, verify.sh
- Heatmap figures, correlation table, 4-6 page report
- If PASS: quantitative coupling-cost predictor usable by TR-003 and TR-007

## Dependencies
Uses TR-001 adapter code but does not require TR-001 to pass.
