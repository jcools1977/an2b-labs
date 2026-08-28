"""LM backends for the trace runtime.

Every call is seeded (D11: the seed derives from system, item, and
component, never from run-level state). StubLM is the deterministic
harness backend: it produces stable digest-tagged text so the substrate
and its determinism guarantees are testable with no model resident.
The mlx backend lands in Phase 2 with pinned versions (D10).
"""
import hashlib


class StubLM:
    """Deterministic stand-in: output is a pure function of (prompt, seed)."""

    name = "stub"

    def generate(self, prompt, seed, max_tokens=128):
        digest = hashlib.sha256(f"{seed}:{prompt}".encode("utf-8")).hexdigest()[:12]
        # Echo a stable, prompt-derived line so downstream components that
        # read this output see content that varies with their inputs.
        head = " ".join(prompt.split()[:12])
        return f"[stub:{digest}] {head}"


class MLXLM:
    """Local MLX backend: loads only the MANIFEST-pinned snapshot (D10,
    D15), chat-templated, greedy. Generation is deterministic, so `seed`
    is accepted for interface parity and intentionally unused."""

    def __init__(self, repo, thinking_capable=False):
        import json
        from pathlib import Path

        import mlx.core as mx  # noqa: F401  (fail fast if MLX absent)
        from mlx_lm import load as mlx_load

        manifest_path = Path(__file__).resolve().parents[2] / "MANIFEST.json"
        pins = json.load(open(manifest_path))["models"]
        if repo not in pins:
            raise SystemExit(f"REVISION GATE: {repo} not pinned in MANIFEST.json (D10)")
        pin = pins[repo]["hf_commit"]
        snap = (Path.home() / ".cache" / "huggingface" / "hub"
                / ("models--" + repo.replace("/", "--")) / "snapshots" / pin)
        if not snap.is_dir():
            raise SystemExit(f"REVISION GATE: pinned snapshot {pin[:12]} of {repo} absent")
        self.model, self.tokenizer = mlx_load(str(snap))
        self.name = f"{repo}@{pin[:12]}"
        self._thinking_capable = thinking_capable

    def generate(self, prompt, seed, max_tokens=128):
        import mlx.core as mx
        from mlx_lm.models.cache import make_prompt_cache

        kwargs = {"enable_thinking": False} if self._thinking_capable else {}
        ids = self.tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}], add_generation_prompt=True, **kwargs
        )
        eos = set(getattr(self.tokenizer, "eos_token_ids", None)
                  or [self.tokenizer.eos_token_id])
        cache = make_prompt_cache(self.model)
        logits = self.model(mx.array(ids)[None], cache=cache)
        out = []
        y = mx.argmax(logits[:, -1, :], axis=-1)
        for _ in range(max_tokens):
            t = int(y.item())
            if t in eos:
                break
            out.append(t)
            logits = self.model(y[None], cache=cache)
            y = mx.argmax(logits[:, -1, :], axis=-1)
        return self.tokenizer.decode(out).strip()
