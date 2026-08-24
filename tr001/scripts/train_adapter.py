#!/usr/bin/env python3
"""Train one sweep config (DECISIONS D19-D21): exactly 2 epochs over
train_core, batch 1, Adam at the config's lr, bf16 adapter, frozen 4-bit B,
final checkpoint only. Resumable: a latest-checkpoint is overwritten every
--checkpoint-every steps and a re-run continues from it (same shuffle
order, deterministic per seed and epoch). Appends one line to
results/sweep_log.jsonl on completion.
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import mlx.core as mx  # noqa: E402
import mlx.nn as nn  # noqa: E402
import mlx.optimizers as optim  # noqa: E402
from mlx.utils import tree_flatten, tree_unflatten  # noqa: E402

from checks.check_leakage import passage_hash  # noqa: E402
from lib.adapter import build_adapter, latent_for, load_latent_cache, soft_prefix  # noqa: E402
from lib.gates import TR_ROOT  # noqa: E402
from lib.model_b import load_b  # noqa: E402
from scripts.run_baselines import build_prompt  # noqa: E402

EPOCHS = 2  # D20, uniform for every config


def get_config(config_id):
    sweep = json.load(open(TR_ROOT / "configs" / "sweep.json"))
    for c in sweep["configs"]:
        if c["id"] == config_id:
            return c
    raise SystemExit(f"unknown config id {config_id}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config-id", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--checkpoint-every", type=int, default=500)
    ap.add_argument("--limit-steps", type=int, default=0, help="smoke test only")
    args = ap.parse_args()

    config = get_config(args.config_id)
    rows = [json.loads(l) for l in open(TR_ROOT / "data" / "train_core.jsonl")]
    stored, rows_index, cache_hash = load_latent_cache(TR_ROOT)

    mx.reset_peak_memory()
    model, tokenizer = load_b()
    probe_emb = model.model.embed_tokens(mx.array([1])[None])
    d_b, act_dtype = probe_emb.shape[-1], probe_emb.dtype
    eos_id = tokenizer.eos_token_id

    in_dim = 4096 if config["pooling"] == "final" else 4 * 4096
    adapter = build_adapter(config, in_dim, d_b)
    optimizer = optim.Adam(learning_rate=config["lr"])

    ckpt_dir = TR_ROOT / "checkpoints"
    ckpt_dir.mkdir(exist_ok=True)
    tag = f"{args.config_id}_seed{args.seed}"
    ckpt_weights = ckpt_dir / f"{tag}.latest.safetensors"
    ckpt_state = ckpt_dir / f"{tag}.latest.json"

    start_epoch = start_step = 0
    if ckpt_weights.exists() and ckpt_state.exists():
        state = json.load(open(ckpt_state))
        if state["config"] == config and state["cache_hash"] == cache_hash:
            adapter.update(tree_unflatten(list(mx.load(str(ckpt_weights)).items())))
            start_epoch, start_step = state["epoch"], state["step"]
            print(f"resuming {tag} at epoch {start_epoch} step {start_step}")
        else:
            raise SystemExit("CHECKPOINT CONFLICT: config or cache changed; delete checkpoint")

    def loss_fn(ad, latent_np, prompt_ids, ans_ids):
        soft = soft_prefix(ad, latent_np, d_b, act_dtype)
        prompt_emb = model.model.embed_tokens(mx.array(prompt_ids)[None])
        ans_emb = model.model.embed_tokens(mx.array(ans_ids)[None])
        embeds = mx.concatenate([soft, prompt_emb, ans_emb], axis=1)
        dummy = mx.zeros((1, embeds.shape[1]), dtype=mx.int32)
        logits = model(dummy, input_embeddings=embeds)
        start = embeds.shape[1] - len(ans_ids)
        pred = logits[0, start - 1 : start - 1 + len(ans_ids)]
        return nn.losses.cross_entropy(pred, mx.array(ans_ids), reduction="mean")

    grad_and_loss = nn.value_and_grad(adapter, loss_fn)

    t0, steps_done, recent = time.time(), 0, []
    import random as _random

    for epoch in range(start_epoch, EPOCHS):
        order = list(range(len(rows)))
        _random.Random(args.seed * 1000 + epoch).shuffle(order)
        for k, ri in enumerate(order):
            if epoch == start_epoch and k < start_step:
                continue
            row = rows[ri]
            latent_np = latent_for(stored, rows_index, config["pooling"], passage_hash(row["passage"]))
            prompt_ids = build_prompt(tokenizer, row["question"], None)  # C4 frame + soft prefix
            ans_ids = tokenizer.encode(row["answers"][0], add_special_tokens=False) + [eos_id]
            loss, grads = grad_and_loss(adapter, latent_np, prompt_ids, ans_ids)
            optimizer.update(adapter, grads)
            mx.eval(adapter.parameters(), optimizer.state, loss)
            recent.append(float(loss.item()))
            recent = recent[-100:]
            steps_done += 1
            if steps_done % args.checkpoint_every == 0:
                mx.save_safetensors(str(ckpt_weights), dict(tree_flatten(adapter.parameters())))
                json.dump(
                    {"config": config, "cache_hash": cache_hash, "epoch": epoch, "step": k + 1},
                    open(ckpt_state, "w"),
                )
                print(
                    f"[{tag}] epoch {epoch} step {k+1}/{len(order)}; "
                    f"loss(100) {sum(recent)/len(recent):.3f}; "
                    f"{(time.time()-t0)/steps_done:.2f} s/step; "
                    f"peak {mx.get_peak_memory()/2**30:.2f} GB",
                    flush=True,
                )
            if args.limit_steps and steps_done >= args.limit_steps:
                print("smoke-test limit reached; not saving a final adapter")
                return 0
        start_step = 0

    adapters_dir = TR_ROOT / "adapters"
    adapters_dir.mkdir(exist_ok=True)
    final_path = adapters_dir / f"{tag}.safetensors"
    mx.save_safetensors(str(final_path), dict(tree_flatten(adapter.parameters())))

    entry = {
        "config_id": args.config_id,
        "seed": args.seed,
        "config": config,
        "cache_hash": cache_hash,
        "epochs": EPOCHS,
        "steps": steps_done + (start_epoch * len(rows) + (start_step or 0)),
        "final_loss_mean100": round(sum(recent) / max(len(recent), 1), 4),
        "wall_seconds": round(time.time() - t0, 1),
        "peak_memory_gb": round(mx.get_peak_memory() / 2**30, 2),
        "adapter_path": str(final_path.relative_to(TR_ROOT)),
    }
    with open(TR_ROOT / "results" / "sweep_log.jsonl", "a") as fh:
        fh.write(json.dumps(entry) + "\n")
    print(json.dumps(entry, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
