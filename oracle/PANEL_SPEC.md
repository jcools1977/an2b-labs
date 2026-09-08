# Multi-vendor oracle panel — pilot specification (DRAFT)
**Prepared 2026-09-08; runs only after the harvest review ratifies
harvest candidate 5 and the reviewer countersigns. First live
subject: the first Wave 3 kickoff.**

## Shape

Three protocol-only oracle seats, one per vendor family, ClawTex-run
on legion over the EngramPort bus, engines resolved through the
single OpenRouter key at seal time:

| Seat | Engine (resolved at seal, recorded per seal) |
|---|---|
| oracle-anthropic | latest Anthropic frontier via OpenRouter |
| oracle-openai | latest OpenAI frontier via OpenRouter |
| oracle-xai | latest xAI frontier via OpenRouter |

Per ARENA.md rule 1 (as amended by review B2/B5): calibration
attaches to the SEAT with Brier series ENGINE-STRATIFIED, never
aggregated across engine changes; each seal records the SERVED
backend metadata the gateway returns (not the routing alias),
sampling parameters (the ledger's standing determinism exception,
now stated: remote frontier forecasts are unseeded; temperature and
top_p are recorded per seal), and the engine's stated training
cutoff. Scores are always read against the always-FAIL baseline as
a standing line, and a cutoff postdating the lab's publications
discounts a seat's score per a rule pre-registered before that seal.
Disclosed limitation: all three vendor seats ride one OpenRouter
account, a shared intermediary and correlated-failure path sitting
under the panel's own cross-vendor-correlation question. The D6
no-reroll rule carries forward explicitly: one forecast per seat per
seal; a superseded forecast is reported beside, labeled, never
selected. A seal becomes a seal when its hash is PUSHED and fetched
by the reviewer's channel before closeout work begins; commit
timestamps alone evidence nothing. The consensus (mean-probability)
column is REPORTED-ONLY and never the headline number.

## Isolation, stated honestly (rewritten per review A6/B1)

Warden's deny-all-tools policy structurally prevents a seat's
OUTBOUND actions: no tool call, no lookup, no repo read. It does not
by itself prove a clean input, and it does not address the ledger's
historical breach mode (plaintext transiting the builder's context);
those remain governed by the seal ceremony and its pass criteria
below. What the receipt actually contains, verifiably: the sha256 of
the Warden policy file IN FORCE hashed into the seal record at seal
time, and the relevant audit-log excerpt (or its hash) EXPORTED into
the repo beside the seal, verified by the reviewer's channel via its
own fetch — never a bare citation to a legion-local mutable file.
Negative control before first duty (BB4C rule 3): a panel seat
attempts a tool call and the DENY is WATCHED to fire, with the
receipt captured; a deny-all policy that has never been observed
denying guards nothing.

## Procedure (per TR, extending the standing oracle procedure)

1. At kickoff, before Phase 0 closes: all three seats receive the
   identical protocol text and schema; three prediction JSONs come
   back; three sha256 hashes are committed
   (oracle/sealed/TRxxx.<seat>.sha256); plaintexts held gitignored
   with legion redundancy, revealed at closeout.
2. Each seal records: seat, engine id resolved, Warden policy,
   audit-log reference, protocol commit.
3. At closeout: reveal, verify, Brier-score all three; grade
   sub-claims; the panel table reports per-seat and consensus
   (mean-probability) scores. The reviewer's context-rich forecast
   remains the ledger's separate second column.
4. Standing analysis: cross-vendor error correlation per experiment
   and cumulatively — the uniformity blind spot (two-experiment
   pattern) is the first pre-registered question the panel exists
   to answer: is it a vendor artifact or a frontier-wide prior?

## Custody and costs, as mechanism (review A5, C)

The OpenRouter key is injected at seat launch from 1Password
(estate law: keys come from 1Password, never disk), held in process
memory only; the account carries a hard spend cap set by the PI at
ratification, and the PI owns the account. Per-experiment panel cost
is a few cents to a few dollars; reports state actual spend, ending
the pure "$0 incremental" line where the panel runs. Bus data path,
stated: prediction JSONs transit the EngramPort bus endpoint and
OpenRouter (and thus three vendors) before sealing; acceptable for
protocol texts destined for publication and their forecasts, and
stated here rather than discovered. If OpenRouter is down at a
kickoff, the standing single-seat oracle procedure applies and the
missing panel seal is recorded as absent, never backfilled.
Disclosed limitation (estate audit 2026-09-01, F127/F131): the
EngramPort Git-v0 bus cannot authenticate the actor named in an
event, so bus identity is untrusted; the seal's integrity rests on
the repo-committed hashes and reviewer-fetched receipts, not on bus
attribution, until Voltron's signed actor admission fronts the bus.

## What the pilot must prove before the panel becomes standing law

One full cycle (seal at a real kickoff, score at its closeout) with
every leg green:
1. Warden policy hash in each seal; audit excerpt exported to the
   repo; both verified from the reviewer's channel by fetch.
2. The DENY negative control watched to fire before first duty.
3. Each seat passes its exam first: the retro-calibration battery
   (all seven closed TRs, labeled RETRO, zero foresight weight) per
   ARENA rule 4.
4. Served-backend, sampling parameters, and training cutoff present
   in every seal; always-FAIL baseline in the scoring.
5. No plaintext transits the builder's context, end to end.
6. Spend within the cap; key never at rest on disk.
7. oracle/README amended in the ratifying commit so the ledger's
   constitution and the panel's mechanics agree on what a valid
   seal is (review A7).
If any leg fails, the panel stays a pilot and the failure is logged
like any other instrument exam.
