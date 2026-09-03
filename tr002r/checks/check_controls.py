#!/usr/bin/env python3
"""TR-002r negative controls. Every block is required (the TR-015
D21 lesson, structural since TR-004).

Schema (results/controls.json):
{
  "shuffled_target": {"top1": f, "chance": f},
  "wrong_model": {"top1": f, "genuine_top1": f},
  "disjointness": {"halves_overlap": int, "train_eval_overlap": int},
  "domain_shift": {"reported": bool, "note": str}
}
"""
import json
import sys

SHUF_MULT, WRONG_FRAC, WRONG_ABS = 10, 0.1, 0.05


def check(path):
    d = json.load(open(path))
    v = []
    st = d.get("shuffled_target")
    if not st:
        v.append("control 1 (shuffled target) missing")
    elif st["top1"] > SHUF_MULT * st["chance"]:
        v.append(f"control 1: shuffled-target top-1 {st['top1']} exceeds "
                 f"{SHUF_MULT}x chance; the pipeline manufactures alignment")
    wm = d.get("wrong_model")
    if not wm:
        v.append("control 2 (wrong model, amendment two) missing")
    else:
        if wm["top1"] >= WRONG_FRAC * wm["genuine_top1"] \
                or wm["top1"] >= WRONG_ABS:
            v.append(f"control 2: wrong-model top-1 {wm['top1']} does not "
                     f"collapse (genuine {wm['genuine_top1']}); the "
                     f"translation exploits gallery geometry, not "
                     f"model-specific alignment")
    dj = d.get("disjointness")
    if not dj:
        v.append("control 3 (disjointness) missing")
    else:
        if dj.get("halves_overlap", 1) != 0:
            v.append("control 3: unpaired training halves share documents")
        if dj.get("train_eval_overlap", 1) != 0:
            v.append("control 3: eval set overlaps training")
    if not d.get("domain_shift", {}).get("reported"):
        v.append("control 4 (domain shift) not reported (reported, "
                 "never gated; absence is the violation)")
    return v


def main():
    if len(sys.argv) != 2:
        return 2
    vs = check(sys.argv[1])
    for x in vs:
        print(f"VIOLATION [{sys.argv[1]}]: {x}")
    if not vs:
        print(f"controls hold: {sys.argv[1]}")
    return 1 if vs else 0


if __name__ == "__main__":
    sys.exit(main())
