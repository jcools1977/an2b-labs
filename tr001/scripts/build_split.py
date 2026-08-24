#!/usr/bin/env python3
"""Build the TR-001 train/eval split from raw SQuAD v1.1 (DECISIONS.md D5,
D8, D9a, D11).

Training pairs from train-v1.1.json, eval pairs from dev-v1.1.json (disjoint
Wikipedia articles). Passages filtered to 200-400 Model B tokens, deduplicated
by normalized hash within each side, capped at 2 questions per passage.
Deterministic under --seed. Writes train.jsonl, eval.jsonl, MANIFEST.json,
then refuses to finish if any train passage hash appears in the eval set.
"""
import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from checks.check_leakage import normalize  # single source of truth (D9a)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def passage_hash(text):
    return hashlib.sha256(normalize(text).encode("utf-8")).hexdigest()


def load_squad(path):
    """Yield (passage, [(qid, question, [answer_texts]), ...]) per paragraph."""
    with open(path) as fh:
        data = json.load(fh)
    for article in data["data"]:
        for para in article["paragraphs"]:
            qas = [
                (qa["id"], qa["question"], [a["text"] for a in qa["answers"]])
                for qa in para["qas"]
                if qa["answers"]
            ]
            if qas:
                yield para["context"], qas


def build_side(raw_path, tok, rng, n_pairs, min_tok, max_tok, max_q, exclude_hashes):
    """Return (rows, passage_hashes) for one side of the split."""
    candidates = []
    seen = set(exclude_hashes)
    for passage, qas in load_squad(raw_path):
        ph = passage_hash(passage)
        if ph in seen:
            continue
        seen.add(ph)
        n = len(tok(passage, add_special_tokens=False)["input_ids"])
        if min_tok <= n <= max_tok:
            candidates.append((passage, ph, n, qas))

    rng.shuffle(candidates)
    rows, used_hashes = [], set()
    for passage, ph, n_tokens, qas in candidates:
        if len(rows) >= n_pairs:
            break
        qas = list(qas)
        rng.shuffle(qas)
        for qid, question, answers in qas[:max_q]:
            if len(rows) >= n_pairs:
                break
            rows.append(
                {
                    "id": qid,
                    "passage": passage,
                    "question": question,
                    "answers": answers,
                    "passage_tokens": n_tokens,
                }
            )
            used_hashes.add(ph)
    return rows, used_hashes, len(candidates)


def write_jsonl(path, rows):
    with open(path, "w") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train-json", default="data/raw/train-v1.1.json")
    ap.add_argument("--dev-json", default="data/raw/dev-v1.1.json")
    ap.add_argument("--tokenizer", default="unsloth/Meta-Llama-3.1-8B-Instruct")
    ap.add_argument("--out-dir", default="data")
    ap.add_argument("--n-train", type=int, default=2000)
    ap.add_argument("--n-eval", type=int, default=500)
    ap.add_argument("--min-tokens", type=int, default=200)
    ap.add_argument("--max-tokens", type=int, default=400)
    ap.add_argument("--max-q-per-passage", type=int, default=2)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(args.tokenizer)
    vocab_hash = hashlib.sha256(
        json.dumps(tok.get_vocab(), sort_keys=True).encode("utf-8")
    ).hexdigest()

    rng = random.Random(args.seed)
    out = Path(args.out_dir)

    # Eval first, from dev; then train, excluding every eval passage hash.
    eval_rows, eval_hashes, eval_cand = build_side(
        args.dev_json, tok, rng, args.n_eval,
        args.min_tokens, args.max_tokens, args.max_q_per_passage, set(),
    )
    train_rows, train_hashes, train_cand = build_side(
        args.train_json, tok, rng, args.n_train,
        args.min_tokens, args.max_tokens, args.max_q_per_passage, eval_hashes,
    )

    if len(eval_rows) < args.n_eval or len(train_rows) < args.n_train:
        print(
            f"FATAL: not enough qualifying pairs "
            f"(eval {len(eval_rows)}/{args.n_eval}, train {len(train_rows)}/{args.n_train})"
        )
        return 1
    if train_hashes & eval_hashes:
        print("FATAL: split builder produced overlapping passage hashes")
        return 1

    write_jsonl(out / "eval.jsonl", eval_rows)
    write_jsonl(out / "train.jsonl", train_rows)

    # Preserve keys owned by other tools (e.g. "models" from
    # record_model_revisions.py, D13) across split rebuilds.
    manifest_path = out / "MANIFEST.json"
    manifest = {}
    if manifest_path.exists():
        with open(manifest_path) as fh:
            manifest = json.load(fh)
    manifest.update({
        "built": "phase 1",
        "seed": args.seed,
        "raw_files": {
            "train-v1.1.json": {
                "url": "https://rajpurkar.github.io/SQuAD-explorer/dataset/train-v1.1.json",
                "sha256": sha256_file(args.train_json),
            },
            "dev-v1.1.json": {
                "url": "https://rajpurkar.github.io/SQuAD-explorer/dataset/dev-v1.1.json",
                "sha256": sha256_file(args.dev_json),
            },
        },
        "tokenizer": {"repo": args.tokenizer, "vocab_sha256": vocab_hash},
        "filters": {
            "min_tokens": args.min_tokens,
            "max_tokens": args.max_tokens,
            "max_q_per_passage": args.max_q_per_passage,
        },
        "counts": {
            "eval_pairs": len(eval_rows),
            "eval_unique_passages": len(eval_hashes),
            "eval_qualifying_passages": eval_cand,
            "train_pairs": len(train_rows),
            "train_unique_passages": len(train_hashes),
            "train_qualifying_passages": train_cand,
        },
    })
    with open(manifest_path, "w") as fh:
        json.dump(manifest, fh, indent=2)

    print(json.dumps(manifest["counts"], indent=2))
    print(f"wrote {out/'train.jsonl'}, {out/'eval.jsonl'}, {out/'MANIFEST.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
