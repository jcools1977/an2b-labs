# Oracle panel pilot: decision log

Every judgment call made while standing the panel up, in order. The
spec is `oracle/PANEL_SPEC.md`; nothing here alters it. Where the spec
was silent, the harder reading was taken and is named as such.

**D1 (2026-09-08). The battery is six closed TRs, not seven.** The spec
says "all seven closed TRs." The repository holds six published
verdicts: TR-001 FAIL, TR-020 SPLIT, TR-011 FAIL, TR-015 FAIL (its
trivially fired KILL coded FAIL per its report and the 2026-09-01
anchor's rule), TR-004 FAIL, TR-002r FAIL. Original TR-002 was retired
at its kickoff gate by radar and has no scorable outcome. The spec's
count is treated as a miscount; the battery is every TR with a verdict.

**D2. Standard library only in the runner.** `panel.py` has no
third-party dependency; ClawTex supplies the Warden on legion. Fewer
pins, and the cockpit can run every leg but the Warden legs for
iteration. A missing Warden is a FAILED leg in `verify.sh`, never a
skipped one.

**D3. "Latest frontier" is a logged mechanical rule, not a memory.**
Per seat: gateway models matching an include glob and none of an
exclude list; newest `created` wins; ties break to the shortest id then
lexicographic. Batch, free, mini, nano, pro, codex, audio, image and
similar variants are excluded by name. The full candidate list is in
every seal. Resolved 2026-09-08 from the live gateway:
oracle-anthropic to `anthropic/claude-fable-5.1`, oracle-openai to
`openai/gpt-6-astra`, oracle-xai to `x-ai/grok-4.6`. The PI may pin any
seat in `seats.json`; a pin is itself logged in the seal. The exclusion
of `-pro` variants is a judgment (they read as compute modes of the same
model, not a different frontier); it is visible in the candidate list
and reversible by pin.

**D4. The builder seat's own family resolves into the panel.** The rule
picks `anthropic/claude-fable-5.1`, the family animating the builder
seat. That is what the rule yields and it is recorded; it is not a
reason to bend the rule. The cross-vendor correlation question the
panel exists to answer is unaffected, and the seat and engine are
recorded on every act so a reader can stratify.

**D5. Training cutoff: gateway field first, self-report second, unknown
treated as contamination-possible.** OpenRouter's `knowledge_cutoff` is
null for all three resolved engines as of 2026-09-08. The seal records
the gateway field verbatim and a one-line self-reported cutoff from a
separate low-cost probe, labeled self-reported. The contamination flag
on a retro item is CLEAR only when a KNOWN cutoff precedes that TR's
publication date; unknown is POSSIBLE. This is the harder reading and
is pre-registered here before any seal.

**D6. The seat exam grades MECHANICS, and calibration is reported, not
gated.** The spec names the retro battery as the exam without a bar.
A calibration bar would invite choosing engines by their retro score,
exactly the laundering review B2 warned against. A seat passes when,
on every battery item, first attempt, no re-roll: the reply is a
schema-valid JSON object (whole message or one fenced block), the
served backend is recorded, no tool call appears in the response, and
the DENY control has fired under the policy in force. Mean Brier,
modal hits, the always-FAIL baseline and the contamination flags are
reported beside as the calibration anchor, RETRO, zero foresight
weight.

**D7. Sampling is recorded as requested and as sent.** All three
resolved engines are reasoning models and the gateway lists
`temperature` and `top_p` as unsupported for two of them. The runner
sends each parameter only where the gateway lists it as supported and
records `sampling_sent` per seal; `reasoning.effort` is fixed at
medium and `response_format` at `json_object` for every seat. The
determinism exception (remote frontier forecasts are unseeded in
effect) is thereby stated in every record rather than once in prose.

**D8. Cost guard is local as well as account-level.** The account cap
is the PI's mechanism. The runner also keeps `spend_ledger.jsonl` from
the gateway's own usage accounting and refuses any call whose
conservative estimate (prompt length over 3.5 plus the full
`max_tokens` at list price) would cross $10 cumulatively. If the cap
trips mid-exam, the exam is incomplete and the seat is not certified;
that is logged, not worked around.

**D9. The bus is declared, not load-bearing.** `clawtex.fleet.yaml`
lists the three seats for `clawtex up`, but the runner does not post to
EngramPort and no seal depends on the bus. Reason: the spec already
places seal integrity on committed hashes and reviewer fetches because
bus identity is untrusted (F127/F131), and the lab's rule is that the
presence of code is not evidence it runs; untested bus code would be
exactly that. Bus presence can be exercised during the proving cycle
once per-seat EngramPort keys are supplied from 1Password.

**D10. The prompt is the standing procedure's, unchanged.** The harvest
packet suggested a pre-registered line warning forecasters that priors
under-price uniform outcomes. It is NOT in the template: adding it
would change the instrument between the 2026-09-01 anchor and the
panel's exam, and it is a lab-wide change for the PI to rule on. The
template's hash is in every record, so a future change is visible.

**D11. The freeze manifest pins the protocol set as of commit 5a58f1a,
including one prior edit.** TR-019's file carries a gate note appended
2026-09-03 on the PI's word (thresholds untouched; diff read before
pinning). Gate packages (`*_KICKOFF_GATE.md`) are adjudication
documents and are not in the manifest. Any future reissue is a logged
act approved through a channel other than the seat it constrains.

**D12. The DENY control has a discriminating leg.** The same five
probes (web.search, file.read, http.get, exec, memory.write) are run
under ClawTex's bundled default policy, where three are ALLOWed. A
control that only ever sees DENY could be a harness that cannot say
ALLOW; this leg proves the difference is the policy.

**D13. Key custody path.** The key is read from 1Password on the
cockpit and piped over ssh into the runner's stdin on legion, read from
file descriptor 0, held in process memory, never exported to the
environment (where same-user process listing could read it) and never
written. `verify.sh` scans the repository tree and the host's shell
profiles for key-shaped material and proves the detector fires on a
planted fixture.

**D14. What could not be done in this session.** The 1Password CLI on
the cockpit is not signed in and `op signin` is interactive, so the
retro exams and any live seal wait on the PI. Everything that does not
need the key is built and verified.

**D15 (2026-09-08). First live attempt stopped by the workspace's ZDR
guardrail; nothing spent.** The key authenticated, then the gateway
refused with "0 endpoints out of 4 requested are available matching
your guardrail restrictions and data policy: ZDR violation
(guardrail)." The OpenRouter workspace has a zero-data-retention
requirement enabled, and the Anthropic engine has no ZDR endpoint
(xAI does; OpenAI's are unlabeled). The panel's data path was already
stated in PANEL_SPEC as acceptable without ZDR: protocol texts are
destined for publication and forecasts are revealed at closeout.
Relaxing the guardrail is an account-level act and therefore the PI's
(ARENA rule 6, money and credentials); the runner does not route
around guardrails. Recorded before the exam rather than after.

**D16 (2026-09-08). Exams ran; two lessons filed.** (a) Legion-origin
commits diverged once because the legion clone had not pulled the
cockpit's later commits before committing; the exam commit was
cherry-picked onto main (content verified identical) and legion reset
to origin. `inject_key.sh` now fast-forwards the legion clone before
every run. (b) The contamination rule (D5) ran entirely on
self-reported cutoffs because the gateway field is null for every
resolved engine; the flags are CLEAR and the summary says plainly that
self-report is the weakest evidence the rule accepts.
