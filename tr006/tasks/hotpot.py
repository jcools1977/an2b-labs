"""HotpotQA distractor validation (7,405 hard items) as TR-006's
multi-hop family. Each item: question, answer, gold paragraphs, and
distractors. Context given to the council (D11): the 2 gold
paragraphs plus 4 seeded distractors, shuffled, about 600 to 900
tokens. Scoring: normalized exact match (SQuAD normalization).
"""
import hashlib
import random
import re
import string

import pyarrow.parquet as pq

RAW = "data/raw/hotpot_distractor_validation.parquet"


def normalize(s: str) -> str:
    s = s.lower()
    s = "".join(ch for ch in s if ch not in set(string.punctuation))
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    return " ".join(s.split())


def exact_match(pred: str, gold: str) -> bool:
    return normalize(pred) == normalize(gold)


def load(path=RAW):
    t = pq.read_table(path)
    return t.to_pylist()


def sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def format_item(row, seed: int, n_distractors: int = 4):
    rng = random.Random(f"{seed}:{row['id']}")
    titles, sents = row["context"]["title"], row["context"]["sentences"]
    gold = set(row["supporting_facts"]["title"])
    paras = [(t, " ".join(ss)) for t, ss in zip(titles, sents)]
    gold_p = [p for p in paras if p[0] in gold]
    dis_p = [p for p in paras if p[0] not in gold]
    rng.shuffle(dis_p)
    chosen = gold_p + dis_p[:n_distractors]
    rng.shuffle(chosen)
    context = "\n\n".join(f"[{t}] {txt}" for t, txt in chosen)
    return {"id": row["id"], "family": "hotpot", "question": row["question"], "answer": row["answer"],
            "context": context, "sha": sha(row["id"] + row["question"]),
            "type": row["type"], "n_gold": len(gold_p)}


def score(pred: str, item) -> bool:
    return exact_match(pred, item["answer"])
