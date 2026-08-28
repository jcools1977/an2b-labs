"""deadwood-audit: ablation auditing for agent systems (AN2B Labs TR-020).

Finds components that run but never causally matter. Three verdicts:
dead (no effect masked alone or jointly), redundant (no effect alone,
effect jointly), live. Certified on a sealed seven-system benchmark
(29/29 class-exact recovery); the cheap textual-influence shortcut is
refuted in the same report (kappa 0.29), which is why this tool runs
real interventions.

Point it at anything that can expose components through the trace
interface: see deadwood_audit.core.trace.System (components with declared reads,
structure-preserving masking) and wild/adapters.py for four worked
examples wrapping LangChain, LlamaIndex, CrewAI, and AutoGen.
"""
from .core.ablate import Auditor  # noqa: F401
from .core.judge import Judge  # noqa: F401
from .core.mask import neutral_mask  # noqa: F401
from .core.trace import Component, System, item_seed, trace_bytes  # noqa: F401

__version__ = "0.1.0"
