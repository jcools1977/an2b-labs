#!/usr/bin/env python3
"""Corpus integrity gate (DECISIONS D9): the manifest must show dedup
ran clean, spans capped, splits and backup list committed BEFORE
scoring, and corpus A's publication-date protection recorded.

Schema:
{
  "dedup": {"cross_corpus_overlaps": int},
  "span_cap_tokens": int,
  "splits_committed": bool, "split_seed": int,
  "backup_list_committed": bool,
  "corpus_a": {"pairs": int, "postdates_scoring_cutoffs": bool},
  "corpus_b": {"published": int, "slush": int}
}
"""
import json
import sys


def check(path):
    d = json.load(open(path))
    v = []
    if d.get("dedup", {}).get("cross_corpus_overlaps", 1) != 0:
        v.append("dedup: cross-corpus normalized-hash overlaps present")
    if d.get("span_cap_tokens") != 8000:
        v.append("span cap is not the frozen 8,000 tokens (D9)")
    if not d.get("splits_committed") or d.get("split_seed") != 31:
        v.append("author-disjoint splits not committed at seed 31 (D9)")
    if not d.get("backup_list_committed"):
        v.append("corpus-B backup list (for D7 exclusions) not committed")
    ca = d.get("corpus_a", {})
    if ca.get("pairs", 0) < 1:
        v.append("corpus A has no draft/published pairs")
    if not ca.get("postdates_scoring_cutoffs", False):
        v.append("corpus A publication-date protection unconfirmed (D7)")
    cb = d.get("corpus_b", {})
    if cb.get("published", 0) < 20 or cb.get("slush", 0) < 20:
        v.append(f"corpus B under-populated: {cb}")
    return v


def main():
    if len(sys.argv) != 2:
        print("usage: check_corpora.py <CORPUS_MANIFEST.json>", file=sys.stderr)
        return 2
    violations = check(sys.argv[1])
    for x in violations:
        print(f"VIOLATION [{sys.argv[1]}]: {x}")
    if not violations:
        print(f"corpora integrity holds: {sys.argv[1]}")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
