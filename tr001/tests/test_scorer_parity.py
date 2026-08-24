#!/usr/bin/env python3
"""Scorer parity gate (DECISIONS.md D15, red-then-green).

Builds a synthetic prediction set with deliberately varied answers (exact,
paraphrase, article variants, punctuation variants, word-order, empty,
partial, second-gold matches), runs the vendored official evaluate-v1.1.py
on it, and asserts lib/scoring.py produces the same aggregate EM and F1.

--self-test additionally proves the check can fail: two deliberately broken
scorers (no article stripping; first-gold-only) must DISAGREE with the
official script on this set. Stdlib only; runs on any machine.
"""
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib import scoring  # noqa: E402

VENDOR = Path(__file__).parent / "vendor" / "evaluate-v1.1.py"
VENDOR_SHA256 = "f5a673dbbd173e29e9ea38f1b2091d883583b77b3a4c17144b223fb0f2f9bd09"

NAMES = ["Tesla", "Marie Curie", "the Amazon River", "Mount Everest", "Beyonce"]


def build_cases():
    """(golds, prediction) pairs exercising every D10 normalization rule."""
    cases = []
    for i, name in enumerate(NAMES):
        cases += [
            ([f"{name}"], f"{name}"),                            # exact
            ([f"the {name}"], f"{name}"),                        # article stripped
            ([f"{name}"], f"The {name}."),                       # article + punctuation + case
            (["U.S. Army", f"{name}"], "US Army"),               # punctuation collapse
            (["Carolina Panthers", f"{name}"], f"{name}"),       # SECOND gold matches
            (["gold and blue"], "blue and gold"),                # word order: F1 hit, EM miss
            ([f"{name} in 1912"], f"{name}"),                    # partial overlap
            ([f"{name}"], ""),                                   # empty prediction
            (["forty-two", "42"], "42"),                         # numeric gold variant
            ([f"{name}'s theory"], f"{name}s theory"),           # apostrophe
        ]
    return [
        {"id": f"case{i:03d}", "golds": g, "pred": p}
        for i, (g, p) in enumerate(cases)
    ]


def official_scores(cases):
    dataset = {
        "version": "1.1",
        "data": [{
            "title": "parity",
            "paragraphs": [{
                "context": "synthetic",
                "qas": [
                    {
                        "id": c["id"],
                        "question": "q",
                        "answers": [{"text": g, "answer_start": 0} for g in c["golds"]],
                    }
                    for c in cases
                ],
            }],
        }],
    }
    predictions = {c["id"]: c["pred"] for c in cases}
    with tempfile.TemporaryDirectory() as td:
        dpath, ppath = Path(td) / "dataset.json", Path(td) / "predictions.json"
        dpath.write_text(json.dumps(dataset))
        ppath.write_text(json.dumps(predictions))
        out = subprocess.run(
            [sys.executable, str(VENDOR), str(dpath), str(ppath)],
            capture_output=True, text=True, check=True,
        )
    return json.loads(out.stdout)


def ours(cases, em_fn, f1_fn):
    n = len(cases)
    return {
        "exact_match": sum(100.0 * em_fn(c["pred"], c["golds"]) for c in cases) / n,
        "f1": sum(100.0 * f1_fn(c["pred"], c["golds"]) for c in cases) / n,
    }


# Deliberately broken variants for the red cases.
def _normalize_keep_articles(s):
    import string as _string
    s = "".join(ch for ch in s.lower() if ch not in set(_string.punctuation))
    return " ".join(s.split())


def broken_no_articles_f1(pred, golds):
    def f1_single(p, g):
        pt, gt = _normalize_keep_articles(p).split(), _normalize_keep_articles(g).split()
        common = Counter(pt) & Counter(gt)
        num = sum(common.values())
        if num == 0:
            return 0.0
        prec, rec = num / len(pt), num / len(gt)
        return 2 * prec * rec / (prec + rec)
    return max(f1_single(pred, g) for g in golds)


def broken_no_articles_em(pred, golds):
    return max(float(_normalize_keep_articles(pred) == _normalize_keep_articles(g)) for g in golds)


def broken_first_gold_em(pred, golds):
    return scoring.em(pred, golds[:1])


def broken_first_gold_f1(pred, golds):
    return scoring.f1(pred, golds[:1])


def close(a, b, tol=1e-6):
    return abs(a["exact_match"] - b["exact_match"]) < tol and abs(a["f1"] - b["f1"]) < tol


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    got_sha = hashlib.sha256(VENDOR.read_bytes()).hexdigest()
    if got_sha != VENDOR_SHA256:
        print(f"VENDOR TAMPERED: evaluate-v1.1.py sha256 {got_sha[:16]}... != recorded")
        return 1

    cases = build_cases()
    ref = official_scores(cases)
    violations = []

    if args.self_test:
        for label, em_fn, f1_fn in [
            ("no-article-stripping scorer", broken_no_articles_em, broken_no_articles_f1),
            ("first-gold-only scorer", broken_first_gold_em, broken_first_gold_f1),
        ]:
            if close(ours(cases, em_fn, f1_fn), ref):
                violations.append(f"red case failed: {label} AGREES with official; test cannot fail")
            else:
                print(f"ok: {label} correctly disagrees with official")

    mine = ours(cases, scoring.em, scoring.f1)
    if close(mine, ref):
        print(f"PARITY: ours {mine} == official {ref} over {len(cases)} cases")
    else:
        violations.append(f"PARITY FAILURE: ours {mine} != official {ref}")

    for v in violations:
        print(f"VIOLATION: {v}")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
