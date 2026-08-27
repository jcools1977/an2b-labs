#!/usr/bin/env python3
"""Supplementary placebo measurement with the 8B judge model as
paraphraser, to separate paraphrase-quality failure (238 D14-invalid
paraphrases from the 1.7B actor) from genuine cascade sensitivity.

Writes results/placebo_8b.json. NEVER touches seeded_controls.json:
this informs the ruling on the placebo leg, it does not replace the
frozen measurement.
"""
import json
import random
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TR_ROOT))

from auditor.ablate import Auditor  # noqa: E402
from auditor.judge import Judge  # noqa: E402
from auditor.lm import MLXLM  # noqa: E402
from auditor.trace import item_seed  # noqa: E402
from scripts.run_seeded import PLACEBO_COMPONENTS_PER_SYSTEM, TASK_OF  # noqa: E402
from seed_systems.systems import build_systems  # noqa: E402


def main():
    actor = MLXLM("mlx-community/Qwen3-1.7B-4bit", thinking_capable=True)
    judge_lm = MLXLM("mlx-community/Meta-Llama-3.1-8B-Instruct-4bit")
    judge = Judge(judge_lm)

    out = {}
    for sid, system in build_systems().items():
        items = [json.loads(l) for l in
                 open(TR_ROOT / "seed_systems" / "probes" / f"probes_{sid}.jsonl")]
        auditor = Auditor(system, items, actor, judge, TASK_OF[sid])
        rng = random.Random(item_seed(sid, "placebo", "pick"))
        components = rng.sample(system.component_names(),
                                min(PLACEBO_COMPONENTS_PER_SYSTEM,
                                    len(system.component_names())))
        out[sid] = auditor.placebo(
            components, rng_seed=item_seed(sid, "placebo", "boot"),
            paraphrase_lm=judge_lm, key_prefix="placebo8b",
        )
        print(sid, json.dumps(out[sid]))
        with open(TR_ROOT / "results" / "placebo_8b.json", "w") as fh:
            json.dump(out, fh, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
