#!/usr/bin/env python3
"""The wild audit (protocol wild phase; D5, D20, D21, D22).

Guards, all structural:
- refuses unless the seeded recovery gate passes (protocol FAIL rule)
- refuses unless the system's bite-proof is green (D22)
- inherits the seeded configuration whole: same Auditor, same criterion,
  same judge, same probe count, zero knobs

Per system: full component audit, placebo on both components with the
capability-matched endpoint paraphraser (D20 clause 1), unauditability
tripwire with the certified-resolution floor (D20 clause 2), dead-token
cost share. Writes results/wild_<sid>.json and results/wild_summary.json.
"""
import json
import math
import subprocess
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TR_ROOT))

from auditor.ablate import Auditor  # noqa: E402
from auditor.canon import FAMILY_OF_SYSTEM  # noqa: E402
from auditor.judge import Judge  # noqa: E402
from auditor.lm import MLXLM  # noqa: E402
from auditor.trace import item_seed  # noqa: E402
from wild.adapters import BUILDERS, FAMILY, TASK_OF  # noqa: E402
from wild.base import EndpointLM, load_probes  # noqa: E402

FAMILY_OF_SYSTEM.update(FAMILY)
CERTIFIED_FLOOR = 1.0  # D20 clause 2, from the D3 judge gate


def guards(sid):
    r = subprocess.run([sys.executable, str(TR_ROOT / "checks" / "check_recovery.py"),
                        str(TR_ROOT / "results" / "seeded_recovery.json")],
                       capture_output=True)
    if r.returncode != 0:
        raise SystemExit("WILD GUARD (D5): seeded recovery gate does not pass")
    bite_path = TR_ROOT / "results" / "wild_bite.json"
    if not bite_path.exists():
        raise SystemExit("BITE GUARD (D22): no bite-proof results")
    bite = json.load(open(bite_path)).get(sid)
    if not bite or not all(bite[k] for k in ("reproducible", "bite", "sabotage_caught")):
        raise SystemExit(f"BITE GUARD (D22): {sid} has no green bite-proof")


def token_estimate(text):
    return max(1, len(str(text).split()))


def main():
    systems = sys.argv[1:] or list(BUILDERS)
    judge = Judge(MLXLM("mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"))
    para_lm = EndpointLM()

    for sid in systems:
        out_path = TR_ROOT / "results" / f"wild_{sid}.json"
        if out_path.exists():
            print(f"[{sid}] already audited, skipping")
            continue
        guards(sid)
        print(f"=== auditing {sid} ===", flush=True)
        system = BUILDERS[sid]()
        items = load_probes(sid)
        auditor = Auditor(system, items, para_lm, judge, TASK_OF[sid])
        result = auditor.audit()

        placebo = auditor.placebo(system.component_names(),
                                  rng_seed=item_seed(sid, "placebo", "boot"),
                                  paraphrase_lm=para_lm)
        result["placebo"] = placebo
        lo, hi = placebo["quality_ci"]
        mean = placebo.get("quality_mean", (lo + hi) / 2)
        trips = not (lo <= 0.0 <= hi) and abs(mean) >= CERTIFIED_FLOOR
        result["unauditable"] = bool(trips)
        result["tripwire"] = {"quality_mean": mean, "quality_ci": [lo, hi],
                              "certified_floor": CERTIFIED_FLOOR,
                              "capability_matched_paraphraser": para_lm.name}

        # Dead-token cost share from baseline traces (word-count proxy,
        # logged as the operationalization).
        base = {}
        for it in items[:50]:
            _, trace = system.run(it)
            for e in trace["events"]:
                base[e["component"]] = base.get(e["component"], 0) + \
                    token_estimate(e["output"])
        dead_like = [c for c, v in result["verdicts"].items()
                     if v in ("dead", "redundant")]
        total = sum(base.values()) or 1
        result["cost_share"] = {
            "proxy": "word count of component outputs, first 50 baseline traces",
            "per_component": base,
            "dead_or_redundant_share": round(
                sum(base.get(c, 0) for c in dead_like) / total, 4),
        }

        with open(out_path, "w") as fh:
            json.dump(result, fh, indent=2)
        print(f"[{sid}] verdicts: {result['verdicts']}"
              f"  unauditable: {result['unauditable']}")

    # Summary across audited systems.
    rows, unauditable = [], []
    for sid in BUILDERS:
        p = TR_ROOT / "results" / f"wild_{sid}.json"
        if not p.exists():
            continue
        r = json.load(open(p))
        if r.get("unauditable"):
            unauditable.append(sid)
            continue
        for comp, v in r["verdicts"].items():
            rows.append({"system": sid, "component": comp, "verdict": v})
    flagged = [r for r in rows if r["verdict"] in ("dead", "redundant")]
    n, k = len(rows), len(flagged)
    if n:
        # Wilson 95% interval on the dead-or-redundant fraction.
        z, phat = 1.96, k / n
        denom = 1 + z * z / n
        center = (phat + z * z / (2 * n)) / denom
        half = z * math.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n)) / denom
        summary = {
            "components_audited": n,
            "dead_or_redundant": k,
            "dead_fraction": round(phat, 4),
            "wilson_ci95": [round(center - half, 4), round(center + half, 4)],
            "per_component": rows,
            "unauditable_systems": unauditable,
        }
        with open(TR_ROOT / "results" / "wild_summary.json", "w") as fh:
            json.dump(summary, fh, indent=2)
        print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
