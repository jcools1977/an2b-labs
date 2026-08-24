#!/usr/bin/env python3
"""Phase 3 baselines: C1 (full context, ceiling), C2 (32-token text
handoff), C4 (no context, floor). DECISIONS.md D16-D18.

Model B answers every eval question under each condition with an identical
prompt frame (only the context block varies), greedy decoding. Per D17
these conditions are deterministic and seed-independent; computed once.

Writes results/preds_{c1,c2,c4}.jsonl (per-item prediction, EM, F1) and
results/baselines.json (aggregates + 10,000-resample bootstrap CIs +
D18 expectation-band verdicts). Sequential residency: loads Llama only.
"""
import argparse
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import mlx.core as mx  # noqa: E402

from lib.gates import TR_ROOT  # noqa: E402
from lib.model_b import greedy_from_ids, load_b  # noqa: E402
from lib.scoring import score_items  # noqa: E402
from scripts.extract_latents import passage_hash  # noqa: E402

MAX_ANSWER_TOKENS = 24
BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED = 7  # split seed; eval-time bootstrap shares it (D8)

INSTRUCTION = (
    "Answer the question with the shortest exact span. "
    "Output only the answer, nothing else."
)


def build_prompt(tokenizer, question, context):
    content = INSTRUCTION
    if context is not None:
        content += f"\n\nContext:\n{context}"
    content += f"\n\nQuestion: {question}"
    return tokenizer.apply_chat_template(
        [{"role": "user", "content": content}], add_generation_prompt=True
    )


def bootstrap_ci(values, rng):
    n = len(values)
    means = sorted(
        sum(values[rng.randrange(n)] for _ in range(n)) / n
        for _ in range(BOOTSTRAP_RESAMPLES)
    )
    return [means[int(0.025 * BOOTSTRAP_RESAMPLES)], means[int(0.975 * BOOTSTRAP_RESAMPLES)]]


def run_condition(model, tokenizer, rows, context_of, name):
    preds = {}
    t0 = time.time()
    for i, row in enumerate(rows, 1):
        ids = build_prompt(tokenizer, row["question"], context_of(row))
        out_ids = greedy_from_ids(model, tokenizer, ids, MAX_ANSWER_TOKENS)
        preds[row["id"]] = tokenizer.decode(
            [t for t in out_ids if t not in set(getattr(tokenizer, "eos_token_ids", []) or [])]
        ).strip().split("\n")[0]
        if i % 100 == 0 or i == len(rows):
            print(
                f"[{name}] {i}/{len(rows)}; {(time.time()-t0)/i:.2f} s/item; "
                f"peak {mx.get_peak_memory()/2**30:.2f} GB",
                flush=True,
            )
    return preds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--conditions", default="c1,c2,c4")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    wanted = args.conditions.split(",")

    rows = [json.loads(l) for l in open(TR_ROOT / "data" / "eval.jsonl")]
    if args.limit:
        rows = rows[: args.limit]

    summaries = {}
    if "c2" in wanted:
        with open(TR_ROOT / "data" / "summaries.jsonl") as fh:
            for line in fh:
                s = json.loads(line)
                summaries[s["passage_hash"]] = s["summary_k32"]
        missing = [r["id"] for r in rows if passage_hash(r["passage"]) not in summaries]
        if missing:
            raise SystemExit(f"{len(missing)} eval rows lack summaries; run generate_summaries.py first")

    conditions = {
        "c1": lambda r: r["passage"],
        "c2": lambda r: summaries[passage_hash(r["passage"])],
        "c4": lambda r: None,
    }

    mx.reset_peak_memory()
    model, tokenizer = load_b()

    results_path = TR_ROOT / "results" / "baselines.json"
    results = json.load(open(results_path)) if results_path.exists() else {}

    for name in wanted:
        preds = run_condition(model, tokenizer, rows, conditions[name], name)
        per_item, agg = score_items(rows, preds)
        rng = random.Random(BOOTSTRAP_SEED)
        agg["f1_ci95"] = bootstrap_ci([r["f1"] for r in per_item], rng)
        agg["em_ci95"] = bootstrap_ci([r["em"] for r in per_item], rng)
        results[name] = agg
        with open(TR_ROOT / "results" / f"preds_{name}.jsonl", "w") as out:
            by_id = {r["id"]: r for r in per_item}
            for row in rows:
                item = dict(by_id[row["id"]])
                item["prediction"] = preds[row["id"]]
                out.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"[{name}] EM {agg['exact_match']:.2f}  F1 {agg['f1']:.2f}  CI95 {agg['f1_ci95']}")

    # D18 expectation bands: sanity alarms on the harness, never criteria.
    alarms = []
    if "c1" in results and results["c1"]["f1"] < 60:
        alarms.append(f"C1 F1 {results['c1']['f1']:.1f} < 60: plumbing alarm (D18)")
    if "c4" in results and results["c4"]["f1"] > 35:
        alarms.append(f"C4 F1 {results['c4']['f1']:.1f} > 35: plumbing alarm (D18)")
    results["d18_alarms"] = alarms

    with open(results_path, "w") as fh:
        json.dump(results, fh, indent=2)
    for a in alarms:
        print(f"ALARM: {a}")
    print(f"wrote {results_path}; peak {mx.get_peak_memory()/2**30:.2f} GB")
    return 1 if alarms else 0


if __name__ == "__main__":
    sys.exit(main())
