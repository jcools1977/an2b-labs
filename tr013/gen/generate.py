#!/usr/bin/env python3
"""TR-013 corpus generation (D3). Runs continue to the horizon; every
turn is written as it is produced (results/runs/<run_id>.jsonl), so
the corpus is resumable per run. Batched in lockstep across runs with
chained prompt caches: each turn feeds only its new tokens with the
run's cache; whenever the template's tokens do not align with the
cache, the run falls back to a fresh full-prompt prefill (always
correct, slower). Certified by tests/test_chain.py: chained output
equals uncached output token for token on multi-turn dialogues.

Usage: generate.py --model qwen|llama --task self_dialogue|loop|rephrase
                   --temperature 0.0|0.3 --topics 0:60 --seeds 1 [--horizon 80] [--smoke]
"""
import argparse
import json
import random
import sys
import time
from pathlib import Path

import mlx.core as mx
from mlx_lm import load
from mlx_lm.generate import batch_generate
from mlx_lm.models.cache import make_prompt_cache
from mlx_lm.sample_utils import make_sampler

TR = Path(__file__).resolve().parents[1]
MODELS = {"qwen": "mlx-community/Qwen3-1.7B-4bit", "llama": "mlx-community/Llama-3.2-3B-Instruct-4bit"}
TURN_TOKENS = 120
BATCH = 8
TOPICS = [
    "the ethics of lighthouse keeping", "why bread rises", "the history of the bicycle", "how rivers choose their paths",
    "the sound of a cello", "what makes a joke land", "tides and the moon", "the taste of winter oranges",
    "why we name hurricanes", "the geometry of honeycombs", "sleep and dreaming", "the life of a mountain goat",
    "coffee versus tea", "how glass is made", "the silence of libraries", "migration of monarch butterflies",
    "the invention of zero", "why old maps have sea monsters", "the smell of rain", "how bridges stay up",
    "the color blue in painting", "what a city sounds like at dawn", "the first telescopes", "knots sailors tie",
    "salt and its history", "the shape of snowflakes", "how memory works", "the rules of chess", "volcanic islands",
    "why cats purr", "the printing press", "the taste of honey from different flowers", "lightning and thunder",
    "how clocks keep time", "the deep sea", "why leaves change color", "the speed of sound", "shadows at noon",
    "the first gardens", "how paper is recycled", "the North Star", "the design of chairs", "fermentation",
    "the language of bees", "why the sky is dark at night", "canals and locks", "the weight of a cloud",
    "how vaccines work", "the oldest trees", "echoes in canyons", "the art of mapmaking", "why we yawn",
    "the mechanics of a piano", "desert flowers", "the invention of the sandwich", "glaciers", "how ships float",
    "the migration of eels", "the fold of a paper crane", "why mirrors reverse left and right",
]


def system_for(task, topic):
    if task == "self_dialogue":
        return (f"You are one of two speakers in a long conversation about {topic}. "
                "Reply to the other speaker in one to three sentences, in your own voice.")
    if task == "loop":
        return (f"You are producing a long list of entries related to {topic}, one entry per reply. "
                "Each reply is a single new entry with a one-sentence note.")
    return "You rewrite text. Each reply restates the previous message in different words, keeping its meaning."


def first_user(task, topic):
    if task == "self_dialogue":
        return f"Let's talk about {topic}. What is your opening thought?"
    if task == "loop":
        return "Give the first entry."
    return f"Here is the text to work with: {topic.capitalize()} is a subject people return to, because it is ordinary and strange at the same time."


def next_user(task, prev_assistant):
    if task == "self_dialogue":
        return prev_assistant
    if task == "loop":
        return "Next entry."
    return "Restate your previous message in different words."


class Chain:
    """One run's chat state as the exact TOKEN STREAM the model consumed,
    with a chained prompt cache. The chat template is used once to learn
    the turn framing (the text between one assistant reply and the next
    generation prompt); after that, turns are appended to the stream
    directly, so the cache and the stream never disagree about history.
    """

    def __init__(self, model, tok, system, enable_thinking_kw):
        self.model, self.tok, self.kw = model, tok, enable_thinking_kw
        self.system = system
        self.stream = []        # token ids the model has consumed (prompt + generated), in order
        self.cache = None
        self.fallbacks = 0
        self.first = True
        self.eos = tok.eos_token_id
        # learn the framing: render a two-turn history with a placeholder reply
        a = tok.apply_chat_template([{"role": "system", "content": system}, {"role": "user", "content": "U1"}],
                                    add_generation_prompt=True, tokenize=False, **enable_thinking_kw)
        b = tok.apply_chat_template([{"role": "system", "content": system}, {"role": "user", "content": "U1"},
                                     {"role": "assistant", "content": "XREPLYX"}, {"role": "user", "content": "U2"}],
                                    add_generation_prompt=True, tokenize=False, **enable_thinking_kw)
        tail = b[b.index("XREPLYX") + len("XREPLYX"):]          # "<eos>\n<user header>U2<...><assistant header>"
        eos_text = tok.decode([self.eos])
        self.after_eos = tail.startswith(eos_text)
        self.frame = tail[len(eos_text):] if self.after_eos else tail   # starts after the reply's EOS
        assert "U2" in self.frame
        self.first_prompt_text = a

    def prepare(self, user_text):
        """Return (new token ids to feed, cache to use)."""
        if self.first:
            self.first = False
            delta = self.tok.encode(self.first_prompt_text.replace("U1", user_text), add_special_tokens=False)
            self.cache = make_prompt_cache(self.model)
            self.stream = []
            self.pending = delta
            return delta, self.cache
        delta = self.tok.encode(self.frame.replace("U2", user_text), add_special_tokens=False)
        if self.cache is None or (hasattr(self.cache[0], "offset") and int(self.cache[0].offset) != len(self.stream)):
            # cache does not hold exactly the stream: rebuild from the full stream
            self.fallbacks += 1
            self.cache = make_prompt_cache(self.model)
            delta = self.stream + delta
            self.stream = []
        self.pending = delta
        return delta, self.cache

    def commit(self, gen_ids, finished_with_eos, new_cache):
        self.cache = new_cache
        self.stream = self.stream + list(self.pending) + list(gen_ids) + ([self.eos] if finished_with_eos else [])
        # if the reply did not end with EOS (hit the token cap), the framing
        # still needs the EOS before the next user turn: feed it with the next delta
        if not finished_with_eos:
            self.stream_needs_eos = True
        else:
            self.stream_needs_eos = False

    def next_delta_prefix(self):
        return [self.eos] if getattr(self, "stream_needs_eos", False) else []


