#!/usr/bin/env python3
"""C2 summary generation (DECISIONS.md D16, D17).

Model A summarizes each unique EVAL passage, question-blind, greedy, chat
template with thinking disabled. The summary is then hard-capped at K=32
tokens of Model B's tokenizer (the pricing ruler), by truncation after
generation. Sequential residency: loads Qwen only; B's tokenizer hash is
taken from MANIFEST, not from a loaded B.

Writes data/summaries.jsonl: {passage_hash, summary_raw, summary_k32,
k_tokens}. Deterministic: greedy decoding, fixed prompt.
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import mlx.core as mx  # noqa: E402
from mlx_lm import load as mlx_load  # noqa: E402
from mlx_lm.models.cache import make_prompt_cache  # noqa: E402

from lib.gates import A_REPO, TR_ROOT, manifest, pinned_snapshot, vocab_sha256  # noqa: E402
from scripts.extract_latents import passage_hash  # noqa: E402

K_TOKENS = 32
GEN_CAP = 120  # generous; the hard cap is applied in B tokens afterward

PROMPT = (
    "Summarize the following passage in two dense sentences. Preserve the "
    "most important names, dates, numbers, and facts. Output only the "
    "summary.\n\nPassage:\n{passage}"
)


def greedy_text(model, tokenizer, ids, max_tokens):
    cache = make_prompt_cache(model)
    logits = model(mx.array(ids)[None], cache=cache)
    eos = set(getattr(tokenizer, "eos_token_ids", None) or [tokenizer.eos_token_id])
    out = []
    y = mx.argmax(logits[:, -1, :], axis=-1)
    for _ in range(max_tokens):
        t = int(y.item())
        if t in eos:
            break
        out.append(t)
        logits = model(y[None], cache=cache)
        y = mx.argmax(logits[:, -1, :], axis=-1)
    return tokenizer.decode(out).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    # B's tokenizer for the hard cap, loaded standalone from the pinned B
    # snapshot's tokenizer files (no B model weights; Qwen stays the only
    # resident model). Gate: its vocab hash must match MANIFEST.
    from transformers import AutoTokenizer

    b_snap, _ = pinned_snapshot("mlx-community/Meta-Llama-3.1-8B-Instruct-4bit")
    tok_b = AutoTokenizer.from_pretrained(str(b_snap))
    if vocab_sha256(tok_b) != manifest()["tokenizer"]["vocab_sha256"]:
        raise SystemExit("TOKENIZER GATE: B tokenizer hash mismatch in summarizer")

    passages = {}
    with open(TR_ROOT / "data" / "eval.jsonl") as fh:
        for line in fh:
            row = json.loads(line)
            passages.setdefault(passage_hash(row["passage"]), row["passage"])
    items = sorted(passages.items())
    if args.limit:
        items = items[: args.limit]

    snap, pin = pinned_snapshot(A_REPO)
    print(f"loading {A_REPO} @ {pin[:12]}")
    mx.reset_peak_memory()
    model, tokenizer = mlx_load(str(snap))

    out_path = TR_ROOT / "data" / "summaries.jsonl"
    t0 = time.time()
    with open(out_path, "w") as out:
        for i, (h, passage) in enumerate(items, 1):
            ids = tokenizer.apply_chat_template(
                [{"role": "user", "content": PROMPT.format(passage=passage)}],
                add_generation_prompt=True,
                enable_thinking=False,  # D16: no hidden reasoning block
            )
            raw = greedy_text(model, tokenizer, ids, GEN_CAP)
            b_ids = tok_b.encode(raw, add_special_tokens=False)[:K_TOKENS]
            out.write(
                json.dumps(
                    {
                        "passage_hash": h,
                        "summary_raw": raw,
                        "summary_k32": tok_b.decode(b_ids),
                        "k_tokens": len(b_ids),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            if i % 50 == 0 or i == len(items):
                print(
                    f"{i}/{len(items)} summaries; "
                    f"{(time.time()-t0)/i:.1f} s each; "
                    f"peak {mx.get_peak_memory()/2**30:.2f} GB",
                    flush=True,
                )
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
