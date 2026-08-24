#!/usr/bin/env python3
"""C3 evaluation for one trained config (DECISIONS D19).

--split dev: score the config on the dev split; writes
  results/dev_<config>_seed<seed>.json. This is the ONLY split configs are
  selected on.
--split eval: the held-out 500, touched once per seed. Refuses to run
  unless results/selection_seed<seed>.json exists and names this exact
  config (structural guard). Writes results/preds_c3_seed<seed>.jsonl and
  results/c3_seed<seed>.json.
"""
import argparse
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import mlx.core as mx  # noqa: E402
from mlx.utils import tree_unflatten  # noqa: E402

from checks.check_leakage import passage_hash  # noqa: E402
from lib.adapter import M_SOFT, build_adapter, latent_for, load_latent_cache, soft_prefix  # noqa: E402
from lib.gates import TR_ROOT  # noqa: E402
from lib.model_b import greedy_from_embeddings, load_b  # noqa: E402
from lib.scoring import score_items  # noqa: E402
from scripts.run_baselines import BOOTSTRAP_SEED, MAX_ANSWER_TOKENS, bootstrap_ci, build_prompt  # noqa: E402
from scripts.train_adapter import get_config  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config-id", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--split", choices=["dev", "eval"], required=True)
    args = ap.parse_args()

    if args.split == "eval":
        sel_path = TR_ROOT / "results" / f"selection_seed{args.seed}.json"
        if not sel_path.exists():
            raise SystemExit(
                "EVAL GUARD (D19): no selection record; the held-out 500 is "
                "only touched by the selected config, after selection."
            )
        sel = json.load(open(sel_path))
        if sel["config_id"] != args.config_id:
            raise SystemExit(
                f"EVAL GUARD (D19): selection names {sel['config_id']}, "
                f"not {args.config_id}."
            )

    config = get_config(args.config_id)
    rows = [json.loads(l) for l in open(TR_ROOT / "data" / f"{args.split}.jsonl")]
    stored, rows_index, cache_hash = load_latent_cache(TR_ROOT)

    tag = f"{args.config_id}_seed{args.seed}"
    weights_path = TR_ROOT / "adapters" / f"{tag}.safetensors"
    if not weights_path.exists():
        raise SystemExit(f"no trained adapter at {weights_path}")

    mx.reset_peak_memory()
    model, tokenizer = load_b()
    probe_emb = model.model.embed_tokens(mx.array([1])[None])
    d_b, act_dtype = probe_emb.shape[-1], probe_emb.dtype

    in_dim = 4096 if config["pooling"] == "final" else 4 * 4096
    adapter = build_adapter(config, in_dim, d_b)
    adapter.update(tree_unflatten(list(mx.load(str(weights_path)).items())))

    preds = {}
    t0 = time.time()
    for i, row in enumerate(rows, 1):
        latent_np = latent_for(stored, rows_index, config["pooling"], passage_hash(row["passage"]))
        soft = soft_prefix(adapter, latent_np, d_b, act_dtype)
        prompt_emb = model.model.embed_tokens(mx.array(build_prompt(tokenizer, row["question"], None))[None])
        embeds = mx.concatenate([soft, prompt_emb], axis=1)
        out_ids = greedy_from_embeddings(model, tokenizer, embeds, MAX_ANSWER_TOKENS)
        eos = set(getattr(tokenizer, "eos_token_ids", []) or [tokenizer.eos_token_id])
        preds[row["id"]] = tokenizer.decode([t for t in out_ids if t not in eos]).strip().split("\n")[0]
        if i % 100 == 0 or i == len(rows):
            print(f"[{tag}/{args.split}] {i}/{len(rows)}; {(time.time()-t0)/i:.2f} s/item", flush=True)

    per_item, agg = score_items(rows, preds)
    agg.update({"config_id": args.config_id, "seed": args.seed, "split": args.split,
                "M": M_SOFT, "K": 32, "cache_hash": cache_hash})

    if args.split == "dev":
        out = TR_ROOT / "results" / f"dev_{args.config_id}_seed{args.seed}.json"
        json.dump(agg, open(out, "w"), indent=2)
    else:
        rng = random.Random(BOOTSTRAP_SEED)
        agg["f1_ci95"] = bootstrap_ci([r["f1"] for r in per_item], rng)
        agg["em_ci95"] = bootstrap_ci([r["em"] for r in per_item], rng)
        with open(TR_ROOT / "results" / f"preds_c3_seed{args.seed}.jsonl", "w") as fh:
            by_id = {r["id"]: r for r in per_item}
            for row in rows:
                item = dict(by_id[row["id"]])
                item["prediction"] = preds[row["id"]]
                fh.write(json.dumps(item, ensure_ascii=False) + "\n")
        out = TR_ROOT / "results" / f"c3_seed{args.seed}.json"
        json.dump(agg, open(out, "w"), indent=2)

    print(json.dumps(agg, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
