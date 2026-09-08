#!/usr/bin/env python3
"""TR-003r PASS gate: three clauses, primary pair only, Q1, RANDOM
anchors at 1,024, C3, both directions, both seeds. Schema
(results/analysis.json):
{"primary_pair": ["bge","minilm"], "query_kind": "q1", "selection": "random",
 "anchors": 1024, "condition": "C3",
 "cells": {"41": {"bge->minilm": {"retention":..,"provenance_work":..,
                  "confident_wrong":..,"native_confident_wrong":..}, "minilm->bge": {...}},
           "43": {...}}}
"""
import json
import sys

PRIMARY = ["bge", "minilm"]
DIRS = ["bge->minilm", "minilm->bge"]
SEEDS = ["41", "43"]


def check(path):
    d = json.load(open(path))
    v = []
    if d.get("primary_pair") != PRIMARY:
        v.append(f"gate read on {d.get('primary_pair')}, not the frozen primary pair")
    if d.get("query_kind") != "q1":
        v.append("gate read on a query kind other than Q1")
    if d.get("selection") != "random":
        v.append("gate read on non-random anchors (medoids are boundary map)")
    if d.get("anchors") != 1024:
        v.append(f"gate read at {d.get('anchors')} anchors, not 1,024")
    if d.get("condition") != "C3":
        v.append(f"gate read on {d.get('condition')}, not C3 (zero-fit relative representations)")
    cells = d.get("cells", {})
    for s in SEEDS:
        if s not in cells:
            v.append(f"seed {s} missing")
            continue
        for dr in DIRS:
            c = cells[s].get(dr)
            if c is None:
                v.append(f"seed {s} direction {dr} missing")
                continue
            if c.get("retention", 0) < 0.80:
                v.append(f"seed {s} {dr}: retention {c.get('retention')} < 0.80 (clause i)")
            if c.get("provenance_work", 0) < 0.90:
                v.append(f"seed {s} {dr}: provenance {c.get('provenance_work')} < 0.90 (clause ii)")
            if c.get("confident_wrong", 1) > 0.05:
                v.append(f"seed {s} {dr}: confident-wrong {c.get('confident_wrong')} > 0.05 (clause iii)")
            if "native_confident_wrong" not in c:
                v.append(f"seed {s} {dr}: native confident-wrong baseline absent (stamp condition one)")
    return v


def main():
    if len(sys.argv) != 2:
        return 2
    vs = check(sys.argv[1])
    for x in vs:
        print(f"VIOLATION [{sys.argv[1]}]: {x}")
    if not vs:
        print(f"PASS gates hold: {sys.argv[1]}")
    return 1 if vs else 0


if __name__ == "__main__":
    sys.exit(main())
