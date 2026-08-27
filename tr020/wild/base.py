"""Wild-phase adapter base (DECISIONS D21, D22).

A WildSystem presents a foreign framework through the same interface the
Auditor already trusts: system_id, component_names(), and
run(item, lm, mask=None, mask_fn=None) -> (answer, trace). The lm
argument is accepted for interface parity and ignored; wild systems call
the local OpenAI-compatible endpoint.

Masking is interception at framework boundaries: the adapter captures a
component's output where the framework hands it over, applies the mask,
and lets the framework's own machinery consume the replacement. The
bite-proof harness (test_bite.py) must show masking reaches the model,
red-then-green, before any adapter's audit counts.

TR020_SABOTAGE_MASK=1 deliberately breaks interception (the mask is
applied to a discarded copy) so the bite-proof can be watched failing.
"""
import json
import os
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TR_ROOT))

from auditor.mask import neutral_mask  # noqa: E402

ENDPOINT = "http://127.0.0.1:8399/v1"
MODEL_ID = "mlx-community/Qwen3-1.7B-4bit"
API_KEY = "local"  # the server ignores it; frameworks require one


def sabotaged():
    return os.environ.get("TR020_SABOTAGE_MASK") == "1"


def apply_mask(name, output, mask, mask_fn, ctx=None):
    """The single interception used by every adapter. Returns the value
    downstream code must consume. Under sabotage, the mask is computed
    and discarded, which is exactly the failure the bite-proof exists
    to catch."""
    if mask is None:
        return output
    mask_set = {mask} if isinstance(mask, str) else set(mask)
    if name not in mask_set:
        return output
    replacement = (mask_fn or (lambda o, _c: neutral_mask(o)))(output, ctx)
    if sabotaged():
        _ = replacement  # computed, discarded: interception broken on purpose
        return output
    return replacement


class EndpointLM:
    """generate() against the local server; used as the capability-matched
    placebo paraphraser for wild systems (D20/D21: same model class the
    system runs on, by construction). Deterministic: temperature 0."""

    name = f"endpoint:{MODEL_ID}"

    def __init__(self):
        from openai import OpenAI

        self.client = OpenAI(base_url=ENDPOINT, api_key=API_KEY)

    def generate(self, prompt, seed, max_tokens=256):
        r = self.client.chat.completions.create(
            model=MODEL_ID,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0,
        )
        return (r.choices[0].message.content or "").strip()


def load_probes(name):
    path = TR_ROOT / "wild" / "probes" / f"probes_{name}.jsonl"
    return [json.loads(l) for l in open(path)]


def trace_dict(system_id, item, mask, events, answer):
    mask_set = {mask} if isinstance(mask, str) else set(mask or [])
    return {
        "system": system_id,
        "item": item["id"],
        "mask": sorted(mask_set) or None,
        "events": events,
        "answer": answer,
    }
