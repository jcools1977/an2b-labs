#!/usr/bin/env python3
"""TR-011 endgame: features, controls, gates, KILL — all pure
computation over the entropy cache, per the frozen decisions
(D1-D2, D4, D15, D19). Refuses to run without the memorization audit
(D7 ordering, structural).

Writes results/features.json, analysis.json, controls.json, kill.json.
"""
import json
import re
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TR_ROOT))

import numpy as np  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402
from sklearn.model_selection import StratifiedKFold  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

from analysis.residualize import residualize  # noqa: E402

FEATS = ["mean", "variance", "acl", "lowfreq", "spike_rate", "boundary_delta"]
DELTA_GATE, RHO_GATE, AUC_GATE = 0.3, 0.7, 0.7


def series_features(npz):
    e = npz["entropy"].astype(float)
    pos = npz["positions"]
    out = {"mean": float(e.mean()), "variance": float(e.var())}
    c = e - e.mean()
    denom = float((c * c).sum()) or 1.0
    acl = len(e) // 2
    for lag in range(1, len(e) // 2):
        r = float((c[:-lag] * c[lag:]).sum()) / denom
        if r < 1 / np.e:
            acl = lag
            break
    out["acl"] = float(acl)
    P = np.abs(np.fft.rfft(c)) ** 2
    freqs = np.fft.rfftfreq(len(c))
    out["lowfreq"] = float(P[freqs < 0.1].sum() / (P.sum() or 1.0))
    out["spike_rate"] = float((e > e.mean() + 2 * e.std()).mean())
    bounds = set(npz["boundaries"].tolist())
    near = np.array([any(b <= p < b + 10 for b in bounds) for p in pos])
    if near.any() and (~near).any():
        out["boundary_delta"] = float(e[near].mean() - e[~near].mean())
    else:
        out["boundary_delta"] = 0.0
    return out


def paired_cliffs(pub_vals, draft_vals):
    wins = sum(1 for p, d in zip(pub_vals, draft_vals) if p > d)
    losses = sum(1 for p, d in zip(pub_vals, draft_vals) if p < d)
    return (wins - losses) / len(pub_vals)


def pooled_auc(X, y, folds_iter):
    scores, truth = [], []
    for tr, te in folds_iter:
        if len(set(y[te])) < 2 or len(set(y[tr])) < 2:
            continue
        sc = StandardScaler().fit(X[tr])
        clf = LogisticRegression(max_iter=2000).fit(sc.transform(X[tr]), y[tr])
        scores += list(clf.predict_proba(sc.transform(X[te]))[:, 1])
        truth += list(y[te])
    return float(roc_auc_score(truth, scores)), np.array(truth), np.array(scores)


def sentence_length_stats(text):
    sents = [s for s in re.split(r"(?<=[.!?])\s+", text.replace("\n", " ")) if s.strip()]
    lens = np.array([len(s.split()) for s in sents]) or np.array([1])
    return [float(lens.mean()), float(lens.std()),
            float(np.percentile(lens, 75) - np.percentile(lens, 25))]


def main():
    audit = TR_ROOT / "results" / "memorization_audit.json"
    if not audit.exists():
        raise SystemExit("D7 ORDERING: memorization audit missing; analysis refuses")
    audit = json.load(open(audit))

    manifest = json.load(open(TR_ROOT / "data" / "CORPUS_MANIFEST.json"))
    reg = manifest["documents"]
    cache_root = next((TR_ROOT / "corpus_store" / "entropy").iterdir())
    doc_ids = sorted(reg)

    # --- unscorable exclusion (D20): no positions under the frozen floor
    unscorable = [d for d in doc_ids
                  if len(np.load(cache_root / "qwen" / f"{d}.npz")["positions"]) == 0]
    doc_ids = [d for d in doc_ids if d not in unscorable]

    # --- features per doc per model, plus shuffled twins
    F = {}  # (doc, model, shuffled) -> dict
    for mkey in ("qwen", "llama"):
        for did in doc_ids:
            for sh in (False, True):
                f = cache_root / mkey / f"{did}{'__shuffled' if sh else ''}.npz"
                F[(did, mkey, sh)] = series_features(np.load(f))
    cons = {(did, sh): {k: (F[(did, 'qwen', sh)][k] + F[(did, 'llama', sh)][k]) / 2
                        for k in FEATS}
            for did in doc_ids for sh in (False, True)}
    json.dump({f"{d}{'__sh' if s else ''}": v for (d, s), v in cons.items()},
              open(TR_ROOT / "results" / "features.json", "w"), indent=1)

    # --- D6 rho per feature (original docs, both corpora pooled)
    rho = {}
    for k in FEATS:
        a = [F[(d, "qwen", False)][k] for d in doc_ids]
        b = [F[(d, "llama", False)][k] for d in doc_ids]
        rho[k] = float(spearmanr(a, b).statistic)

    # --- corpus A paired deltas (D18/D20 reading)
    pairs = [p for p in manifest["corpus_a"]["pairing"]
             if p["draft"] not in unscorable and p["published"] not in unscorable]
    deltas_a = {k: paired_cliffs(
        [cons[(p["published"], False)][k] for p in pairs],
        [cons[(p["draft"], False)][k] for p in pairs]) for k in FEATS}

    # --- corpus B sets (D15; final sets from the audit)
    gut = [d for d in audit["final_sets"]["gutenberg"] if d not in unscorable]
    slush = [d for d in audit["final_sets"]["slush"] if d not in unscorable]
    for backup in manifest["backups"]["slush"]:  # D20 promotion ladder
        if len(slush) >= 20:
            break
        if backup not in unscorable and backup not in slush:
            slush.append(backup)
    dev_pub = [d for d in doc_ids if reg[d]["side"] == "a_published"]
    b_pub = gut + dev_pub
    sign_b = {k: float(np.median([cons[(d, False)][k] for d in b_pub]) -
                       np.median([cons[(d, False)][k] for d in slush]))
              for k in FEATS}

    Xb = np.array([[cons[(d, False)][k] for k in FEATS] for d in b_pub + slush])
    yb = np.array([1] * len(b_pub) + [0] * len(slush))
    folds = manifest["author_folds"]
    fold_of = np.array([folds[reg[d]["author"]] for d in b_pub + slush])
    fold_iter = [(np.where(fold_of != i)[0], np.where(fold_of == i)[0])
                 for i in sorted(set(fold_of))]
    auc, truth_b, score_b = pooled_auc(Xb, yb, fold_iter)

    # --- author-identity control (D15/D19: stratified doc-level)
    Xa = np.array([[cons[(d, False)][k] for k in FEATS] for d in dev_pub + gut])
    ya = np.array([1] * len(dev_pub) + [0] * len(gut))
    skf = StratifiedKFold(5, shuffle=True, random_state=31)
    auth_auc, _, _ = pooled_auc(Xa, ya, skf.split(Xa, ya))

    corpus_b_valid = bool(audit["corpus_b_group_ok"]) and auth_auc < 0.7
    analysis = {
        "unscorable_excluded": unscorable,
        "corpus_b_valid": corpus_b_valid,
        "author_control_auc": round(auth_auc, 4),
        "auc": round(auc, 4),
        "features": {k: {"delta_a": round(deltas_a[k], 4),
                         "sign_agrees_b": bool(np.sign(sign_b[k]) ==
                                               np.sign(deltas_a[k]) and deltas_a[k] != 0),
                         "rho": round(rho[k], 4),
                         "sign_b_direction": round(sign_b[k], 5)}
                     for k in FEATS},
        "n_pairs_corpus_a": len(pairs),
        "reading": "D18: corpus-A deltas are a demonstration on n=4, not an inference",
    }
    json.dump(analysis, open(TR_ROOT / "results" / "analysis.json", "w"), indent=2)

    # --- controls
    shuffle_deltas = {k: paired_cliffs(
        [cons[(d, True)][k] for d in doc_ids],
        [cons[(d, False)][k] for d in doc_ids]) for k in ("acl", "lowfreq")}
    topics = json.load(open(TR_ROOT / "data" / "topic_labels.json"))
    Xt = np.array([[cons[(d, False)][k] for k in FEATS] for d in doc_ids])
    yt = np.array([topics[d] for d in doc_ids])
    skf = StratifiedKFold(5, shuffle=True, random_state=31)
    preds, truth = [], []
    for tr, te in skf.split(Xt, yt):
        sc = StandardScaler().fit(Xt[tr])
        clf = LogisticRegression(max_iter=2000).fit(sc.transform(Xt[tr]), yt[tr])
        preds += list(clf.predict(sc.transform(Xt[te])))
        truth += list(yt[te])
    correct = np.array(preds) == np.array(truth)
    rng = np.random.default_rng(31)
    boots = sorted(rng.choice(correct, (10000, len(correct))).mean(1))
    chance = float(max(np.bincount(yt)) / len(yt))
    dup_ok = True
    for did in [d for d in doc_ids if reg[d]["side"] == "dup_control"]:
        src = did.replace("_dupcheck", "")
        for mkey in ("qwen", "llama"):
            a = np.load(cache_root / mkey / f"{did}.npz")["entropy"]
            b = np.load(cache_root / mkey / f"{src}.npz")["entropy"]
            dup_ok = dup_ok and np.array_equal(a, b)
    controls = {
        "shuffle": {"acl_delta": round(shuffle_deltas["acl"], 4),
                    "lowfreq_delta": round(shuffle_deltas["lowfreq"], 4)},
        "topic": {"accuracy_ci": [round(float(boots[250]), 4),
                                  round(float(boots[9750]), 4)],
                  "chance": round(chance, 4)},
        "duplicates": {"byte_identical": bool(dup_ok)},
    }
    json.dump(controls, open(TR_ROOT / "results" / "controls.json", "w"), indent=2)

    # --- KILL (D4/D19): residualize consensus features on length stats
    L = np.array([sentence_length_stats(
        (TR_ROOT / "corpus_store" / "docs" / f"{d}.txt").read_text())
        for d in doc_ids])
    Xall = np.array([[cons[(d, False)][k] for k in FEATS] for d in doc_ids])
    R = residualize(Xall, L)
    rcons = {d: dict(zip(FEATS, R[i])) for i, d in enumerate(doc_ids)}
    r_deltas = {k: paired_cliffs(
        [rcons[p["published"]][k] for p in pairs],
        [rcons[p["draft"]][k] for p in pairs]) for k in FEATS}
    r_sign_b = {k: float(np.median([rcons[d][k] for d in b_pub]) -
                         np.median([rcons[d][k] for d in slush])) for k in FEATS}
    Xrb = np.array([[rcons[d][k] for k in FEATS] for d in b_pub + slush])
    r_auc, _, _ = pooled_auc(Xrb, yb, [(np.where(fold_of != i)[0],
                                        np.where(fold_of == i)[0])
                                       for i in sorted(set(fold_of))])
    qual_resid = [k for k in FEATS
                  if abs(r_deltas[k]) >= DELTA_GATE and rho[k] >= RHO_GATE
                  and np.sign(r_sign_b[k]) == np.sign(r_deltas[k]) and r_deltas[k] != 0]
    killed = bool(len(qual_resid) < 2 or r_auc < AUC_GATE)

    import subprocess
    bp = subprocess.run([sys.executable, str(TR_ROOT / "tests" / "test_residualizer.py")],
                        capture_output=True, text=True)
    kill = {
        "residualizer_biteproof": {
            "length_collapse": "length signal collapses" in bp.stdout,
            "signal_survives": "orthogonal signal survives" in bp.stdout,
        },
        "killed": killed,
        "auc_residualized": round(r_auc, 4),
        "qualifying_features_residualized": len(qual_resid),
        "residualized_deltas_a": {k: round(v, 4) for k, v in r_deltas.items()},
    }
    json.dump(kill, open(TR_ROOT / "results" / "kill.json", "w"), indent=2)

    print(json.dumps({"analysis": analysis, "controls": controls,
                      "kill": {k: v for k, v in kill.items()
                               if k != "residualized_deltas_a"}}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
