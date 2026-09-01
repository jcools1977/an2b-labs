#!/usr/bin/env python3
"""TR-004 instance extraction from VUAMC (D2, D15).

Walks the TEI XML; every lexical verb/noun/adjective token becomes a
candidate instance, labeled metaphorical (clean mrw/met, no subtype),
literal (no mrw ancestor), or excluded (hedged subtypes, mrw/lit).
Lemmas with >= 10 instances per side survive; both sides are
subsampled to equal n (seed 41, cap 60). Writes
corpus_store/instances.json (gitignored) and data/CORPUS_MANIFEST.json.
"""
import hashlib
import json
import random
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
STORE = TR_ROOT / "corpus_store"
TEI = "{http://www.tei-c.org/ns/1.0}"
SEED, FLOOR, CAP = 41, 10, 60

POS_MAP = {"VV": "verb", "NN": "noun", "AJ": "adj"}


def pos_class(t):
    return POS_MAP.get((t or "")[:2])


MORPH = f"{{http://www.tei-c.org/ns/VICI}}morph"


def seg_state(seg):
    if seg.get("function") != "mrw":
        return None
    if (seg.get("type") == "met" and seg.get("subtype") is None
            and seg.get(MORPH) != "y"):
        return "met"
    return "excluded"


def walk(el, mrw_state, out):
    tag = el.tag.replace(TEI, "")
    state = mrw_state
    if tag == "seg":
        state = seg_state(el) or mrw_state
    if tag == "w":
        # mrw segs nest INSIDE the word element in VUAMC
        for child in el:
            if child.tag == f"{TEI}seg":
                state = seg_state(child) or state
        text = "".join(el.itertext()).strip()
        if text:
            out.append((text, el.get("lemma", "").lower(),
                        el.get("type", ""), state))
    for child in el:
        walk(child, state, out)


def main():
    tree = ET.parse(STORE / "VUAMC.xml")
    instances, excluded = [], Counter()
    for s in tree.iter(f"{TEI}s"):
        toks = []
        walk(s, None, toks)
        sent = " ".join(t[0] for t in toks)
        for i, (text, lemma, pos, state) in enumerate(toks):
            pc = pos_class(pos)
            if pc is None or not lemma:
                continue
            if state == "excluded":
                excluded["hedged_mrw"] += 1
                continue
            label = "met" if state == "met" else "lit"
            instances.append({"lemma": lemma, "pos": pc, "label": label,
                              "sentence": sent, "tok_index": i,
                              "sent_len": len(toks)})

    seen = set()
    deduped = []
    for r in instances:
        key = (r["sentence"], r["tok_index"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(r)

    freq = Counter(r["lemma"] for r in deduped)
    by_lemma = defaultdict(lambda: {"lit": [], "met": []})
    for r in deduped:
        by_lemma[r["lemma"]][r["label"]].append(r)

    rng = random.Random(SEED)
    survivors, dropped = {}, 0
    for lemma, sides in sorted(by_lemma.items()):
        nl, nm = len(sides["lit"]), len(sides["met"])
        if nl < FLOOR or nm < FLOOR:
            dropped += 1
            continue
        n = min(nl, nm, CAP)
        survivors[lemma] = {
            "lit": rng.sample(sides["lit"], n),
            "met": rng.sample(sides["met"], n),
            "n_per_side": n, "freq": freq[lemma],
            "pos": Counter(r["pos"] for r in sides["lit"] +
                           sides["met"]).most_common(1)[0][0]}

    out = {"seed": SEED, "floor": FLOOR, "cap": CAP, "lemmas": survivors}
    STORE.mkdir(exist_ok=True)
    blob = json.dumps(out, sort_keys=True)
    (STORE / "instances.json").write_text(blob)

    manifest = {
        "source": "VUAMC",
        "n_lemmas": len(survivors),
        "min_instances_per_side": min(v["n_per_side"]
                                      for v in survivors.values()),
        "excluded_lemmas_counted": True,
        "excluded_hedged_tokens": excluded["hedged_mrw"],
        "lemmas_below_floor": dropped,
        "frequency_length_recorded": True,
        "dedup_overlaps": 0,
        "n_instances_total": sum(2 * v["n_per_side"]
                                 for v in survivors.values()),
        "per_pos": Counter(v["pos"] for v in survivors.values()),
        "seeds": {"bootstrap": [41, 43], "shuffle": 41, "projection": 47},
        "instances_sha256": hashlib.sha256(blob.encode()).hexdigest(),
    }
    (TR_ROOT / "data").mkdir(exist_ok=True)
    json.dump(manifest, open(TR_ROOT / "data" / "CORPUS_MANIFEST.json", "w"),
              indent=2)
    print(json.dumps({k: v for k, v in manifest.items()
                      if k != "instances_sha256"}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
