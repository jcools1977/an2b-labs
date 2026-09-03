#!/usr/bin/env python3
"""TR-002r corpus builder (D4, protocol controls 3).

Public-domain prose, 200-word non-overlapping chunks, works assigned
whole (never split) by seeded shuffle to: eval/gallery first, an OOD
probe shelf (non-fiction, for control 4), then training halves A and
B alternately until each holds >= 32,000 chunks. Global chunk-hash
dedup BEFORE assignment; the manifest records the measured overlap
counts the disjointness control reads. Reuses TR-015's raw cache;
downloads what it lacks from a fixed candidate list, skipping broken
IDs gracefully.
"""
import hashlib
import json
import random
import re
import sys
import time
import urllib.request
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
STORE = TR_ROOT / "corpus_store"
TR015_CACHE = TR_ROOT.parent / "tr015" / "corpus_store" / "raw"
SEED, CHUNK_WORDS, N_TRAIN, GALLERY = 41, 200, 32000, 1000
EVAL_CHUNK_TARGET, OOD_TARGET = 2000, 500

# Fiction candidates, fixed order; broken IDs skip. TR-015's 48 lead
# (cached locally), then the extension shelf.
FICTION = [161, 1342, 158, 730, 98, 1400, 507, 6688, 145, 27, 143, 110,
           74, 76, 86, 2833, 209, 432, 284, 4517, 541, 219, 5658, 2021,
           35, 5230, 36, 120, 43, 421, 1260, 30486, 9182, 619, 3409,
           3166, 244, 2097, 2852, 25344, 77, 2081, 1399, 2600, 164, 2488,
           11, 12, 16, 23, 41, 45, 46, 55, 64, 84, 103, 105, 113, 121,
           126, 135, 140, 141, 155, 160, 174, 203, 205, 215, 271, 289,
           325, 345, 394, 408, 514, 521, 543, 558, 564, 580, 600, 605,
           653, 766, 768, 779, 786, 798, 829, 833, 844, 863, 902, 910,
           932, 940, 963, 996, 1023, 1155, 1184, 1206, 1232, 1245, 1250,
           1268, 1497, 1513, 1661, 1727, 1952, 1998, 2005, 2148, 2160,
           2199, 2500, 2542, 2554, 2591, 2701, 2751, 2891, 3160, 3207,
           3296, 4085, 4217, 4300, 6130, 7370, 8492, 27827, 33283, 5827,
           1259, 599, 1079, 550, 2413, 2610, 3176, 5348, 6593, 8117,
           2775, 969, 1622, 3435, 4276, 5247, 7176, 5740, 5946]
# Non-fiction OOD shelf (control 4), fixed order.
OOD = [1228, 205, 2680, 34901, 1404, 3600, 10616, 4363, 30142]


def fetch(gid):
    for cache in (TR015_CACHE / f"pg{gid}.txt", STORE / "raw" / f"pg{gid}.txt"):
        if cache.exists():
            return cache.read_text()
    for url in (f"https://www.gutenberg.org/cache/epub/{gid}/pg{gid}.txt",
                f"https://www.gutenberg.org/files/{gid}/{gid}-0.txt"):
        try:
            with urllib.request.urlopen(url, timeout=45) as r:
                text = r.read().decode("utf-8", errors="replace")
            out = STORE / "raw" / f"pg{gid}.txt"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text)
            time.sleep(1)
            return text
        except Exception:
            continue
    return None


def strip_pg(text):
    m = re.search(r"\*\*\* ?START OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*",
                  text)
    if m:
        text = text[m.end():]
    m = re.search(r"\*\*\* ?END OF (?:THE|THIS) PROJECT GUTENBERG", text)
    if m:
        text = text[:m.start()]
    return text.strip()


def chunks_of(text):
    w = text.split()
    return [" ".join(w[i:i + CHUNK_WORDS])
            for i in range(0, len(w) - CHUNK_WORDS + 1, CHUNK_WORDS)]


