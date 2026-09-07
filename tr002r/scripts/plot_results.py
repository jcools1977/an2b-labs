#!/usr/bin/env python3
"""TR-002r report figures.

Fig 1: the census — every pair's supervised skyline retrieval against
its unsupervised retrieval; the gap between the columns is the
verdict.
Fig 2: the flatline — the primary pair across the n grid: retrieval
at chance at every size, raw cosine flat, the centered companion at
zero exposing the mean artifact.
"""
import json
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

BLUE, ORANGE, PURPLE = "#2a78d6", "#eb6834", "#7d54c9"
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"


def rows():
    return [json.loads(x) for x in
            open(TR_ROOT / "results" / "grid.jsonl")]


def fig1(rs):
    pairs = [r for r in rs if r["kind"] in
             ("boundary", "primary_gate", "precision_arm")
             and r["seed"] == 41]
    seen, uniq = set(), []
    for r in pairs:
        k = frozenset((r["a"], r["b"]))
        if k in seen:
            continue
        seen.add(k)
        uniq.append(r)
    uniq.sort(key=lambda r: r["skyline_top1"])
    fig, ax = plt.subplots(figsize=(8, 5.8), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    ys = np.arange(len(uniq))
    for y, r in zip(ys, uniq):
        pk = "primary" if r["kind"] == "primary_gate" else r["kind"]
        color = ORANGE if pk == "primary" else (
            PURPLE if pk == "precision_arm" else BLUE)
        ax.plot([r["top1"], r["skyline_top1"]], [y, y], color=GRID,
                lw=1.4, zorder=2)
        ax.plot(r["skyline_top1"], y, "o", color=color, ms=7, zorder=3)
        ax.plot(r["top1"], y, "o", mfc="white", mec=color, ms=7,
                zorder=3)
        label = f"{r['a']} <-> {r['b']}" + (
            "  (PRIMARY)" if pk == "primary" else "")
        ax.text(-0.03, y, label, ha="right", va="center", fontsize=8.5,
                color=INK)
    ax.axvline(0.30, color="#c0392b", lw=1.2, ls="--", zorder=1)
    ax.text(0.305, len(uniq) - 0.4, "PASS gate 0.30", fontsize=8,
            color="#c0392b")
    ax.axvline(0.001, color=INK2, lw=1, ls=":", zorder=1)
    ax.text(0.008, -0.45, "chance", fontsize=8, color=INK2)
    ax.set_xlim(-0.02, 1.05)
    ax.set_yticks([])
    ax.set_xlabel("gallery top-1 retrieval (filled: supervised skyline; "
                  "hollow: unsupervised)", fontsize=9, color=INK2)
    ax.grid(axis="x", color=GRID, lw=0.6, zorder=0)
    ax.tick_params(colors=INK2, length=0, labelsize=8)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("The geometry is there and unsupervised access is not:\n"
                 "17 pairs, supervised skylines vs chance-level "
                 "unsupervised retrieval", fontsize=10.5, color=INK,
                 pad=10)
    fig.tight_layout()
    fig.savefig(TR_ROOT / "report" / "fig1_census.png",
                facecolor=SURFACE, bbox_inches="tight")
    print("wrote fig1")


def fig2(rs):
    prim = {}
    for r in rs:
        if r["a"] == "bge" and r["b"] == "llama4" and r["seed"] == 41 \
                and r["kind"] in ("primary_curve", "primary_gate"):
            prim[r["n"]] = r
    ns = sorted(prim)
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    x = np.arange(len(ns))
    ax.plot(x, [prim[n]["skyline_top1"] for n in ns], "-o", color=INK2,
            lw=1.6, ms=6, label="skyline top-1 (supervised)")
    ax.plot(x, [prim[n]["top1"] for n in ns], "-o", color=ORANGE,
            lw=2, ms=6, label="unsupervised top-1")
    ax.plot(x, [prim[n]["cosine"] for n in ns], "--s", color=BLUE,
            lw=1.4, ms=5, label="unsupervised raw cosine")
    ax.plot(x, [prim[n]["cosine_centered"] for n in ns], "--s",
            color=PURPLE, lw=1.4, ms=5,
            label="unsupervised centered cosine")
    ax.axhline(0.30, color="#c0392b", lw=1.1, ls="--")
    ax.text(len(ns) - 1.02, 0.315, "PASS gate", fontsize=8,
            color="#c0392b", ha="right")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{n//1000}k" for n in ns], fontsize=9)
    ax.set_xlabel("unpaired training chunks per half (bge -> llama4, "
                  "seed 41)", fontsize=9, color=INK2)
    ax.set_ylim(-0.1, 1.0)
    ax.legend(fontsize=8.5, frameon=False, loc="center left")
    ax.grid(axis="y", color=GRID, lw=0.6, zorder=0)
    ax.tick_params(colors=INK2, length=0, labelsize=8)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("The flatline: more data does not help, and the raw "
                 "cosine is a mean artifact\n(centered companion at "
                 "zero, retrieval at chance, skyline healthy)",
                 fontsize=10.5, color=INK, pad=10)
    fig.tight_layout()
    fig.savefig(TR_ROOT / "report" / "fig2_flatline.png",
                facecolor=SURFACE, bbox_inches="tight")
    print("wrote fig2")


def main():
    (TR_ROOT / "report").mkdir(exist_ok=True)
    rs = rows()
    fig1(rs)
    fig2(rs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
