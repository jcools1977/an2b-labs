#!/usr/bin/env python3
"""The entropy-trace visualizer (protocol deliverable), honestly
labeled: a temperature strip of a manuscript's per-token entropy under
a language model. TR-011's verdict means these strips read style and
subject, not craft; they remain an instrument for seeing a
manuscript's texture, published here as numbers only (D11).

Tool use: plot_entropy_trace.py <series.npz> [<series2.npz>] [out.png]
Report mode (no args): renders Figure 1 from the highest-cosine
surviving lineage pair, scoring model Llama, rolling-mean smoothed.
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

TR_ROOT = Path(__file__).resolve().parents[1]
BLUE, ORANGE = "#2a78d6", "#eb6834"  # validated dataviz slots 1-2
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"


def smooth(x, w=25):
    if len(x) < w:
        return x
    k = np.ones(w) / w
    return np.convolve(x, k, mode="valid")


def strip(ax, npz_path, color, label):
    d = np.load(npz_path)
    e = smooth(d["entropy"].astype(float))
    x = np.arange(len(e))
    ax.plot(x, e, color=color, lw=1.6, zorder=3)
    ax.fill_between(x, e, e.min() - 0.05, color=color, alpha=0.10, zorder=2)
    ax.text(0.01, 0.92, label, transform=ax.transAxes, fontsize=9.5,
            color=INK, va="top")
    ax.set_facecolor(SURFACE)
    ax.grid(axis="y", color=GRID, lw=0.6, zorder=0)
    ax.tick_params(colors=INK2, length=0, labelsize=8)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.margins(x=0)


def main():
    args = sys.argv[1:]
    if args and args[0].endswith(".npz"):
        paths = [Path(a) for a in args if a.endswith(".npz")][:2]
        out = Path(args[-1]) if args[-1].endswith(".png") else Path("entropy_trace.png")
        labels = [p.stem for p in paths]
        title = "Entropy trace"
    else:
        manifest = json.load(open(TR_ROOT / "data" / "CORPUS_MANIFEST.json"))
        pairs = [p for p in manifest["corpus_a"]["pairing"]
                 if p["draft"] != "a_draft_03"]
        pair = max(pairs, key=lambda p: p["cosine"])
        cache = next((TR_ROOT / "corpus_store" / "entropy").iterdir()) / "llama"
        paths = [cache / f"{pair['published']}.npz", cache / f"{pair['draft']}.npz"]
        labels = [f"published unit ({pair['published']})",
                  f"December draft unit ({pair['draft']}), cosine {pair['cosine']}"]
        out = TR_ROOT / "report" / "fig1_entropy_trace.png"
        title = ("The temperature of revision: the published form runs hotter "
                 "than its predecessor")

    fig, axes = plt.subplots(len(paths), 1, figsize=(9, 2.1 * len(paths) + 0.8),
                             dpi=200, sharey=True)
    axes = np.atleast_1d(axes)
    fig.patch.set_facecolor(SURFACE)
    for ax, p, c, l in zip(axes, paths, [BLUE, ORANGE], labels):
        strip(ax, p, c, l)
    axes[-1].set_xlabel("token position (rolling mean, window 25)",
                        fontsize=9, color=INK2)
    axes[0].set_title(title, fontsize=11.5, color=INK, pad=10)
    fig.text(0.005, 0.5, "entropy (nats)", rotation=90, va="center",
             fontsize=9, color=INK2)
    fig.tight_layout(rect=(0.02, 0, 1, 1))
    fig.savefig(out, facecolor=SURFACE, bbox_inches="tight")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
