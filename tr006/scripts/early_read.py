#!/usr/bin/env python3
"""Read-only single-seed look at the main grid (reported only; never a
verdict, which needs both seeds through the checkers).
Usage: early_read.py [seed]"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.regime import S_GRID, regime_test  # noqa: E402

TR = Path(__file__).resolve().parents[1]
seed = sys.argv[1] if len(sys.argv) > 1 else "41"
raw = TR / "results" / "raw" / seed


def acc(name):
    p = raw / name
    if not p.exists():
        return None
    rows = [json.loads(l) for l in open(p) if l.strip()]
    return sum(r["correct"] for r in rows) / max(1, len(rows))


for fam in ("hotpot", "puzzles"):
    pts = []
    for s in S_GRID:
        for F in (1, 2, 4):
            p = raw / f"{fam}__main_S{s}_F{F}.jsonl"
            if not p.exists():
                continue
            rows = [json.loads(l) for l in open(p) if l.strip()]
            pts.append({"S": s, "F": F, "k": sum(r["correct"] for r in rows), "n": len(rows)})
    if len(pts) < 18:
        print(f"{fam}: {len(pts)}/18 main points; no read")
        continue
    r = regime_test(pts)
    by_s = {s: sum(p["k"] for p in pts if p["S"] == s) / sum(p["n"] for p in pts if p["S"] == s) for s in S_GRID}
    best = max(pts, key=lambda p: p["k"] / p["n"])
    singles = {m: acc(f"{fam}__single_S1_F1_{m}.jsonl") for m in ("llama", "qwen", "gemma")}
    unl = {F: acc(f"{fam}__unlimited_S1_F{F}.jsonl") for F in (1, 2, 4)}
    print(f"{fam:7} seed {seed}: AIC smooth {r['aic_smooth']:.1f}, regime {r['aic_regime']:.1f}, "
          f"margin {r['aic_margin']:+.1f} (PASS clause needs >= +10); regime breakpoint S={r['breakpoint_S']}")
    print("        acc by S (over F): " + "  ".join(f"S{s}={v:.3f}" for s, v in by_s.items()))
    print(f"        best bounded {best['k']/best['n']:.3f} at S={best['S']} F={best['F']}; "
          f"unlimited by F {({k: round(v, 3) if v is not None else None for k, v in unl.items()})}; "
          f"singles {({k: round(v, 3) if v is not None else None for k, v in singles.items()})}")
