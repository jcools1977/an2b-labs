#!/usr/bin/env python3
"""Negative controls 1-3 on the held-out set (protocol section 8), run as
part of the single post-selection eval batch for one seed, alongside the
C3 headline. Control 4 (leakage) is data-side and lives in verify.sh.

1. Random adapter: fresh seeded init, correct latents. Must collapse
   toward the C4 floor or B is answering from priors.
2. Shuffled pairing: trained adapter, latents from a different passage
   (deterministic derangement: rotation by one in sorted unique-hash
   order). Must collapse or the soft prompt is a generic instruction.
3. Ablation: no soft prefix at inference on the trained adapter's eval
   path (prompt embeddings only through the injection code path). Delta
   must roughly equal the C3-over-C4 margin; in this design the ablated
   run is C4's prompt through C3's code path, so it also cross-checks the
   two generation paths against each other on the full eval workload.

Requires the seed's selection record and the C3 headline result to exist.
Writes results/controls_seed<N>.json in the schema check_controls.py has
enforced (red-then-green) since Phase 0.
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import mlx.core as mx  # noqa: E402
from mlx.utils import tree_unflatten  # noqa: E402

from checks.check_leakage import passage_hash  # noqa: E402
from lib.adapter import K_TEXT_TOKENS, M_SOFT, build_adapter, latent_for, load_latent_cache, soft_prefix  # noqa: E402
from lib.gates import TR_ROOT  # noqa: E402
from lib.model_b import greedy_from_embeddings, load_b  # noqa: E402
from lib.scoring import score_items  # noqa: E402
from scripts.run_baselines import MAX_ANSWER_TOKENS, build_prompt  # noqa: E402
from scripts.train_adapter import get_config  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    args = ap.parse_args()

    sel_path = TR_ROOT / "results" / f"selection_seed{args.seed}.json"
    c3_path = TR_ROOT / "results" / f"c3_seed{args.seed}.json"
    if not sel_path.exists() or not c3_path.exists():
        raise SystemExit("controls run after selection and the C3 headline, not before")
    sel = json.load(open(sel_path))
    config = get_config(sel["config_id"])
    c3_f1 = json.load(open(c3_path))["f1"]
    c4_f1 = json.load(open(TR_ROOT / "results" / "baselines.json"))["c4"]["f1"]

    rows = [json.loads(l) for l in open(TR_ROOT / "data" / "eval.jsonl")]
    stored, rows_index, _ = load_latent_cache(TR_ROOT)

    mx.reset_peak_memory()
    model, tokenizer = load_b()
    probe_emb = model.model.embed_tokens(mx.array([1])[None])
    d_b, act_dtype = probe_emb.shape[-1], probe_emb.dtype
    in_dim = 4096 if config["pooling"] == "final" else 4 * 4096

    trained = build_adapter(config, in_dim, d_b)
    trained.update(tree_unflatten(list(mx.load(
        str(TR_ROOT / "adapters" / f"{sel['config_id']}_seed{args.seed}.safetensors")
    ).items())))

    mx.random.seed(args.seed * 4242)
    random_adapter = build_adapter(config, in_dim, d_b)  # frozen at fresh init

    hashes = sorted({passage_hash(r["passage"]) for r in rows})
    derange = {h: hashes[(i + 1) % len(hashes)] for i, h in enumerate(hashes)}

    def run_mode(name, adapter, latent_hash_of):
        preds = {}
        t0 = time.time()
        eos = set(getattr(tokenizer, "eos_token_ids", []) or [tokenizer.eos_token_id])
        for i, row in enumerate(rows, 1):
            prompt_emb = model.model.embed_tokens(
                mx.array(build_prompt(tokenizer, row["question"], None))[None]
            )
            if adapter is None:
                embeds = prompt_emb  # ablation: C4's prompt through C3's path
            else:
                latent_np = latent_for(
                    stored, rows_index, config["pooling"], latent_hash_of(row)
                )
                embeds = mx.concatenate(
                    [soft_prefix(adapter, latent_np, d_b, act_dtype), prompt_emb], axis=1
                )
            out_ids = greedy_from_embeddings(model, tokenizer, embeds, MAX_ANSWER_TOKENS)
            preds[row["id"]] = tokenizer.decode(
                [t for t in out_ids if t not in eos]
            ).strip().split("\n")[0]
            if i % 100 == 0 or i == len(rows):
                print(f"[{name}] {i}/{len(rows)}; {(time.time()-t0)/i:.2f} s/item", flush=True)
        per_item, agg = score_items(rows, preds)
        with open(TR_ROOT / "results" / f"preds_control_{name}_seed{args.seed}.jsonl", "w") as fh:
            by_id = {r["id"]: r for r in per_item}
            for row in rows:
                item = dict(by_id[row["id"]])
                item["prediction"] = preds[row["id"]]
                fh.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"[{name}] F1 {agg['f1']:.2f} EM {agg['exact_match']:.2f}")
        return agg["f1"]

    own = lambda row: passage_hash(row["passage"])
    result = {
        "seed": args.seed,
        "config": {"M": M_SOFT, "K": K_TEXT_TOKENS},
        "f1": {
            "c3_latent_handoff": c3_f1,
            "c4_no_context": c4_f1,
            "control_random_adapter": run_mode("random", random_adapter, own),
            "control_shuffled_pairing": run_mode(
                "shuffled", trained, lambda row: derange[passage_hash(row["passage"])]
            ),
            "control_ablated_soft_prompt": run_mode("ablated", None, own),
        },
    }
    out = TR_ROOT / "results" / f"controls_seed{args.seed}.json"
    json.dump(result, open(out, "w"), indent=2)
    print(json.dumps(result, indent=2))
    print(f"peak {mx.get_peak_memory()/2**30:.2f} GB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
