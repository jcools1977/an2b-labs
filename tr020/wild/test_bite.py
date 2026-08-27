#!/usr/bin/env python3
"""The bite-proof gate (D22): each adapter must prove masking reaches
the model before its audit counts.

Per adapter, three checks on its designated dependent component and
probe item:
1. Reproducibility: the item's trace is byte-identical across two runs
   (D11 on foreign plumbing).
2. Bite (green): masking the dependent component changes the
   canonicalized answer. Absence-of-bite is only allowed to mean
   anything after bite has been shown to happen.
3. Sabotage (red): with TR020_SABOTAGE_MASK=1 in a subprocess, the same
   masking must NOT change the answer, proving the bite check can fail
   when interception is broken.

Writes results/wild_bite.json. Requires the endpoint to be up.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TR_ROOT))

from auditor.canon import CANON  # noqa: E402
from wild.adapters import BITE, BUILDERS, FAMILY  # noqa: E402
from wild.base import load_probes  # noqa: E402


def run_one(sid):
    system = BUILDERS[sid]()
    comp, idx = BITE[sid]
    item = load_probes(sid)[idx]
    canon = CANON[FAMILY[sid]]

    a1, t1 = system.run(item)
    a2, t2 = system.run(item)
    reproducible = json.dumps(t1, sort_keys=True) == json.dumps(t2, sort_keys=True)

    masked_answer, _ = system.run(item, mask=comp)
    bite = canon(masked_answer) != canon(a1)

    return {
        "component": comp, "item": item["id"],
        "reproducible": reproducible, "bite": bite,
        "baseline_answer": a1, "masked_answer": masked_answer,
    }


def sabotage_one(sid):
    """Subprocess so the env flag cannot leak. Success = bite NOT seen."""
    code = (
        "import sys, json; sys.path.insert(0, '.');"
        "from wild.adapters import BITE, BUILDERS, FAMILY;"
        "from wild.base import load_probes;"
        "from auditor.canon import CANON;"
        f"sid = {sid!r};"
        "system = BUILDERS[sid](); comp, idx = BITE[sid];"
        "item = load_probes(sid)[idx]; canon = CANON[FAMILY[sid]];"
        "a, _ = system.run(item); m, _ = system.run(item, mask=comp);"
        "sys.exit(0 if canon(m) == canon(a) else 1)"
    )
    env = dict(os.environ, TR020_SABOTAGE_MASK="1")
    r = subprocess.run([sys.executable, "-c", code], cwd=TR_ROOT, env=env)
    return r.returncode == 0


def main():
    systems = sys.argv[1:] or list(BUILDERS)
    out_path = TR_ROOT / "results" / "wild_bite.json"
    results = json.load(open(out_path)) if out_path.exists() else {}
    bad = 0
    for sid in systems:
        print(f"=== {sid} ===", flush=True)
        r = run_one(sid)
        r["sabotage_caught"] = sabotage_one(sid)
        results[sid] = r
        for k in ("reproducible", "bite", "sabotage_caught"):
            print(f"  {k}: {r[k]}")
            if not r[k]:
                bad = 1
        with open(out_path, "w") as fh:
            json.dump(results, fh, indent=2)
    return bad


if __name__ == "__main__":
    sys.exit(main())
