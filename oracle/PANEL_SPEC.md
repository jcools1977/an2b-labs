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

Per ARENA.md rule 1, calibration history attaches to the SEAT;
the engine id and version are recorded in every seal so engine
swaps are visible in the Brier series, never laundered through it.

## Isolation, upgraded

Each seat runs under a Warden deny-all-tools policy: the seat
receives the frozen protocol text and the fixed schema, and can do
nothing else. The seal record cites the policy file and the audit
log entry, replacing the ledger's instruction-level isolation (its
standing disclosed limitation, breached twice by transit) with
policy-enforced isolation and a receipt.

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

## Costs, stated plainly

Per-experiment panel cost is a few cents to a few dollars via
OpenRouter; reports state actual spend, ending the pure
"$0 incremental" line where the panel runs. Keys stay in ClawTex's
runtime management, never on disk in this estate.

## What the pilot must prove before the panel becomes standing law

One full cycle (seal at a real kickoff, score at its closeout) with:
the Warden receipts verifiable, the engine ids recorded, and no
transit of any plaintext through the builder's context. If any leg
fails, the panel stays a pilot and the failure is logged like any
other instrument exam.
