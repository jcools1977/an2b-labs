# TR-006 DECISIONS

Every judgment call, logged before the numbers it could bend toward.
Protocol thresholds untouched; ambiguity resolves toward the reading
that makes H1 harder to pass. The CREDO firewall applies.

## D1. FRONTIER consultation (standing macro-check clause)
Dated 2026-09-09: FRONTIER-002 (scanned 2026-09-08, countersigned by
the reviewer with citations spot-checked) consulted at this kickoff.
It names TR-006's lane explicitly: GWT-flavored architectures
proliferate (Theater of Mind arXiv:2604.08206, brain-inspired graph
MAS arXiv:2603.15371, GWT-marker frameworks preprints.org
202601.1683) and none publishes a capacity SWEEP with a frozen
regime-change criterion; the lane is open and well timed. The entry
is one day old and named this kickoff in its scan-cadence line, so
it satisfies the fresh-entry requirement as TR-002r's and TR-003r's
D1 did. Sensing only; no threshold derives from it.

## D2. Kickoff state
TR-006 opens on the Wave 3 slate (Word 1: TR-003 door (a) then
TR-006) with no hold on it. The protocol is the original 2026-08-24
text, unchanged; no rescope. Phase 0 is OPEN and closes only after
the PI's three words in PLAN.md and both oracle seals. TR-003r's
verdict is on the table awaiting ratification and is not affected.

## D3. Machine, transfer, sweep: the PI's word of 2026-09-09
The PI's word: the cockpit and legion are free from 5 pm and may be
used as the builder judges best. Judgment, logged: the sweep runs on
the cockpit (M5 Pro, 48 GB), the only machine holding the three
models resident; the three 4-bit snapshots were copied from legion's
cache over the tailnet (about 15 GB, no internet download); legion
remains available for the panel and for any encoder-side work. The
sweep launches at 17:00 EDT by a timer and runs checkpointed per
configuration and per item so sleep or interruption loses at most
one item.

## D4. Rounds R = 4, fixed before any council run
The protocol leaves the rounds per item unstated. R = 4 is the
smallest count at which the broadcast-frequency sweep {1, 2, 4} is
meaningful (F = 4 broadcasts once; F = 1 four times); fewer rounds
would make two of three frequencies identical. Not a threshold; a
design constant, and the volume estimate in PLAN.md (about 190,000
generations) follows from it.

## D5. Environment
tr006/.venv on the cockpit: mlx 0.32.2, mlx-lm 0.31.3, numpy 2.5.3,
scipy 1.18.1, transformers 5.16.1, pinned in requirements.txt. Model
snapshots by HuggingFace hub commit: Llama-3.1-8B-Instruct-4bit
241a666d, Qwen3-8B-4bit 545dc425, gemma-2-9b-it-4bit ff12eb39.

## D6. The transfer failed and a download happened; disclosed
The rsync from legion's cache reported success line by line but
copied nothing (its error, "source ... directory", was swallowed by
a tail). The cockpit throughput benchmark then fetched all three
models from HuggingFace, about 15 GB over the internet, which the
plan had asked for as a tailnet transfer and not as a download. The
snapshots that arrived are byte-for-byte the same hub commits legion
pins (241a666d, 545dc425, ff12eb39; D5 holds). Logged because the
route was not the one asked for, even though the bytes are.

