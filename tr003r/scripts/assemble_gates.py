#!/usr/bin/env python3
"""Assemble results/analysis.json, kill.json, controls.json from
results/grid.jsonl and data/CORPUS_MANIFEST.json. Pure bookkeeping:
no number is computed here that the grid did not already emit.

Usage: assemble_gates.py [--grid results/grid.jsonl] [--manifest data/CORPUS_MANIFEST.json] [--outdir results]
"""
import argparse
import json
from pathlib import Path

TR = Path(__file__).resolve().parents[1]
PRIMARY = ("bge", "minilm")
DIRS = [f"{PRIMARY[0]}->{PRIMARY[1]}", f"{PRIMARY[1]}->{PRIMARY[0]}"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid", default=str(TR / "results" / "grid.jsonl"))
    ap.add_argument("--manifest", default=str(TR / "data" / "CORPUS_MANIFEST.json"))
    ap.add_argument("--outdir", default=str(TR / "results"))
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.grid) if l.strip()]
    man = json.load(open(a.manifest))
    out = Path(a.outdir)

    def find(**kw):
        return [r for r in rows if all(r.get(k) == v for k, v in kw.items())]

    def one(**kw):
        m = find(**kw)
        return m[0] if len(m) == 1 else None

    # PASS: C3, q1, random, 1024, primary, both dirs, both seeds
    cells = {}
    for seed in (41, 43):
        cells[str(seed)] = {}
        for dr in DIRS:
            r = one(seed=seed, qkind="q1", pair=dr, condition="C3", anchors=1024, selection="random", arm=None)
            if r:
                cells[str(seed)][dr] = {"retention": r["retention"], "provenance_work": r["provenance_work"],
                                        "confident_wrong": r["confident_wrong"],
                                        "native_confident_wrong": r["native_confident_wrong"],
                                        "excess_confident_wrong": r["excess_confident_wrong"],
                                        "r5": r["r5"], "native_r5": r["native_r5"], "jaccard10": r.get("jaccard10")}
    json.dump({"primary_pair": list(PRIMARY), "query_kind": "q1", "selection": "random",
               "anchors": 1024, "condition": "C3", "cells": cells}, open(out / "analysis.json", "w"), indent=1)
    # KILL: C4 retention
    kc = {}
    for seed in (41, 43):
        kc[str(seed)] = {}
        for dr in DIRS:
            r = one(seed=seed, qkind="q1", pair=dr, condition="C4", anchors=1024, selection="random", arm=None)
            if r:
                kc[str(seed)][dr] = r["retention"]
    killed = any(v < 0.50 for s in kc.values() for v in s.values())
    json.dump({"primary_pair": list(PRIMARY), "anchors": 1024, "condition": "C4", "cells": kc,
               "killed": killed}, open(out / "kill.json", "w"), indent=1)
    # controls
    nf = {}
    for r in find(condition="C1", qkind="q1", seed=41):
        nf[r["space"]] = r["r5"]
    cc = {}
    for seed in (41, 43):
        cc[str(seed)] = {}
        for dr in DIRS:
            c2 = one(seed=seed, qkind="q1", pair=dr, condition="C2")
            cell = {"scrambled": {}, "mismatched": {}}
            for k in (64, 256, 1024):
                s = one(seed=seed, qkind="q1", pair=dr, condition="C3", anchors=k, selection="random", arm="scrambled")
                m = one(seed=seed, qkind="q1", pair=dr, condition="C3", anchors=k, selection="random", arm="mismatched")
                if s and c2:
                    cell["scrambled"][str(k)] = {"c3_r5": s["r5"], "c2_r5": c2["r5"]}
                if m and c2:
                    cell["mismatched"][str(k)] = {"c3_r5": m["r5"], "c2_r5": c2["r5"], "retention": m["retention"]}
            c3 = one(seed=seed, qkind="q1", pair=dr, condition="C3", anchors=1024, selection="random", arm=None)
            rp = one(seed=seed, qkind="q1", pair=dr, condition="RP", arm="random_projection")
            if c3 and rp:
                cell["random_projection"] = {"c3_r5": c3["r5"], "rp_r5": rp["r5"]}
            cc[str(seed)][dr] = cell
    dj = man.get("disjointness", {})
    disj = all(dj.get(f) is True for f in ("store_vs_anchor_pool", "query_sources_vs_anchor_pool",
                                            "anchors_vs_queries_all_seed_pairs", "works_partition_global"))
    json.dump({"primary_pair": list(PRIMARY), "disjointness_ok": disj, "native_floor": nf, "cells": cc},
              open(out / "controls.json", "w"), indent=1)
    print(f"assembled: pass cells {sum(len(v) for v in cells.values())}, kill cells "
          f"{sum(len(v) for v in kc.values())} killed={killed}, native floor {len(nf)} spaces")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
