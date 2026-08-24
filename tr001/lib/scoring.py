"""SQuAD scoring for TR-001, per DECISIONS.md D10.

Official SQuAD v1.1 normalization (lowercase, strip articles, strip
punctuation, collapse whitespace); EM and F1 both taken as the max over the
full gold answer set. A scorer reading only answers[0] is a bug, not a
choice. tests/test_scorer_parity.py proves parity with the vendored
official script before any experiment number is believed.

Stdlib only, so verify.sh can run the parity check on any machine.
"""
import re
import string
from collections import Counter

_PUNC = set(string.punctuation)


def normalize_answer(s):
    s = "".join(ch for ch in s.lower() if ch not in _PUNC)
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    return " ".join(s.split())


def _f1_single(prediction, gold):
    pred_tokens = normalize_answer(prediction).split()
    gold_tokens = normalize_answer(gold).split()
    common = Counter(pred_tokens) & Counter(gold_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return 0.0
    precision = num_same / len(pred_tokens)
    recall = num_same / len(gold_tokens)
    return 2 * precision * recall / (precision + recall)


def em(prediction, golds):
    return max(float(normalize_answer(prediction) == normalize_answer(g)) for g in golds)


def f1(prediction, golds):
    return max(_f1_single(prediction, g) for g in golds)


def score_items(rows, predictions):
    """rows: iterable of {"id", "answers"}; predictions: {id: text}.
    Returns (per_item, aggregate) with scores on the 0-100 scale."""
    per_item = []
    for row in rows:
        pred = predictions[row["id"]]
        per_item.append(
            {
                "id": row["id"],
                "em": 100.0 * em(pred, row["answers"]),
                "f1": 100.0 * f1(pred, row["answers"]),
            }
        )
    n = len(per_item)
    aggregate = {
        "exact_match": sum(r["em"] for r in per_item) / n,
        "f1": sum(r["f1"] for r in per_item) / n,
        "n": n,
    }
    return per_item, aggregate
