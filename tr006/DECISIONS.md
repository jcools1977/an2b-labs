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
