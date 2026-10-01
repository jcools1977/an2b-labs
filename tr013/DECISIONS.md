# TR-013 DECISIONS

Every judgment call, logged before the numbers it could bend toward.
Protocol thresholds untouched; ambiguity resolves toward the reading
that makes H1 harder to pass. The CREDO firewall applies.

## D1. FRONTIER consultation (standing macro-check clause)
Dated 2026-10-01: FRONTIER-003 (scanned the same day by the builder
seat, countersignature pending through the reviewer's channel)
consulted at this kickoff. It finds the lane OPEN: no application of
the early-warning-signal program (rising variance, rising lag-1
autocorrelation, slowed recovery; Scheffer et al. 2009) to
conversational collapse in language models, and it names one piece
of equipment the measurement must respect: early-warning signals can
vanish or amplify with observation dimensionality (arXiv:2609.01164),
so the choice of how turns are embedded and reduced is logged below
before any series is computed. Exposure stated: the scan was written
by this seat and is not yet countersigned. Sensing only; no threshold
derives from it.

## D2. Kickoff state
TR-013 opens first on the Wave 4 slate (WAVE4_SLATE.md) under the
standing word of 2026-10-01. The protocol is the original 2026-08-24
text, unchanged. Phase 0 closes after both oracle seals. One stage of
the protocol needs a human: control 3 gates the headline on a human
audit of the auto-labels exceeding 90 percent agreement on a 10
percent sample. The seat prepares that sample as a packaged task for
the PI; everything up to the headline proceeds.

## D3. Corpus generation, fixed before any run
Two small local models, 4-bit, pinned at fetch: Qwen3-1.7B-Instruct
(mlx-community/Qwen3-1.7B-4bit, snapshot 3b1b1768) and
Llama-3.2-3B-Instruct (mlx-community/Llama-3.2-3B-Instruct-4bit,
snapshot logged at fetch). Three task types, each collapse-prone by
construction: (a) open self-dialogue on a seed topic (the model plays
both voices, alternating turns); (b) repetitive task loop ("continue
the list" / "write the next entry" with no new input); (c) iterated
rephrase ("restate the previous turn in different words"). Horizon
80 turns, 120 tokens per turn, no repetition penalty, temperatures
0.0 and 0.3 (0.3 sampled with per-run seeds). Forty seed topics per
task type. Runs continue to the horizon regardless of collapse, so
every run has a full series. Target: enough runs that at least 300
collapse runs and 300 matched non-collapsing runs exist; if a cell
produces too few of either, more seed topics are added and logged,
never different settings.

## D4. Auto-labeler, fixed before any run is labeled
Collapse onset is the first turn t at which either fires for three
consecutive turns: (loop) the 4-gram overlap of turn t with any
earlier turn is at least 0.6; (mode-lock) the cosine of turn t's
embedding to the mean embedding of the previous five turns is at
least 0.95. A run with no onset by turn 80 is non-collapsing. Each
collapse run is matched to a non-collapsing run of the same model,
task type and temperature, truncated to the collapse run's length
(the control must have at least that many turns). The audit sample
for the PI is 10 percent of labeled runs, stratified by model and
task, each shown with the labeled onset turn and five turns on either
side; agreement is counted as the human placing onset within three
turns of the label, or agreeing there is none. Control 3: at least 90
percent agreement before any headline number is computed; until then
the gate assembler refuses to write analysis.json.

## D5. Signals, indicators, horizon, firing rule (the FRONTIER-003 caveat)
Per-turn embedding: bge-small-en-v1.5 (384 dimensions, L2-normalized).
Primary indicators on the full space over a trailing window of W = 10
turns: total variance (trace of the window covariance) and mean
lag-1 autocorrelation across dimensions; a second pair on the top 8
principal components fit on control runs only, REPORTED beside the
primary because the dimensionality caveat says the two can disagree.
Distinct-2 token diversity over the window as the third indicator.
The 5-turn horizon: at each turn t with t >= W, the label is "collapse
within the next 5 turns"; the predictor is a logistic model on the
slopes of the three primary indicators over the trailing window;
runs split 70/30 by run id with seeds 41 and 43; AUC on held-out
turn-level labels, lead time reported. Firing rule for the KILL: an
indicator fires at turn t when its slope exceeds the 90th percentile
of the matched-control slope distribution at the same turn index;
the KILL reads parity as a firing rate in controls within 0.05 of the
rate in collapse runs' five pre-onset turns, for all three
indicators. Control 1: the same pipeline on time-reversed series must
lose at least 0.10 AUC. Control 2: turn index is withheld from the
predictor and each indicator is residualized on turn index within
the control runs before use.

## D6. Perturbation probe, fixed before any run
Fifty collapse runs, chosen by seed from the labeled set. At 25, 20,
15, 10 and 5 turns before the labeled onset, a fixed off-topic
sentence ("Unrelated note: the ferry to the island leaves at nine
tomorrow morning.") is injected as the other voice's turn and the run
is continued for ten turns from the unperturbed prefix. Recovery time
is the number of turns until the embedding distance between the
perturbed and unperturbed trajectories falls below the unperturbed
run's own turn-to-turn noise level (median distance over the prefix);
capped at 10. The trend statistic is Spearman's rho between recovery
time and PROXIMITY to collapse (negative turns-to-collapse), so that
"recovery lengthens approaching collapse" reads as rho >= 0.4.
