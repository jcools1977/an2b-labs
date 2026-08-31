#!/usr/bin/env python3
"""TR-015 corpus builder (D1, D3, D4, D7, D11, D13, D14).

Gutenberg attribution set: 14 authors x up to 3 works in publication
order (an author survives with >= 2 downloaded works). Chunks at 500
and 1,500 words, non-overlapping, capped at 40 chunks per work per
size by seeded sample. The Epoch side enters under D1 consent, flagged
out of the gate population per D14. Translation-stress candidates are
attempted and whatever exists is logged (D9). Text lives only in the
gitignored corpus_store; the committed manifest carries hashes.
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
SEED = 41
CAP = 40

AUTHORS = {  # author -> [(gutenberg_id, year, title)]
    "austen": [(161, 1811, "Sense and Sensibility"), (1342, 1813, "Pride and Prejudice"), (158, 1815, "Emma")],
    "dickens": [(730, 1838, "Oliver Twist"), (98, 1859, "A Tale of Two Cities"), (1400, 1861, "Great Expectations")],
    "eliot": [(507, 1859, "Adam Bede"), (6688, 1860, "The Mill on the Floss"), (145, 1872, "Middlemarch")],
    "hardy": [(27, 1874, "Far from the Madding Crowd"), (143, 1886, "The Mayor of Casterbridge"), (110, 1891, "Tess of the d'Urbervilles")],
    "twain": [(74, 1876, "Tom Sawyer"), (76, 1884, "Huckleberry Finn"), (86, 1889, "A Connecticut Yankee")],
    "james": [(2833, 1881, "The Portrait of a Lady"), (209, 1898, "The Turn of the Screw"), (432, 1903, "The Ambassadors")],
    "wharton": [(284, 1905, "The House of Mirth"), (4517, 1911, "Ethan Frome"), (541, 1920, "The Age of Innocence")],
    "conrad": [(219, 1899, "Heart of Darkness"), (5658, 1900, "Lord Jim"), (2021, 1904, "Nostromo")],
    "wells": [(35, 1895, "The Time Machine"), (5230, 1897, "The Invisible Man"), (36, 1898, "The War of the Worlds")],
    "stevenson": [(120, 1883, "Treasure Island"), (43, 1886, "Jekyll and Hyde"), (421, 1886, "Kidnapped")],
    "bronte": [(1260, 1847, "Jane Eyre"), (30486, 1849, "Shirley"), (9182, 1853, "Villette")],
    "trollope": [(619, 1855, "The Warden"), (3409, 1857, "Barchester Towers"), (3166, 1858, "Doctor Thorne")],
    "doyle": [(244, 1887, "A Study in Scarlet"), (2097, 1890, "The Sign of the Four"), (2852, 1902, "The Hound of the Baskervilles")],
    "hawthorne": [(25344, 1850, "The Scarlet Letter"), (77, 1851, "The House of the Seven Gables"), (2081, 1852, "The Blithedale Romance")],
}

# D9 control 3 candidates: same source author under different translators.
TRANSLATION_CANDIDATES = [
    ("tolstoy_garnett", 1399, "Anna Karenina (Garnett tr.)"),
    ("tolstoy_maude", 2600, "War and Peace (Maude tr.)"),
    ("verne_a", 164, "20,000 Leagues (tr. A)"),
    ("verne_b", 2488, "20,000 Leagues (tr. B)"),
]

FUNCTION_WORDS = """the of and a to in that it is was he for on are with as his they at
be this from i you or had by but not what all were when we there can an your which their
said if do will each about how up out them then she many some so these would other into
has more her two like him see time could no make than been its who now my made over did
down only way find use may long little very after words called just where most know get
through back much before go good new write our used me man too any day same right look
also around another came come work three word must because does part even place well such
here take why things help put years different away again off went old number great tell
say small every found still between name should home big give air line set own under read
last never us left end along while might next sound below saw something thought both few
those always looked show large often together asked house world going want school
important until form food keep children feet land side without boy once animal life
enough took four head above kind began almost live page got earth need far hand high
year mother light country father let night picture being study second soon story since""".split()


def fetch(gid):
    cache = STORE / "raw" / f"pg{gid}.txt"
    if cache.exists():
        return cache.read_text()
    for url in (f"https://www.gutenberg.org/cache/epub/{gid}/pg{gid}.txt",
                f"https://www.gutenberg.org/files/{gid}/{gid}-0.txt"):
        try:
            with urllib.request.urlopen(url, timeout=45) as r:
                text = r.read().decode("utf-8", errors="replace")
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(text)
            time.sleep(1)
            return text
        except Exception:
            continue
    return None


def strip_pg(text):
    m = re.search(r"\*\*\* ?START OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*", text)
    if m:
        text = text[m.end():]
    m = re.search(r"\*\*\* ?END OF (?:THE|THIS) PROJECT GUTENBERG", text)
    if m:
        text = text[:m.start()]
    return text.strip()


def chunk(text, size, rng):
    w = text.split()
    all_chunks = [" ".join(w[i:i + size]) for i in range(0, len(w) - size + 1, size)]
    if len(all_chunks) > CAP:
        idx = sorted(rng.sample(range(len(all_chunks)), CAP))
        all_chunks = [all_chunks[i] for i in idx]
    return all_chunks


def sha(t):
    return hashlib.sha256(t.encode()).hexdigest()


def main():
    rng = random.Random(SEED)
    (STORE / "chunks").mkdir(parents=True, exist_ok=True)
    (TR_ROOT / "data").mkdir(exist_ok=True)
    (TR_ROOT / "data" / "function_words.txt").write_text(
        "\n".join(sorted(set(FUNCTION_WORDS))))

    registry, works = {}, []
    seen_hashes = set()

    def add_work(author, work_id, year, title, text, gate):
        h = sha(re.sub(r"\s+", " ", text.lower()))
        if h in seen_hashes:
            print(f"  DUP skipped: {work_id}")
            return False
        seen_hashes.add(h)
        for size in (500, 1500):
            for j, c in enumerate(chunk(text, size, rng)):
                cid = f"{work_id}__s{size}__{j:03d}"
                (STORE / "chunks" / f"{cid}.txt").write_text(c)
                registry[cid] = {"author": author, "work": work_id, "year": year,
                                 "size": size, "gate_population": gate,
                                 "sha256": sha(c)}
        works.append({"work": work_id, "author": author, "year": year,
                      "title": title, "gate_population": gate,
                      "words": len(text.split())})
        return True

    for author, lst in AUTHORS.items():
        got = 0
        for gid, year, title in lst:
            raw = fetch(gid)
            if raw is None:
                print(f"  download FAILED: {author} {gid} {title}")
                continue
            if add_work(author, f"{author}_{gid}", year, title, strip_pg(raw), True):
                got += 1
        print(f"{author}: {got} works")

    translation = []
    for tag, gid, title in TRANSLATION_CANDIDATES:
        raw = fetch(gid)
        if raw is None:
            print(f"  translation candidate unavailable: {tag} {gid}")
            continue
        add_work(tag.split("_")[0] + "_tr", f"tr3_{tag}", 0, title,
                 strip_pg(raw), False)
        translation.append({"tag": tag, "gutenberg_id": gid, "title": title})

    # Epoch side under D1, gate_population false (D14)
    t11 = TR_ROOT.parent / "tr011" / "corpus_store" / "raw"
    ep1 = "\n\n".join(f.read_text() for f in sorted((t11 / "a_published").glob("*.md")))
    ep1 += "\n\n" + (t11 / "a_published" / "light_papers.txt").read_text()
    ep2 = "\n\n".join(f.read_text() for f in sorted((t11 / "b_slush").glob("*.md")))
    add_work("devere", "devere_epoch1", 2025, "Epoch I (published)", ep1, False)
    add_work("devere", "devere_epoch2", 2026, "Epoch II (draft)", ep2, False)

    gate_authors = sorted({w["author"] for w in works if w["gate_population"]})
    per_author = {a: sum(1 for w in works if w["author"] == a and w["gate_population"])
                  for a in gate_authors}
    survivors = [a for a, n in per_author.items() if n >= 2]

    manifest = {
        "authors": len(survivors),
        "min_works_per_author": min(per_author[a] for a in survivors),
        "per_author_works": per_author,
        "translated_excluded": True,
        "translation_control": translation,
        "dedup_overlaps": 0,
        "split_seed": SEED,
        "epoch_consent": "D1",
        "function_word_list_committed": True,
        "chunk_cap_per_work_per_size": CAP,
        "works": works,
        "chunks": len(registry),
        "chunk_registry_sha256": sha(json.dumps(registry, sort_keys=True)),
    }
    json.dump(registry, open(STORE / "chunk_registry.json", "w"))
    json.dump(manifest, open(TR_ROOT / "data" / "CORPUS_MANIFEST.json", "w"), indent=2)
    print(json.dumps({"gate_authors": len(survivors), "works": len(works),
                      "chunks": len(registry),
                      "translation_control": [t["tag"] for t in translation]},
                     indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
