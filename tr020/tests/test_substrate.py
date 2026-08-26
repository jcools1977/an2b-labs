#!/usr/bin/env python3
"""Substrate determinism gate (DECISIONS D11), red-then-green.

1. Red: with TR020_SABOTAGE_RNG=1 (run-level entropy), two runs of the
   same probe item must produce DIFFERENT trace bytes; if the sabotage
   is invisible, the reproducibility check cannot fail and proves
   nothing.
2. Green: without sabotage, every system's first probe item is
   byte-identical across repeated runs and under mask of each component
   the trace remains well-formed.
"""
import os
import subprocess
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TR_ROOT))

import json  # noqa: E402

from auditor.lm import StubLM  # noqa: E402
from auditor.trace import trace_bytes  # noqa: E402
from seed_systems.systems import build_systems  # noqa: E402


def first_item(sid):
    path = TR_ROOT / "seed_systems" / "probes" / f"probes_{sid}.jsonl"
    with open(path) as fh:
        return json.loads(fh.readline())


def sabotage_differs():
    """Run in a subprocess so the env flag cannot leak into green runs."""
    code = (
        "import sys, json; sys.path.insert(0, '.');"
        "from auditor.lm import StubLM; from auditor.trace import trace_bytes;"
        "from seed_systems.systems import build_systems;"
        "s = build_systems()['s1_research_brief'];"
        "it = json.loads(open('seed_systems/probes/probes_s1_research_brief.jsonl').readline());"
        "a = trace_bytes(s.run(it, StubLM())[1]);"
        "b = trace_bytes(s.run(it, StubLM())[1]);"
        "sys.exit(0 if a != b else 1)"
    )
    env = dict(os.environ, TR020_SABOTAGE_RNG="1")
    return subprocess.run([sys.executable, "-c", code], cwd=TR_ROOT, env=env).returncode == 0


def main():
    bad = 0
    if os.environ.get("TR020_SABOTAGE_RNG") == "1":
        print("refusing to run the green suite with sabotage enabled")
        return 1

    if sabotage_differs():
        print("ok: sabotaged run-level RNG is caught (traces differ)")
    else:
        print("BROKEN: sabotage invisible; the reproducibility check cannot fail")
        bad = 1

    systems = build_systems()
    lm = StubLM()
    for sid, system in systems.items():
        item = first_item(sid)
        a = trace_bytes(system.run(item, lm)[1])
        b = trace_bytes(system.run(item, lm)[1])
        if a != b:
            print(f"BROKEN: {sid} trace not byte-reproducible")
            bad = 1
            continue
        for name in system.component_names():
            answer, trace = system.run(item, lm, mask=name)
            masked_flags = [e["masked"] for e in trace["events"]]
            if sum(masked_flags) != 1:
                print(f"BROKEN: {sid} mask of {name} flagged {sum(masked_flags)} events")
                bad = 1
        print(f"ok: {sid} byte-reproducible; {len(system.component_names())} masks well-formed")
    return bad


if __name__ == "__main__":
    sys.exit(main())
