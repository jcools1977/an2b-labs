#!/usr/bin/env python3
"""D21 condition 2: supplementary work-level shuffle diagnostic.
Replaces nothing; results/workshuffle_supplement.json only.

Control 1 shuffled labels per CHUNK and read slightly above chance at
500 words. Hypothesized mechanism: chunks of one work are near-
neighbors, so chunk-level shuffling leaves work identity partially
intact. Here the shuffle is at the WORK level: training works receive
a permutation of the work-label multiset (seed 41), every chunk rides
with its work, and the identical pipeline (residualize, rank from the
gated run, LDA subspace, nearest centroid, 10,000-resample bootstrap
over test chunks) reports its CI. If the excess vanishes, the
clustering mechanism is confirmed with evidence.
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
BOOT_SEED, BOOT_N = 41, 10_000


def main():
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

    registry = json.load(open(STORE / "chunk_registry.json"))
    detail = json.load(open(TR_ROOT / "results" / "analysis_detail_bge.json"))
    out = {}
    for size in (500, 1500):
        d = np.load(STORE / f"topics_{size}.npz", allow_pickle=True)
        ids, T = [str(x) for x in d["ids"]], d["T"]
        e = np.load(STORE / "embeddings" / "bge.npz", allow_pickle=True)
        eidx = {str(c): i for i, c in enumerate(e["ids"])}
        X = np.array([e["X"][eidx[c]] for c in ids])
        R = residualize(X, T)
        pos = {c: i for i, c in enumerate(ids)}
        train, test = split_ids(registry, size)
        itr = np.array([pos[c] for c in train])
        ite = np.array([pos[c] for c in test])
        yte = np.array([registry[c]["author"] for c in test])

        works = sorted({registry[c]["work"] for c in train})
        wlabels = [registry[next(c for c in train
                                 if registry[c]["work"] == w)]["author"]
                   for w in works]
        rng = np.random.default_rng(BOOT_SEED)
        shuffled = list(wlabels)
        rng.shuffle(shuffled)
        wmap = dict(zip(works, shuffled))
        ysh = np.array([wmap[registry[c]["work"]] for c in train])

        rank = detail["per_size"][str(size)]["rank_used"]
        lda = LinearDiscriminantAnalysis(n_components=rank)
        Ptr = lda.fit(R[itr], ysh).transform(R[itr])
        Pte = lda.transform(R[ite])
        authors = sorted(set(ysh))
        cents = np.array([Ptr[ysh == a].mean(0) for a in authors])
        pred = np.array([authors[int(np.argmin(
            np.linalg.norm(cents - x, axis=1)))] for x in Pte])
        hits = (pred == yte).astype(float)
        boots = np.array([hits[rng.integers(0, len(hits), len(hits))].mean()
                          for _ in range(BOOT_N)])
        out[str(size)] = {
            "work_shuffle_ci": [float(np.quantile(boots, 0.025)),
                                float(np.quantile(boots, 0.975))],
            "point": float(hits.mean()),
            "chance": 1 / len(set(yte)),
            "chunk_shuffle_ci":
                detail["per_size"][str(size)]["label_shuffle_ci"],
        }
        print(size, out[str(size)])
    json.dump(out, open(TR_ROOT / "results" /
                        "workshuffle_supplement.json", "w"), indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
