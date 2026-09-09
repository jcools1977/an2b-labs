#!/usr/bin/env python3
"""Read-only summary of results/grid.jsonl for the report: natives,
per-pair boundary map at 1,024 random anchors (Q1), class means,
Q2 on the primary, medoid vs random, direction asymmetry, C4
confident-wrong at 64 anchors. Writes results/summary.json."""
import json
from collections import defaultdict
from pathlib import Path

TR = Path(__file__).resolve().parents[1]
ENC = {"bge", "e5", "minilm"}
rows = [json.loads(l) for l in open(TR / "results" / "grid.jsonl") if l.strip()]


def cls(pair):
    a, b = pair.split("->")
    return ("enc-enc" if a in ENC and b in ENC else "dec-dec" if a not in ENC and b not in ENC else "enc-dec")


def get(**kw):
    return [r for r in rows if all(r.get(k) == v for k, v in kw.items())]


def mean(xs):
    return sum(xs) / len(xs) if xs else float("nan")


out = {"natives": {}, "pairs": {}, "class_means": {}, "primary_q2": {}, "asymmetry": {}}
print("=== natives C1 (Q1, Q2) R@5 by space, mean of seeds ===")
for sp in ["bge", "e5", "minilm", "llama4", "qwen4", "gemma4"]:
    q1 = mean([r["r5"] for r in get(condition="C1", space=sp, qkind="q1")])
    q2 = mean([r["r5"] for r in get(condition="C1", space=sp, qkind="q2")])
    cw = mean([r["confident_wrong"] for r in get(condition="C1", space=sp, qkind="q1")])
    out["natives"][sp] = {"q1_r5": q1, "q2_r5": q2, "q1_cw": cw}
    print(f"  {sp:7} Q1 {q1:.3f}  Q2 {q2:.3f}  cw {cw:.3f}  {'BELOW 0.90 FLOOR' if q1 < 0.90 else ''}")
print("\n=== boundary map, Q1, 1,024 random anchors, mean of seeds (retention = R@5 / native) ===")
print(f"  {'pair':16} {'class':8} {'C2 r5':>6} {'C3 ret':>7} {'C4 ret':>7} {'scr r5':>7} {'C3 prov':>8} {'C4 prov':>8} {'C4@64 cw':>9} {'medoid dC3':>10}")
pairs = sorted({r["pair"] for r in rows if r.get("pair")}, key=lambda p: (cls(p), p))
by_cls = defaultdict(lambda: defaultdict(list))
for p in pairs:
    c2 = mean([r["r5"] for r in get(pair=p, qkind="q1", condition="C2")])
    c3 = get(pair=p, qkind="q1", condition="C3", anchors=1024, selection="random", arm=None)
    c4 = get(pair=p, qkind="q1", condition="C4", anchors=1024, selection="random", arm=None)
    sc = get(pair=p, qkind="q1", condition="C3", anchors=1024, selection="random", arm="scrambled")
    c3m = get(pair=p, qkind="q1", condition="C3", anchors=1024, selection="medoid", arm=None)
    c4_64 = get(pair=p, qkind="q1", condition="C4", anchors=64, selection="random", arm=None)
    rec = {"class": cls(p), "c2_r5": c2, "c3_ret": mean([r["retention"] for r in c3]),
           "c4_ret": mean([r["retention"] for r in c4]), "scr_r5": mean([r["r5"] for r in sc]),
           "c3_prov": mean([r["provenance_work"] for r in c3]), "c4_prov": mean([r["provenance_work"] for r in c4]),
           "c4_64_cw": mean([r["confident_wrong"] for r in c4_64]),
           "medoid_minus_random_c3_r5": mean([r["r5"] for r in c3m]) - mean([r["r5"] for r in c3]),
           "c3_r5": mean([r["r5"] for r in c3]), "c4_r5": mean([r["r5"] for r in c4])}
    out["pairs"][p] = rec
    for k, v in rec.items():
        if isinstance(v, float):
            by_cls[rec["class"]][k].append(v)
    print(f"  {p:16} {rec['class']:8} {c2:6.3f} {rec['c3_ret']:7.3f} {rec['c4_ret']:7.3f} {rec['scr_r5']:7.3f} {rec['c3_prov']:8.3f} {rec['c4_prov']:8.3f} {rec['c4_64_cw']:9.3f} {rec['medoid_minus_random_c3_r5']:+10.3f}")
print("\n=== class means ===")
for c, d in by_cls.items():
    out["class_means"][c] = {k: mean(v) for k, v in d.items()}
    print(f"  {c:8} C2 {mean(d['c2_r5']):.3f}  C3 ret {mean(d['c3_ret']):.3f}  C4 ret {mean(d['c4_ret']):.3f}  scrambled {mean(d['scr_r5']):.3f}  C4@64 cw {mean(d['c4_64_cw']):.3f}")
print("\n=== primary pair, Q2 neighbor recall, 1,024 random ===")
for dr in ("bge->minilm", "minilm->bge"):
    for cond in ("C2", "C3", "C4"):
        kw = dict(pair=dr, qkind="q2", condition=cond)
        if cond != "C2":
            kw.update(anchors=1024, selection="random", arm=None)
        rr = get(**kw)
        out["primary_q2"][f"{dr}|{cond}"] = {"r5": mean([r["r5"] for r in rr]), "ret": mean([r["retention"] for r in rr]), "prov": mean([r["provenance_work"] for r in rr])}
        print(f"  {dr:13} {cond} r5 {mean([r['r5'] for r in rr]):.3f} ret {mean([r['retention'] for r in rr]):.3f} prov {mean([r['provenance_work'] for r in rr]):.3f}")
print("\n=== primary anchor-count curve, C3 random, Q1, mean of seeds (r5) ===")
for dr in ("bge->minilm", "minilm->bge"):
    curve = [mean([r["r5"] for r in get(pair=dr, qkind="q1", condition="C3", anchors=k, selection="random", arm=None)]) for k in (64, 256, 1024)]
    curve4 = [mean([r["r5"] for r in get(pair=dr, qkind="q1", condition="C4", anchors=k, selection="random", arm=None)]) for k in (64, 256, 1024)]
    out["asymmetry"][dr] = {"c3_curve": curve, "c4_curve": curve4}
    print(f"  {dr:13} C3 {curve}  C4 {curve4}")
json.dump(out, open(TR / "results" / "summary.json", "w"), indent=1)
