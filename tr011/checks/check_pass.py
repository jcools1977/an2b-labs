#!/usr/bin/env python3
"""TR-011 PASS gates (protocol; DECISIONS D2, D6, D7).

Reads results/analysis.json and exits nonzero unless:
- corpus B is valid per the memorization audit (D7); a PASS claim over
  an invalidated corpus B is a contradiction, not a judgment call
- at least two features QUALIFY (cross-model rho >= 0.7, D6) AND meet
  |paired Cliff's delta| >= 0.3 on corpus A AND agree in sign on B
- author-disjoint AUC >= 0.7

Schema:
{
  "corpus_b_valid": bool,
  "author_control_auc": float,
  "auc": float,
  "features": {name: {"delta_a": f, "sign_agrees_b": bool, "rho": f}}
}
"""
import json
import sys

DELTA_GATE = 0.3
RHO_GATE = 0.7
AUC_GATE = 0.7


def check(path):
    d = json.load(open(path))
    violations = []
    feats = d.get("features", {})
    if not feats:
        return [f"{path}: no features; a gate over nothing proves nothing"]

    if not d.get("corpus_b_valid", False):
        violations.append(
            "corpus B invalid per the D7/D15 rules; no PASS is "
            "reachable and corpus A stands alone as evidence"
        )
    auth = d.get("author_control_auc")
    if not isinstance(auth, (int, float)):
        violations.append("author_control_auc missing (D15)")
    elif auth >= 0.7 and d.get("corpus_b_valid", False):
        violations.append(
            f"CONTRADICTION (D15): author-identity control AUC {auth} >= 0.7 "
            f"while corpus_b_valid is claimed; author style, not polish, can "
            f"carry that score"
        )

    passing = [
        n for n, f in feats.items()
        if abs(f.get("delta_a", 0)) >= DELTA_GATE
        and f.get("sign_agrees_b", False)
        and f.get("rho", 0) >= RHO_GATE
    ]
    if len(passing) < 2:
        violations.append(
            f"only {len(passing)} feature(s) qualify and clear |delta| >= "
            f"{DELTA_GATE} with corpus-B sign agreement and rho >= {RHO_GATE} "
            f"(need 2): {passing}"
        )
    auc = d.get("auc")
    if not isinstance(auc, (int, float)):
        violations.append("auc missing")
    elif auc < AUC_GATE:
        violations.append(f"author-disjoint AUC {auc} < {AUC_GATE}")
    return violations


def main():
    if len(sys.argv) != 2:
        print("usage: check_pass.py <analysis.json>", file=sys.stderr)
        return 2
    violations = check(sys.argv[1])
    for v in violations:
        print(f"VIOLATION [{sys.argv[1]}]: {v}")
    if not violations:
        print(f"PASS gates hold: {sys.argv[1]}")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
