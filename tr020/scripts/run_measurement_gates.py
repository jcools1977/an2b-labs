#!/usr/bin/env python3
"""Produce results/measurement_gates.json (DECISIONS D3, D13, D15).

Canonicalizer leg runs anywhere (pure). Judge leg needs the pinned
judge model (--with-judge, legion). Refuses to run at all while the
fixtures are unratified: an unratified gate must not even generate the
numbers it would be judged green by.
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TR_ROOT))

from auditor.canon import CANON  # noqa: E402
from checks.check_ratification import check as ratification_check  # noqa: E402


def canon_results():
    per_family = defaultdict(lambda: {"n": 0, "match": 0})
    with open(TR_ROOT / "fixtures" / "canon_pairs.jsonl") as fh:
        for line in fh:
            row = json.loads(line)
            fam = row["family"]
            predicted = "change" if CANON[fam](row["a"]) != CANON[fam](row["b"]) else "no-change"
            per_family[fam]["n"] += 1
            per_family[fam]["match"] += predicted == row["label"]
    out = {}
    for fam, d in per_family.items():
        out[fam] = {"match_rate": round(d["match"] / d["n"], 4), "n": d["n"]}
        mism = d["n"] - d["match"]
        print(f"canon[{fam}]: {d['match']}/{d['n']} match" + (f"  ({mism} MISMATCH)" if mism else ""))
    return out


def judge_results():
    from auditor.judge import Judge
    from auditor.lm import MLXLM

    judge = Judge(MLXLM("mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"))
    rows = [json.loads(l) for l in open(TR_ROOT / "fixtures" / "judge_damage.jsonl")]
    intact_scores, degraded = [], defaultdict(list)
    for i, row in enumerate(rows):
        si = judge.score(row["task"], row["intact"], seed=1000 + i)
        sd = judge.score(row["task"], row["damaged"], seed=2000 + i)
        if si is None or sd is None:
            raise SystemExit(f"judge error on fixture {i}: unparseable score")
        intact_scores.append(si)
        degraded[row["damage_class"]].append(sd)
    result = {
        "intact_mean": round(sum(intact_scores) / len(intact_scores), 3),
        "degraded_means": {
            cls: round(sum(v) / len(v), 3) for cls, v in degraded.items()
        },
    }
    print("judge:", json.dumps(result))
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--with-judge", action="store_true")
    args = ap.parse_args()

    violations = ratification_check(TR_ROOT / "fixtures")
    if violations:
        for v in violations:
            print(f"REFUSING TO RUN: {v}")
        return 1

    out_path = TR_ROOT / "results" / "measurement_gates.json"
    result = json.load(open(out_path)) if out_path.exists() else {}
    result["canonicalizer"] = {"families": canon_results()}
    if args.with_judge:
        result["judge"] = judge_results()
    with open(out_path, "w") as fh:
        json.dump(result, fh, indent=2)
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
