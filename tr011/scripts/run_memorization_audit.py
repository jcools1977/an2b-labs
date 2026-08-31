#!/usr/bin/env python3
"""Memorization audit (D7, refined by D17): runs BEFORE any feature
exists, structurally (the analysis runner refuses to start without this
file's output).

Per candidate corpus-B document (Gutenberg primary+backup, slush
primary+backup, DeVere-published units): 20 seeded 50-token prefixes,
greedy-continue 20 tokens per scoring model, per-prefix exact-token-
match rate; document score = max over models of the mean. Individual
> 0.5 excluded and replaced from backups; the group gap is Gutenberg
median minus slush median over the FINAL primary sets (D17: measured
where the risk lives). Records model pins to MANIFEST.json.
"""
import hashlib
import json
import sys
import time
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
DOCS = TR_ROOT / "corpus_store" / "docs"

MODELS = {
    "qwen": ("mlx-community/Qwen3-1.7B-4bit",
             "3b1b1768f8f8cf8351c712464f906e86c2b8269e"),
    "llama": ("mlx-community/Meta-Llama-3.1-8B-Instruct-4bit",
              "241a666dad6cb93c8ff213d39a7f34a36bf26db4"),
}
N_PREFIXES, PREFIX_LEN, CONT_LEN, EXCLUDE_ABOVE = 20, 50, 20, 0.5


def doc_seed(doc_id, k):
    return int(hashlib.sha256(f"{doc_id}:{k}".encode()).hexdigest()[:12], 16)


def main():
    import mlx.core as mx
    from mlx_lm import load as mlx_load

    manifest = json.load(open(TR_ROOT / "data" / "CORPUS_MANIFEST.json"))
    reg = manifest["documents"]
    candidates = [d for d, m in reg.items() if m["side"] in
                  ("b_published_gutenberg", "b_slush", "b_slush_backup",
                   "a_published")]

    json.dump({"models": {k: {"repo": r, "hf_commit": c}
                          for k, (r, c) in MODELS.items()}},
              open(TR_ROOT / "MANIFEST.json", "w"), indent=2)

    scores = {d: {} for d in candidates}
    for mkey, (repo, pin) in MODELS.items():
        snap = (Path.home() / ".cache/huggingface/hub" /
                ("models--" + repo.replace("/", "--")) / "snapshots" / pin)
        print(f"loading {repo} @ {pin[:12]}", flush=True)
        model, tok = mlx_load(str(snap))
        t0 = time.time()
        for n, did in enumerate(candidates, 1):
            ids = tok.encode((DOCS / f"{did}.txt").read_text())
            if len(ids) < PREFIX_LEN + CONT_LEN + 10:
                scores[did][mkey] = 0.0
                continue
            import random as _r
            rates = []
            for k in range(N_PREFIXES):
                rng = _r.Random(doc_seed(did, k))
                pos = rng.randrange(0, len(ids) - PREFIX_LEN - CONT_LEN)
                prefix = ids[pos:pos + PREFIX_LEN]
                truth = ids[pos + PREFIX_LEN:pos + PREFIX_LEN + CONT_LEN]
                from mlx_lm.models.cache import make_prompt_cache
                cache = make_prompt_cache(model)
                logits = model(mx.array(prefix)[None], cache=cache)
                match = 0
                y = mx.argmax(logits[:, -1, :], axis=-1)
                for t in truth:
                    if int(y.item()) == t:
                        match += 1
                    logits = model(y[None], cache=cache)
                    y = mx.argmax(logits[:, -1, :], axis=-1)
                rates.append(match / CONT_LEN)
            scores[did][mkey] = round(sum(rates) / len(rates), 4)
            if n % 15 == 0 or n == len(candidates):
                print(f"  [{mkey}] {n}/{len(candidates)} "
                      f"({(time.time()-t0)/n:.1f} s/doc)", flush=True)
        del model
        mx.clear_cache()

    per_doc = {d: {"per_model": s, "score": max(s.values())}
               for d, s in scores.items()}
    excluded = [d for d, v in per_doc.items() if v["score"] > EXCLUDE_ABOVE]

    def final_primary(side, backup_side, n=20):
        pool = [d for d in candidates if reg[d]["side"] == side and d not in excluded]
        pool += [d for d in candidates if backup_side and reg[d]["side"] == backup_side
                 and d not in excluded]
        return pool[:n]

    gut_all = [d for d in candidates if reg[d]["side"] == "b_published_gutenberg"]
    gut_final = [d for d in gut_all if d not in excluded][:20]
    slush_final = final_primary("b_slush", "b_slush_backup")
    devere_pub = [d for d in candidates if reg[d]["side"] == "a_published"]

    def median(xs):
        xs = sorted(xs)
        return xs[len(xs) // 2] if len(xs) % 2 else (xs[len(xs)//2 - 1] + xs[len(xs)//2]) / 2

    gut_med = median([per_doc[d]["score"] for d in gut_final])
    slush_med = median([per_doc[d]["score"] for d in slush_final])
    dev_med = median([per_doc[d]["score"] for d in devere_pub])
    gap = round(gut_med - slush_med, 4)

    out = {
        "per_doc": per_doc,
        "excluded_above_0.5": excluded,
        "final_sets": {"gutenberg": gut_final, "slush": slush_final},
        "medians": {"gutenberg": gut_med, "slush": slush_med,
                    "devere_published": dev_med},
        "group_gap_gutenberg_minus_slush": gap,
        "corpus_b_group_ok": gap <= 0.05,
        "rule": "D7/D17: gap > 0.05 scopes corpus B out of PASS support",
    }
    with open(TR_ROOT / "results" / "memorization_audit.json", "w") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps({k: v for k, v in out.items() if k != "per_doc"}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
