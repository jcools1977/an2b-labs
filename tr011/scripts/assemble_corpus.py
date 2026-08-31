#!/usr/bin/env python3
"""Corpus assembly and blind alignment (D9, D12, D15, D16, D17).

Runs on legion in the recorded tr020 wild environment (embeddings +
tokenizer; NEVER a scoring model: this module must stay blind to
entropy by construction). Produces:
- corpus_store/docs/<doc_id>.txt  (final scoring units, gitignored)
- data/CORPUS_MANIFEST.json       (committed: hashes, pairs, yield,
                                   splits, backups; no text)
"""
import hashlib
import json
import random
import re
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
RAW = TR_ROOT / "corpus_store" / "raw"
DOCS = TR_ROOT / "corpus_store" / "docs"
SPLIT_SEED = 31
SPAN_CAP = 8000
UNIT_MIN_WORDS = 1500
SUBSTANTIAL_WORDS = 10000
ALIGN_THRESHOLD = 0.60
CUTOFFS = {"llama-3.1": "2023-12", "qwen3": "2024 (pre-2025)"}
PUBLICATION = "2025-05"


def norm_hash(text):
    n = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]", " ", text.lower())).strip()
    return hashlib.sha256(n.encode()).hexdigest()


def words(t):
    return len(t.split())


def chunk_paragraph_units(text, min_words):
    paras = [p for p in text.split("\n\n") if p.strip()]
    units, cur = [], []
    for p in paras:
        cur.append(p)
        if words("\n\n".join(cur)) >= min_words:
            units.append("\n\n".join(cur))
            cur = []
    if cur and units:
        units[-1] += "\n\n" + "\n\n".join(cur)
    elif cur:
        units.append("\n\n".join(cur))
    return units


