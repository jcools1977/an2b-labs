"""TR-006 council harness (Track B infrastructure; DECISIONS D11-D12).

Three role seats over a bounded broadcast buffer of S slots, batched
in lockstep across items with mlx_lm.batch_generate. Modes:
  main            bounded buffer, top-S by self-assessed salience
  unlimited       every item ever submitted is visible (no cut)
  frozen          the round-1 buffer is broadcast every round after
  random_salience salience replaced by a seeded uniform draw at the cut
  role_shuffle    role -> model mapping permuted per item (seeded)
  single          one model alone, private history, no buffer
Rounds r = 1..R: seats generate (seeing the last broadcast), the cut
happens, the buffer is broadcast when r % F == 0. After round R a
final broadcast always happens and the synthesizer answers in an
answer step seeing it, so every F condition contains at least one
exchange. Greedy decoding; 200 tokens per submission.
"""
from __future__ import annotations

import json
import random
import re
import time

import mlx.core as mx
from mlx_lm import load
from mlx_lm.generate import batch_generate

from workspace import gemma_batch_patch
from workspace.prefix_cache import prefill, split_tokens

gemma_batch_patch.apply()  # certified by tests/test_gemma_batch.py (D13)

# D16: MLX's buffer cache grew to 23-34 GB after one long-prompt batch and
# Metal ran out of memory with three models resident. Cap the cache and
# the working set; halve the batch on any out-of-memory and retry.
mx.set_cache_limit(int(3e9))
mx.set_memory_limit(int(34e9))

MODELS = {
    "llama": "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit",
    "qwen": "mlx-community/Qwen3-8B-4bit",
    "gemma": "mlx-community/gemma-2-9b-it-4bit",
}
ROLE_MODEL = {"proposer": "llama", "critic": "qwen", "synthesizer": "gemma"}  # D12
ROLES = ["proposer", "critic", "synthesizer"]
ROLE_TEXT = {
    "proposer": "You are the PROPOSER. Propose a concrete line of reasoning or a candidate answer, "
                "citing the specific facts from the context that support it.",
    "critic": "You are the CRITIC. Find the weakest step in the reasoning so far, check it against the "
              "context, and state what is wrong or what is missing. Do not propose from scratch.",
    "synthesizer": "You are the SYNTHESIZER. Integrate the strongest points on the board into one "
                   "coherent chain of reasoning and state your current best answer.",
}
MAX_TOKENS = 200
BATCH = 8
BOARD_CHARS = 200  # D16: rendered item text on the board is capped so S=32 stays under ~2k tokens


