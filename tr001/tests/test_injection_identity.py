#!/usr/bin/env python3
"""Phase 2 red-then-green gate: the injection identity test.

Feeding B's own token embeddings through the soft-prompt injection path must
reproduce greedy generation over the normal tokenized path exactly. If it
does not, the plumbing is broken, and the alternative is discovering that as
a mysterious C3 floor collapse three phases later.

--self-test runs the red cases first: two deliberately mis-wired injections
(position offset, magnitude scale) must produce DIFFERENT output, proving
the test can fail; then the clean case must be identical. Writes
results/injection_identity.json. Exit nonzero on any violation.
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import mlx.core as mx  # noqa: E402
from lib.model_b import greedy_from_embeddings, greedy_from_ids, load_b  # noqa: E402

PROMPT = (
    "The corpus callosum is the bundle of nerve fibers that connects the "
    "two hemispheres of the brain. In one word, what does it connect?"
)
MAX_TOKENS = 30


def sabotage(embeds, mode):
    if mode == "offset":  # roll one position: right vectors, wrong nerves
        return mx.concatenate([embeds[:, -1:], embeds[:, :-1]], axis=1)
    if mode == "collapse":  # every position becomes the sequence mean:
        # realistic magnitudes, content destroyed. The failure shape of a
        # dead adapter. (A uniform scale sabotage was tried first and is
        # useless here: the block's leading RMSNorm erases it, D14.)
        return mx.broadcast_to(embeds.mean(axis=1, keepdims=True), embeds.shape)
    raise ValueError(mode)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true",
                    help="red cases (must fail) then clean case (must pass)")
    args = ap.parse_args()

    mx.reset_peak_memory()
    model, tokenizer = load_b()
    ids = tokenizer.encode(PROMPT)

    t0 = time.time()
    ref = greedy_from_ids(model, tokenizer, ids, MAX_TOKENS)
    gen_seconds = time.time() - t0
    embeds = model.model.embed_tokens(mx.array(ids)[None])

    result = {
        "prompt_tokens": len(ids),
        "reference_output": tokenizer.decode(ref),
        "gen_seconds_tokenized_path": round(gen_seconds, 2),
    }
    violations = []

    if args.self_test:
        for mode in ("offset", "collapse"):
            out = greedy_from_embeddings(model, tokenizer, sabotage(embeds, mode), MAX_TOKENS)
            caught = out != ref
            result[f"sabotage_{mode}_detected"] = caught
            if not caught:
                violations.append(
                    f"sabotage '{mode}' NOT detected: a mis-wired injection "
                    f"reproduced reference output, the test cannot fail"
                )

    inj = greedy_from_embeddings(model, tokenizer, embeds, MAX_TOKENS)
    result["clean_identical"] = inj == ref
    if inj != ref:
        violations.append(
            "IDENTITY FAILURE: injecting real token embeddings did not "
            f"reproduce the tokenized path (got: {tokenizer.decode(inj)!r})"
        )

    result["peak_memory_gb"] = round(mx.get_peak_memory() / 2**30, 2)
    result["violations"] = violations

    out_path = Path(__file__).resolve().parents[1] / "results" / "injection_identity.json"
    with open(out_path, "w") as fh:
        json.dump(result, fh, indent=2)

    for v in violations:
        print(f"VIOLATION: {v}")
    print(json.dumps(result, indent=2))
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
