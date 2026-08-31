#!/usr/bin/env python3
"""D8 paraphrase KILL evaluation + D6 bite-proof booleans ->
results/kill.json (frozen checker schema).

Pipeline mirrors run_analysis at size 500: paraphrase embeddings pass
through the fitted topic model, are residualized through the certified
function (concatenated with the corpus matrix so only certified code
touches the KILL path), projected into the voice subspace trained on
the frozen split's training chunks, and attributed by nearest author
centroid. KILL iff true-author accuracy < 2x chance.
"""
import json
import subprocess
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TR_ROOT))
import numpy as np  # noqa: E402
import joblib  # noqa: E402

from analysis.residualize import residualize  # noqa: E402
from analysis.split import split_ids  # noqa: E402

STORE = TR_ROOT / "corpus_store"
SIZE = 500


def main():
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

    registry = json.load(open(STORE / "chunk_registry.json"))
    detail = json.load(open(TR_ROOT / "results" / "analysis_detail_bge.json"))
    rank = detail["per_size"][str(SIZE)]["rank_used"]

    d = np.load(STORE / f"topics_{SIZE}.npz", allow_pickle=True)
    ids, T = [str(x) for x in d["ids"]], d["T"]
    e = np.load(STORE / "embeddings" / "bge.npz", allow_pickle=True)
    eidx = {str(c): i for i, c in enumerate(e["ids"])}
    X = np.array([e["X"][eidx[c]] for c in ids])

    p = np.load(STORE / "embeddings" / "para_bge.npz", allow_pickle=True)
    pids, Xp = [str(x) for x in p["ids"]], p["X"]
    tm = joblib.load(STORE / f"topic_model_{SIZE}.joblib")
    texts = [(STORE / "paraphrases" / f"{c}.txt").read_text() for c in pids]
    Tp = tm["lda"].transform(tm["vectorizer"].transform(texts))

    R_all = residualize(np.vstack([X, Xp]), np.vstack([T, Tp]))
    R, Rp = R_all[:len(ids)], R_all[len(ids):]

    train, _ = split_ids(registry, SIZE)
    pos = {c: i for i, c in enumerate(ids)}
    itr = np.array([pos[c] for c in train])
    ytr = np.array([registry[c]["author"] for c in train])
    lda = LinearDiscriminantAnalysis(n_components=rank)
    Ptr = lda.fit(R[itr], ytr).transform(R[itr])
    Pp = lda.transform(Rp)
    authors = sorted(set(ytr))
    cents = np.array([Ptr[ytr == a].mean(0) for a in authors])
    pred = [authors[int(np.argmin(np.linalg.norm(cents - x, axis=1)))]
            for x in Pp]
    ytrue = [registry[c]["author"] for c in pids]
    acc = float(np.mean([a == b for a, b in zip(pred, ytrue)]))
    chance = 1 / len(authors)

    plog = json.load(open(STORE / "paraphrase_log.json"))
    bp = subprocess.run([sys.executable, str(TR_ROOT / "tests" /
                                             "test_residualizer.py")],
                        capture_output=True, text=True)
    out = {
        "residualizer_biteproof": {
            "topic_collapse": "planted topic signal collapses" in bp.stdout,
            "voice_survives": "planted voice signal survives" in bp.stdout},
        "paraphrase": {"true_author_accuracy": acc, "chance": chance,
                       "invalid_paraphrases": plog["n_sampled"] - plog["n_valid"],
                       "n": plog["n_valid"]},
        "killed": acc < 2 * chance,
    }
    json.dump(out, open(TR_ROOT / "results" / "kill.json", "w"), indent=2)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
