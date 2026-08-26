# AN2B Labs Technical Report #001
## Latent Corpus Callosum: A Learned Adapter Between Two Models' Latent Spaces Does Not Beat Text, and Its Margin Over Nothing Is Not Transfer

**J. DeVere Cooley, AN2B Labs**
**Status: draft v0.1, 2026-08-26**
**Pre-registration: commit `7b7262d`, 2026-08-24, github.com/jcools1977/an2b-labs**

---

## Abstract

TR-001 asked whether a small learned adapter mapping a reader model's
pooled hidden states into an answerer model's embedding space transfers
more task-relevant information than a text summary of equal token budget.
The answer is no: the hypothesis **FAILS** its pre-registered criteria on
both seeds. On 500 held-out SQuAD questions, the best of 16 swept adapter
configurations scored 25.8 and 26.8 F1 against a 43.5 F1 text baseline
(paired difference −17.6 and −16.7, 95% CIs excluding zero) and cleared
the no-context floor of 21.5 by only 4.3 and 5.3 points against a
required 15. The sharper finding came from a pre-registered negative
control: feeding the adapter latents from the *wrong* passage produced
the same score as the right passage (26.2 and 26.3 F1, within half a
point of the treatment, both seeds). The entire above-floor margin is a
passage-independent learned instruction riding the soft prefix, not
information transfer. Without that control, this report would have
claimed a small, replicated, CI-backed transfer effect, and the claim
would have been false. We localize the failure twice: twelve convergent
sweep configurations spanning linear and MLP adapters, two pooling
depths, and two orders of magnitude of learning rate all landed within a
4.4-point band, implicating the one stage the sweep held constant (mean
pooling over positions), and the shuffled control shows the residue that
survives pooling is not passage signal at all. Everything ran on one
Apple M4 Mac with 16 GB of RAM at $0 incremental cost.

## 1. Hypothesis and stakes

**H1:** a learned adapter carrying Model A's pooled hidden states into
Model B's input embedding space transfers more task-relevant information
than a text summary at matched budget, measured by downstream QA accuracy.

**H0:** it does not.

The hypothesis is the desk-scale form of a larger thesis: that a "higher
order connective layer" between models could couple them more richly
than text. The protocol committed in advance: if H0 holds here, that
thesis dies at desk scale and is not built at cathedral scale. H0 holds.

## 2. Method

Pre-registered before any code or data (commit `7b7262d`): thresholds,
kill criteria, negative controls, and models. Every judgment call made
during implementation is logged in `tr001/DECISIONS.md` (D1–D28), each
timestamped before the numbers it could have bent toward.

**Models.** Reader A: Qwen 3 8B (MLX, 4-bit, pinned snapshot
`545dc425`). Answerer B: Llama 3.1 8B Instruct (MLX, 4-bit, pinned
snapshot `241a666d`). Cross-family on purpose: same-family pairs share
tokenizers and lineage, which would inflate transfer. One quantization
level for every condition and control, so all comparisons share a ruler.

**Task and data.** Extractive QA on SQuAD v1.1. 2,000 training pairs
(1,750 train-core plus a 250-pair config-selection dev split, carved at
the passage level), 500 held-out eval pairs drawn from the disjoint dev
articles. Passages 200–400 tokens of B's tokenizer. Leakage is checked
by code: punctuation-aggressive normalized passage hashing, zero overlap
across all three split relations.

**Conditions.**

| | Description | Role |
|---|---|---|
| C1 | B reads the raw passage | ceiling |
| C2 | A summarizes to a hard cap of 32 B-tokens, question-blind; B answers from the summary | baseline to beat |
| C3 | A's mean-pooled hidden states, mapped by a trained adapter to 32 soft vectors prepended to B | treatment |
| C4 | B answers from the question alone | floor |

C3's prompt frame is identical to C4's; the soft prefix is the only
difference, so the C3-over-C4 margin is causally attributable to the
prefix. Compute matching (M = K = 32) is enforced in code. All eval
decoding is greedy. Scoring is official SQuAD normalization, EM and F1
as max over the gold set, with parity against the vendored official
script proven on adversarial cases before any number was produced.

**Adapters and sweep.** Trained by answer-token cross-entropy through
frozen quantized B (the QLoRA configuration), adapter in bf16, exactly
2 epochs per config, batch 1, final checkpoint only, no early stopping.
The 20-config grid (linear and 2-layer MLP; final-layer and last-4
pooling; learning-rate grids) was committed before config 1 trained.
Four grid cells (linear on the 16,384-dim concat, a 2.15B-parameter
matrix needing ~17 GB of training state) are closed as untrainable on
16 GB hardware, their slots left permanently vacant rather than
reallocated. Configs were selected on the dev split only; the held-out
500 was touched exactly once per seed, by the selected config, enforced
by code that refuses to run without a committed selection record.

## 3. Results

**The field** (held-out 500; C1/C2/C4 are deterministic and
seed-independent):

| Condition | EM | F1 | 95% CI (F1) |
|---|---|---|---|
| C1 full context | 77.6 | 87.8 | [85.4, 90.1] |
| C2 text handoff | 29.2 | 43.5 | [39.7, 47.2] |
| C3 latent handoff, seed 1 | 14.2 | 25.8 | [22.6, 29.2] |
| C3 latent handoff, seed 2 | 15.8 | 26.8 | [23.5, 30.2] |
| C4 no context | 9.4 | 21.5 | [18.7, 24.5] |

