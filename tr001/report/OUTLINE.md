# TR-001 report outline

Drafted 2026-08-25, before tier 3's numbers exist, so the structure cannot
bend toward them. Three regimes; two start the writeup immediately.
Fixed elements regardless of regime: the field (C1 87.8 / C2 43.5 / C4
21.5, D18 bands held), the paired-CI pass line (C3 >= C2+5, CI excluding
zero, and >= C4+15), the paper trail (pre-registration commit 7b7262d,
DECISIONS D1-D25), and the verdict stated plainly on page one.

## Regime 1: MLPs clear the dev bar (48.56)
Selection fires; the held-out 500 gets its single touch per seed; the
negative controls (protocol section 8) run for real before the headline
is believed. Story: "pooled signal exists, but only a nonlinear readout
can decompress it," with tier 1 as the built-in ablation showing
linearity was the constraint. PASS/FAIL still decided only by the frozen
held-out criteria.

## Regime 2: MLPs cluster with tier 1 in the low 20s
D24's diagnostic becomes the thesis: grid cells spanning input depth and
nonlinearity all landed within a few points, so the invariant across the
sweep (mean-pooling) is the bottleneck, not anything the sweep varied.
Sharper than "text wins": it localizes the failure to a single stage and
says precisely what a TR-001b (per-token latents, attention readout)
would have to change. FSA companion framing: imposed geometry destroyed
signal there; destroyed-by-averaging is this paper's version.

## Regime 3: MLPs move meaningfully but miss the bar
The regime where p-hacked papers are born, answered in writing twice
before the numbers existed: D7's no-config-21 clause and D25's
permanent-vacancy rider. Tier 4 runs as declared; if the global best
still misses, D21 already covers the ending: dev-best runs the 500 once
so the FAIL carries an honest number. Framing: "latent handoff recovers
X% of the floor-to-baseline gap at desk scale," a real quantity, not a
consolation.

## Limitations (verbatim commitments, all regimes)
- Scope: mean-pooled latent handoff versus text (D24). Sequence-level
  transfer is untested future work, named, not discovered by a reviewer.
- The linear readout of the full 16,384-dim concat is permanently
  untested on this hardware (D25): "infeasible at desk scale, untested,"
  not "covered elsewhere." The one scenario that cell uniquely covered:
  linearly-readable signal that a narrow bottleneck destroys.
- Both models 4-bit quantized, same ruler everywhere (D6); B's behavior
  at bf16 untested at desk scale.
- Single task family (SQuAD-style extractive QA), single model pairing
  (Qwen 3 8B -> Llama 3.1 8B), 500 held-out items.

## Numbers table (to fill)
All four conditions, both seeds, EM/F1 with CIs; C3 paired-difference CI
vs C2; all four negative controls per seed; sweep_log summary (16
trained configs, 4 untrainable); wall-clock and $0 budget line.
