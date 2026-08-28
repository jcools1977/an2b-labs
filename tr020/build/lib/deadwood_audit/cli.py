"""deadwood CLI, v0.1: orientation and honest scoping.

`deadwood audit <target>` against an arbitrary repo requires an adapter
exposing that system's components through the trace interface; v0.1
ships the engine, the interface, and four worked framework adapters
rather than pretending auto-discovery exists. The command prints where
everything lives.
"""
import argparse
import sys


def main():
    ap = argparse.ArgumentParser(
        prog="deadwood",
        description=("Ablation auditor for agent systems: dead / redundant / "
                     "live verdicts by intervention, not text-tracing."),
    )
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("audit", help="audit a system exposed through the trace interface")
    ap.parse_args()

    print(__doc__)
    print("Engine:   deadwood_audit.Auditor (see deadwood_audit/core/ablate.py)")
    print("Interface: deadwood_audit.System / Component (see deadwood_audit/core/trace.py)")
    print("Examples: tr020/wild/adapters.py (LangChain, LlamaIndex, CrewAI, AutoGen)")
    print("Report:   https://github.com/jcools1977/an2b-labs/tree/main/tr020/report")
    return 0


if __name__ == "__main__":
    sys.exit(main())
