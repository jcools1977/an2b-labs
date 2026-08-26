#!/usr/bin/env python3
"""Seeded-phase audit (protocol ground-truth phase; D1, D7, D16).

Runs the auditor over all seven systems with the pinned models, writes:
- results/seeded_detail.json  (full per-component effects, pairs, halves)
- results/seeded_controls.json (all-live flags, placebo aggregate,
  replication agreement across all systems)
Never touches the seal; scoring against it is scripts/score_recovery.py.

Checkpointed per system: an interrupted run resumes at the next system.
--limit N (smoke) audits N probe items per system with the stub LM.
"""
import argparse
import json
import random
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TR_ROOT))

from auditor.ablate import Auditor  # noqa: E402
from auditor.judge import Judge  # noqa: E402
from auditor.trace import item_seed  # noqa: E402
from seed_systems.systems import build_systems  # noqa: E402

TASK_OF = {
    "s1_research_brief": lambda it: f"Write a brief on {it['topic']}",
    "s2_rag_qa": lambda it: f"Answer: {it['question']}",
    "s3_math_tools": lambda it: f"Compute {it['expression']}",
    "s4_committee": lambda it: f"Give a verdict on: {it['question']}",
    "s5_plan_exec": lambda it: f"Alphabetize: {', '.join(it['words'])}",
    "s6_support_triage": lambda it: f"Reply to this support ticket: {it['ticket']}",
    "s7_all_live_qa": lambda it: f"Answer: {it['question']}",
}
PLACEBO_COMPONENTS_PER_SYSTEM = 2  # D16


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="smoke: stub LM, N items")
    args = ap.parse_args()

    if args.limit:
        from auditor.lm import StubLM

        lm = judge_lm = StubLM()
    else:
        from auditor.lm import MLXLM

        lm = MLXLM("mlx-community/Qwen3-1.7B-4bit", thinking_capable=True)
        judge_lm = MLXLM("mlx-community/Meta-Llama-3.1-8B-Instruct-4bit")
    judge = Judge(judge_lm)

    import os
    out_dir = TR_ROOT / "results"
    if args.limit:  # smoke runs never pollute results/
        out_dir = Path(os.environ.get("TMPDIR", "/tmp"))
    detail_path = out_dir / "seeded_detail.json"
    detail = json.load(open(detail_path)) if detail_path.exists() and not args.limit else {}

    systems = build_systems()
    for sid, system in systems.items():
        if sid in detail:
            print(f"[{sid}] already audited, skipping")
            continue
        items = [json.loads(l) for l in
                 open(TR_ROOT / "seed_systems" / "probes" / f"probes_{sid}.jsonl")]
        if args.limit:
            items = items[: args.limit]
        auditor = Auditor(system, items, lm, judge, TASK_OF[sid])
        result = auditor.audit()
        rng = random.Random(item_seed(sid, "placebo", "pick"))
        placebo_components = rng.sample(system.component_names(),
                                        min(PLACEBO_COMPONENTS_PER_SYSTEM,
                                            len(system.component_names())))
        result["placebo"] = auditor.placebo(
            placebo_components, rng_seed=item_seed(sid, "placebo", "boot")
        )
        detail[sid] = result
        with open(detail_path, "w") as fh:
            json.dump(detail, fh, indent=2)
        print(f"[{sid}] verdicts: {result['verdicts']}")

    # Controls aggregate (checker schema).
    all_live = detail["s7_all_live_qa"]["verdicts"]
    flags = sum(1 for v in all_live.values() if v != "live")
    rates = [detail[s]["placebo"]["answer_change_rate"] for s in detail]
    cis = [detail[s]["placebo"]["quality_ci"] for s in detail]
    controls = {
        "all_live_flags": flags,
        "placebo": {
            "answer_change_rate": round(sum(rates) / len(rates), 4),
            "quality_ci": [round(min(c[0] for c in cis), 3),
                           round(max(c[1] for c in cis), 3)],
            "invalid_paraphrases": sum(
                detail[s]["placebo"]["invalid_paraphrases"] for s in detail),
        },
        "replication_agreement": round(
            sum(detail[s]["replication"]["agreement"] * len(detail[s]["verdicts"])
                for s in detail)
            / sum(len(detail[s]["verdicts"]) for s in detail), 4),
    }
    with open(out_dir / "seeded_controls.json", "w") as fh:
        json.dump(controls, fh, indent=2)
    print(json.dumps(controls, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
