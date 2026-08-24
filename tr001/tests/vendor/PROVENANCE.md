# Vendored reference implementations

## evaluate-v1.1.py
Official evaluation script for SQuAD v1.1, vendored 2026-08-24 from
https://raw.githubusercontent.com/allenai/bi-att-flow/master/squad/evaluate-v1.1.py
(a widely used mirror of the original CodaLab bundle).

SHA-256: f5a673dbbd173e29e9ea38f1b2091d883583b77b3a4c17144b223fb0f2f9bd09

Used only as the parity reference for lib/scoring.py (DECISIONS.md D15).
Never edited; tests/test_scorer_parity.py verifies the hash before use.
