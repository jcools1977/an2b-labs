"""Placebo paraphraser (protocol control 2; DECISIONS D14).

Replaces a component's output with a meaning-preserving paraphrase.
Every paraphrase is bounds-checked at generation time: length ratio in
[0.5, 2.0] and content-word Jaccard >= 0.3. Out-of-bounds paraphrases
are regenerated once with a stricter prompt; a second failure marks the
item's placebo run invalid and reported, never silently used.
"""
import re

LEN_RATIO = (0.5, 2.0)
JACCARD_FLOOR = 0.3

_STOP = {"a", "an", "the", "is", "are", "was", "were", "of", "in", "on", "to",
         "and", "or", "for", "with", "this", "that", "it", "its", "be", "as"}

PROMPT = "Rewrite the following text with different wording but exactly the same meaning. Output only the rewrite.\n\n{text}"
PROMPT_STRICT = (
    "Rewrite the following text, changing only word choice and sentence "
    "structure. Keep every fact, name, and number identical. Keep it about "
    "the same length. Output only the rewrite.\n\n{text}"
)


def _content_words(text):
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in _STOP}


def bounds(original, paraphrase):
    ratio = len(paraphrase) / max(len(original), 1)
    a, b = _content_words(original), _content_words(paraphrase)
    jac = len(a & b) / max(len(a | b), 1)
    ok = LEN_RATIO[0] <= ratio <= LEN_RATIO[1] and jac >= JACCARD_FLOOR
    return ok, {"length_ratio": round(ratio, 3), "jaccard": round(jac, 3)}


def paraphrase_output(lm, output, seed):
    """Paraphrase one component output, preserving structure. Returns
    (paraphrased_or_None, log). None means invalid placebo (D14)."""

    def one(text, item_seed, strict):
        p = (PROMPT_STRICT if strict else PROMPT).format(text=text)
        cand = lm.generate(p, seed=item_seed, max_tokens=256).strip()
        ok, measured = bounds(text, cand)
        return (cand if ok else None), measured

    if isinstance(output, str):
        cand, measured = one(output, seed, strict=False)
        if cand is None:
            cand, measured = one(output, seed + 1, strict=True)
        return cand, {"bounds": measured, "valid": cand is not None}
    if isinstance(output, list):
        outs, logs, valid = [], [], True
        for i, part in enumerate(output):
            c, log = paraphrase_output(lm, part, seed + 100 + i)
            valid = valid and log["valid"]
            outs.append(c if c is not None else part)
            logs.append(log)
        return (outs if valid else None), {"parts": logs, "valid": valid}
    if isinstance(output, dict):
        outs, logs, valid = {}, {}, True
        for i, (k, v) in enumerate(sorted(output.items())):
            c, log = paraphrase_output(lm, v, seed + 200 + i)
            valid = valid and log["valid"]
            outs[k] = c if c is not None else v
            logs[k] = log
        return (outs if valid else None), {"parts": logs, "valid": valid}
    raise TypeError(f"unparaphrasable output type {type(output).__name__}")
