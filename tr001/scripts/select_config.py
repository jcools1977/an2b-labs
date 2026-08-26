#!/usr/bin/env python3
"""Config selection on dev (DECISIONS D19, D21).

Walks tiers in declared order. A tier is judged only when every one of its
configs has a dev result for this seed. The first tier whose best config
clears the dev bar (dev C3 F1 >= dev C2 F1 + 5 AND >= dev C4 F1 + 15,
operational trigger only, never the verdict) supplies the winner: its
highest-dev-F1 config. Later tiers are then irrelevant per the protocol's
escalation rule. If a judged tier fails, the next tier must run; if all 20
fail, the global best is selected anyway so the held-out number for the
FAIL writeup is produced honestly.

Writes results/selection_seed<seed>.json, the record the D19 eval guard
requires. Exit 2 means "sweep must continue" (not an error).
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.gates import TR_ROOT  # noqa: E402

DEV_MARGIN_OVER_C2 = 5.0
DEV_MARGIN_OVER_C4 = 15.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    args = ap.parse_args()

    sweep = json.load(open(TR_ROOT / "configs" / "sweep.json"))
    baselines = json.load(open(TR_ROOT / "results" / "baselines_dev.json"))
    c2_f1, c4_f1 = baselines["c2"]["f1"], baselines["c4"]["f1"]
    bar = max(c2_f1 + DEV_MARGIN_OVER_C2, c4_f1 + DEV_MARGIN_OVER_C4)

    tiers = {}
    for c in sweep["configs"]:
        tiers.setdefault(c["tier"], []).append(c)
    closed = {int(k): v for k, v in sweep.get("closed_tiers", {}).items()}

    all_results = {}
    for tier in sorted(tiers):
        if tier in closed:
            print(f"tier {tier}: CLOSED, not judged. {closed[tier]}")
            continue
        configs = tiers[tier]
        results = {}
        for c in configs:
            p = TR_ROOT / "results" / f"dev_{c['id']}_seed{args.seed}.json"
            if p.exists():
                results[c["id"]] = json.load(open(p))
        if len(results) < len(configs):
            missing = [c["id"] for c in configs if c["id"] not in results]
            print(
                f"tier {tier} incomplete for seed {args.seed}: missing {missing}. "
                f"Sweep must continue (earlier tiers all failed the dev bar)."
            )
            return 2
        all_results.update(results)
        best_id = max(results, key=lambda k: results[k]["f1"])
        best_f1 = results[best_id]["f1"]
        cleared = best_f1 >= bar
        print(
            f"tier {tier}: best {best_id} dev F1 {best_f1:.2f}; bar {bar:.2f} "
            f"(devC2 {c2_f1:.2f}+{DEV_MARGIN_OVER_C2}, devC4 {c4_f1:.2f}+{DEV_MARGIN_OVER_C4}); "
            f"{'CLEARED' if cleared else 'failed'}"
        )
        if cleared:
            selection = {
                "seed": args.seed,
                "config_id": best_id,
                "dev_f1": best_f1,
                "tier": tier,
                "dev_bar": bar,
                "dev_bar_cleared": True,
                "judged": {k: v["f1"] for k, v in all_results.items()},
            }
            break
    else:
        best_id = max(all_results, key=lambda k: all_results[k]["f1"])
        selection = {
            "seed": args.seed,
            "config_id": best_id,
            "dev_f1": all_results[best_id]["f1"],
            "tier": None,
            "dev_bar": bar,
            "dev_bar_cleared": False,
            "judged": {k: v["f1"] for k, v in all_results.items()},
            "note": "no tier cleared the dev bar; global best selected for the honest held-out FAIL number",
        }

    out = TR_ROOT / "results" / f"selection_seed{args.seed}.json"
    json.dump(selection, open(out, "w"), indent=2)
    print(json.dumps(selection, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