## D7. Phase 0 CLOSED 2026-09-09: seals of record
Oracle of record sealed (oracle/sealed/TR006.sha256, one tool use,
never in the builder's context). Panel sealed as its second live
cycle against protocol commit 7b7262d: three seats, three hashes
pushed from legion. Implementation code begins after this commit.

## D8. The AIC test and the KILL, operationalized before any council run
Per family per seed, the 18 (S, F) points are pooled (harder than
picking the best frequency), each a binomial of 200 items. Smooth
monotone model: logistic in log2 S with a non-negative slope, two
parameters. Regime model: a step at a grid midpoint, low level below
and high level at or above, high >= low (a jump, not a drop), the
breakpoint counted as a third parameter. AIC = 2k - 2 logL. The
protocol's margin >= 10 reads as AIC_smooth - AIC_regime >= 10. KILL
is evaluated only where both families show a regime (margin >= 10 in
each) and fires when their breakpoints differ by more than one grid
step. If only one family shows a regime, that is FAIL, not KILL.
The test is certified on synthetic worlds (tests/test_regime.py): a
true step must be found at the right S, and smooth or flat curves
must NOT produce a margin of 10.

## D9. Controls, operationalized
Random salience: at F = 1 across the S grid, the control's AIC margin
must fall to at most half the main margin or below 10; vacuous (and
said so) where the main margin is under 10. Frozen buffer: best
accuracy over S at F = 1 must sit within 0.05 of the single best
agent. Role shuffle (roles permuted across the three models per item,
seeded): accuracy at the best bounded configuration must move by at
least 0.03; an unchanged number withdraws every specialization claim
and is recorded as a violation so verify.sh shows it.

## D10. Task families and the screening rule
Multi-hop QA: HotpotQA distractor validation (7,405 hard items;
parquet sha256 c20b638ca82b21d0...), context = the two gold
paragraphs plus four seeded distractors, shuffled, normalized
exact-match scoring. Constraint puzzles: seeded logic-grid puzzles,
four entities by three attributes, indirect clues, brute-force solver
proving a unique solution, clue set minimized, exact-match scoring
on the asked value. "No single agent solves reliably alone" is
frozen as: an item enters the scored set only if AT MOST ONE of the
three models answers it correctly in one shot; screening candidates
are drawn seeded, and the 200 scored items per family per seed are
disjoint across seeds by hash. The single-best-agent baseline is
measured on the scored items with the same R rounds of
self-revision, so it is not the screening pass re-read.

## D11. Council mechanics fixed before any run
Greedy decoding (temperature 0), 200 output tokens per submission,
Qwen3 thinking disabled. Each round every seat receives the task,
the current broadcast buffer, and its own prior submissions, and
returns JSON: an item, a self-assessed salience 0 to 100, and (the
synthesizer, every round) a current answer. Candidates = surviving
items plus the round's three submissions; the top S by salience
survive (ties to the newer item); the buffer is broadcast on rounds
that are multiples of F, otherwise seats see the last broadcast. The
final answer is the synthesizer's answer at round R = 4. Unlimited
log: every item ever submitted is visible, no cut. Frozen buffer:
the round-1 buffer is broadcast every round thereafter. Traces record
every submission's salience and rank at its cut, so the
slot-competition statistic (final-broadcast items that held the last
slot at their cut) is computed after the fact, never re-run.

## D12. Role to model assignment and the answer step
Fixed before any run: proposer = Llama-3.1-8B, critic = Qwen3-8B,
synthesizer = gemma-2-9b. Role shuffle permutes this map per item.
After round R a final broadcast always happens and the synthesizer
answers in a separate answer step seeing it, so every broadcast
frequency contains at least one exchange (with R = 4 and F = 4 the
only exchange is that final one). Thirteen generations per item.

## D13. gemma-2 batched attention: a certified one-line fix
mlx-lm 0.31.3 cannot batch gemma-2 (grouped-query scores are five-
dimensional, the batched mask four; the broadcast fails and surfaces
as a ZeroDivisionError in the stats). workspace/gemma_batch_patch.py
inserts the missing mask axis. Certified by tests/test_gemma_batch.py:
batched greedy output equals sequential greedy output token for token
on three prompts of unequal length; the exam also asserts the
unpatched failure is real. verify.sh runs it. Without it, gemma would
have run sequentially at about five seconds per generation.

## D14. Screening candidates
600 seeded HotpotQA candidates and 400 generated puzzles per seed;
each model answers once, alone, in the answer-step format; items with
at most one correct model are kept and the first 200 per family are
scored, disjoint across seeds by content hash. The single-shot
outcomes of every candidate are stored so the selection is auditable.

## D15. Execution order and the clock
Seed 41 runs completely (screening, main grid, baselines, controls)
before seed 43 begins, so a partial run still yields one complete
seed. Batched throughput measured at 0.67 seconds per generation at
16 items; the plan's volume (about 190,000 generations with the
answer step) reads as roughly 35 hours of machine time per seed,
under caffeinate, checkpointed per item. Launch by timer at 17:00 EDT
2026-09-09 on the PI's word.