def run_batch(model, tok, kw, runs, horizon, temperature, out_dir, seed):
    sampler = make_sampler(temp=temperature) if temperature > 0 else None
    if temperature > 0:
        mx.random.seed(seed)
    chains = []
    for r in runs:
        c = Chain(model, tok, system_for(r["task"], r["topic"]), kw)
        c.user_next = first_user(r["task"], r["topic"])
        c.run = r
        chains.append(c)
    files = {c.run["run_id"]: open(out_dir / f"{c.run['run_id']}.jsonl", "a") for c in chains}
    for t in range(1, horizon + 1):
        prompts, caches = [], []
        for c in chains:
            pre = c.next_delta_prefix()
            p, cache = c.prepare(c.user_next)
            if pre:
                p = pre + p
                c.pending = p
            prompts.append(p); caches.append(cache)
        t0 = time.time()
        kwargs = {"sampler": sampler} if sampler else {}
        res = batch_generate(model, tok, prompts=prompts, prompt_caches=caches, max_tokens=TURN_TOKENS,
                             return_prompt_caches=True, return_token_ids=True, verbose=False, **kwargs)
        dt = time.time() - t0
        for i, c in enumerate(chains):
            gen_ids = list(res.token_ids[i]) if hasattr(res, "token_ids") else tok.encode(res.texts[i], add_special_tokens=False)
            text = res.texts[i].strip()
            nc = res.caches[i]
            before = len(c.stream) + len(c.pending)
            offset = int(nc[0].offset)
            finished_eos = (offset - before - len(gen_ids)) == 1
            c.commit(gen_ids, finished_eos, nc)
            c.user_next = next_user(c.run["task"], text)
            files[c.run["run_id"]].write(json.dumps({"turn": t, "text": text, "n_tokens": len(gen_ids), "eos": finished_eos,
                                                    "fallbacks": c.fallbacks, "batch_seconds": round(dt, 2)}) + "\n")
            files[c.run["run_id"]].flush()
        mx.clear_cache()
    for f in files.values():
        f.close()
    return [c.fallbacks for c in chains]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=list(MODELS))
    ap.add_argument("--task", required=True, choices=["self_dialogue", "loop", "rephrase"])
    ap.add_argument("--temperature", type=float, required=True)
    ap.add_argument("--topics", default="0:60")
    ap.add_argument("--seeds", type=int, default=1)
    ap.add_argument("--horizon", type=int, default=80)
    ap.add_argument("--out", default=str(TR / "results" / "runs"))
    a = ap.parse_args()
    lo, hi = (int(x) for x in a.topics.split(":"))
    out_dir = Path(a.out); out_dir.mkdir(parents=True, exist_ok=True)
    model, tok = load(MODELS[a.model])
    kw = {"enable_thinking": False} if a.model == "qwen" else {}
    runs = []
    for ti in range(lo, hi):
        for s in range(a.seeds):
            rid = f"{a.model}__{a.task}__t{a.temperature:.1f}__{ti:03d}__s{s}"
            p = out_dir / f"{rid}.jsonl"
            if p.exists() and sum(1 for _ in open(p)) >= a.horizon:
                continue
            if p.exists():
                p.unlink()  # partial run: regenerate from scratch (deterministic for temp 0)
            runs.append({"run_id": rid, "model": a.model, "task": a.task, "temperature": a.temperature,
                         "topic": TOPICS[ti % len(TOPICS)], "topic_index": ti, "seed": 1000 * s + ti})
    print(f"{a.model} {a.task} T={a.temperature}: {len(runs)} runs to generate, horizon {a.horizon}", flush=True)
    t_all = time.time()
    for lo_i in range(0, len(runs), BATCH):
        batch = runs[lo_i:lo_i + BATCH]
        t0 = time.time()
        fb = run_batch(model, tok, kw, batch, a.horizon, a.temperature, out_dir, seed=batch[0]["seed"])
        print(f"  batch {lo_i // BATCH + 1}/{(len(runs) + BATCH - 1) // BATCH}: {len(batch)} runs x {a.horizon} turns in {time.time()-t0:.0f}s; "
              f"cache fallbacks {sum(fb)} (elapsed {(time.time()-t_all)/60:.1f} min)", flush=True)
    print("GEN_DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