Paired per-item C3−C2: **−17.64** [−21.54, −13.78] (seed 1) and
**−16.66** [−20.60, −12.81] (seed 2). The pass criterion required +5
with the CI excluding zero, and +15 over floor. **Verdict: FAIL,
replicated.** The kill criterion "linear and MLP both fail after an
honest sweep" is met.

**The sweep band.** Twelve convergent configurations, spanning linear
versus MLP, one versus four pooled layers, and learning rates from 3e-5
to 3e-3, landed between 20.1 and 24.4 dev F1 against a dev bar of 48.6.
Four more diverged below floor at high learning rates. Nothing the sweep
varied mattered. The diagnosis was registered before the MLP tiers ran
(D24): the invariant across all twenty cells is mean pooling, which
compresses a ~300-token passage into one vector (or four) before any
adapter sees it.

**The controls** (held-out 500, run with the selected config after
selection, per seed):

| Control | Seed 1 F1 | Seed 2 F1 | Requirement | Leg |
|---|---|---|---|---|
| 1. Random-init adapter | 7.1 | 5.5 | collapse to floor +3 | green |
| 2. Shuffled pairing (wrong passage) | 26.2 | 26.3 | collapse to floor +3 | **red** |
| 3. Ablated (no prefix) | 21.5 | 21.5 | delta ≈ C3−C4 margin | green |
| 4. Leakage (hash overlap) | 0 | 0 | zero | green |

**Control 2 is the finding.** Latents from the wrong passage scored
within half a point of latents from the right passage, on both seeds.
The 4.3–5.3 point margin over floor that survived the sweep is therefore
not information transfer: it is a passage-independent instruction the
prefix learned during training, and it works as well for any question.
Had this control not been pre-registered, this report would have shipped
"latent handoff recovers ~13% of the floor-to-baseline gap" as a small,
replicated, CI-backed mechanism claim. It would have been false. The red
leg is the evidence, and it is reproducible: re-running the pipeline
shows control 2 red in exactly this way (DECISIONS D28).

**Instrument certification.** The ablated control reproduces C4 to the
hundredth of a point across all 500 items, which means the tokenized
generation path and the embedding-injection path agree on the full eval
workload, hardening every number in the table. The injection identity
test (real token embeddings through the soft-prefix path must reproduce
tokenized generation exactly, with sabotaged variants caught) and scorer
parity with the official SQuAD script were both proven red-then-green
before any experiment number existed. Dev-side and eval-side baselines
agree to 0.1 (C2) and 1.4 (C4) F1.

## 4. A small third finding: what the prefix actually learned

A 32-vector soft prefix trained on QA pairs through a frozen model
functions as a passage-independent instruction worth roughly 4–5 F1 over
the floor, plausibly "answer tersely in extractive style." It is
bracketed from below by the random-init control: an untrained prefix is
actively harmful (5.5–7.1 F1, well under the 21.5 floor), consistent
with the four sweep configs that diverged and landed at or below floor.
So prefix training under an information bottleneck reliably converges to
a useful generic instruction while transferring nothing measurable about
the specific input. This is a clean observation about what prefix tuning
learns when the conditioning signal is too compressed to be useful.

## 5. Why text won

The 32-token summary is lossy (43.5 against a ceiling of 87.8), but it
is lossy *selectively*: a summarizer keeps names, numbers, and facts,
which is precisely what extractive QA needs. Mean pooling is lossy
*uniformly*: averaging over ~300 positions preserves topic-level gist
and destroys the positional, span-level structure answers live in. The
sweep shows no readout, linear or nonlinear, shallow or deep, recovers
what the averaging already destroyed; control 2 shows the small residue
that does survive is not about the passage at all. Text won because
selection beats compression at equal budget.

## 6. Limitations, as pre-committed

- The claim is scoped to **mean-pooled** latent handoff versus
  compute-matched, question-blind text. Sequence-level transfer
  (per-token latents, attention-based readout) is untested here, named
  as future work rather than discovered by a reviewer.
- The linear readout of the full 16,384-dim last-4 concat is permanently
  untested on this hardware: infeasible at desk scale, not covered
  elsewhere. The one scenario that cell uniquely covered is
  linearly-readable signal that a narrow bottleneck destroys.
- Both models ran 4-bit throughout; behavior at bf16 is untested at desk
  scale. All comparisons are internal to one quantization ruler.
- One task family (SQuAD-style extractive QA), one model pairing
  (Qwen 3 8B into Llama 3.1 8B Instruct), 500 held-out items.

## 7. What TR-001b would have to change

The failure is localized to averaging over positions. The successor
hypothesis is per-token or attention-read latent transfer, where B (or a
cross-attention adapter) can address individual positions of A's hidden
states rather than their mean. That is a different memory budget
(sequence-length latents instead of one vector per passage) and honestly
a different machine. Until it is run, the honest summary of latent
coupling at desk scale is: worse than text, and the part that looks like
signal is not.

## 8. Reproducibility

Public repository: github.com/jcools1977/an2b-labs. Pre-registration is
the root commit (`7b7262d`, 2026-08-24), containing only the frozen
protocols; every threshold in this report predates every number. The
repo contains the full pipeline, the 28-entry decision log, per-item
predictions for every condition and control, the append-only sweep log
(16 trained configs, 4 recorded untrainable), seeds (data 7, dev split
11, experiment 1 and 2), pinned model snapshots and dependency versions,
and `verify.sh`, which re-certifies the instrument legs and reports
control 2 red for the pre-registered reason. Hardware: one Apple M4 Mac
mini, 16 GB RAM. Incremental cost: $0. Wall-clock: two overnight sweep
runs plus roughly one attended day.
