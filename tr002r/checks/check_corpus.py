#!/usr/bin/env python3
"""TR-002r corpus gate (protocol; D4).

Schema (data/CORPUS_MANIFEST.json):
{
  "source": "gutenberg", "chunk_words": 200,
  "n_grid": [2000, 8000, 32000],
  "halves_disjoint_by_work": bool, "eval_gallery_disjoint": bool,
  "gallery_size": 1000,
  "spaces": int, "primary_pair_present": bool,
  "seeds": {"main": 41, "replicate": 43}
}
"""
import json
import sys


def check(path):
    d = json.load(open(path))
    v = []
    if d.get("source") != "gutenberg":
        v.append(f"source {d.get('source')} not the pre-registered corpus")
    if d.get("chunk_words") != 200:
        v.append("chunk size is not the frozen 200 words (D4)")
    if d.get("n_grid") != [2000, 8000, 32000]:
        v.append("n grid is not the frozen {2k, 8k, 32k}")
    if not d.get("halves_disjoint_by_work"):
        v.append("training halves not disjoint BY WORK (D4)")
    if not d.get("eval_gallery_disjoint"):
        v.append("eval/gallery works not disjoint from training")
    if d.get("gallery_size") != 1000:
        v.append(f"gallery {d.get('gallery_size')} != frozen 1,000")
    if d.get("spaces", 0) < 5:
        v.append(f"only {d.get('spaces')} embedding spaces (protocol: 5-6)")
    if not d.get("primary_pair_present"):
        v.append("frozen primary pair absent from the slate")
    s = d.get("seeds", {})
    if s.get("main") != 41 or s.get("replicate") != 43:
        v.append("seeds are not the frozen (41, 43)")
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
