#!/usr/bin/env python3
"""Corpus gate (D3, D11, D13): schema
{"authors": int, "min_works_per_author": int, "translated_excluded": bool,
 "dedup_overlaps": int, "split_seed": int, "epoch_consent": "D1",
 "function_word_list_committed": bool}
"""
import json
import sys


def check(path):
    d = json.load(open(path))
    v = []
    if d.get("authors", 0) < 12:
        v.append(f"authors {d.get('authors')} < 12")
    if d.get("min_works_per_author", 0) < 2:
        v.append("some author has fewer than 2 works")
    if not d.get("translated_excluded"):
        v.append("translated-author exclusion not asserted (D11)")
    if d.get("dedup_overlaps", 1) != 0:
        v.append("dedup overlaps present")
    if d.get("split_seed") != 41:
        v.append("work-split seed is not the frozen 41 (D13)")
    if d.get("epoch_consent") != "D1":
        v.append("Epoch material present without D1 consent reference")
    if not d.get("function_word_list_committed"):
        v.append("Burrows function-word list not committed before accuracies (D7)")
    return v


def main():
    if len(sys.argv) != 2:
        return 2
    vs = check(sys.argv[1])
    for x in vs:
        print(f"VIOLATION [{sys.argv[1]}]: {x}")
    if not vs:
        print(f"corpus integrity holds: {sys.argv[1]}")
    return 1 if vs else 0


if __name__ == "__main__":
    sys.exit(main())
