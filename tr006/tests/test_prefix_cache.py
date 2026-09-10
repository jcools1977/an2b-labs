#!/usr/bin/env python3
"""Certification exam for prefix caching (D17): for each model, three
real items, the answer-step prompt: cached greedy output (prefix
prefilled once, suffix fed with the cache) must equal uncached greedy
output token for token over 48 tokens. Also checks the tokenization
boundary aligns for every item. Exit nonzero on any difference."""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workspace.council import MAX_TOKENS, Seats, build_prompt_parts  # noqa: E402
import workspace.council as council  # noqa: E402


def main():
    council.MAX_TOKENS = 48
    seats = Seats()
    d = json.load(open(Path(__file__).resolve().parents[1] / "data" / "tasks_41.json"))
    items = d["families"]["hotpot"]["scored"][:2] + d["families"]["puzzles"]["scored"][:1]
    bad = 0
    for name in ("llama", "qwen", "gemma"):
        prompts, caches, pres = [], [], []
        for it in items:
            prefix, suffix = build_prompt_parts("synthesizer", it, [], [], final=True)
            c, pre = seats.prefix_cache(name, prefix)
            if c is None:
                print(f"  FAIL {name}: tokenization boundary did not align for {it['id']}")
                bad += 1
            prompts.append(prefix + suffix); caches.append(c); pres.append(pre)
        t0 = time.time(); plain = seats.generate(name, prompts); tp = time.time() - t0
        t0 = time.time(); cached = seats.generate(name, prompts, caches=caches, prefix_ids=pres); tc = time.time() - t0
        for it, a, b in zip(items, plain, cached):
            same = a.strip() == b.strip()
            bad += 0 if same else 1
            print(f"  {'ok ' if same else 'FAIL'} {name:6} {it['id'][:14]:14} uncached {a.strip()[:34]!r} | cached {b.strip()[:34]!r}")
        print(f"       {name}: uncached {tp:.1f}s, cached {tc:.1f}s (prefill excluded)")
    print(f"prefix cache exam: {'CERTIFIED' if bad == 0 else str(bad) + ' legs differ; caching NOT certified'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
