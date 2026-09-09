# TR-006 implementation plan (before any code; Word 3)

Protocol: TR006_minimum_viable_workspace.md, frozen 2026-08-24 at
7b7262d, unchanged. Nothing below touches a threshold; every
operationalization is a Phase 0 decision logged before data.

## The protocol as tasks

1. **Council harness** (`tr006/workspace/`, reusable by TR-008 to
   TR-010): three role seats (proposer, critic, synthesizer), a
   bounded buffer of S slots, self-assessed salience per submitted
   item, top-S survival, broadcast every F rounds, an unlimited-log
   mode, and per-item traces (every submission, its salience, its
   rank at the cut, whether it survived) so the slot-competition
   statistic is computable afterward and never re-run.
2. **Task families** (two, per protocol): multi-hop QA and constraint
   puzzles. QA: a public multi-hop set, held-out split, normalized
   exact-match scoring. Puzzles: deterministic logic-grid puzzles
   generated with a solver, unique solutions, exact scoring. Items
   selected where no single agent solves reliably alone, using a
   screening set disjoint from the 200 scored items per family, with
   the screening rule frozen in DECISIONS before any council run.
3. **Sweep**: S in {1, 2, 4, 8, 16, 32} x F in {1, 2, 4}, 200 items per
   family per configuration, R rounds per item (R fixed in Phase 0),
   resumable per configuration with one JSON line per item.
4. **Baselines**: single best agent (each model alone, same rounds,
   best of three reported); unlimited shared log (no competition) at
   each F.
5. **Controls, red first**: random salience (S sweep at F=1),
   frozen round-1 buffer (S sweep at F=1), role shuffle (S sweep at
   F=1). Each control's checker gets its red fixture before the
   mechanism exists, as TR-003r's did.
6. **Gate machinery**: accuracy-vs-S curves; the AIC test
   operationalized in Phase 0 (piecewise two-segment fit vs monotone
   smooth fit, pooled over F within a family; PASS needs AIC margin
   >= 10 in BOTH families and the unlimited log under the best
   bounded configuration); KILL operationalized as the breakpoint S
   differing by more than one grid step between families. Checkers
   with red fixtures; verify.sh exits nonzero on any violation.
7. **Closeout**: curves, slot-competition statistics, report,
   utilization draft, disk line, seal reveal and score.

## Machine and compute, stated before the word

- **Models**: Llama-3.1-8B-Instruct-4bit, Qwen3-8B-4bit, gemma-2-9b-
  it-4bit (three 7B-class families, all cached on legion). Together
  about 15 GB resident: they fit the cockpit (M5 Pro, 48 GB) and do
  not fit legion (16 GB; TR-003r's decoders ran swap-bound at 45
  texts a minute there).
- **Throughput**: 21 tokens a second per 8B model on legion measured
  today; the cockpit is expected faster, and batching prompts across
  items with all three models resident is the lever.
- **Volume**: 18 configurations x 400 items x 3 agents x R rounds,
  plus baselines and three controls at F=1: about 190,000
  generations at R=4, 100,000 at R=2. At 1.5 to 3 seconds each,
  unbatched, that is 40 to 160 hours; batched, plausibly 10 to 30.
  Either way it crosses the 8-hour ask line in CLAUDE.md.
- **Transfer**: copying the three 4-bit snapshots from legion's
  cache to the cockpit over the tailnet is about 15 GB, no internet
  download, but over the 2 GB line and asked for as such.

## The three words this plan waits for

1. Machine: run on the cockpit (recommended: the only box that holds
   the three models resident), accepting a multi-day sweep on the
   machine that travels, with per-configuration checkpoints so it
   survives sleep and interruption.
2. The 15 GB model transfer from legion to the cockpit.
3. The sweep budget: an estimated 10 to 30 hours batched, up to 160
   unbatched; R=2 rounds halves it and is the leaner pre-registration
   if the PI wants the sweep bounded.

On those words: oracle of record and panel seal against the frozen
protocol before Phase 0 closes; then code, red first.
