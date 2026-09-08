# Multi-vendor oracle panel: pilot runner

Stood up 2026-09-08 under Word 1 (RATIFICATION_WAVE3.md): AEGIS Gate 2
hold lifted for the panel pilot and arena seat work inside AN2B Labs,
spend cap $10. The specification is `oracle/PANEL_SPEC.md`; the ledger
constitution is `oracle/README.md`; every judgment call is in
`DECISIONS.md` beside this file. This is a PILOT: it becomes standing
law only after one full cycle (seal at a real kickoff, score at its
closeout) with every leg of the spec's proving list green.

## What is here

| File | Role |
|---|---|
| `panel.py` | the runner: resolve, deny-control, exam, seal, reveal, score. Standard library only; the Warden comes from ClawTex on legion |
| `seats.json` | three seats, one per vendor family; engine resolved live by a logged rule; the $10 cap mirrored |
| `policies/oracle_deny_all.yaml` | the Warden policy in force: default DENY plus a catch-all DENY; hashed into every seal |
| `PROMPT_TEMPLATE.md` | the exact prompt; its hash and the assembled prompt's hash are in every seal |
| `verify.sh` | the negative controls; every leg watches its check fail on a bad input |
| `inject_key.sh` | cockpit side: 1Password to legion over ssh, into the runner's stdin, never disk |
| `clawtex.fleet.yaml` | declarative seat manifest for the bus; not load-bearing for a seal |
| `controls/` | DENY control records with the audit-log excerpt and policy hash |
| `exams/` | retro-calibration exam results per seat and engine (RETRO, zero foresight weight) |
| `seals/` | seal records per TR and seat: hashes and metadata only |
| `spend_ledger.jsonl` | every paid call's usage as the gateway reported it |
| `../sealed/TRxxx.<seat>.sha256` | the committed hash of each plaintext; plaintext itself stays gitignored beside it |

## The cycle

```
freeze/freeze_check.sh                      # frozen protocol set intact
panel.py check-policy                       # policy in force == committed blob
panel.py deny-control                       # DENY watched to fire; record written
panel.py resolve                            # what "latest" resolves to today, logged
inject_key.sh exam                          # retro battery, all seats  (paid)
inject_key.sh seal TR-xxx TRxxx_file.md     # live seal at a kickoff    (paid)
git add oracle/sealed/*.sha256 oracle/panel/seals oracle/panel/controls oracle/panel/exams oracle/panel/spend_ledger.jsonl
git commit && git push                      # a seal is a seal when the hash is pushed and fetched
...closeout...
panel.py reveal TR-xxx                      # plaintexts verified against committed hashes
panel.py score  TR-xxx VERDICT              # Brier per seat, always-FAIL baseline, consensus reported-only
```

The runner refuses to seal unless the freeze check is green, the policy
matches its committed blob, and a passing DENY control exists for that
exact policy hash. Mock runs (`--engine mock --out DIR`) must write
outside the repository and are labeled mock in every record.

## Isolation, stated honestly

The Warden structurally prevents a seat's OUTBOUND actions: the only
tool path is `dispatch_tool()`, which routes through ClawTex's Warden in
strict mode under the deny-all policy, and even an ALLOW would find no
executable tool behind it. The engine request carries no tools field,
asserted before every call. What this does not prove is a clean input:
that rests on the prompt hash (template plus protocol text, both in the
seal) and on the runner's construction, which the reviewer can read.
Forecast plaintext never reaches stdout, so it never transits the
builder's context; the mock leg of `verify.sh` watches for that.

Bus identity is untrusted (audit F127/F131), so nothing about a seal's
validity depends on the EngramPort bus; it depends on the committed hash
being pushed and fetched by the reviewer's channel.

## Scoring rules carried into every record

Calibration attaches to the SEAT; Brier series are reported per served
engine within a seat and never aggregated across engine changes. The
served backend is what the gateway returns, not the routing alias. The
always-FAIL baseline is a standing line. The consensus column is
reported only. One forecast per seat per seal; a superseded forecast is
kept beside, labeled, never selected. The retro-calibration exam is a
MECHANICS exam (D6): calibration numbers are the anchor, not a bar.

## Standing requirements on the operator

`op signin` on the cockpit before `inject_key.sh`; the OpenRouter item
lives in 1Password at `op://Private/OpenRouter/credential` unless
`OP_OPENROUTER_ITEM` says otherwise. The account-level hard cap is set
by the PI on the OpenRouter account; `seats.json` mirrors it and the
runner's own guard stops before any call whose estimate would cross it.
