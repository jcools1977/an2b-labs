#!/usr/bin/env python3
"""TR-003r negative controls 1-5 on the primary pair. Schema
(results/controls.json):
{"primary_pair":..., "disjointness_ok": bool,
 "native_floor": {"bge": r5, "minilm": r5, ...},
 "cells": {"41": {"bge->minilm": {
     "scrambled": {"64": {"c3_r5":..,"c2_r5":..}, "256":..., "1024":...},
     "mismatched": {"64": {"c3_r5":..,"c2_r5":..,"retention":..}, ...},
     "random_projection": {"c3_r5":..,"rp_r5":..}}, ...}, "43": {...}}}
"""
import json
import sys

KS = ("64", "256", "1024")


def check(path):
    d = json.load(open(path))
    v = []
    if not d.get("disjointness_ok"):
        v.append("control 4: disjointness not established by code")
    nf = d.get("native_floor", {})
    for sp in d.get("primary_pair", []):
        if nf.get(sp, 0) < 0.90:
            v.append(f"control 5: primary space {sp} native R@5 {nf.get(sp)} < 0.90; STOP for the PI")
    for sp, r in nf.items():
        if r < 0.90 and sp not in d.get("primary_pair", []):
            print(f"note: {sp} native R@5 {r} < 0.90; excluded from the boundary map, number published")
    for s in ("41", "43"):
        for dr, c in d.get("cells", {}).get(s, {}).items():
            sc = c.get("scrambled", {})
            mm = c.get("mismatched", {})
            for k in KS:
                if k not in sc:
                    v.append(f"seed {s} {dr}: scrambled arm missing at {k}")
                elif abs(sc[k]["c3_r5"] - sc[k]["c2_r5"]) > 0.05:
                    v.append(f"seed {s} {dr}: control 1 scrambled anchors at {k}: C3 {sc[k]['c3_r5']} not within 0.05 of C2 {sc[k]['c2_r5']}")
                if k not in mm:
                    v.append(f"seed {s} {dr}: mismatched arm missing at {k}")
                else:
                    if abs(mm[k]["c3_r5"] - mm[k]["c2_r5"]) > 0.05:
                        v.append(f"seed {s} {dr}: control 2 mismatched anchors at {k}: C3 {mm[k]['c3_r5']} not within 0.05 of C2 {mm[k]['c2_r5']}")
                    if mm[k].get("retention", 1) >= 0.25:
                        v.append(f"seed {s} {dr}: control 2 mismatched retention {mm[k].get('retention')} not below 0.25 at {k}")
            rp = c.get("random_projection")
            if rp is None:
                v.append(f"seed {s} {dr}: random-projection arm missing")
            elif rp["c3_r5"] - rp["rp_r5"] < 0.20:
                v.append(f"seed {s} {dr}: control 3: C3 {rp['c3_r5']} not >= random projection {rp['rp_r5']} + 0.20")
    return v


def main():
    vs = check(sys.argv[1])
    for x in vs:
        print(f"VIOLATION [{sys.argv[1]}]: {x}")
    if not vs:
        print(f"controls hold: {sys.argv[1]}")
    return 1 if vs else 0


if __name__ == "__main__":
    sys.exit(main())
