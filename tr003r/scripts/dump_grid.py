#!/usr/bin/env python3
"""Print the grid for one seed and query kind, all pairs. Read-only."""
import json
import sys
from pathlib import Path

TR = Path(__file__).resolve().parents[1]
seed = int(sys.argv[1]) if len(sys.argv) > 1 else 41
qk = sys.argv[2] if len(sys.argv) > 2 else "q1"
rows = [json.loads(l) for l in open(TR / "results" / "grid.jsonl") if l.strip()]
print(f"=== natives (C1) {qk} seed {seed} ===")
for r in rows:
    if r["condition"] == "C1" and r["qkind"] == qk and r["seed"] == seed:
        print(f"  {r['space']:7} r5={r['r5']:.3f} r1={r['r1']:.3f} cw={r['confident_wrong']:.3f} margin={r['median_margin']:.4f}")
pairs = sorted({r["pair"] for r in rows if r.get("pair")})
for pair in pairs:
    print(f"--- {pair} ---")
    for r in rows:
        if r.get("pair") == pair and r["qkind"] == qk and r["seed"] == seed:
            print(f"  {r['condition']:3} k={str(r.get('anchors')):5} {str(r.get('selection')):7} {str(r.get('arm')):18} "
                  f"r5={r['r5']:.3f} ret={r['retention']:.3f} prov={r['provenance_work']:.3f} "
                  f"cw={r['confident_wrong']:.3f} excess={r['excess_confident_wrong']:+.3f} jac={r.get('jaccard10', 0):.3f}")
