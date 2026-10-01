#!/usr/bin/env python3
"""TR-013 auto-labeler (D4): collapse onset = first turn t at which,
for three consecutive turns, either the 4-gram overlap of turn t with
any earlier turn is >= 0.6 (loop) or the cosine of turn t's embedding
to the mean of the previous five turns' embeddings is >= 0.95
(mode-lock). Runs with no onset by the horizon are non-collapsing.
Writes results/labels.json: {run_id: {"onset": t or null, "kind": loop|modelock|null,
 "n_turns": n, "model":..., "task":..., "temperature":...}}.
Thresholds are the frozen D4 values; the --thresholds flag exists
only for the red-fixture test and prints a loud warning.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from label.embed import run_embeddings  # noqa: E402

TR = Path(__file__).resolve().parents[1]
NGRAM, OVERLAP, SELFSIM, CONSEC, PREV = 4, 0.6, 0.95, 3, 5


def ngrams(text, n=NGRAM):
    w = re.findall(r"[a-z0-9']+", text.lower())
    return {tuple(w[i:i + n]) for i in range(max(0, len(w) - n + 1))}


def overlap(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a)


def label_run(texts, E):
    """Return (onset_turn or None, kind, per-turn flags) with 1-based turns."""
    grams = [ngrams(t) for t in texts]
    loop_flag, lock_flag = [], []
    for t in range(len(texts)):
        lf = any(overlap(grams[t], grams[j]) >= OVERLAP for j in range(t))
        if t >= PREV:
            mean = E[t - PREV:t].mean(0)
            mean = mean / (np.linalg.norm(mean) + 1e-12)
            kf = float(E[t] @ mean) >= SELFSIM
        else:
            kf = False
        loop_flag.append(lf); lock_flag.append(kf)
    for t in range(len(texts) - CONSEC + 1):
        if all(loop_flag[t:t + CONSEC]):
            return t + 1, "loop", (loop_flag, lock_flag)
        if all(lock_flag[t:t + CONSEC]):
            return t + 1, "modelock", (loop_flag, lock_flag)
    return None, None, (loop_flag, lock_flag)


def parse_run_id(rid):
    model, task, temp, topic, seed = rid.split("__")
    return {"model": model, "task": task, "temperature": float(temp[1:]), "topic_index": int(topic), "seed": seed}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default=str(TR / "results" / "runs"))
    ap.add_argument("--out", default=str(TR / "results" / "labels.json"))
    a = ap.parse_args()
    labels = {}
    files = sorted(Path(a.runs).glob("*.jsonl"))
    for i, p in enumerate(files):
        rows = [json.loads(l) for l in open(p) if l.strip()]
        texts = [r["text"] for r in rows]
        if not texts:
            continue
        E = run_embeddings(p.stem, texts)
        onset, kind, _ = label_run(texts, E)
        labels[p.stem] = {"onset": onset, "kind": kind, "n_turns": len(texts), **parse_run_id(p.stem)}
        if (i + 1) % 100 == 0:
            print(f"  labeled {i+1}/{len(files)}", flush=True)
    json.dump(labels, open(a.out, "w"), indent=1)
    n = len(labels); c = sum(1 for v in labels.values() if v["onset"])
    print(f"labeled {n} runs: {c} collapse ({sum(1 for v in labels.values() if v['kind']=='loop')} loop, "
          f"{sum(1 for v in labels.values() if v['kind']=='modelock')} mode-lock), {n-c} non-collapsing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
