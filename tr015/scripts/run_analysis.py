#!/usr/bin/env python3
"""TR-015 main analysis: residualized attribution, voice subspace,
drift, and the D9 controls, at both chunk sizes (D4), on the one
frozen split (D17). Writes results/analysis.json and
results/controls.json to the frozen checker schemas, plus
results/analysis_detail.json with the per-size numbers.

Gate arithmetic reads hardest (per CLAUDE.md): accuracy_resid is the
MINIMUM over the two chunk sizes; the Burrows comparison is taken at
whichever size gives the latent instrument its worst margin; rank_used
is the larger of the two ranks; a drift author satisfies only with
ratio < 0.5 at BOTH sizes and cross-size direction cosine > 0.
"""
import json
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TR_ROOT))
import numpy as np  # noqa: E402

from analysis.residualize import residualize  # noqa: E402
from analysis.split import split_ids  # noqa: E402

STORE = TR_ROOT / "corpus_store"
ACC_GATE, RANK_MAX = 0.90, 10
BOOT_SEED, BOOT_N = 41, 10_000


def centroid_acc(Xtr, ytr, Xte, yte):
    authors = sorted(set(ytr))
    cents = np.array([Xtr[ytr == a].mean(0) for a in authors])
    pred = [authors[int(np.argmin(np.linalg.norm(cents - x, axis=1)))]
            for x in Xte]
    return float((np.array(pred) == yte).mean())


def load_size(embed, size, registry):
    d = np.load(STORE / f"topics_{size}.npz", allow_pickle=True)
    tids, T = [str(x) for x in d["ids"]], d["T"]
    e = np.load(STORE / "embeddings" / f"{embed}.npz", allow_pickle=True)
    eidx = {str(c): i for i, c in enumerate(e["ids"])}
    X = np.array([e["X"][eidx[c]] for c in tids])
    return tids, X, T


def analyze_size(embed, size, registry):
    ids, X, T = load_size(embed, size, registry)
    pos = {c: i for i, c in enumerate(ids)}
    R = residualize(X, T)  # certified interface: full matrix (D6 exam form)
    train, test = split_ids(registry, size)
    itr = np.array([pos[c] for c in train])
    ite = np.array([pos[c] for c in test])
    ytr = np.array([registry[c]["author"] for c in train])
    yte = np.array([registry[c]["author"] for c in test])

    out = {"size": size,
           "acc_raw_fulldim": centroid_acc(X[itr], ytr, X[ite], yte),
           "acc_resid_fulldim": centroid_acc(R[itr], ytr, R[ite], yte)}

    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    rank_used, acc_at_rank, best_lda = RANK_MAX, None, None
    for r in range(1, RANK_MAX + 1):
        lda = LinearDiscriminantAnalysis(n_components=r)
        Ptr = lda.fit(R[itr], ytr).transform(R[itr])
        Pte = lda.transform(R[ite])
        acc = centroid_acc(Ptr, ytr, Pte, yte)
        if best_lda is None or r == RANK_MAX:
            acc_at_rank, best_lda, rank_used = acc, lda, r
        if acc >= ACC_GATE:
            acc_at_rank, best_lda, rank_used = acc, lda, r
            break
    out["rank_used"], out["acc_resid_subspace"] = rank_used, acc_at_rank

    # Drift (D10): per-author work centroids in the final subspace,
    # publication order, all of the author's chunks.
    V = best_lda.transform(R)
    gate_authors = sorted(set(ytr))
    between = []
    author_cent = {}
    for a in gate_authors:
        idx = [pos[c] for c, m in registry.items()
               if m["size"] == size and m["author"] == a]
        author_cent[a] = V[idx].mean(0)
    for i, a in enumerate(gate_authors):
        for b in gate_authors[i + 1:]:
            between.append(np.linalg.norm(author_cent[a] - author_cent[b]))
    mean_between = float(np.mean(between))

    drift = {}
    for a in gate_authors:
        works = sorted({(registry[c]["year"], registry[c]["work"])
                        for c, m in registry.items()
                        if m["size"] == size and m["author"] == a})
        cents = []
        for _, w in works:
            idx = [pos[c] for c, m in registry.items()
                   if m["size"] == size and m["work"] == w]
            cents.append(V[idx].mean(0))
        steps = [float(np.linalg.norm(cents[k + 1] - cents[k]))
                 for k in range(len(cents) - 1)]
        direction = cents[-1] - cents[0]
        drift[a] = {"mean_step": float(np.mean(steps)),
                    "ratio": float(np.mean(steps) / mean_between),
                    "direction": [float(x) for x in direction]}
    out["drift"], out["mean_between_author"] = drift, mean_between

    # Controls at this size
    rng = np.random.default_rng(BOOT_SEED)
    ysh = ytr.copy()
    rng.shuffle(ysh)
    lda_sh = LinearDiscriminantAnalysis(n_components=rank_used)
    Ps_tr = lda_sh.fit(R[itr], ysh).transform(R[itr])
    Ps_te = lda_sh.transform(R[ite])
    authors_sh = sorted(set(ysh))
    cents_sh = np.array([Ps_tr[ysh == a].mean(0) for a in authors_sh])
    pred_sh = np.array([authors_sh[int(np.argmin(
        np.linalg.norm(cents_sh - x, axis=1)))] for x in Ps_te])
    hits = (pred_sh == yte).astype(float)
    boots = np.array([hits[rng.integers(0, len(hits), len(hits))].mean()
                      for _ in range(BOOT_N)])
    out["label_shuffle_ci"] = [float(np.quantile(boots, 0.025)),
                               float(np.quantile(boots, 0.975))]
    out["topic_only_acc"] = centroid_acc(T[itr], ytr, T[ite], yte)
    out["chance"] = 1 / len(gate_authors)

    # Translation stress (D9 control 3, reported never gated):
    # same-novel two-translator centroid similarity vs the same-author
    # and different-author baselines, in the voice subspace.
    def work_cent(w):
        idx = [pos[c] for c, m in registry.items()
               if m["size"] == size and m["work"] == w]
        return V[idx].mean(0)

    def cos(u, v):
        return float(u @ v / (np.linalg.norm(u) * np.linalg.norm(v)))

    same_author = []
    for a in gate_authors:
        ws = sorted({m["work"] for c, m in registry.items()
                     if m["size"] == size and m["author"] == a})
        for i in range(len(ws)):
            for j in range(i + 1, len(ws)):
                same_author.append(cos(work_cent(ws[i]), work_cent(ws[j])))
    out["translation"] = {
        "verne_same_novel_two_translators":
            cos(work_cent("tr3_verne_a"), work_cent("tr3_verne_b")),
        "tolstoy_two_novels_two_translators":
            cos(work_cent("tr3_tolstoy_garnett"),
                work_cent("tr3_tolstoy_maude")),
        "same_author_mean": float(np.mean(same_author)),
        "between_author_mean": float(np.mean([
            cos(author_cent[a], author_cent[b])
            for i, a in enumerate(gate_authors)
            for b in gate_authors[i + 1:]])),
    }
    return out


