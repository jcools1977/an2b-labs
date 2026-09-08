#!/usr/bin/env python3
"""TR-003r figures from results/grid.jsonl (matplotlib, headless).
fig1_survival.png: primary pair, Q1, random anchors: retention,
provenance, confident-wrong vs anchor count, C3 and C4, both
directions, seeds as markers, with the frozen bars drawn.
fig2_boundary.png: class-stratified boundary map at 1,024 random
anchors: C3 retention per ordered pair, colored by class.
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

TR = Path(__file__).resolve().parents[1]
ENC = {"bge", "e5", "minilm"}
KS = [64, 256, 1024]


def cls(pair):
    a, b = pair.split("->")
    return ("encoder-encoder" if a in ENC and b in ENC else
            "decoder-decoder" if a not in ENC and b not in ENC else "encoder-decoder")


def main():
    rows = [json.loads(l) for l in open(TR / "results" / "grid.jsonl") if l.strip()]
    out = TR / "report"
    out.mkdir(exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    for ax, metric, bar, title in zip(axes, ("retention", "provenance_work", "confident_wrong"),
                                      (0.80, 0.90, 0.05), ("retention of native R@5", "work-level provenance survival", "confident-wrong rate")):
        for cond, ls in (("C3", "-"), ("C4", "--")):
            for dr, col in (("bge->minilm", "C0"), ("minilm->bge", "C1")):
                for seed, mk in ((41, "o"), (43, "s")):
                    ys = []
                    for k in KS:
                        r = [x for x in rows if x.get("seed") == seed and x.get("qkind") == "q1" and x.get("pair") == dr
                             and x.get("condition") == cond and x.get("anchors") == k and x.get("selection") == "random" and x.get("arm") is None]
                        ys.append(r[0][metric] if r else float("nan"))
                    ax.plot(KS, ys, ls, marker=mk, color=col, alpha=0.85,
                            label=f"{cond} {dr} s{seed}" if metric == "retention" else None)
        ax.axhline(bar, color="k", lw=0.8, ls=":")
        ax.set_xscale("log", base=2)
        ax.set_xticks(KS)
        ax.set_xticklabels([str(k) for k in KS])
        ax.set_xlabel("anchors (random)")
        ax.set_title(title, fontsize=10)
    axes[0].legend(fontsize=6, ncol=2)
    fig.suptitle("TR-003r primary pair, Q1: what survives translation (bars = frozen gates)")
    fig.tight_layout()
    fig.savefig(out / "fig1_survival.png", dpi=150)

    fig, ax = plt.subplots(figsize=(11, 4.5))
    pairs = sorted({x["pair"] for x in rows if x.get("pair")}, key=lambda p: (cls(p), p))
    colors = {"encoder-encoder": "C2", "decoder-decoder": "C3", "encoder-decoder": "C4"}
    for i, p in enumerate(pairs):
        for cond, mk in (("C3", "o"), ("C4", "_")):
            vals = [x["retention"] for x in rows if x.get("qkind") == "q1" and x.get("pair") == p and x.get("condition") == cond
                    and x.get("anchors") == 1024 and x.get("selection") == "random" and x.get("arm") is None]
            if vals:
                ax.scatter([i] * len(vals), vals, marker=mk, color=colors[cls(p)], s=40 if mk == "o" else 120)
    ax.axhline(0.80, color="k", lw=0.8, ls=":")
    ax.set_xticks(range(len(pairs)))
    ax.set_xticklabels(pairs, rotation=75, fontsize=7)
    ax.set_ylabel("retention of native R@5 at 1,024 random anchors")
    ax.set_title("Boundary map: C3 (dots) and C4 ceiling (bars), colored by class")
    fig.tight_layout()
    fig.savefig(out / "fig2_boundary.png", dpi=150)
    print("figures written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
