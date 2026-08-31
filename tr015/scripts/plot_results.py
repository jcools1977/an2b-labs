#!/usr/bin/env python3
"""TR-015 report figures.

Fig 1: the confiscation bar chart — Burrows baseline, raw embeddings,
topic-only, and topic-residualized subspace attribution, both chunk
sizes, gate line at 0.90.
Fig 2: the voice manifold — rank-2 discriminant projection (1500-word
chunks), gate-author work centroids joined in publication order, with
the Epoch I -> Epoch II trajectory drawn as coordinates only (D12,
demonstration, outside all gates).
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

from analysis.residualize import residualize  # noqa: E402
from analysis.split import split_ids  # noqa: E402

STORE = TR_ROOT / "corpus_store"
BLUE, ORANGE = "#2a78d6", "#eb6834"  # validated dataviz slots
GREEN, PURPLE = "#2e8540", "#7d54c9"
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"


def fig1(detail):
    labels = ["Burrows Delta\n(word freqs)", "raw bge\n(full dim)",
              "topic factors\nonly", "residualized\nsubspace"]
    colors = [INK2, BLUE, ORANGE, PURPLE]
    fig, ax = plt.subplots(figsize=(8, 4.4), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    width = 0.38
    for k, size in enumerate(("500", "1500")):
        p = detail["per_size"][size]
        vals = [detail["burrows"][size], p["acc_raw_fulldim"],
                p["topic_only_acc"], p["acc_resid_subspace"]]
        x = np.arange(4) + (k - 0.5) * width
        bars = ax.bar(x, vals, width * 0.92, color=colors,
                      alpha=1.0 if k else 0.45, zorder=3)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.012, f"{v:.2f}",
                    ha="center", fontsize=7.5, color=INK)
    ax.axhline(0.90, color="#c0392b", lw=1.2, ls="--", zorder=2)
    ax.text(3.45, 0.905, "PASS gate 0.90", fontsize=8, color="#c0392b",
            ha="right")
    ax.axhline(1 / 14, color=INK2, lw=1, ls=":", zorder=2)
    ax.text(-0.55, 1 / 14 + 0.012, "chance", fontsize=8, color=INK2,
            ha="left")
    ax.set_xticks(np.arange(4))
    ax.set_xticklabels(labels, fontsize=8.5, color=INK)
    ax.set_ylabel("held-out-by-works attribution accuracy", fontsize=9,
                  color=INK2)
    ax.set_ylim(0, 1.0)
    ax.grid(axis="y", color=GRID, lw=0.6, zorder=0)
    ax.tick_params(colors=INK2, length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("Voice was topic: remove topic and latent attribution "
                 "collapses below Burrows\n(pale = 500-word chunks, "
                 "solid = 1,500-word chunks; 14 authors)",
                 fontsize=10.5, color=INK, pad=10)
    fig.tight_layout()
    fig.savefig(TR_ROOT / "report" / "fig1_confiscation.png",
                facecolor=SURFACE, bbox_inches="tight")
    print("wrote fig1")


def fig2(registry):
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    size = 1500
    d = np.load(STORE / f"topics_{size}.npz", allow_pickle=True)
    ids, T = [str(x) for x in d["ids"]], d["T"]
    e = np.load(STORE / "embeddings" / "bge.npz", allow_pickle=True)
    eidx = {str(c): i for i, c in enumerate(e["ids"])}
    X = np.array([e["X"][eidx[c]] for c in ids])
    R = residualize(X, T)
    pos = {c: i for i, c in enumerate(ids)}
    train, _ = split_ids(registry, size)
    itr = np.array([pos[c] for c in train])
    ytr = np.array([registry[c]["author"] for c in train])
    lda = LinearDiscriminantAnalysis(n_components=2)
    lda.fit(R[itr], ytr)
    V = lda.transform(R)

    fig, ax = plt.subplots(figsize=(8, 6.4), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    gate_authors = sorted(set(ytr))
    cmap = plt.cm.tab20(np.linspace(0, 1, len(gate_authors)))
    for a, col in zip(gate_authors, cmap):
        works = sorted({(registry[c]["year"], registry[c]["work"])
                        for c, m in registry.items()
                        if m["size"] == size and m["author"] == a})
        cents = []
        for _, w in works:
            idx = [pos[c] for c, m in registry.items()
                   if m["size"] == size and m["work"] == w]
            cents.append(V[idx].mean(0))
        cents = np.array(cents)
        ax.plot(cents[:, 0], cents[:, 1], "-o", color=col, lw=1.1,
                ms=4, alpha=0.85, zorder=3)
        ax.annotate(a, cents[-1], fontsize=7.5, color=INK,
                    xytext=(4, 2), textcoords="offset points")
    # Epoch trajectory: coordinates only (D12), demonstration, non-gate
    ep = []
    for w in ("devere_epoch1", "devere_epoch2"):
        idx = [pos[c] for c, m in registry.items()
               if m["size"] == size and m["work"] == w]
        ep.append(V[idx].mean(0))
    ep = np.array(ep)
    ax.plot(ep[:, 0], ep[:, 1], "-s", color=INK, lw=2.0, ms=7, zorder=4)
    ax.annotate("Epoch I (2025)", ep[0], fontsize=8.5, color=INK,
                fontweight="bold", ha="right", xytext=(-8, 6),
                textcoords="offset points")
    ax.annotate("Epoch II (2026, draft)", ep[1], fontsize=8.5, color=INK,
                fontweight="bold", xytext=(6, 4), textcoords="offset points")
    ax.grid(color=GRID, lw=0.6, zorder=0)
    ax.tick_params(colors=INK2, length=0, labelsize=8)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xlabel("discriminant 1", fontsize=9, color=INK2)
    ax.set_ylabel("discriminant 2", fontsize=9, color=INK2)
    ax.set_title("The residualized plane, work centroids in publication "
                 "order\n(1,500-word chunks; the Epoch trajectory is a "
                 "demonstration, outside every gate)",
                 fontsize=10.5, color=INK, pad=10)
    fig.tight_layout()
    fig.savefig(TR_ROOT / "report" / "fig2_manifold.png",
                facecolor=SURFACE, bbox_inches="tight")
    print("wrote fig2")


def main():
    (TR_ROOT / "report").mkdir(exist_ok=True)
    detail = json.load(open(TR_ROOT / "results" / "analysis_detail_bge.json"))
    registry = json.load(open(STORE / "chunk_registry.json"))
    fig1(detail)
    fig2(registry)
    return 0


if __name__ == "__main__":
    sys.exit(main())
