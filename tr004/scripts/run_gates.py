#!/usr/bin/env python3
"""TR-004 gates, controls, and KILL, read cold (D6-D10, D18-D20).
Writes results/analysis.json, results/controls.json, results/kill.json
to the frozen checker schemas, plus results/detail.json.
"""
import json
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TR_ROOT))
import numpy as np  # noqa: E402

from analysis.lid import mle, pr  # noqa: E402
from analysis.curvature import geodesic_chordal_ratio  # noqa: E402
from analysis.residualize import residualize_diffs  # noqa: E402

STORE = TR_ROOT / "corpus_store"
GATE, BOOT_N = 0.2, 10_000
ESTS = {"pr": pr, "mle": mle}


def cliffs(x):
    return float((np.sum(x > 0) - np.sum(x < 0)) / len(x))


def boot_ci(diffs, seed):
    rng = np.random.default_rng(seed)
    n = len(diffs)
    stats = np.array([cliffs(diffs[rng.integers(0, n, n)])
                      for _ in range(BOOT_N)])
    return [float(np.quantile(stats, 0.025)),
            float(np.quantile(stats, 0.975))]


def gate_ok(delta, ci):
    return delta >= GATE and not (ci[0] <= 0 <= ci[1])


def clouds_from(X, ids, lemmas):
    out = {}
    idx = {}
    for i, rid in enumerate(ids):
        lemma, label, _ = rid.split("::")
        idx.setdefault((lemma, label), []).append(i)
    for lemma in lemmas:
        out[lemma] = {lab: X[idx[(lemma, lab)]] for lab in ("lit", "met")}
    return out


def paired_diffs(clouds, est, transform=None):
    d = []
    for lemma in sorted(clouds):
        a, b = clouds[lemma]["met"], clouds[lemma]["lit"]
        if transform is not None:
            a, b = transform(a), transform(b)
        d.append(est(a) - est(b))
    return np.array(d)


def block(diffs):
    return {"delta": cliffs(diffs), "ci": boot_ci(diffs, 41),
            "ci_seed43": boot_ci(diffs, 43)}


