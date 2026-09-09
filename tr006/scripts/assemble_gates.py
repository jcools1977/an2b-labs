#!/usr/bin/env python3
"""Assemble results/{analysis,kill,controls,curves}.json from
results/raw. Pure bookkeeping plus the certified regime test (D8)."""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.regime import regime_test  # noqa: E402

TR = Path(__file__).resolve().parents[1]
S_GRID = [1, 2, 4, 8, 16, 32]


def load_raw(raw_dir):
    acc = {}
    for p in Path(raw_dir).glob("*/*.jsonl"):
        seed = p.parent.name
        fam, cfg = p.stem.split("__", 1)
        rows = [json.loads(l) for l in open(p) if l.strip()]
        acc[(seed, fam, cfg)] = {"k": sum(r["correct"] for r in rows), "n": len(rows),
                                 "last_slot": sum((r.get("final_board_last_slot") or 0) for r in rows),
                                 "parse_fail": sum(r.get("n_parse_fail", 0) for r in rows)}
    return acc


def main():
    raw_dir = sys.argv[1] if len(sys.argv) > 1 else TR / "results" / "raw"
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else TR / "results"
    acc = load_raw(raw_dir)
    analysis, kill, controls, curves = {"seeds": {}}, {"seeds": {}, "killed": False}, {"seeds": {}}, {}
    for seed in ("41", "43"):
        analysis["seeds"][seed], kill["seeds"][seed], controls["seeds"][seed] = {}, {}, {}
        for fam in ("hotpot", "puzzles"):
            pts = []
            for S in S_GRID:
                for F in (1, 2, 4):
                    c = acc.get((seed, fam, f"main_S{S}_F{F}"))
                    if c and c["n"]:
                        pts.append({"S": S, "F": F, "k": c["k"], "n": c["n"], "acc": c["k"] / c["n"],
                                    "last_slot_rate": c["last_slot"] / c["n"]})
            if len(pts) < 18:
                print(f"seed {seed} {fam}: {len(pts)}/18 main points present; gates not assembled")
                continue
            rt = regime_test(pts)
            best = max(pts, key=lambda p: p["acc"])
            singles = {m: acc.get((seed, fam, f"single_S1_F1_{m}")) for m in ("llama", "qwen", "gemma")}
            single_best = max((v["k"] / v["n"]) for v in singles.values() if v and v["n"])
            unl = [acc.get((seed, fam, f"unlimited_S1_F{F}")) for F in (1, 2, 4)]
            unl_best = max((u["k"] / u["n"]) for u in unl if u and u["n"])
            cell = {"aic_smooth": rt["aic_smooth"], "aic_regime": rt["aic_regime"], "aic_margin": rt["aic_margin"],
                    "breakpoint_S": rt["breakpoint_S"], "best_bounded_acc": best["acc"],
                    "best_bounded": {"S": best["S"], "F": best["F"]}, "unlimited_log_best_acc": unl_best,
                    "single_best_acc": single_best, "singles": {m: (v["k"] / v["n"] if v else None) for m, v in singles.items()},
                    "unlimited_by_F": {str(F): (u["k"] / u["n"] if u else None) for F, u in zip((1, 2, 4), unl)}}
            analysis["seeds"][seed][fam] = cell
            kill["seeds"][seed][fam] = {"aic_margin": rt["aic_margin"], "breakpoint_S": rt["breakpoint_S"]}
            curves[f"{seed}:{fam}"] = {"points": pts, "regime": rt["regime"], "smooth": rt["smooth"]}
            # controls at F=1 across S
            def ctrl_pts(mode):
                out = []
                for S in S_GRID:
                    c = acc.get((seed, fam, f"{mode}_S{S}_F1"))
                    if c and c["n"]:
                        out.append({"S": S, "F": 1, "k": c["k"], "n": c["n"], "acc": c["k"] / c["n"]})
                return out
            rs, fz, sh = ctrl_pts("random_salience"), ctrl_pts("frozen"), ctrl_pts("role_shuffle")
            if len(rs) == 6 and len(fz) == 6 and len(sh) == 6:
                main_f1 = [p for p in pts if p["F"] == 1]
                sh_best = next((p["acc"] for p in sh if p["S"] == best["S"]), None) if best["F"] == 1 else None
                # role shuffle is run at F=1; compare at the best bounded S using the F=1 main curve
                main_at_bestS_f1 = next(p["acc"] for p in main_f1 if p["S"] == best["S"])
                sh_at_bestS = next(p["acc"] for p in sh if p["S"] == best["S"])
                controls["seeds"][seed][fam] = {
                    "main_aic_margin": rt["aic_margin"],
                    "random_salience_aic_margin": regime_test(rs)["aic_margin"],
                    "frozen_buffer_best_acc": max(p["acc"] for p in fz), "single_best_acc": single_best,
                    "role_shuffle_acc": sh_at_bestS, "main_best_bounded_acc": main_at_bestS_f1,
                    "note": "controls run at F=1; role shuffle compared at the best bounded S on the F=1 main curve",
                    "curves": {"random_salience": rs, "frozen": fz, "role_shuffle": sh}}
    seeds_ok = [s for s in ("41", "43") if len(kill["seeds"][s]) == 2]
    import math
    kill["killed"] = any(
        kill["seeds"][s]["hotpot"]["aic_margin"] >= 10 and kill["seeds"][s]["puzzles"]["aic_margin"] >= 10
        and abs(math.log2(kill["seeds"][s]["hotpot"]["breakpoint_S"]) - math.log2(kill["seeds"][s]["puzzles"]["breakpoint_S"])) > 1
        for s in seeds_ok)
    out = out_dir
    out.mkdir(parents=True, exist_ok=True)
    json.dump(analysis, open(out / "analysis.json", "w"), indent=1)
    json.dump(kill, open(out / "kill.json", "w"), indent=1)
    json.dump(controls, open(out / "controls.json", "w"), indent=1)
    json.dump(curves, open(out / "curves.json", "w"), indent=1)
    print(f"assembled: {sum(len(v) for v in analysis['seeds'].values())} gate cells, killed={kill['killed']}, "
          f"{sum(len(v) for v in controls['seeds'].values())} control cells")
    return 0


if __name__ == "__main__":
    sys.exit(main())
