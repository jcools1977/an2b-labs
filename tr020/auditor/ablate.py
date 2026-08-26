"""The ablation engine (protocol design; DECISIONS D1, D7, D14).

Pure measurement: this module never sees the seal. For one system and
its probe set it produces per-component verdicts (dead / redundant /
live), the pairwise interaction sample, the per-half replication
verdicts, and optionally the placebo aggregate.

Dead criterion (frozen): canonicalized answer-change rate < 5% AND
judged-quality delta CI (95% bootstrap, paired) includes zero.
Taxonomy (D1): no effect alone -> pairwise with other no-effect
partners; joint effect reclassifies the pair as redundant; no joint
effect anywhere leaves it dead. Any solo effect is live.
"""
import itertools
import random

from .canon import CANON, FAMILY_OF_SYSTEM
from .placebo import paraphrase_output
from .trace import item_seed

CHANGE_RATE_MAX = 0.05
BOOTSTRAP = 2000
PAIR_EXTRA_SAMPLE = 5


def _ci(deltas, rng):
    if not deltas:
        return [0.0, 0.0]
    n = len(deltas)
    means = sorted(
        sum(deltas[rng.randrange(n)] for _ in range(n)) / n for _ in range(BOOTSTRAP)
    )
    return [means[int(0.025 * BOOTSTRAP)], means[int(0.975 * BOOTSTRAP)]]


def _no_effect(rate, ci):
    return rate < CHANGE_RATE_MAX and ci[0] <= 0.0 <= ci[1]


class Auditor:
    def __init__(self, system, items, lm, judge, task_of):
        self.system, self.items, self.lm, self.judge = system, items, lm, judge
        self.task_of = task_of  # item -> task description for the judge
        self.canon = CANON[FAMILY_OF_SYSTEM[system.system_id]]
        self._answers = {}  # mask_key -> {item_id: answer}

    def _answers_for(self, mask=None, mask_fn=None, key=None):
        key = key or (tuple(sorted(mask)) if isinstance(mask, (list, tuple, set))
                      else mask)
        if key not in self._answers:
            out = {}
            for it in self.items:
                out[it["id"]], _ = self.system.run(it, self.lm, mask=mask, mask_fn=mask_fn)
            self._answers[key] = out
        return self._answers[key]

    def _judge_scores(self, answers):
        scores = {}
        for it in self.items:
            s = self.judge.score(
                self.task_of(it), answers[it["id"]],
                seed=item_seed(self.system.system_id, it["id"], "judge"),
            )
            if s is not None:
                scores[it["id"]] = s
        return scores

    def _effect(self, base_answers, base_scores, mask, mask_fn=None, items=None, key=None):
        items = items or self.items
        answers = self._answers_for(mask=mask, mask_fn=mask_fn, key=key)
        changes = [
            self.canon(answers[it["id"]]) != self.canon(base_answers[it["id"]])
            for it in items
        ]
        rate = sum(changes) / len(items)
        scores = self._judge_scores(answers)
        deltas = [scores[i] - base_scores[i] for i in scores if i in base_scores]
        rng = random.Random(item_seed(self.system.system_id, str(mask), "boot"))
        ci = _ci(deltas, rng)
        return {"change_rate": round(rate, 4), "quality_ci": [round(x, 3) for x in ci],
                "n_judged": len(deltas)}

    def audit(self):
        base_answers = self._answers_for(key="__baseline__")
        base_scores = self._judge_scores(base_answers)

        names = self.system.component_names()
        solo = {}
        for name in names:
            solo[name] = self._effect(base_answers, base_scores, name)
            solo[name]["no_effect_alone"] = _no_effect(
                solo[name]["change_rate"], solo[name]["quality_ci"]
            )

        # Pairwise: all pairs among no-effect components (drives the D1
        # taxonomy) plus a seeded sample of other pairs (interaction bound).
        quiet = [n for n in names if solo[n]["no_effect_alone"]]
        pairs = list(itertools.combinations(sorted(quiet), 2))
        others = [p for p in itertools.combinations(sorted(names), 2) if p not in pairs]
        rng = random.Random(item_seed(self.system.system_id, "pairs", "sample"))
        pair_list = pairs + (rng.sample(others, min(PAIR_EXTRA_SAMPLE, len(others))))

        pair_results = []
        joint_effect_with = {n: [] for n in names}
        for a, b in pair_list:
            eff = self._effect(base_answers, base_scores, (a, b))
            joint = not _no_effect(eff["change_rate"], eff["quality_ci"])
            pair_results.append({"pair": [a, b], **eff, "joint_effect": joint})
            if joint and a in quiet and b in quiet:
                joint_effect_with[a].append(b)
                joint_effect_with[b].append(a)

        verdicts = {}
        for n in names:
            if not solo[n]["no_effect_alone"]:
                verdicts[n] = "live"
            elif joint_effect_with[n]:
                verdicts[n] = "redundant"
            else:
                verdicts[n] = "dead"

        # Replication (D7): identical three-class verdict on each probe half.
        halves = [self.items[: len(self.items) // 2], self.items[len(self.items) // 2:]]
        half_verdicts = []
        for half in halves:
            hv = {}
            for n in names:
                eff = self._effect(base_answers, base_scores, n, items=half)
                quiet_h = _no_effect(eff["change_rate"], eff["quality_ci"])
                if not quiet_h:
                    hv[n] = "live"
                elif joint_effect_with[n]:
                    hv[n] = "redundant"
                else:
                    hv[n] = "dead"
            half_verdicts.append(hv)
        agree = sum(
            1 for n in names if half_verdicts[0][n] == half_verdicts[1][n] == verdicts[n]
        )

        return {
            "system": self.system.system_id,
            "verdicts": verdicts,
            "solo": solo,
            "pairs": pair_results,
            "replication": {
                "agreement": round(agree / len(names), 4),
                "halves": half_verdicts,
            },
            "baseline_judge_mean": round(
                sum(base_scores.values()) / max(len(base_scores), 1), 3
            ),
        }

    def placebo(self, components, rng_seed):
        """Placebo control on the given components: paraphrase-mask each,
        aggregate change rate and quality CI (D14 bounds enforced)."""
        base_answers = self._answers_for(key="__baseline__")
        base_scores = self._judge_scores(base_answers)
        rates, deltas, invalid = [], [], 0

        for name in components:
            logs = {}

            def mask_fn(output, ctx, _logs=logs):
                out, log = paraphrase_output(self.lm, output, ctx.seed)
                _logs[ctx.seed] = log
                return out if out is not None else output

            eff = self._effect(
                base_answers, base_scores, name, mask_fn=mask_fn, key=f"placebo:{name}"
            )
            invalid += sum(1 for l in logs.values() if not l.get("valid", True))
            rates.append(eff["change_rate"])
            answers = self._answers_for(mask=name, mask_fn=mask_fn, key=f"placebo:{name}")
            scores = self._judge_scores(answers)
            deltas += [scores[i] - base_scores[i] for i in scores if i in base_scores]

        rng = random.Random(rng_seed)
        return {
            "answer_change_rate": round(sum(rates) / max(len(rates), 1), 4),
            "quality_ci": [round(x, 3) for x in _ci(deltas, rng)],
            "invalid_paraphrases": invalid,
            "components": list(components),
        }
