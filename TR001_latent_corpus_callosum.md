# AN2B Labs Technical Report #001 (Protocol)
## Experiment 1: Latent Corpus Callosum
### Can a learned adapter between two models' latent spaces beat text as the coupling medium?

**Status:** Protocol draft v0.1 (pre-registration)
**Author:** J. DeVere Cooley, AN2B Labs
**Method discipline:** BB4C. Pass/fail criteria and negative controls fixed before any data is collected.

---

## 1. Hypothesis

**H1:** A small learned adapter mapping Model A's pooled hidden states into Model B's input embedding space transfers more task-relevant information than a text summary of equal or greater token budget, measured by downstream QA accuracy at matched compute.

**H0 (null):** Latent handoff performs no better than text handoff, or fails to beat the no-context floor.

If H0 holds, the "higher-order connective layer" thesis dies at desk scale and should not be built at cathedral scale. That result is publishable as-is (companion to the FSA postmortem).

---

## 2. Models and environment

- **Model A (reader):** Qwen 3 8B, MLX build, an2b-norman or an2b-legion
- **Model B (answerer):** Llama 3.1 8B Instruct, MLX build, same machine
- MLX chosen over llama.cpp because hidden-state extraction and soft-prompt injection are straightforward in Python
- All runs seeded. Environment pinned in `requirements.txt` and logged per run.

Rationale for cross-family pairing: same-family models share tokenizers and training lineage, which would inflate transfer. Cross-family is the honest test.

## 3. Task

Extractive QA over passages. Suggested corpus: SQuAD-style pairs, or the synthetic federal-procurement corpus already built for MedComm refusal calibration (reuse what exists).

- N = 500 passage/question pairs for evaluation (held out)
- N = 2,000 pairs for adapter training
- Passages 200-400 tokens. Long enough that summarization is lossy, short enough for Mac memory.

## 4. Conditions

| # | Condition | Description | Role |
|---|-----------|-------------|------|
| C1 | Full context (ceiling) | Model B reads the raw passage, answers | Upper bound |
| C2 | Text handoff | Model A summarizes passage to K tokens; B answers from summary only | Baseline to beat |
| C3 | Latent handoff | Model A's pooled hidden states mapped via adapter to M soft-prompt vectors prepended to B | Treatment |
| C4 | No context (floor) | Model B answers from the question alone | Lower bound |

**Compute matching:** M soft vectors in C3 must not exceed K tokens in C2 (start with K = M = 32). If C3 wins only by using more slots, the win is fake.

## 5. Adapter

- Architecture: single linear layer first; escalate to 2-layer MLP (hidden dim 1024, GELU) only if linear fails
- Input: mean-pooled final-layer hidden states from Model A (optionally last 4 layers concatenated)
- Output: M vectors in Model B's embedding dimension
- Training objective: minimize B's answer loss with B frozen (only the adapter trains)
- Budget: hours on M-series hardware, not days. If it needs a GPU cluster, the experiment is misdesigned.

## 6. Metrics

- Primary: Exact Match and token-level F1 on held-out set
- Secondary: answer latency, adapter parameter count, tokens/vectors transferred
- Report mean with 95% bootstrap CI (10,000 resamples)

## 7. Pass/fail criteria (fixed now, before data)

**PASS:** C3 F1 exceeds C2 F1 by at least 5 points, CI excluding zero, AND C3 beats C4 floor by at least 15 points.

**FAIL:** C3 minus C2 is under 5 points, or CI includes zero, or C3 fails the floor margin.

**KILL (do not iterate past these):**
- Linear and MLP adapters both fail after honest hyperparameter sweep (max 20 configs)
- C3 only passes when M > K (compute mismatch)
- Results do not replicate across two seeds

No moving the goalposts after seeing results. A near-miss is a FAIL, written up as one.

## 8. Negative controls (the tests that watch it fail)

Per the zero-callers covenant, every claimed mechanism needs a demonstration of its absence breaking things:

1. **Random adapter:** freeze adapter at random init. C3 performance must collapse toward C4 floor. If it doesn't, B is answering from priors and the pipeline is leaking.
2. **Shuffled pairing:** feed A's latents from a *different* passage. Must collapse to floor. If not, the soft prompt is acting as a generic instruction, not information transfer.
3. **Ablation delta:** remove the soft prompt at inference on the trained adapter. Delta must equal roughly the full C3-over-C4 margin. Confirms the adapter is a live caller, not dead code.
4. **Label leakage check:** verify no eval passage appears in adapter training set (hash overlap check, must be zero).

All four controls run before the headline number is believed.

## 9. Deliverables

- `tr001/` repo: adapter code, run configs, seeds, `verify.sh` asserting controls 1-4 hold (red-then-green fixtures)
- Results table (all four conditions, both seeds, CIs)
- TR-001 writeup: 4-8 pages, posted publicly (Dev.to or arXiv) as disclosure event regardless of outcome
- If PASS: Experiment 7 (Committee Memos vs Corpus Callosum) unlocks as TR-002
- If FAIL: postmortem section on *why* text won, which is itself a contribution

## 10. Estimated cost

- Hardware: existing fleet (an2b-norman / an2b-legion), $0 incremental
- Data: public QA sets or existing synthetic corpus, $0
- Time: est. 2-4 focused sessions (model plumbing is the long pole, adapter training is minutes)

---

*Breath before code: this document is the breath. Nothing gets built until the pass/fail line above is agreed and frozen.*
