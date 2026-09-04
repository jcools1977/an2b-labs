#!/usr/bin/env python3
"""Assemble the frozen-checker gate files from the completed grid
(results/grid.jsonl -> analysis.json, controls.json, kill.json), with
detail.json carrying every run and both frames. Strictest-value rules
per D18-analog house practice: the primary skyline reported to the
gate is the WEAKER direction's; seeds_replicate demands identical
gate-clause outcomes at both seeds.
"""
import json
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
GATE = {"cos": 0.70, "top1": 0.30, "sky": 0.80}


def main():
    rows = [json.loads(x) for x in
            open(TR_ROOT / "results" / "grid.jsonl")]
    by = {}
    for r in rows:
        by[(r["a"], r["b"], r["n"], r["seed"], r["kind"])] = r

    def gaterun(a, b, seed):
        return by[(a, b, 16000, seed, "primary_gate")]

    d41 = {"bge_to_llama": gaterun("bge", "llama4", 41),
           "llama_to_bge": gaterun("llama4", "bge", 41)}
    d43 = {"bge_to_llama": gaterun("bge", "llama4", 43),
           "llama_to_bge": gaterun("llama4", "bge", 43)}

    def clause(runs):
        ok = all(r["cosine"] >= GATE["cos"] and r["top1"] >= GATE["top1"]
                 for r in runs.values())
        sky = min(r["skyline_cosine"] for r in runs.values())
        return ok and sky >= GATE["sky"]

    analysis = {
        "primary_pair": "bge-small-en-v1.5<->Llama-3.1-8B-4bit",
        "method": "mini-vec2vec-linear",
        "n_used": 16000,
        "directions": {k: {"cosine": v["cosine"], "top1": v["top1"]}
                       for k, v in d41.items()},
        "skyline_cosine_primary": min(v["skyline_cosine"]
                                      for v in d41.values()),
        "seeds_replicate": clause(d41) == clause(d43),
    }

    st = by[("bge", "llama4", 16000, 41, "shuffled_target")]
    wm = by[("bge", "llama4", 16000, 41, "wrong_model")]
    ds = by[("bge", "llama4", 16000, 41, "domain_shift")]
    manifest = json.load(open(TR_ROOT / "data" / "CORPUS_MANIFEST.json"))
    controls = {
        "shuffled_target": {"top1": st["top1"], "chance": 0.001},
        "wrong_model": {"top1": wm["wrong_model_top1"],
                        "genuine_top1": wm["top1"]},
        "disjointness": {
            "halves_overlap": manifest["overlap_check"]["halves_overlap"],
            "train_eval_overlap":
                manifest["overlap_check"]["train_eval_overlap"]},
        "domain_shift": {"reported": True,
                         "note": f"OOD probe through the primary "
                                 f"translator: raw cosine "
                                 f"{ds['ood_cosine']:.3f}, top-1 "
                                 f"{ds['ood_top1']:.3f}"},
    }

    sky_pairs = {}
    for r in rows:
        if r["kind"] in ("boundary", "primary_gate", "precision_arm") \
                and r["seed"] == 41:
            sky_pairs[f"{r['a']}<->{r['b']}"] = r["skyline_cosine"]
    failing = sum(1 for c in sky_pairs.values() if c < GATE["sky"])
    kill = {"skyline_pairs": sky_pairs,
            "killed": failing > len(sky_pairs) / 2}

    res = TR_ROOT / "results"
    json.dump(analysis, open(res / "analysis.json", "w"), indent=2)
    json.dump(controls, open(res / "controls.json", "w"), indent=2)
    json.dump(kill, open(res / "kill.json", "w"), indent=2)
    json.dump(rows, open(res / "detail.json", "w"), indent=2)
    print(json.dumps({"analysis": analysis,
                      "kill_failing_skylines": failing,
                      "n_skyline_pairs": len(sky_pairs)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
