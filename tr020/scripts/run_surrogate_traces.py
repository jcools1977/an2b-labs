#!/usr/bin/env python3
"""Surrogate stage A (D23): trace-persisting baseline re-run plus the
re-run certificate.

- --pass1 / --pass2: run all seeded baselines with the real actor,
  persisting full traces. The two passes run as separate processes.
- --certify: assert pass1 == pass2 byte-for-byte, then recompute one
  full masked condition per system and assert its canonicalized
  answer-change rate EXACTLY equals the value persisted in
  seeded_detail.json. Any drift stops the surrogate phase.

Writes cache/seeded_traces_pass{1,2}.jsonl and
results/surrogate_cert.json.
"""
import argparse
import json
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TR_ROOT))

from auditor.canon import CANON, FAMILY_OF_SYSTEM  # noqa: E402
from auditor.lm import MLXLM  # noqa: E402
from seed_systems.systems import build_systems  # noqa: E402


def probes(sid):
    path = TR_ROOT / "seed_systems" / "probes" / f"probes_{sid}.jsonl"
    return [json.loads(l) for l in open(path)]


def run_pass(out_path):
    from auditor.trace import trace_bytes

    lm = MLXLM("mlx-community/Qwen3-1.7B-4bit", thinking_capable=True)
    with open(out_path, "w") as fh:
        for sid, system in build_systems().items():
            for it in probes(sid):
                _, trace = system.run(it, lm)
                fh.write(trace_bytes(trace).decode("utf-8") + "\n")
            print(f"[{sid}] baseline traced", flush=True)


def certify():
    p1 = (TR_ROOT / "cache" / "seeded_traces_pass1.jsonl").read_bytes()
    p2 = (TR_ROOT / "cache" / "seeded_traces_pass2.jsonl").read_bytes()
    byte_identical = p1 == p2

    detail = json.load(open(TR_ROOT / "results" / "seeded_detail.json"))
    lm = MLXLM("mlx-community/Qwen3-1.7B-4bit", thinking_capable=True)
    per_system = {}
    for sid, system in build_systems().items():
        comp = sorted(system.component_names())[0]
        canon = CANON[FAMILY_OF_SYSTEM[sid]]
        items = probes(sid)
        changes = 0
        for it in items:
            base, _ = system.run(it, lm)
            masked, _ = system.run(it, lm, mask=comp)
            changes += canon(masked) != canon(base)
        recomputed = round(changes / len(items), 4)
        persisted = detail[sid]["solo"][comp]["change_rate"]
        per_system[sid] = {"component": comp, "recomputed": recomputed,
                           "persisted": persisted,
                           "match": recomputed == persisted}

    cert = {"byte_identical": byte_identical, "per_system": per_system,
            "all_match": byte_identical and all(v["match"] for v in per_system.values())}
    with open(TR_ROOT / "results" / "surrogate_cert.json", "w") as fh:
        json.dump(cert, fh, indent=2)
    print(json.dumps(cert, indent=2))
    return 0 if cert["all_match"] else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass1", action="store_true")
    ap.add_argument("--pass2", action="store_true")
    ap.add_argument("--certify", action="store_true")
    args = ap.parse_args()
    (TR_ROOT / "cache").mkdir(exist_ok=True)
    if args.pass1:
        run_pass(TR_ROOT / "cache" / "seeded_traces_pass1.jsonl")
    elif args.pass2:
        run_pass(TR_ROOT / "cache" / "seeded_traces_pass2.jsonl")
    elif args.certify:
        return certify()
    return 0


if __name__ == "__main__":
    sys.exit(main())
