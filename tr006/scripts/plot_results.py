#!/usr/bin/env python3
"""TR-006 figures from results/curves.json, analysis.json, controls.json.
fig1_capacity.png: accuracy vs S per family, both seeds, one line per
F, with the unlimited-log best and single-best-agent reference lines.
fig2_controls.png: at F=1, main vs frozen vs role-shuffle vs random
salience per family and seed."""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

TR = Path(__file__).resolve().parents[1]
S = [1, 2, 4, 8, 16, 32]
import os
RES = Path(os.environ.get("TR006_RESULTS", TR / "results"))
cv = json.load(open(RES / "curves.json"))
an = json.load(open(RES / "analysis.json"))
ct = json.load(open(RES / "controls.json"))
out = TR / "report"
out.mkdir(exist_ok=True)
NAME = {"hotpot": "multi-hop QA", "puzzles": "constraint puzzles"}

fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharex=True)
for i, fam in enumerate(("hotpot", "puzzles")):
    for j, seed in enumerate(("41", "43")):
        ax = axes[i][j]
        pts = cv[f"{seed}:{fam}"]["points"]
        for F, col in ((1, "C0"), (2, "C1"), (4, "C2")):
            ys = [next(p["acc"] for p in pts if p["S"] == s and p["F"] == F) for s in S]
            ax.plot(S, ys, marker="o", color=col, label=f"bounded, F={F}")
        a = an["seeds"][seed][fam]
        ax.axhline(a["unlimited_log_best_acc"], color="k", ls="--", lw=1, label="unlimited log (best F)")
        ax.axhline(a["single_best_acc"], color="gray", ls=":", lw=1, label="single best agent")
        ax.axvspan(6, 40, color="0.92", zorder=0)
        ax.set_xscale("log", base=2)
        ax.set_xticks(S)
        ax.set_xticklabels([str(s) for s in S])
        ax.set_title(f"{NAME[fam]}, seed {seed}: AIC margin {a['aic_margin']:+.1f}", fontsize=10)
        ax.set_ylim(0, 0.45)
        if i == 1:
            ax.set_xlabel("workspace capacity S (slots); shaded: cut never binds at R=2")
        if j == 0:
            ax.set_ylabel("accuracy (200 items)")
        if i == 0 and j == 0:
            ax.legend(fontsize=7)
fig.suptitle("TR-006: accuracy vs workspace capacity (PASS needed a regime with AIC margin >= 10 in both families)")
fig.tight_layout()
fig.savefig(out / "fig1_capacity.png", dpi=150)

fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharex=True)
for i, fam in enumerate(("hotpot", "puzzles")):
    for j, seed in enumerate(("41", "43")):
        ax = axes[i][j]
        pts = cv[f"{seed}:{fam}"]["points"]
        main = [next(p["acc"] for p in pts if p["S"] == s and p["F"] == 1) for s in S]
        c = ct["seeds"][seed][fam]["curves"]
        ax.plot(S, main, marker="o", color="C0", label="main (self-assessed salience)")
        ax.plot(S, [p["acc"] for p in c["random_salience"]], marker="s", color="C3", label="random salience")
        ax.plot(S, [p["acc"] for p in c["frozen"]], marker="^", color="C4", label="frozen round-1 buffer")
        ax.plot(S, [p["acc"] for p in c["role_shuffle"]], marker="v", color="C5", label="roles shuffled")
        ax.axhline(an["seeds"][seed][fam]["single_best_acc"], color="gray", ls=":", lw=1, label="single best agent")
        ax.set_xscale("log", base=2)
        ax.set_xticks(S)
        ax.set_xticklabels([str(s) for s in S])
        ax.set_ylim(0, 0.45)
        ax.set_title(f"{NAME[fam]}, seed {seed}, F=1", fontsize=10)
        if i == 1:
            ax.set_xlabel("workspace capacity S (slots)")
        if j == 0:
            ax.set_ylabel("accuracy (200 items)")
        if i == 0 and j == 0:
            ax.legend(fontsize=7)
fig.suptitle("TR-006 controls at F=1: the null and its mechanism")
fig.tight_layout()
fig.savefig(out / "fig2_controls.png", dpi=150)
print("figures written")
