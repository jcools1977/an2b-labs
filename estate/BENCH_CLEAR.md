# Bench clearance: the lab cleans up after itself

**Standing protocol, drafted 2026-09-11 on the PI's word ("after we
write the report and we have the evidence we need, we go in and clean
up after ourselves, just like a lab"). Binds every session alongside
CLAUDE.md once the PI ratifies this text.**

## The rule

An experiment is cleared from the bench when its report is ratified
and its evidence is on origin, and not before. Clearing means the
rebuildable bulk it left on each machine is removed, and what was
removed is written into that experiment's decision log as its final
entry. The evidence is never touched.

## What "evidence" is (kept, always)

Everything committed: protocol, decision log, checkers and fixtures,
results JSON, figures, report, manifests with content hashes, the
embedding and corpus hash sidecars, the oracle seals and their
revealed plaintexts. Plus the sealed plaintexts of forecasts not yet
revealed (gitignored by design), on every machine that holds them.

## What "bulk" is (swept at clearance)

Inside `trXXX/`: `corpus_store/`, `data/raw/`, `cache/`,
`checkpoints/`, `.venv/`, `build/`, `dist/`, `*.egg-info/`,
`__pycache__/`, `adapters/`, and log files. All of it is rebuildable
from committed code, pinned snapshots, and manifests; the manifests
say how long the rebuild takes.

Model snapshots in the HuggingFace cache: swept when every experiment
that references them is ratified and at least one of those is being
cleared. A snapshot an open experiment references is kept. A snapshot
nothing references is reported, never swept, because its provenance
is unknown to the tool.

## What the PI's word keeps

A `trXXX/KEEP` file lists paths the PI has named as kept, one per
line with the reason (tr001/KEEP: the adapters, by the PI's word of
Wave 1). `estate/KEEP` lists cache snapshots kept regardless. The tool
never touches a listed path; changing a KEEP file is a logged act.

## The mechanism

`estate/bench_clear.py TR [TR...]` refuses unless, for each TR:
`trXXX/report/RATIFIED` exists (written at ratification with the date
and commit), the TR's tracked files are clean, and HEAD is on origin.
Without `--execute` it prints what it would remove with sizes. With
`--execute` it removes the bulk, appends the disk line to
`trXXX/DECISIONS.md`, and the session commits that entry. Run it on
every machine the experiment touched (legion, and any machine named
in the disk line). `estate/verify.sh` proves the refusals fire.

## Ratification marker

Ratifying a report is the PI's act. The session that records it
writes `trXXX/report/RATIFIED` (date, commit, the PI's words in
brief), sets the report's status line to v1.0, and clears the bench
in the same closeout. Backfilled 2026-09-11 for TR-001, TR-020,
TR-011, TR-015, TR-004, TR-002r from their ratification commits.
