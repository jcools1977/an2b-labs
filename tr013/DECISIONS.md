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

## D8. The corpus is the token stream the model consumed; chained caches certified for framing, numerics disclosed
Generation chains each run's prompt cache turn to turn and appends
turn framing to the exact token stream rather than re-rendering the
history through the chat template (whose rendering of past assistant
turns differs from the generation prompt it emits, for Qwen3's
thinking stub). The exam (tests/test_chain.py) compares the chained
stream against a full-stream prefill from scratch at every turn, same
batched kernel, greedy: six legs (two models, three tasks), zero cache
fallbacks, and the first eight tokens of every turn identical on
every leg, which is what a framing error would break. Five of six
legs are identical end to end; the sixth (Qwen3, self-dialogue)
diverges at token 29 of its second turn on a near-tie
("responsibility" against "consciousness"), which is kernel numerics
between one-shot and chunked prefill in MLX, not logic. Consequence
stated for reproducibility: a run is reproducible given the same
batch composition (fixed by the manifest's run order and batch size
8); a different grouping may flip a near-tie. The corpus and its
labels are what the models actually produced under that fixed
procedure, which is all the protocol's claims need.

## D9. First smoke batch stalled on memory; MLX cache and working set capped before any counted run
The first smoke batch (one lockstep batch of eight runs, Qwen3-1.7B,
self-dialogue, temperature 0.0, horizon 80, on the cockpit's 48 GB)
slowed about sixty-fold at turn 41 with 38 GB of swap in use. MLX's
Metal buffer cache is unbounded by default and the per-turn
clear_cache call was not holding it down; the machine went to swap
and the terminal session died with it. The TR-006 D16 lesson,
applied here before any run counts: the generator now sets
mx.set_cache_limit(2 GB) and mx.set_memory_limit(30 GB) at import.
Nothing about the corpus settings (D3) changes; the smoke output is
scratch and is not part of the corpus. The smoke batch is rerun under
the caps and its per-turn timing and swap are recorded below before
generation proper starts.

**D9 amended, same day, after measurement.** The diagnosis above was
wrong and the caps did not fix it: the rerun under them died the same
way, Metal out of memory at turn 58, and the per-turn trace added to
the generator showed buffer-cache memory never above 0.7 GB. Active
memory grew about 635 MB per turn against about 95 MB per turn of
real KV across the eight runs, and a probe placed the growth inside
each generate call, not between turns: at the start of every turn
memory was exactly model plus live KV, at return it was model plus
seven times KV for a batch of eight and plus a third of KV for a
batch of one. Cause, in mlx_lm 0.32.0 as pinned: when a run finishes
its reply mid-batch, the batched KV cache is filtered by copying it,
and the finished run's cache is handed back as an unevaluated slice
of the pre-filter array, so eight runs finishing at eight different
steps keep eight superseded copies of the batched cache alive until
the slices are evaluated. Evaluating the returned caches at the end
of the turn freed the baseline but not the in-call peak, which is
what kills the process. The fix evaluates the slice at extraction
(BatchKVCache.extract wrapped in gen/generate.py), so each superseded
copy dies when the next is made. Rerun of the same smoke batch: eight
runs, eighty turns, 207 seconds, zero fallbacks, every turn ending on
EOS, active memory linear in KV (15.6 GB at turn 80, in-call peak
19.9 GB against a 40 GB working set), no swap added. Numerics are
untouched by evaluating earlier; the generator now records active,
peak and cache memory per turn in every run record; the smoke output
lives in the session scratchpad and is not corpus.
The D8 exam was rerun against the patched generator: six legs, zero
fallbacks, framing exact on all six, five legs identical end to end
and the Qwen3 self-dialogue leg diverging at the same token D8
recorded (second turn, token 29). CERTIFIED, unchanged.
