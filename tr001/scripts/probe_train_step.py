#!/usr/bin/env python3
"""Phase 2 memory and gradient-flow probe: one adapter training step
through frozen quantized Model B (D6, QLoRA configuration).

Not training. This measures peak memory and step time for the exact shape
Phase 4 will run (fp32 linear adapter, 32 soft vectors, chat-templated
question, CE loss on answer tokens), and proves gradient flow with a
negative control:

  1. Loss WITH the soft prefix: adapter gradients must be finite and
     nonzero (gradients traverse the frozen quantized model).
  2. Loss WITHOUT the soft prefix: adapter gradients must be exactly zero
     (nothing leaks into the adapter when its output is unused).

Writes results/train_step_probe.json; exit nonzero on any violation.
Sequential residency: loads Llama only; refuses to run if extraction has
not finished (the latent comes from the cache, never from a live Qwen).
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
import mlx.core as mx  # noqa: E402
import mlx.nn as nn  # noqa: E402
import mlx.optimizers as optim  # noqa: E402
from mlx.utils import tree_flatten  # noqa: E402

from lib.gates import TR_ROOT  # noqa: E402
from lib.model_b import load_b  # noqa: E402
from scripts.extract_latents import passage_hash  # noqa: E402

M_SOFT = 32


def load_one_latent():
    caches = sorted((TR_ROOT / "cache").glob("latents_*.index.json"))
    if len(caches) != 1:
        raise SystemExit(f"expected exactly one latent cache, found {len(caches)}")
    with open(caches[0]) as fh:
        idx = json.load(fh)
    stored = np.load(str(caches[0]).replace(".index.json", ".npz"))
    with open(TR_ROOT / "data" / "train.jsonl") as fh:
        for line in fh:
            row = json.loads(line)
            h = passage_hash(row["passage"])
            if h in idx["rows"]:
                return stored["final"][idx["rows"][h]], row, idx["config_hash"]
    raise SystemExit("no train row found in latent cache")


def main():
    latent_np, row, config_hash = load_one_latent()

    mx.reset_peak_memory()
    model, tokenizer = load_b()

    prompt = tokenizer.apply_chat_template(
        [{"role": "user", "content": f"Answer with a short span only.\nQuestion: {row['question']}"}],
        add_generation_prompt=True,
    )
    ans_ids = tokenizer.encode(row["answers"][0], add_special_tokens=False)
    prompt_emb = model.model.embed_tokens(mx.array(prompt)[None])
    ans_emb = model.model.embed_tokens(mx.array(ans_ids)[None])
    act_dtype = prompt_emb.dtype
    # Embedding width from an actual output: the quantized layer's stored
    # weight is packed, so its shape lies about the real dimension.
    d_b = prompt_emb.shape[-1]

    latent = mx.array(latent_np)  # fp32
    adapter = nn.Linear(latent.shape[-1], M_SOFT * d_b)  # fp32 (D6: adapter stays full precision)
    targets = mx.array(ans_ids)

    def loss_fn(ad, use_soft):
        parts = []
        if use_soft:
            soft = ad(latent).reshape(1, M_SOFT, d_b).astype(act_dtype)
            parts.append(soft)
        parts += [prompt_emb, ans_emb]
        embeds = mx.concatenate(parts, axis=1)
        dummy = mx.zeros((1, embeds.shape[1]), dtype=mx.int32)
        logits = model(dummy, input_embeddings=embeds)
        start = embeds.shape[1] - ans_emb.shape[1]
        pred = logits[0, start - 1 : start - 1 + len(ans_ids)]
        return nn.losses.cross_entropy(pred, targets, reduction="mean")

    violations = []
    grad_and_loss = nn.value_and_grad(adapter, loss_fn)

    t0 = time.time()
    loss, grads = grad_and_loss(adapter, True)
    optimizer = optim.Adam(learning_rate=1e-4)
    optimizer.update(adapter, grads)
    mx.eval(adapter.parameters(), optimizer.state, loss)
    step_seconds = time.time() - t0

    flat = [g for _, g in tree_flatten(grads)]
    grad_norm = float(mx.sqrt(sum((g.astype(mx.float32) ** 2).sum() for g in flat)).item())
    if not np.isfinite(grad_norm) or grad_norm == 0.0:
        violations.append(f"gradient flow broken: grad norm {grad_norm}")

    _, grads0 = grad_and_loss(adapter, False)
    dead_norm = float(
        mx.sqrt(sum((g.astype(mx.float32) ** 2).sum() for _, g in tree_flatten(grads0))).item()
    )
    if dead_norm != 0.0:
        violations.append(
            f"negative control broken: adapter got gradient {dead_norm} with "
            f"its output absent from the loss path"
        )

    result = {
        "config_hash": config_hash,
        "loss": round(float(loss.item()), 4),
        "grad_norm_with_soft": grad_norm,
        "grad_norm_without_soft": dead_norm,
        "step_seconds": round(step_seconds, 2),
        "peak_memory_gb": round(mx.get_peak_memory() / 2**30, 2),
        "seq_len": M_SOFT + prompt_emb.shape[1] + ans_emb.shape[1],
        "violations": violations,
    }
    with open(TR_ROOT / "results" / "train_step_probe.json", "w") as fh:
        json.dump(result, fh, indent=2)
    for v in violations:
        print(f"VIOLATION: {v}")
    print(json.dumps(result, indent=2))
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
