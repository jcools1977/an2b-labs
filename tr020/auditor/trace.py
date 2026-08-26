"""Trace-graph runtime for TR-020.

A System is an ordered list of Components; each declares which earlier
components it reads. Running one probe item produces a Trace: every
component's inputs, output, and mask status, serialized canonically so
byte-identity is a meaningful check (D11).

Seeding (D11): every random draw and LM call is seeded by
(system_id, item_id, component_name), never by run-level state. A probe
item's trace is byte-identical whether run alone, twice, or inside the
full set. TR020_SABOTAGE_RNG=1 deliberately breaks this (run-level
entropy) so the reproducibility test can be watched failing red.

Masking: `mask={component_name}` replaces that component's output with
the structure-preserving neutral placeholder AFTER the component runs
(the component still executes and burns its cost; only its causal
influence is severed — that is the quantity under audit).
"""
import hashlib
import json
import os

from .mask import neutral_mask


def item_seed(system_id, item_id, component=""):
    h = hashlib.sha256(f"{system_id}:{item_id}:{component}".encode("utf-8")).hexdigest()
    return int(h[:12], 16)


class Ctx:
    """Per-component execution context: seeded LM access, no ambient state."""

    def __init__(self, lm, system_id, item_id, component):
        self._lm = lm
        self.seed = item_seed(system_id, item_id, component)
        if os.environ.get("TR020_SABOTAGE_RNG") == "1":
            import random  # run-level entropy: exactly what D11 forbids

            self.seed = random.getrandbits(48)

    def generate(self, prompt, max_tokens=128):
        return self._lm.generate(prompt, seed=self.seed, max_tokens=max_tokens)


class Component:
    def __init__(self, name, fn, reads):
        self.name, self.fn, self.reads = name, fn, list(reads)


class System:
    def __init__(self, system_id, components, final):
        self.system_id = system_id
        self.components = components
        self.final = final  # name of the component whose output is the answer
        names = [c.name for c in components]
        assert len(set(names)) == len(names), "duplicate component names"
        seen = set()
        for c in components:
            missing = [r for r in c.reads if r not in seen]
            assert not missing, f"{c.name} reads {missing} before they exist"
            seen.add(c.name)
        assert final in seen

    def component_names(self):
        return [c.name for c in self.components]

    def run(self, item, lm, mask=None):
        """Execute one probe item; returns (answer, trace_dict)."""
        outputs, events = {}, []
        for c in self.components:
            ctx = Ctx(lm, self.system_id, item["id"], c.name)
            inputs = {r: outputs[r] for r in c.reads}
            out = c.fn(ctx, item, inputs)
            masked = mask is not None and c.name == mask
            if masked:
                out = neutral_mask(out)
            outputs[c.name] = out
            events.append(
                {"component": c.name, "reads": c.reads, "masked": masked, "output": out}
            )
        trace = {
            "system": self.system_id,
            "item": item["id"],
            "mask": mask,
            "lm": lm.name,
            "events": events,
            "answer": outputs[self.final],
        }
        return outputs[self.final], trace


def trace_bytes(trace):
    """Canonical serialization; the unit of byte-reproducibility (D11)."""
    return json.dumps(trace, sort_keys=True, ensure_ascii=False).encode("utf-8")
