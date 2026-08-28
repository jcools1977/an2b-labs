#!/usr/bin/env python3
"""Figure 1 for TR-020: textual influence rate for all 29 seeded
components, grouped by ablation verdict. The picture is the argument:
four of five dead components sit at 0.993-1.000, inside the live
cluster, and only the vocabulary-disjoint plant is separable. No
threshold on this axis distinguishes dead from live.

Palette: reference dataviz slots 1-3 (documented as all-pairs valid in
both modes). Reads only committed result files.
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

TR_ROOT = Path(__file__).resolve().parents[1]

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"  # slots 1-3
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"


def main():
    rows = json.load(open(TR_ROOT / "results" / "surrogate.json"))["per_component"]
    lanes = {"live": 0, "redundant": 1, "dead": 2}
    colors = {"live": BLUE, "redundant": AQUA, "dead": ORANGE}
    markers = {"live": "o", "redundant": "s", "dead": "x"}

    fig, ax = plt.subplots(figsize=(7.5, 5.2), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    import collections
    tie = collections.defaultdict(int)
    for r in rows:
        v = r["ablation_verdict"]
        y = r["influence_rate"]
        k = tie[(v, round(y, 2))]
        tie[(v, round(y, 2))] += 1
        dx = (k % 5 - 2) * 0.11
        dy = (k // 5) * 0.018
        x = lanes[v] + dx
        kw = dict(color=colors[v], zorder=3)
        if markers[v] == "x":
            ax.scatter(x, y + dy, marker="x", s=90, lw=2.4, **kw)
        else:
            ax.scatter(x, y + dy, marker=markers[v], s=52, **kw)

    ax.axhline(0.05, color=INK2, lw=1, ls=(0, (5, 3)), zorder=1)
    ax.text(-0.44, 0.07, "frozen dead threshold 0.05", fontsize=8.5, color=INK2)

    ax.annotate("the one catch:\nvocabulary-disjoint plant", xy=(2.0, 0.0),
                xytext=(0.9, 0.12), fontsize=8.5, color=INK,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
    ax.annotate("four dead components level with\nthe live cluster: no threshold\nseparates them",
                xy=(2.0, 0.99), xytext=(0.62, 0.72), fontsize=8.5, color=INK,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))

    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["live (20)", "redundant (4)", "dead (5)"],
                       fontsize=9.5, color=INK)
    ax.set_ylabel("textual influence rate (frozen tracer, 150 probes per system)",
                  fontsize=9.5, color=INK)
    ax.set_ylim(-0.06, 1.12)
    ax.set_xlim(-0.55, 2.55)
    ax.tick_params(colors=INK2, length=0)
    ax.grid(axis="y", color=GRID, lw=0.7, zorder=0)
    for sp in ax.spines.values():
        sp.set_visible(False)

    ax.set_title("Topicality is not causality: textual influence cannot find dead components",
                 fontsize=11.5, color=INK, pad=12)
    out = TR_ROOT / "report" / "fig1_surrogate_overlap.png"
    fig.tight_layout()
    fig.savefig(out, facecolor=SURFACE, bbox_inches="tight")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