def main():
    embed = sys.argv[1] if len(sys.argv) > 1 else "bge"
    registry = json.load(open(STORE / "chunk_registry.json"))
    burrows = {r["size"]: r["accuracy"]
               for r in json.load(open(TR_ROOT / "results" /
                                       "burrows_baseline.json"))["runs"]}
    per = {s: analyze_size(embed, s, registry) for s in (500, 1500)}

    # Cross-size drift direction cosine per author (D10)
    drift_sat, n_authors = 0, 0
    drift_detail = {}
    for a in per[500]["drift"]:
        n_authors += 1
        r500 = per[500]["drift"][a]["ratio"]
        r1500 = per[1500]["drift"][a]["ratio"]
        d500 = np.array(per[500]["drift"][a]["direction"])
        d1500 = np.array(per[1500]["drift"][a]["direction"])
        k = min(len(d500), len(d1500))
        cosine = float(d500[:k] @ d1500[:k] /
                       (np.linalg.norm(d500[:k]) * np.linalg.norm(d1500[:k])))
        ok = (r500 < 0.5) and (r1500 < 0.5) and (cosine > 0)
        drift_sat += ok
        drift_detail[a] = {"ratio_500": r500, "ratio_1500": r1500,
                           "direction_cosine": cosine, "satisfies": bool(ok)}

    # Hardest reading: worst margin over Burrows picks the reported pair
    margins = {s: per[s]["acc_resid_subspace"] - burrows[s] for s in per}
    worst = min(margins, key=margins.get)
    analysis = {
        "embedder": embed,
        "accuracy_resid": min(p["acc_resid_subspace"] for p in per.values()),
        "rank_used": max(p["rank_used"] for p in per.values()),
        "accuracy_burrows": burrows[worst],
        "accuracy_resid_at_worst_margin_size": per[worst]["acc_resid_subspace"],
        "accuracy_fulldim": min(p["acc_resid_fulldim"] for p in per.values()),
        "drift": {"fraction_satisfying": drift_sat / n_authors,
                  "n_authors": n_authors},
        "chunk_sizes_gated": [500, 1500],
    }
    controls = {
        "label_shuffle": {
            "accuracy_ci": per[worst]["label_shuffle_ci"],
            "chance": per[worst]["chance"],
            "per_size_ci": {s: per[s]["label_shuffle_ci"] for s in per}},
        "topic_only": {"accuracy": max(p["topic_only_acc"]
                                       for p in per.values()),
                       "reported": True,
                       "per_size": {s: per[s]["topic_only_acc"] for s in per}},
        "translation": {"reported": True,
                        "note": ("Two translators of the same Verne novel and "
                                 "two Tolstoy novels under different "
                                 "translators, work-centroid cosines in the "
                                 "voice subspace vs same/between-author "
                                 "baselines; numbers in analysis_detail."),
                        "per_size": {s: per[s]["translation"] for s in per}},
    }
    (TR_ROOT / "results").mkdir(exist_ok=True)
    if embed == "bge":  # only the gated embedder writes the gate files (D2)
        json.dump(analysis, open(TR_ROOT / "results" / "analysis.json", "w"),
                  indent=2)
        json.dump(controls, open(TR_ROOT / "results" / "controls.json", "w"),
                  indent=2)
    json.dump({"per_size": per, "drift_detail": drift_detail,
               "burrows": burrows, "analysis": analysis},
              open(TR_ROOT / "results" / f"analysis_detail_{embed}.json", "w"),
              indent=2)
    print(json.dumps(analysis, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
