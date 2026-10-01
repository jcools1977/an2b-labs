#!/usr/bin/env python3
"""TR-013 corpus gate (D3, D4). Schema (data/CORPUS_MANIFEST.json):
{"models": [2 ids], "task_types": [3], "temperatures": [0.0, 0.3], "horizon": 80,
 "turn_tokens": 120, "runs_total": n, "collapse_runs": n, "control_runs_matched": n,
 "matched_by": ["model","task","temperature","length"],
 "labeler": {"ngram_overlap": 0.6, "selfsim": 0.95, "consecutive": 3},
 "audit_sample": {"n": int, "fraction": float, "stratified": true}, "seeds": [41, 43]}
"""
import json
import sys


def check(path):
    d = json.load(open(path))
    v = []
    if len(d.get("models", [])) != 2:
        v.append("two small local models required (D3)")
    if sorted(d.get("task_types", [])) != ["loop", "rephrase", "self_dialogue"]:
        v.append("task types are not the three frozen in D3")
    if d.get("temperatures") != [0.0, 0.3]:
        v.append("temperatures are not {0.0, 0.3} (D3)")
    if d.get("horizon") != 80 or d.get("turn_tokens") != 120:
        v.append("horizon or turn length not the frozen D3 values")
    if d.get("collapse_runs", 0) < 300:
        v.append(f"{d.get('collapse_runs')} collapse runs; protocol requires 300")
    if d.get("control_runs_matched", 0) < 300:
        v.append(f"{d.get('control_runs_matched')} matched controls; protocol requires 300")
    if d.get("matched_by") != ["model", "task", "temperature", "length"]:
        v.append("controls not matched on model, task, temperature and length (D4)")
    lb = d.get("labeler", {})
    if (lb.get("ngram_overlap"), lb.get("selfsim"), lb.get("consecutive")) != (0.6, 0.95, 3):
        v.append("labeler thresholds are not the frozen D4 values")
    a = d.get("audit_sample", {})
    if a.get("fraction", 0) < 0.10 or not a.get("stratified"):
        v.append("audit sample under 10 percent or not stratified (control 3)")
    if d.get("seeds") != [41, 43]:
        v.append("seeds are not the frozen (41, 43)")
    return v


def main():
    vs = check(sys.argv[1])
    for x in vs:
        print(f"VIOLATION [{sys.argv[1]}]: {x}")
    if not vs:
        print(f"corpus integrity holds: {sys.argv[1]}")
    return 1 if vs else 0


if __name__ == "__main__":
    sys.exit(main())
