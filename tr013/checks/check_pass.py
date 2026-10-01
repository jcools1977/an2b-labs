#!/usr/bin/env python3
"""TR-013 PASS: AUC >= 0.75 at the 5-turn horizon on held-out runs at
both seeds, and perturbation recovery time trends with proximity to
collapse, rho >= 0.4. Refuses without a cleared audit (control 3).
Schema (results/analysis.json): {"auc_5turn": {"41": x, "43": x},
 "rho_recovery": x, "n_probe_runs": int, "audit_cleared": true}"""
import json
import sys


def check(path):
    d = json.load(open(path))
    v = []
    if d.get("audit_cleared") is not True:
        v.append("headline computed without a cleared label audit (control 3)")
    for s in ("41", "43"):
        a = d.get("auc_5turn", {}).get(s)
        if a is None:
            v.append(f"seed {s} AUC missing")
        elif a < 0.75:
            v.append(f"seed {s}: AUC {a} < 0.75 at the 5-turn horizon")
    if d.get("rho_recovery", -1) < 0.4:
        v.append(f"recovery-time trend rho {d.get('rho_recovery')} < 0.4")
    if d.get("n_probe_runs", 0) < 50:
        v.append(f"perturbation subset has {d.get('n_probe_runs')} runs, protocol says 50")
    return v


def main():
    vs = check(sys.argv[1])
    for x in vs:
        print(f"VIOLATION [{sys.argv[1]}]: {x}")
    if not vs:
        print(f"PASS gates hold: {sys.argv[1]}")
    return 1 if vs else 0


if __name__ == "__main__":
    sys.exit(main())
