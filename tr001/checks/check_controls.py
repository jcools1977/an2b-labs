#!/usr/bin/env python3
"""Negative-control checks for TR-001, protocol section 8, controls 1-3
plus the section 4 compute-match rule.

Reads one controls JSON (results/controls_seed<N>.json) and exits nonzero
on any violation. Numeric thresholds are fixed in DECISIONS.md D2 before
any results existed; do not adjust them after data.

Expected schema:
{
  "seed": 1,
  "config": {"M": 32, "K": 32},
  "f1": {
    "c3_latent_handoff": float,
    "c4_no_context": float,
    "control_random_adapter": float,
    "control_shuffled_pairing": float,
    "control_ablated_soft_prompt": float
  }
}
"""
import json
import sys

FLOOR_MARGIN = 3.0        # D2: "collapse toward floor" = within 3 F1 of C4
ABLATION_TOL_FRAC = 0.20  # D2: delta within 20% of the C3-over-C4 margin
ABLATION_TOL_MIN = 2.0    # D2: or 2.0 F1 points, whichever is larger

REQUIRED_F1 = [
    "c3_latent_handoff",
    "c4_no_context",
    "control_random_adapter",
    "control_shuffled_pairing",
    "control_ablated_soft_prompt",
]


def check(path):
    violations = []
    with open(path) as fh:
        data = json.load(fh)

    cfg = data.get("config", {})
    f1 = data.get("f1", {})

    for key in ("M", "K"):
        if not isinstance(cfg.get(key), (int, float)):
            violations.append(f"config.{key} missing or non-numeric")
    for key in REQUIRED_F1:
        if not isinstance(f1.get(key), (int, float)):
            violations.append(f"f1.{key} missing or non-numeric")
    if violations:
        return violations

    m, k = cfg["M"], cfg["K"]
    c3 = f1["c3_latent_handoff"]
    c4 = f1["c4_no_context"]
    rnd = f1["control_random_adapter"]
    shuf = f1["control_shuffled_pairing"]
    abl = f1["control_ablated_soft_prompt"]

    if m > k:
        violations.append(
            f"compute mismatch: M={m} soft vectors > K={k} summary tokens; "
            f"a C3 win under these settings is fake by construction"
        )

    if rnd > c4 + FLOOR_MARGIN:
        violations.append(
            f"control 1 (random adapter): F1 {rnd:.2f} did not collapse to "
            f"floor {c4:.2f} (+{FLOOR_MARGIN}); B is answering from priors, "
            f"the pipeline is leaking"
        )

    if shuf > c4 + FLOOR_MARGIN:
        violations.append(
            f"control 2 (shuffled pairing): F1 {shuf:.2f} did not collapse "
            f"to floor {c4:.2f} (+{FLOOR_MARGIN}); the soft prompt acts as a "
            f"generic instruction, not information transfer"
        )

    margin = c3 - c4
    delta = c3 - abl
    tol = max(ABLATION_TOL_FRAC * abs(margin), ABLATION_TOL_MIN)
    if abs(delta - margin) > tol:
        violations.append(
            f"control 3 (ablation): removing the soft prompt changed F1 by "
            f"{delta:.2f} but the C3-over-C4 margin is {margin:.2f} "
            f"(tolerance {tol:.2f}); the adapter is not the live caller"
        )

    return violations


def main():
    if len(sys.argv) != 2:
        print("usage: check_controls.py <controls.json>", file=sys.stderr)
        return 2
    violations = check(sys.argv[1])
    if violations:
        for v in violations:
            print(f"CONTROL VIOLATION [{sys.argv[1]}]: {v}")
        return 1
    print(f"controls hold: {sys.argv[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
