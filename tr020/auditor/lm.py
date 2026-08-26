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
