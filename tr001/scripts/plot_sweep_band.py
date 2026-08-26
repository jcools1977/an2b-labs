#!/usr/bin/env python3
"""Figure 1: the sweep band. Selection-split F1 for all 16 trained
configurations, the four divergent configs marked distinctly (shape as
well as color), the four untrainable slots shown as a labeled vacancy
(D25), and the selection bar, text baseline, and floor as labeled
reference lines. Reads only committed result files, so the figure is
reproducible from the repository.

Palette: reference dataviz slots 1-2, validated (CVD dE 24.7, normal
33.6, all checks pass on the light surface).
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

TR_ROOT = Path(__file__).resolve().parents[1]

BLUE, ORANGE = "#2a78d6", "#eb6834"  # slots 1-2, validated
SURFACE, INK, INK2 = "#fcfcfb", "#0b0b0b", "#52514e"
GRID = "#e4e3df"

ORDER = ["L01", "L02", "L03", "L04", "L05", "L06",
         "CLOSED",  # LC07-LC10 vacancy (D25)
         "M11", "M12", "M13", "M14", "M15", "M16",
         "MC17", "MC18", "MC19", "MC20"]
DIVERGENT = {"L06", "M16", "MC19", "MC20"}
GROUPS = [("linear / final", 0, 5), ("MLP / final", 7, 12), ("MLP / last4", 13, 16)]

BAR, C2_SEL, C4_SEL = 48.56, 43.56, 20.15


def main():
    f1 = {
        cid: json.load(open(TR_ROOT / "results" / f"dev_{cid}_seed1.json"))["f1"]
        for cid in ORDER if cid != "CLOSED"
    }

    fig, ax = plt.subplots(figsize=(9, 5), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    for y, label, style in [
        (BAR, f"selection bar {BAR:.1f}", (0, (5, 3))),
        (C2_SEL, f"text baseline C2 {C2_SEL:.1f}", (0, (2, 2))),
        (C4_SEL, f"no-context floor C4 {C4_SEL:.1f}", (0, (2, 2))),
    ]:
        ax.axhline(y, color=INK2, lw=1, ls=style, zorder=1)
        ax.text(len(ORDER) - 0.4, y + 0.7, label, ha="right", fontsize=8.5,
                color=INK2, zorder=4)

    for i, cid in enumerate(ORDER):
        if cid == "CLOSED":
            continue
        v = f1[cid]
        if cid in DIVERGENT:
            ax.scatter(i, v, marker="x", s=70, color=ORANGE, lw=2, zorder=3)
        else:
            ax.scatter(i, v, marker="o", s=55, color=BLUE, zorder=3)

    ci = ORDER.index("CLOSED")
    ax.axvspan(ci - 0.45, ci + 0.45, color=GRID, alpha=0.6, zorder=0)
    ax.text(ci, 33, "LC07–10\nuntrainable\n(D25)", ha="center", va="center",
            fontsize=8, color=INK2, zorder=4)

    best = max((v, k) for k, v in f1.items())
    ax.annotate(f"best: {best[1]}  {best[0]:.1f}",
                xy=(ORDER.index(best[1]), best[0]),
                xytext=(ORDER.index(best[1]) - 1.6, best[0] + 4.5),
                fontsize=9, color=INK,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))

    for label, a, b in GROUPS:
        ax.text((a + b) / 2, -7.5, label, ha="center", fontsize=9, color=INK2)

    ax.set_xticks([i for i, c in enumerate(ORDER) if c != "CLOSED"])
    ax.set_xticklabels([c for c in ORDER if c != "CLOSED"], fontsize=8, color=INK2)
    ax.set_ylabel("selection-split F1 (250 pairs, greedy)", fontsize=9.5, color=INK)
    ax.set_ylim(-2, 55)
    ax.set_xlim(-0.7, len(ORDER) - 0.3)
    ax.tick_params(colors=INK2, length=0)
    ax.grid(axis="y", color=GRID, lw=0.7, zorder=0)
    for s in ax.spines.values():
        s.set_visible(False)

    handles = [
        plt.Line2D([], [], marker="o", ls="", color=BLUE, markersize=8,
                   label="convergent (12)"),
        plt.Line2D([], [], marker="x", ls="", color=ORANGE, markersize=8,
                   markeredgewidth=2, label="diverged (4)"),
    ]
    ax.legend(handles=handles, loc="upper left", frameon=False, fontsize=9,
              labelcolor=INK)

    ax.set_title(
        "TR-001 sweep: every trained configuration, one band, one bar",
        fontsize=11.5, color=INK, pad=12,
    )
    out = TR_ROOT / "report" / "fig1_sweep_band.png"
    fig.tight_layout()
    fig.savefig(out, facecolor=SURFACE, bbox_inches="tight")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
