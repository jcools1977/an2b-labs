#!/usr/bin/env python3
"""Build the TR-011 corpus store (D9, D11, D14).

The store is GITIGNORED: manuscript and draft text never enters the lab
repo (D11 covenant). Only store_inventory.json (paths, hashes, word
counts) feeds the later committed manifest.

Sides:
- a_published: Epoch I Sacred Story sections (from the infinite-loop
  clone) + the Light Papers (parsed from the published interior PDF).
- a_drafts: every text-bearing docx in the draft archive, by relative
  path (read-only extraction; bytes of the archive untouched).
- b_slush: Epoch II manuscript chapters from the clone.
- b_published: 25 Gutenberg works (20 primary + 5 backup, distinct
  authors), headers stripped, generous mid-book slice (final 8k-token
  spans are cut later with the tokenizer of record).
"""
import argparse
import hashlib
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
STORE = TR_ROOT / "corpus_store" / "raw"

GUTENBERG = [  # (id, author, title) - 25 distinct authors
    (1342, "Austen", "Pride and Prejudice"),
    (84, "Shelley", "Frankenstein"),
    (11, "Carroll", "Alice in Wonderland"),
    (2701, "Melville", "Moby-Dick"),
    (1661, "Doyle", "Adventures of Sherlock Holmes"),
    (74, "Twain", "Tom Sawyer"),
    (98, "Dickens", "A Tale of Two Cities"),
    (345, "Stoker", "Dracula"),
    (43, "Stevenson", "Jekyll and Hyde"),
    (35, "Wells", "The Time Machine"),
    (174, "Wilde", "Dorian Gray"),
    (219, "Conrad", "Heart of Darkness"),
    (16, "Barrie", "Peter Pan"),
    (55, "Baum", "Wizard of Oz"),
    (113, "Burnett", "The Secret Garden"),
    (2814, "Joyce", "Dubliners"),
    (1260, "BronteC", "Jane Eyre"),
    (768, "BronteE", "Wuthering Heights"),
    (64317, "Fitzgerald", "The Great Gatsby"),
    (25344, "Hawthorne", "The Scarlet Letter"),
    (145, "Eliot", "Middlemarch"),
    (2554, "Dostoevsky", "Crime and Punishment"),
    (1399, "Tolstoy", "Anna Karenina"),
    (541, "Wharton", "The Age of Innocence"),
    (583, "Collins", "The Woman in White"),
]

RUN_HEADS = ["Breath Between Worlds", "The Infinite Loop – Epoch I: ReGenesis",
             "The Infinite Loop - Epoch I: ReGenesis"]


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def clean_pdf_text(text):
    for h in RUN_HEADS:
        text = text.replace(h, "\n")
    lines = []
    for line in text.split("\n"):
        s = line.strip()
        if re.fullmatch(r"\d+", s):
            continue
        s = re.sub(r"^\d+(?=[A-Z])", "", s)  # page number glued to a heading
        lines.append(s)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def extract_light_papers(pdf_path, out_dir):
    from pypdf import PdfReader

    r = PdfReader(str(pdf_path))
    pages = [(p.extract_text() or "") for p in r.pages]
    start = None
    for i in range(100, len(pages)):
        low = " ".join(pages[i].lower().split())
        if "the light p" in low and len(pages[i].split()) < 40:
            start = i
            break
    assert start is not None, "Light Papers title page not found"
    body = "\n".join(pages[start + 1:])
    text = clean_pdf_text(body)
    out = out_dir / "light_papers.txt"
    out.write_text(text)
    return {"file": str(out.relative_to(STORE)), "words": len(text.split()),
            "sha256": sha(text), "pdf_start_page": start + 1}


def extract_docx(path):
    from docx import Document

    doc = Document(str(path))
    return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())


def gutenberg_fetch(gid):
    for url in (f"https://www.gutenberg.org/cache/epub/{gid}/pg{gid}.txt",
                f"https://www.gutenberg.org/files/{gid}/{gid}-0.txt"):
        try:
            with urllib.request.urlopen(url, timeout=45) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception:
            continue
    return None


def strip_gutenberg(text):
    m = re.search(r"\*\*\* ?START OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*", text)
    if m:
        text = text[m.end():]
    m = re.search(r"\*\*\* ?END OF (?:THE|THIS) PROJECT GUTENBERG", text)
    if m:
        text = text[:m.start()]
    return text.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clone", required=True, help="path to infinite-loop clone")
    ap.add_argument("--pdf", required=True, help="published interior PDF")
    args = ap.parse_args()
    clone = Path(args.clone)
    inv = {"built": time.strftime("%Y-%m-%d"), "sides": {}}

    # a_published: sections + light papers
    d = STORE / "a_published"
    d.mkdir(parents=True, exist_ok=True)
    entries = []
    for f in sorted((clone / "manuscript" / "epoch1").glob("*.md")):
        text = f.read_text()
        (d / f.name).write_text(text)
        entries.append({"file": f"a_published/{f.name}", "words": len(text.split()),
                        "sha256": sha(text)})
    entries.append(extract_light_papers(Path(args.pdf), d))
    inv["sides"]["a_published"] = entries
    print(f"a_published: {len(entries)} files, "
          f"{sum(e['words'] for e in entries)} words")

    # a_drafts: every docx under the archive
    d = STORE / "a_drafts"
    entries = []
    root = clone / "archive" / "epoch1-draftwork"
    for f in sorted(root.rglob("*.docx")):
        if f.name.startswith("~$"):
            continue
        rel = f.relative_to(root)
        try:
            text = extract_docx(f)
        except Exception as e:
            print(f"  skip {rel}: {type(e).__name__}")
            continue
        out = d / rel.with_suffix(".txt")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
        entries.append({"file": str(out.relative_to(STORE)),
                        "words": len(text.split()), "sha256": sha(text)})
    inv["sides"]["a_drafts"] = entries
    print(f"a_drafts: {len(entries)} files, "
          f"{sum(e['words'] for e in entries)} words")

    # b_slush: epoch2 chapters
    d = STORE / "b_slush"
    d.mkdir(parents=True, exist_ok=True)
    entries = []
    for f in sorted((clone / "manuscript" / "epoch2").glob("*.md")):
        text = f.read_text()
        (d / f.name).write_text(text)
        entries.append({"file": f"b_slush/{f.name}", "words": len(text.split()),
                        "sha256": sha(text)})
    inv["sides"]["b_slush"] = entries
    print(f"b_slush: {len(entries)} files, {sum(e['words'] for e in entries)} words")

    # b_published: gutenberg mid-book slices
    d = STORE / "b_published"
    d.mkdir(parents=True, exist_ok=True)
    entries = []
    for gid, author, title in GUTENBERG:
        raw = gutenberg_fetch(gid)
        if raw is None:
            print(f"  FAILED download {gid} {author}")
            continue
        body = strip_gutenberg(raw)
        mid = len(body) // 2
        piece = body[mid - 30000: mid + 30000]
        piece = piece[piece.find("\n\n") + 2: piece.rfind("\n\n")]
        out = d / f"{gid}_{author}.txt"
        out.write_text(piece)
        entries.append({"file": f"b_published/{out.name}", "author": author,
                        "title": title, "gutenberg_id": gid,
                        "words": len(piece.split()), "sha256": sha(piece)})
        time.sleep(1)  # be polite to Gutenberg
    inv["sides"]["b_published"] = entries
    print(f"b_published: {len(entries)}/{len(GUTENBERG)} works")

    with open(STORE.parent / "store_inventory.json", "w") as fh:
        json.dump(inv, fh, indent=2)
    print("wrote corpus_store/store_inventory.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
