# TR-002r forecast scoring

Published verdict pending ratification: **FAIL** (H0 shape; KILL did
not fire). Scored 2026-09-07 at closeout against the cold gate read.
Brier baselines: uniform 0.75, always-FAIL 0.0 on this outcome.

## Protocol-only oracle, OF RECORD (AutoBot channel seal, hash
verified 3750e42f..., plaintext committed beside its seal)

Verdict forecast: PASS 0.15 / FAIL 0.55 / SPLIT 0.18 / KILL 0.12.
**Brier 0.2718. Modal call FAIL: HIT** — the ledger's best isolated
score yet.

| Claim | p | Graded | Why |
|---|---|---|---|
| Skyline clears 0.80 on all three encoder-encoder pairs | 0.85 | FALSE | bge-e5 0.938 clears; both MiniLM pairs miss (0.755, 0.737) |
| Primary unsupervised top-1 below encoder-encoder unsupervised top-1 | 0.88 | UNRESOLVABLE | every unsupervised run at chance; no ordering exists |
| Monotonic fidelity rise 2k->8k->16k, largest jump first | 0.75 | FALSE | flat at chance; raw cosine +0.013 then -0.002 |
| Direction asymmetry: higher cosine INTO the decoder space, top-1 stays discriminating | 0.65 | TRUE | 0.807 into llama vs 0.666 into bge; top-1 decided the gate |
| Both hard negatives behave | 0.85 | TRUE (with a degeneracy note) | shuffled at chance; wrong-model at 0.0, its ratio clause vacuous under total collapse |
| Precision matters less than corpus size | 0.60 | UNRESOLVABLE | both gaps are zero-vs-zero |

The mechanism paragraph aged well: anisotropic mean-pooled decoder
spaces degrading distributional matching was named before any number
existed — though the collapse reached even encoder-encoder pairs,
which the forecast did not anticipate.

## Protocol-only oracle, SUPERSEDED (this session's earlier seal,
d89674bd..., reported beside per the D6 rule, never selected)

Verdict forecast: PASS 0.10 / FAIL 0.48 / SPLIT 0.15 / KILL 0.27.
**Brier 0.3758. Modal FAIL: HIT.** Its three sub-claims: encoder
pairs beat decoder pairs unsupervised (UNRESOLVABLE, all at chance);
monotonic rise with sub-half-skyline at 2k (FALSE on the rise,
trivially true on the 2k weakness); CKA-fidelity correlation
(UNRESOLVABLE, no fidelity variance to correlate).

## Context-rich reviewer forecast (hash a98fb8fd..., plaintext held
by the PI): scoring PENDING the paste at ratification.

## Reading

Both protocol-only seals modal-called FAIL and both under-priced the
totality of the collapse: the shared blind spot from TR-004 (the
uniformity of the result) repeats with the sign flipped — there,
direction was real everywhere; here, collapse was total everywhere.
Two experiments running, the priors keep missing the UNIFORMITY of
outcomes, in both directions. Wave 2's standing whisper, sharpened.
