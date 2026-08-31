#!/usr/bin/env python3
"""Paraphrase KILL material (D8): 100 chunks sampled seed-41 from the
held-out TEST works (never training text), 500-word size (the size on
which attribution is hardest, per the read-hardest rule), rewritten
content-preserving by the pinned Llama-3.1-8B
(mlx-community/Meta-Llama-3.1-8B-Instruct-4bit @ 241a666d).

TR-011 D14 bounds enforced per paraphrase: length ratio in [0.5, 2.0]
and content-word Jaccard >= 0.3 against the original; one regeneration
allowed on a bounds failure, then the paraphrase is logged INVALID and
excluded. Runs on legion; writes corpus_store/paraphrases/{cid}.txt
and paraphrase_log.json (bounds, attempts, validity, per D8).
"""
import json
import random
import re
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TR_ROOT))
from analysis.split import split_ids  # noqa: E402

STORE = TR_ROOT / "corpus_store"
MODEL = "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"
REVISION = "241a666dad6cb93c8ff213d39a7f34a36bf26db4"
SEED, N, SIZE = 41, 100, 500

PROMPT = (
    "Rewrite the following passage in different words. Preserve every "
    "fact, event, and meaning exactly; change the wording, sentence "
    "structure, and rhythm as much as possible. Output only the "
    "rewritten passage, no preamble.\n\nPASSAGE:\n{text}\n\nREWRITE:")


def content_words(text, frozen):
    return {w for w in re.findall(r"[a-z']+", text.lower())
            if w not in frozen}


def in_bounds(orig, para, frozen):
    lo, lp = len(orig.split()), len(para.split())
    ratio = lp / max(lo, 1)
    a, b = content_words(orig, frozen), content_words(para, frozen)
    jac = len(a & b) / max(len(a | b), 1)
    return (0.5 <= ratio <= 2.0) and (jac >= 0.3), ratio, jac


def main():
    from mlx_lm import load, generate
    from mlx_lm.sample_utils import make_sampler

    frozen = set((TR_ROOT / "data" / "function_words.txt").read_text().split())
    registry = json.load(open(STORE / "chunk_registry.json"))
    _, test = split_ids(registry, SIZE)
    rng = random.Random(SEED)
    sample = sorted(rng.sample(test, N))
    authors = {registry[c]["author"] for c in sample}
    assert len(authors) >= 6, f"only {len(authors)} authors in sample (D8)"

    model, tok = load(MODEL, revision=REVISION)
    sampler = make_sampler(temp=0.7)
    (STORE / "paraphrases").mkdir(exist_ok=True)
    log = {"model": MODEL, "revision": REVISION, "seed": SEED,
           "size": SIZE, "n_sampled": N, "n_authors": len(authors),
           "chunks": {}}
    valid = 0
    for i, cid in enumerate(sample):
        orig = (STORE / "chunks" / f"{cid}.txt").read_text()
        entry = {"attempts": []}
        for attempt in range(2):  # regenerate once, then invalid (D14 bounds)
            msgs = [{"role": "user",
                     "content": PROMPT.format(text=orig)}]
            prompt = tok.apply_chat_template(msgs, add_generation_prompt=True)
            para = generate(model, tok, prompt=prompt, max_tokens=1400,
                            sampler=sampler).strip()
            ok, ratio, jac = in_bounds(orig, para, frozen)
            entry["attempts"].append({"ratio": round(ratio, 3),
                                      "jaccard": round(jac, 3), "ok": ok})
            if ok:
                (STORE / "paraphrases" / f"{cid}.txt").write_text(para)
                valid += 1
                break
        entry["valid"] = entry["attempts"][-1]["ok"]
        log["chunks"][cid] = entry
        if (i + 1) % 10 == 0:
            print(f"{i + 1}/{N} ({valid} valid)", flush=True)
    log["n_valid"] = valid
    json.dump(log, open(STORE / "paraphrase_log.json", "w"), indent=2)
    print(f"done: {valid}/{N} valid paraphrases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