## D16. First launch died of GPU memory at 18:40; cause, fix, and a corrected clock
Launched 15:54 on the PI's word. Seed 41 screening completed and
checkpointed (600 HotpotQA candidates, 246 pass the screen; 400
puzzles, 301 pass; 200 scored each). Seed 43 screening then died with
a Metal out-of-memory error. Measured cause: MLX's buffer cache grew
to 23 to 34 GB after one batch of 16 to 32 prompts of about 950
tokens, and with three models resident (14.3 GB) Metal could not wire
more; no limit had been set. Fix: cache limit 3 GB, memory limit
34 GB, batch 8, halve the batch and retry on any out-of-memory, and
the rendered board text capped at 200 characters per item so the
S = 32 prompts stay under about two thousand tokens. Screening is now
checkpointed per family. Nothing scored changed: seed 41's task set
is the one screened under the original settings.
The clock, corrected on measurement: these prompts are prefill-bound
at about one second per generation regardless of batch size (0.9 s
Llama, 1.6 s gemma at batch 8), not the 0.67 s measured on short
prompts. Roughly two days of machine time per seed; seed 41 lands
about Friday night, seed 43 early the following week if the lid
stays open. Relaunched at the time stamped in sweep.log.

## D17. Paused 2026-09-10 08:2x on the PI's word; prompt reordered for prefix caching; prompt-v1 results discarded
The PI works on the cockpit by day; the run was paused after 11 of
36 main configurations (about 1.7 s per generation on the QA family,
1.0 s on puzzles, 1.9 hours per (S, F) point). To cut the repeated
950-token prefill, the prompt was reordered so the task context and
question lead and are KV-cached once per item and model; every
generation then feeds only its suffix. Certified token for token
against uncached output on all three models (tests/test_prefix_cache.py,
in verify.sh). Because the prompt text changed, the 11 configurations
already run under the old order are set aside in
results/discarded/promptv1_seed41_raw and never mixed with the new
run; the task sets (screened under prompts that are unchanged by this
reorder, the single-shot answer step) stand.
Measured after the change: block of 8 items through the full four-
round council, 1.04 s per generation on QA and 0.98 s on puzzles with
prefill included, 13 s per item; block 16 peaks at 40 GB, trips the
out-of-memory fallback and ends slower (1.79 s). Block 8 is the
ceiling with three models resident. Honest clock at R = 4: about 45
minutes per family per configuration, 1.5 hours per (S, F) point,
roughly 58 hours per seed of continuous running (main grid 27,
baselines 4, controls 27), five days for both seeds; nights only
doubles it. This is the floor for this prompt size on this hardware.

## D18. The PI's word of 2026-09-10: no TR-006 compute on the cockpit; artifacts removed
The PI reversed D3: the cockpit is the working machine that travels
and holds every key, and a sweep that loads it for days is the wrong
shape (the estate rule in the orchestrator's CLAUDE.md, now applied to
the lab). One further fault forced the point: after the pause, a
block-size diagnostic's Python child survived its killed shell as an
orphan for 23 minutes at 38 GB and a full core, while this seat
reported nothing running because its process checks matched script
text rather than the interpreter's command line. Corrected rule:
a stopped process is verified gone by PID before it is reported gone.
Executed: everything committed and pushed (HEAD 00d3bfa on origin);
the unrevealed oracle-of-record plaintext copied to legion's
redundancy directory and clone with its hash verified
(27de79260aae...); then removed from the cockpit: the three 4-bit
model snapshots (13.4 GB), the tr006 virtual environment, the raw
HotpotQA parquet (re-fetchable by hash), sweep.log, and the local
sealed plaintext. The lab clone stays as the PI's seat. Where and
whether TR-006 runs next (legion holds one 8B model at a time; a
three-model council there means model swapping or R = 2 and days) is
the PI's call and is not decided here.
