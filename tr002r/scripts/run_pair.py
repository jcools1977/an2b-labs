#!/usr/bin/env python3
"""TR-002r pair evaluation core (D3, D13): train the certified
unsupervised translator on the disjoint halves of two spaces, read
fidelity on the gallery, and fit the supervised skyline on the
non-gallery eval anchors.

Library + CLI. CLI: run_pair.py <spaceA> <spaceB> <n> <seed>
prints one JSON result line (used by the smoke test and the grid
driver). All numbers land in results/ only through the grid driver.
"""
import json
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TR_ROOT))
import numpy as np  # noqa: E402

from analysis.translator import (apply_translator, target_space,  # noqa: E402
                                 to_raw_frame, train_translator, _procrustes)

STORE = TR_ROOT / "corpus_store"


def load_emb(space, split):
    d = np.load(STORE / "embeddings" / f"{space}__{split}.npz",
                allow_pickle=True)
    return [str(x) for x in d["ids"]], d["X"].astype(np.float64)


def gallery_ids():
    sp = json.load(open(STORE / "splits.json"))
    return sp["gallery"], sorted(set(sp["splits"]["eval"])
                                 - set(sp["gallery"]))


def fidelity(pred, gal):
    pn = pred / (np.linalg.norm(pred, axis=1, keepdims=True) + 1e-12)
    gn = gal / (np.linalg.norm(gal, axis=1, keepdims=True) + 1e-12)
    sims = pn @ gn.T
    top1 = float((np.argmax(sims, axis=1) ==
                  np.arange(len(pred))).mean())
    cosine = float(np.diag(sims).mean())
    return cosine, top1


def eval_pair(space_a, space_b, n, seed, shuffle_target=False):
    """Translator space_a -> space_b: A trains on half A, B on half B."""
    _, XA = load_emb(space_a, "A")
    _, XB = load_emb(space_b, "B")
    XA, XB = XA[:n], XB[:n]
    if shuffle_target:
        rng = np.random.default_rng(41)
        XB = np.array([row[rng.permutation(XB.shape[1])] for row in XB])
    T = train_translator(XA, XB, seed=seed)

    gal, anchors = gallery_ids()
    ea_ids, EA = load_emb(space_a, "eval")
    eb_ids, EB = load_emb(space_b, "eval")
    pos_a = {c: i for i, c in enumerate(ea_ids)}
    pos_b = {c: i for i, c in enumerate(eb_ids)}
    GA = EA[[pos_a[c] for c in gal]]
    GB = EB[[pos_b[c] for c in gal]]

    pred = apply_translator(T, GA)
    gal_frame = target_space(T, GB)
    cos_centered, top1_centered = fidelity(pred, gal_frame)
    cosine, top1 = fidelity(to_raw_frame(T, pred), GB)  # D17 raw frame

    AA = T["sa"].transform(EA[[pos_a[c] for c in anchors]])[:, :T["d"]]
    AB = T["sb"].transform(EB[[pos_b[c] for c in anchors]])[:, :T["d"]]
    Wsky = _procrustes(AA, AB)
    ga_frame = T["sa"].transform(GA)[:, :T["d"]]
    sky_cos_c, sky_top1_c = fidelity(ga_frame @ Wsky, gal_frame)
    sky_cos, sky_top1 = fidelity(to_raw_frame(T, ga_frame @ Wsky), GB)

    return {"pair": f"{space_a}->{space_b}", "n": n, "seed": seed,
            "cosine": round(cosine, 4), "top1": round(top1, 4),
            "cosine_centered": round(cos_centered, 4),
            "top1_centered": round(top1_centered, 4),
            "skyline_cosine": round(sky_cos, 4),
            "skyline_top1": round(sky_top1, 4),
            "skyline_cosine_centered": round(sky_cos_c, 4),
            "shuffled_target": shuffle_target}, T


def wrong_model_top1(T, space_c, space_b):
    """Feed space_c gallery embeddings through the A->B translator."""
    gal, _ = gallery_ids()
    ec_ids, EC = load_emb(space_c, "eval")
    eb_ids, EB = load_emb(space_b, "eval")
    pos_c = {c: i for i, c in enumerate(ec_ids)}
    pos_b = {c: i for i, c in enumerate(eb_ids)}
    GC = EC[[pos_c[c] for c in gal]]
    GB = EB[[pos_b[c] for c in gal]]
    pred = apply_translator(T, GC)
    _, t1 = fidelity(to_raw_frame(T, pred), GB)  # D17: same raw frame
    return t1


if __name__ == "__main__":
    a, b, n, seed = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    res, _ = eval_pair(a, b, n, seed)
    print(json.dumps(res))
