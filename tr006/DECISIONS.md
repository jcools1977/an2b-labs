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
