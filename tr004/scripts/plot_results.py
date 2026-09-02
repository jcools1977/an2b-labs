#!/usr/bin/env python3
"""TR-004 report figures.

Fig 1: forest plot of every Cliff's delta the experiment read, with
the zero line and the frozen 0.2 gate; gated, comparator, and fenced
sections labeled.
Fig 2: the distribution of per-lemma paired LID differences (PR,
layer 16), colored by part of speech; the honest curvature atlas,
which turned out to be a small shift rather than a map.
"""
import json
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TR_ROOT))
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from analysis.lid import pr  # noqa: E402

STORE = TR_ROOT / "corpus_store"
BLUE, ORANGE, PURPLE = "#2a78d6", "#eb6834", "#7d54c9"
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"


def fig1(detail):
    rows = [
        ("PR, layer 16 (gated)", detail["main"]["pr"], BLUE),
        ("MLE, layer 16 (gated)", detail["main"]["mle"], BLUE),
        ("PR after controls (gated)", detail["main"]["pr_after_controls"], BLUE),
        ("MLE after controls (gated)", detail["main"]["mle_after_controls"], BLUE),
        ("PR, bge comparator", detail["model2"]["pr"], ORANGE),
        ("MLE, bge comparator", detail["model2"]["mle"], ORANGE),
        ("PR, layer 8 (fenced)", detail["layers"]["8"]["pr"], PURPLE),
        ("MLE, layer 8 (fenced)", detail["layers"]["8"]["mle"], PURPLE),
        ("PR, layer 24 (fenced)", detail["layers"]["24"]["pr"], PURPLE),
        ("MLE, layer 24 (fenced)", detail["layers"]["24"]["mle"], PURPLE),
        ("curvature proxy (clean-only)", detail["curvature"], INK2),
    ]
    fig, ax = plt.subplots(figsize=(8, 5.6), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    ys = np.arange(len(rows))[::-1]
    for y, (label, b, color) in zip(ys, rows):
        lo, hi = b["ci"]
        ax.plot([lo, hi], [y, y], color=color, lw=2, zorder=3)
        ax.plot(b["delta"], y, "o", color=color, ms=6, zorder=4)
        ax.text(-0.58, y, label, ha="right", va="center", fontsize=8.5,
                color=INK)
        ax.text(hi + 0.03, y, f"{b['delta']:+.3f}", va="center",
                fontsize=8, color=INK2)
    ax.axvline(0, color=INK2, lw=1, ls=":", zorder=2)
    ax.axvline(0.2, color="#c0392b", lw=1.2, ls="--", zorder=2)
    ax.text(0.205, ys[0] + 0.6, "PASS gate 0.2", fontsize=8,
            color="#c0392b")
    ax.set_xlim(-0.56, 0.7)
    ax.set_ylim(-0.7, len(rows) - 0.1)
    ax.set_yticks([])
    ax.set_xlabel("paired Cliff's delta, metaphorical minus literal "
                  "(95% bootstrap CI, seed 41)", fontsize=9, color=INK2)
    ax.grid(axis="x", color=GRID, lw=0.6, zorder=0)
    ax.tick_params(colors=INK2, length=0, labelsize=8)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("Real, small, and under the gate: intrinsic dimension "
                 "runs higher\naround metaphor everywhere measured, and "
                 "never by enough", fontsize=10.5, color=INK, pad=10)
    fig.tight_layout()
    fig.savefig(TR_ROOT / "report" / "fig1_forest.png",
                facecolor=SURFACE, bbox_inches="tight")
    print("wrote fig1")


def fig2():
    data = json.load(open(STORE / "instances.json"))
    lemmas = sorted(data["lemmas"])
    e = np.load(STORE / "embeddings" / "llama.npz", allow_pickle=True)
    ids = [str(x) for x in e["ids"]]
    X = e["X_l16"].astype(np.float64)
    idx = {}
    for i, rid in enumerate(ids):
        m, lab, _ = rid.split("::")
        idx.setdefault((m, lab), []).append(i)
    diffs, poses = [], []
    for m in lemmas:
        diffs.append(pr(X[idx[(m, "met")]]) - pr(X[idx[(m, "lit")]]))
        poses.append(data["lemmas"][m]["pos"])
    diffs = np.array(diffs)
    per_pos = json.load(open(TR_ROOT / "results" / "per_pos.json"))

    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    colors = {"noun": BLUE, "verb": ORANGE, "adj": PURPLE}
    bins = np.linspace(diffs.min() - 0.1, diffs.max() + 0.1, 36)
    bottom = np.zeros(len(bins) - 1)
    for posc in ("noun", "verb", "adj"):
        h, _ = np.histogram(diffs[[p == posc for p in poses]], bins=bins)
        ax.bar(bins[:-1], h, width=np.diff(bins) * 0.94, bottom=bottom,
               color=colors[posc], zorder=3, align="edge",
               label=f"{posc} (n={per_pos[posc]['pr']['n']}, "
                     f"PR delta {per_pos[posc]['pr']['delta']:+.2f})")
        bottom += h
    ax.axvline(0, color=INK, lw=1.2, ls=":", zorder=4)
    med = float(np.median(diffs))
    ax.axvline(med, color=INK, lw=1.4, zorder=4)
    ax.text(med + 0.05, ax.get_ylim()[1] * 0.92,
            f"median {med:+.2f}", fontsize=8.5, color=INK)
    ax.legend(fontsize=8.5, frameon=False, loc="upper left")
    ax.set_xlabel("per-lemma PR difference, metaphorical minus literal "
                  "cloud (layer 16)", fontsize=9, color=INK2)
    ax.set_ylabel("lemmas", fontsize=9, color=INK2)
    ax.grid(axis="y", color=GRID, lw=0.6, zorder=0)
    ax.tick_params(colors=INK2, length=0, labelsize=8)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("The atlas that turned out to be a shift: 166 lemmas, "
                 "one small push right", fontsize=10.5, color=INK, pad=10)
    fig.tight_layout()
    fig.savefig(TR_ROOT / "report" / "fig2_distribution.png",
                facecolor=SURFACE, bbox_inches="tight")
    print("wrote fig2")


def main():
    (TR_ROOT / "report").mkdir(exist_ok=True)
    detail = json.load(open(TR_ROOT / "results" / "detail.json"))
    fig1(detail)
    fig2()
    return 0


if __name__ == "__main__":
    sys.exit(main())