def main():
    data = json.load(open(STORE / "instances.json"))
    lemmas = sorted(data["lemmas"])
    e = np.load(STORE / "embeddings" / "llama.npz", allow_pickle=True)
    ids = [str(x) for x in e["ids"]]
    X16 = e["X_l16"].astype(np.float64)
    clouds = clouds_from(X16, ids, lemmas)

    # covariates (D7/D17/D20)
    Z = np.array([[np.log(data["lemmas"][m]["freq"]),
                   np.mean([r["sent_len"] for r in data["lemmas"][m]["met"]])
                   - np.mean([r["sent_len"] for r in data["lemmas"][m]["lit"]])]
                  for m in lemmas])
    MZ = [False, True]

    detail = {"main": {}, "layers": {}, "curvature": {}}
    main_diffs = {}
    analysis = {"after_controls": {}}
    for name, est in ESTS.items():
        d = paired_diffs(clouds, est)
        main_diffs[name] = d
        b = block(d)
        analysis[name] = {"delta": b["delta"], "ci": b["ci"]}
        detail["main"][name] = b
        rd = residualize_diffs(d, Z, MZ)
        rb = block(rd)
        analysis["after_controls"][name] = {"delta": rb["delta"],
                                            "ci": rb["ci"]}
        detail["main"][f"{name}_after_controls"] = rb
    analysis["estimators_direction_agree"] = (
        np.sign(analysis["pr"]["delta"]) == np.sign(analysis["mle"]["delta"]))

    def replicates(bl):
        d = bl["delta"]
        return gate_ok(d, bl["ci"]) == gate_ok(d, bl["ci_seed43"])
    analysis["seeds_replicate"] = all(
        replicates(detail["main"][k]) for k in detail["main"])

    # curvature, reported clean-only (D18); layers 8/24 fenced (D13)
    curv = paired_diffs(clouds, geodesic_chordal_ratio)
    detail["curvature"] = {"scope": "clean-only certification (D18)",
                           **block(curv)}
    for L in (8, 24):
        XL = e[f"X_l{L}"].astype(np.float64)
        cl = clouds_from(XL, ids, lemmas)
        detail["layers"][L] = {n: block(paired_diffs(cl, est))
                               for n, est in ESTS.items()}

    # ---- controls ----
    rng = np.random.default_rng(41)
    shuffle = {}
    for name, est in ESTS.items():
        d = []
        for lemma in sorted(clouds):
            pool = np.vstack([clouds[lemma]["met"], clouds[lemma]["lit"]])
            perm = rng.permutation(len(pool))
            n = len(pool) // 2
            d.append(est(pool[perm[:n]]) - est(pool[perm[n:]]))
        b = block(np.array(d))
        shuffle[name] = {"delta": b["delta"], "ci": b["ci"]}

    by_freq = sorted(lemmas, key=lambda m: data["lemmas"][m]["freq"])
    pairs = [(by_freq[i], by_freq[i + 1])
             for i in range(0, len(by_freq) - 1, 2)]
    synonym = {}
    for name, est in ESTS.items():
        d = np.array([est(clouds[b_]["lit"]) - est(clouds[a_]["lit"])
                      for a_, b_ in pairs])
        bl = block(d)
        synonym[name] = {"delta": bl["delta"], "ci": bl["ci"]}

    prng = np.random.default_rng(47)
    projected = {}
    for rank in (32, 64):
        G = np.linalg.qr(prng.normal(0, 1, (X16.shape[1], rank)))[0]
        clp = clouds_from(X16 @ G, ids, lemmas)
        for name, est in ESTS.items():
            projected[f"{rank}:{name}"] = cliffs(paired_diffs(clp, est))
    orig_min = min(analysis["pr"]["delta"], analysis["mle"]["delta"])

    var_rank = np.argsort(X16.var(axis=0))[::-1]
    rogue = {}
    for k in (3, 10):
        keep = np.setdiff1d(np.arange(X16.shape[1]), var_rank[:k])
        clr = clouds_from(X16[:, keep], ids, lemmas)
        worst = None
        for name, est in ESTS.items():
            bl = block(paired_diffs(clr, est))
            if worst is None or bl["delta"] < worst["delta"]:
                worst = {"delta": bl["delta"], "ci": bl["ci"],
                         "estimator": name}
        rogue[str(k)] = worst
    controls = {"label_shuffle": shuffle, "synonym": synonym,
                "random_subspace": {"orig_delta": orig_min,
                                    "projected": projected},
                "rogue_dims": {"orig_delta": orig_min, "removed": rogue}}

    # ---- KILL (D8, D20: raw main effect) ----
    m1_present = any(gate_ok(analysis[n]["delta"], analysis[n]["ci"])
                     for n in ESTS)
    m1_sign = np.sign(analysis["pr"]["delta"] + analysis["mle"]["delta"])
    be = np.load(STORE / "embeddings" / "bge.npz", allow_pickle=True)
    bclouds = clouds_from(be["X"].astype(np.float64),
                          [str(x) for x in be["ids"]], lemmas)
    m2 = {}
    for name, est in ESTS.items():
        bl = block(paired_diffs(bclouds, est))
        m2[f"delta_{name}"] = bl["delta"]
        m2[f"ci_{name}"] = bl["ci"]
        detail.setdefault("model2", {})[name] = bl
    m2["direction_reversed"] = bool(
        np.sign(m2["delta_pr"]) != m1_sign
        and np.sign(m2["delta_mle"]) != m1_sign)

    def est_absent(ci, rev):
        return rev or (ci[0] <= 0 <= ci[1])
    m2["absent"] = bool(est_absent(m2["ci_pr"], m2["direction_reversed"])
                        and est_absent(m2["ci_mle"], m2["direction_reversed"]))
    kill = {"model1_present": bool(m1_present), "model2": m2,
            "killed": bool(m1_present and m2["absent"])}

    (TR_ROOT / "results").mkdir(exist_ok=True)
    json.dump(analysis, open(TR_ROOT / "results" / "analysis.json", "w"),
              indent=2, default=bool)
    json.dump(controls, open(TR_ROOT / "results" / "controls.json", "w"),
              indent=2)
    json.dump(kill, open(TR_ROOT / "results" / "kill.json", "w"), indent=2)
    json.dump(detail, open(TR_ROOT / "results" / "detail.json", "w"),
              indent=2)
    print(json.dumps({"analysis": analysis, "kill": {
        "model1_present": kill["model1_present"],
        "killed": kill["killed"]}}, indent=2, default=bool))
    return 0


if __name__ == "__main__":
    sys.exit(main())