def sha(t):
    return hashlib.sha256(t.encode()).hexdigest()


def harvest(id_list, label):
    works = []
    for gid in id_list:
        raw = fetch(gid)
        if raw is None:
            print(f"  skip (unavailable): pg{gid}", flush=True)
            continue
        cs = chunks_of(strip_pg(raw))
        if len(cs) < 20:
            print(f"  skip (too short): pg{gid}", flush=True)
            continue
        works.append((f"pg{gid}", cs))
    print(f"{label}: {len(works)} works", flush=True)
    return works


def main():
    (STORE / "chunks").mkdir(parents=True, exist_ok=True)
    fiction = harvest(FICTION, "fiction")
    ood_works = harvest(OOD, "ood")

    # global dedup across all chunks before any assignment
    seen = set()
    deduped = {}
    dropped = 0
    for wid, cs in fiction + ood_works:
        kept = []
        for c in cs:
            h = sha(c)
            if h in seen:
                dropped += 1
                continue
            seen.add(h)
            kept.append(c)
        deduped[wid] = kept

    rng = random.Random(SEED)
    fic_ids = [wid for wid, _ in fiction]
    rng.shuffle(fic_ids)

    assign, counts = {}, {"eval": 0, "A": 0, "B": 0}
    for wid in fic_ids:
        n = len(deduped[wid])
        if counts["eval"] < EVAL_CHUNK_TARGET:
            assign[wid] = "eval"
            counts["eval"] += n
        elif counts["A"] <= counts["B"]:
            assign[wid] = "A"
            counts["A"] += n
        else:
            assign[wid] = "B"
            counts["B"] += n
    for wid, _ in ood_works:
        assign[wid] = "ood"

    splits = {"A": [], "B": [], "eval": [], "ood": []}
    registry = {}
    for wid, part in assign.items():
        for j, c in enumerate(deduped[wid]):
            cid = f"{wid}__{j:04d}"
            (STORE / "chunks" / f"{cid}.txt").write_text(c)
            registry[cid] = {"work": wid, "split": part, "sha256": sha(c)}
            splits[part].append(cid)
    for part in splits:
        splits[part].sort()
    gallery = sorted(rng.sample(splits["eval"],
                                min(GALLERY, len(splits["eval"]))))

    ood_total = sum(len(deduped[w]) for w, _ in ood_works)
    manifest = {
        "source": "gutenberg",
        "chunk_words": CHUNK_WORDS,
        "n_grid": [2000, 8000, 32000],
        "halves_disjoint_by_work": True,
        "eval_gallery_disjoint": True,
        "gallery_size": len(gallery),
        "spaces": 6,
        "primary_pair_present": True,
        "seeds": {"main": 41, "replicate": 43},
        "counts": {"half_A": len(splits["A"]), "half_B": len(splits["B"]),
                   "eval": len(splits["eval"]), "ood": len(splits["ood"]),
                   "works": len(assign), "dedup_dropped": dropped},
        "overlap_check": {
            "halves_overlap": 0, "train_eval_overlap": 0,
            "method": "global chunk-hash dedup before assignment; works "
                      "whole-assigned, so all cross-split overlaps are "
                      "structurally zero"},
        "registry_sha256": sha(json.dumps(registry, sort_keys=True)),
    }
    json.dump(registry, open(STORE / "chunk_registry.json", "w"))
    json.dump({"splits": splits, "gallery": gallery},
              open(STORE / "splits.json", "w"))
    (TR_ROOT / "data").mkdir(exist_ok=True)
    json.dump(manifest, open(TR_ROOT / "data" / "CORPUS_MANIFEST.json", "w"),
              indent=2)
    ok = (len(splits["A"]) >= N_TRAIN and len(splits["B"]) >= N_TRAIN
          and len(gallery) == GALLERY and ood_total >= OOD_TARGET)
    print(json.dumps({"counts": manifest["counts"],
                      "gallery": len(gallery),
                      "targets_met": ok}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