def main():
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from transformers import AutoTokenizer
    import numpy as np

    embedder = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    tok = AutoTokenizer.from_pretrained(
        str(Path.home() / ".cache/huggingface/hub/models--mlx-community--Meta-Llama-3.1-8B-Instruct-4bit/snapshots/241a666dad6cb93c8ff213d39a7f34a36bf26db4"))

    def cap_tokens(text):
        ids = tok(text, add_special_tokens=False)["input_ids"][:SPAN_CAP]
        return tok.decode(ids)

    def embed_unit(text):
        w = text.split()
        chunks = [" ".join(w[i:i + 400]) for i in range(0, len(w), 400)][:12]
        vecs = [np.array(embedder.get_text_embedding(c)) for c in chunks]
        v = np.mean(vecs, axis=0)
        return v / np.linalg.norm(v)

    DOCS.mkdir(parents=True, exist_ok=True)
    manifest = {"span_cap_tokens": SPAN_CAP, "split_seed": SPLIT_SEED}
    docs = {}  # doc_id -> {text, group, author, side}

    # --- Published Epoch I units (corpus A published; also B published, D15)
    sec_files = sorted((RAW / "a_published").glob("*.md"))
    sacred = "\n\n".join(f.read_text() for f in sec_files)
    lp = (RAW / "a_published" / "light_papers.txt").read_text()
    pub_units = chunk_paragraph_units(sacred, UNIT_MIN_WORDS) + \
        chunk_paragraph_units(lp, UNIT_MIN_WORDS)
    for i, u in enumerate(pub_units):
        docs[f"a_pub_{i:02d}"] = {"text": cap_tokens(u), "author": "devere",
                                  "side": "a_published"}

    # --- Earliest-substantial draft generation (D17)
    inv = json.load(open(TR_ROOT / "corpus_store" / "store_inventory.json"))
    gens = {}
    for e in inv["sides"]["a_drafts"]:
        m = re.search(r"/(V\d|4_15_25|4_27_25|5_13_25|New Draft)/", "/" + e["file"] + "/")
        if m:
            gens.setdefault(m.group(1), []).append(e)
    order = ["V1", "V2", "V3", "V4", "V5", "V6", "4_15_25", "4_27_25",
             "5_13_25", "New Draft"]
    gen_words = {g: sum(e["words"] for e in gens.get(g, [])) for g in order}
    gate_gen = next(g for g in order if gen_words.get(g, 0) >= SUBSTANTIAL_WORDS)
    manifest["gate_generation"] = {"name": gate_gen, "words": gen_words[gate_gen],
                                   "all_generations_words": gen_words}
    draft_ids = []
    for j, e in enumerate(sorted(gens[gate_gen], key=lambda x: x["file"])):
        text = (RAW / e["file"]).read_text()
        if words(text) < 300:
            continue
        did = f"a_draft_{j:02d}"
        docs[did] = {"text": cap_tokens(text), "author": "devere",
                     "side": "a_draft", "source": e["file"]}
        draft_ids.append(did)

    # --- Blind alignment (D12/D17): greedy 1:1 by cosine, threshold 0.60
    pub_ids = [d for d in docs if docs[d]["side"] == "a_published"]
    emb = {d: embed_unit(docs[d]["text"]) for d in pub_ids + draft_ids}
    cands = sorted(((float(emb[a] @ emb[b]), a, b)
                    for a in draft_ids for b in pub_ids), reverse=True)
    used_d, used_p, pairs = set(), set(), []
    for s, a, b in cands:
        if s < ALIGN_THRESHOLD:
            break
        if a in used_d or b in used_p:
            continue
        used_d.add(a); used_p.add(b)
        pairs.append({"draft": a, "published": b, "cosine": round(s, 4)})
    manifest["corpus_a"] = {
        "pairs": len(pairs), "pairing": pairs,
        "postdates_scoring_cutoffs": True,
        "publication": PUBLICATION, "scoring_cutoffs": CUTOFFS,
        "yield": {
            "draft_units": len(draft_ids), "published_units": len(pub_ids),
            "paired": len(pairs),
            "draft_unpaired": len(draft_ids) - len(pairs),
            "published_unpaired": len(pub_ids) - len(pairs),
            "threshold": ALIGN_THRESHOLD,
        },
    }

    # --- Corpus B (D15/D17)
    gut = sorted((RAW / "b_published").glob("*.txt"))
    rng = random.Random(SPLIT_SEED)
    for f in gut:
        gid, author = f.stem.split("_", 1)
        docs[f"b_gut_{f.stem}"] = {"text": cap_tokens(f.read_text()),
                                   "author": author.lower(), "side": "b_published_gutenberg"}
    slush_files = sorted((RAW / "b_slush").glob("*.md"))
    rng.shuffle(slush_files)
    for k, f in enumerate(slush_files):
        side = "b_slush" if k < 20 else "b_slush_backup"
        docs[f"b_slush_{f.stem}"] = {"text": cap_tokens(f.read_text()),
                                     "author": "devere", "side": side}
    gut_primary = [f"b_gut_{f.stem}" for f in gut[:20]]
    gut_backup = [f"b_gut_{f.stem}" for f in gut[20:]]

    # duplicates control docs (D3): two copies of one gutenberg + one slush
    dup_srcs = [gut_primary[0], "b_slush_" + slush_files[0].stem]
    for s_id in dup_srcs:
        docs[s_id + "_dupcheck"] = dict(docs[s_id], side="dup_control")

    # --- dedup across corpora (normalized hashes)
    hashes = {}
    overlaps = 0
    for did, d in docs.items():
        if d["side"] == "dup_control":
            continue
        h = norm_hash(d["text"])
        if h in hashes:
            overlaps += 1
            print(f"OVERLAP: {did} == {hashes[h]}")
        hashes[h] = did
    manifest["dedup"] = {"cross_corpus_overlaps": overlaps}

    # --- author-disjoint folds (seed 31; all devere docs one group)
    authors = sorted({d["author"] for d in docs.values()})
    rng = random.Random(SPLIT_SEED)
    rng.shuffle(authors)
    folds = {a: i % 5 for i, a in enumerate(authors)}
    manifest["splits_committed"] = True
    manifest["author_folds"] = folds
    manifest["backup_list_committed"] = True
    manifest["backups"] = {"gutenberg": gut_backup,
                           "slush": [f"b_slush_{f.stem}" for f in slush_files[20:]]}
    manifest["corpus_b"] = {
        "published": len(gut_primary),
        "devere_published_in_b": len(pub_ids),
        "slush": 20,
    }

    # --- write docs + registry
    registry = {}
    for did, d in docs.items():
        (DOCS / f"{did}.txt").write_text(d["text"])
        registry[did] = {"sha256": hashlib.sha256(d["text"].encode()).hexdigest(),
                         "words": words(d["text"]), "author": d["author"],
                         "side": d["side"]}
    manifest["documents"] = registry

    with open(TR_ROOT / "data" / "CORPUS_MANIFEST.json", "w") as fh:
        json.dump(manifest, fh, indent=2)
    print(json.dumps({"gate_generation": manifest["gate_generation"]["name"],
                      "generation_words": gen_words,
                      "yield": manifest["corpus_a"]["yield"],
                      "docs": len(registry), "overlaps": overlaps}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