class Seats:
    def __init__(self, names=("llama", "qwen", "gemma")):
        self.m = {}
        for n in names:
            t0 = time.time()
            self.m[n] = load(MODELS[n])
            print(f"loaded {n} in {time.time()-t0:.1f}s", flush=True)

    def template(self, name, content, tokenize=True):
        model, tok = self.m[name]
        kw = {"enable_thinking": False} if name == "qwen" else {}
        return tok.apply_chat_template([{"role": "user", "content": content}], add_generation_prompt=True,
                                       tokenize=tokenize, **kw)

    def prefix_cache(self, name, prefix_text):
        """Prefill the chat-template head plus the prefix text once (D17).
        Returns (cache, prefix_ids) or (None, None) if the boundary does not
        tokenize cleanly; the caller then runs that item uncached."""
        model, tok = self.m[name]
        full_probe = self.template(name, prefix_text + "PROBE", tokenize=False)
        head_plus_prefix = full_probe[:full_probe.index("PROBE")]
        pre, _ = split_tokens(tok, head_plus_prefix, full_probe)
        if pre is None:
            return None, None
        return prefill(model, pre), pre

    def generate(self, name, prompts_text, caches=None, prefix_ids=None):
        """prompts_text: full user contents. With caches, each prompt's
        tokens are split at its prefix and only the suffix is fed."""
        model, tok = self.m[name]
        full = [self.template(name, c) for c in prompts_text]
        if caches is None:
            return self._batched(model, tok, full, None)
        suffix, use_cache = [], []
        for ids, pre, c in zip(full, prefix_ids, caches):
            if c is not None and pre is not None and ids[:len(pre)] == pre:
                suffix.append(ids[len(pre):]); use_cache.append(c)
            else:
                suffix.append(ids); use_cache.append(None)
        outs = [None] * len(full)
        cached_idx = [i for i, c in enumerate(use_cache) if c is not None]
        plain_idx = [i for i, c in enumerate(use_cache) if c is None]
        if cached_idx:
            res = self._batched(model, tok, [suffix[i] for i in cached_idx], [use_cache[i] for i in cached_idx])
            for i, t in zip(cached_idx, res):
                outs[i] = t
        if plain_idx:
            res = self._batched(model, tok, [full[i] for i in plain_idx], None)
            for i, t in zip(plain_idx, res):
                outs[i] = t
        self.n_uncached = getattr(self, "n_uncached", 0) + len(plain_idx) * (1 if caches is not None else 0)
        return outs

    def _batched(self, model, tok, prompts, caches):
        outs, lo, bs = [], 0, BATCH
        while lo < len(prompts):
            try:
                kw = {"prompt_caches": caches[lo:lo + bs]} if caches is not None else {}
                res = batch_generate(model, tok, prompts=prompts[lo:lo + bs], max_tokens=MAX_TOKENS, verbose=False, **kw)
            except RuntimeError as exc:
                if "Memory" not in str(exc) or bs == 1:
                    raise
                mx.clear_cache()
                bs = max(1, bs // 2)
                print(f"  OOM; retrying with batch {bs}", flush=True)
                continue
            outs.extend(res.texts if hasattr(res, "texts") else res)
            lo += bs
            mx.clear_cache()
        return outs


def parse_submission(text):
    """Extract {"item","salience","answer"}; record parse failures."""
    m = re.search(r"\{.*\}", text, re.S)
    if m:
        try:
            d = json.loads(m.group(0))
            item = str(d.get("item", "")).strip()
            sal = float(d.get("salience", 50))
            ans = str(d.get("answer", "")).strip()
            return {"item": item or text.strip()[:600], "salience": max(0.0, min(100.0, sal)),
                    "answer": ans, "parsed": True}
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
    ans = ""
    am = re.search(r"answer\s*[:=]\s*(.+)", text, re.I)
    if am:
        ans = am.group(1).strip().strip('"').split("\n")[0][:100]
    return {"item": text.strip()[:600], "salience": 50.0, "answer": ans, "parsed": False}


def build_prompt_parts(role, item, board, own_history, final=False):
    """(prefix_text, suffix_text): the prefix is identical for every
    generation of an item, so it can be KV-cached (D17)."""
    prefix = f"TASK CONTEXT:\n{item['context']}\n\nQUESTION: {item['question']}\n\n"
    board_txt = "\n".join(f"[{b['id']}] (salience {b['salience']:.0f}, {b['author']}, round {b['round']}) {b['item'][:BOARD_CHARS]}"
                          for b in board) or "(empty)"
    own = "\n".join(f"- round {h['round']}: {h['item'][:300]}" for h in own_history) or "(none)"
    if final:
        ask = ("Give your FINAL answer. Reply with a JSON object only: "
               '{"item": "one-sentence justification", "salience": 0-100, "answer": "the short answer"}. '
               "The answer must be a short phrase (a name, a number, yes or no, or a single value), nothing else.")
    else:
        ask = ("Reply with a JSON object only: "
               '{"item": "your contribution in at most three sentences", "salience": 0-100, "answer": "your current best short answer"}. '
               "Salience is your honest estimate of how much this contribution matters for reaching the correct answer.")
    suffix = (f"{ROLE_TEXT[role]}\n\nSHARED WORKSPACE (broadcast items):\n{board_txt}\n\n"
              f"YOUR OWN EARLIER CONTRIBUTIONS:\n{own}\n\n{ask}")
    return prefix, suffix


def build_messages(role, item, board, own_history, final=False):
    prefix, suffix = build_prompt_parts(role, item, board, own_history, final=final)
    return [{"role": "user", "content": prefix + suffix}]


def run_config(seats, items, S, F, R, mode="main", seed=41, single_model=None, log=None, block=BATCH, use_cache=True):
    """Run every item through one configuration, in blocks of `block`
    items held in lockstep so only a block's prefix caches are resident."""
    out = []
    for lo in range(0, len(items), block):
        out.extend(_run_block(seats, items[lo:lo + block], S, F, R, mode, seed, single_model, use_cache))
    return out


def _run_block(seats, items, S, F, R, mode, seed, single_model, use_cache):
    n = len(items)
    rng = random.Random(f"{mode}:{seed}:{S}:{F}")
    role_map = []
    for it in items:
        if mode == "role_shuffle":
            models = list(ROLE_MODEL.values())
            random.Random(f"shuffle:{seed}:{it['id']}").shuffle(models)
            role_map.append(dict(zip(ROLES, models)))
        else:
            role_map.append(dict(ROLE_MODEL))
    state = [{"buffer": [], "broadcast": [], "frozen": None, "all": [], "hist": {r: [] for r in ROLES},
              "trace": [], "counter": 0} for _ in items]
    roles_active = ROLES if mode != "single" else ["synthesizer"]
    # prefix caches: one per (item, model) actually used in this block
    caches = {}
    if use_cache:
        needed = set()
        for i in range(n):
            for role in roles_active:
                needed.add((i, single_model if mode == "single" else role_map[i][role]))
        for i, mdl in sorted(needed):
            prefix, _ = build_prompt_parts("proposer", items[i], [], [])
            caches[(i, mdl)] = seats.prefix_cache(mdl, prefix)

    def submissions_for(role, r, final=False):
        by_model = {}
        for i, it in enumerate(items):
            mdl = single_model if mode == "single" else role_map[i][role]
            board = state[i]["broadcast"] if mode != "single" else []
            prefix, suffix = build_prompt_parts(role, it, board, state[i]["hist"][role], final=final)
            by_model.setdefault(mdl, []).append((i, prefix + suffix))
        out = [None] * n
        for mdl, lst in by_model.items():
            if use_cache:
                cs = [caches[(i, mdl)][0] for i, _ in lst]
                ps = [caches[(i, mdl)][1] for i, _ in lst]
                texts = seats.generate(mdl, [c for _, c in lst], caches=cs, prefix_ids=ps)
            else:
                texts = seats.generate(mdl, [c for _, c in lst])
            for (i, _), t in zip(lst, texts):
                out[i] = t
        return out

    for r in range(1, R + 1):
        for role in roles_active:
            texts = submissions_for(role, r)
            for i, t in enumerate(texts):
                sub = parse_submission(t)
                st = state[i]
                st["counter"] += 1
                sal = sub["salience"]
                if mode == "random_salience":
                    sal = rng.uniform(0, 100)
                rec = {"id": f"i{st['counter']}", "item": sub["item"], "salience": sal, "author": role,
                       "round": r, "parsed": sub["parsed"], "answer": sub["answer"]}
                st["hist"][role].append(rec)
                st["all"].append(rec)
                st["buffer"].append(rec)
        if mode == "single":
            continue
        for i in range(n):
            st = state[i]
            cand = sorted(st["buffer"], key=lambda b: (-b["salience"], -b["round"]))
            for rank, b in enumerate(cand, 1):
                b.setdefault("rank_at_cut", []).append(rank)
            survivors = cand if mode == "unlimited" else cand[:S]
            st["buffer"] = list(survivors)
            st["trace"].append({"round": r, "n_candidates": len(cand), "survivors": [b["id"] for b in survivors],
                                "cut_ranks": {b["id"]: rank for rank, b in enumerate(cand, 1)}})
            if r == 1 and mode == "frozen":
                st["frozen"] = list(survivors)
            if r % F == 0:
                st["broadcast"] = st["frozen"] if (mode == "frozen" and st["frozen"] is not None) else list(survivors)
    for i in range(n):
        st = state[i]
        if mode == "single":
            continue
        st["broadcast"] = st["frozen"] if (mode == "frozen" and st["frozen"] is not None) else list(st["buffer"])
    texts = submissions_for("synthesizer", R + 1, final=True)
    records = []
    for i, it in enumerate(items):
        sub = parse_submission(texts[i])
        st = state[i]
        final_board = st["broadcast"]
        barely = sum(1 for b in final_board if b.get("rank_at_cut") and b["rank_at_cut"][-1] == S) if mode == "main" else None
        records.append({"id": it["id"], "family": it["family"], "answer": sub["answer"], "gold": it["answer"],
                        "parsed_final": sub["parsed"], "n_parse_fail": sum(1 for a in st["all"] if not a["parsed"]),
                        "final_board": [b["id"] for b in final_board], "final_board_last_slot": barely,
                        "role_map": role_map[i], "n_items_submitted": len(st["all"]),
                        "trace": st["trace"],
                        "submissions": [{k: (v[:300] if k == "item" else v) for k, v in a.items()} for a in st["all"]]})
    caches.clear()
    mx.clear_cache()
    return records
