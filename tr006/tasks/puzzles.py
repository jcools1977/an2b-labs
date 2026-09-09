"""Deterministic logic-grid (zebra-style) puzzles as TR-006's
constraint family. N entities, 3 attribute categories with N values
each; clues drawn from a fixed clue grammar until the brute-force
solver finds exactly one assignment; the question asks for one
attribute of one entity. Everything is seeded; no model writes any
puzzle. Scoring: normalized exact match on the asked value.
"""
import hashlib
import itertools
import random

NAMES = ["Alice", "Bob", "Carol", "Dave", "Erin", "Frank"]
CATS = {
    "pet": ["cat", "dog", "fish", "bird", "hamster", "turtle"],
    "drink": ["tea", "coffee", "milk", "juice", "water", "cocoa"],
    "city": ["Paris", "Lima", "Oslo", "Cairo", "Tokyo", "Quito"],
}


def _solve(n, clues):
    """Return all assignments satisfying the clues. Assignment: dict
    cat -> tuple of values indexed by entity."""
    cats = list(CATS)
    vals = {c: CATS[c][:n] for c in cats}
    sols = []
    for perm_pet in itertools.permutations(vals["pet"]):
        for perm_drink in itertools.permutations(vals["drink"]):
            for perm_city in itertools.permutations(vals["city"]):
                a = {"pet": perm_pet, "drink": perm_drink, "city": perm_city}
                if all(_holds(a, cl) for cl in clues):
                    sols.append(a)
                    if len(sols) > 1:
                        return sols
    return sols


def _holds(a, cl):
    kind = cl[0]
    if kind == "is":          # entity i has value v in cat c
        _, i, c, v = cl
        return a[c][i] == v
    if kind == "not":         # entity i does not have value v in cat c
        _, i, c, v = cl
        return a[c][i] != v
    if kind == "same":        # whoever has c1=v1 also has c2=v2
        _, c1, v1, c2, v2 = cl
        i = a[c1].index(v1)
        return a[c2][i] == v2
    if kind == "diff":        # whoever has c1=v1 does not have c2=v2
        _, c1, v1, c2, v2 = cl
        i = a[c1].index(v1)
        return a[c2][i] != v2
    raise ValueError(kind)


def _render(cl, names):
    kind = cl[0]
    if kind == "is":
        return f"{names[cl[1]]}'s {cl[2]} is {cl[3]}."
    if kind == "not":
        return f"{names[cl[1]]}'s {cl[2]} is not {cl[3]}."
    if kind == "same":
        return f"The person whose {cl[1]} is {cl[2]} has {cl[3]} {cl[4]}."
    if kind == "diff":
        return f"The person whose {cl[1]} is {cl[2]} does not have {cl[3]} {cl[4]}."


def generate(seed: int, idx: int, n: int = 4):
    rng = random.Random(f"puzzle:{seed}:{idx}")
    names = NAMES[:n]
    cats = list(CATS)
    truth = {c: tuple(rng.sample(CATS[c][:n], n)) for c in cats}
    clues = []
    # candidate clue pool, all true of the truth
    pool = []
    for i in range(n):
        for c in cats:
            pool.append(("is", i, c, truth[c][i]))
            for v in CATS[c][:n]:
                if v != truth[c][i]:
                    pool.append(("not", i, c, v))
    for c1 in cats:
        for c2 in cats:
            if c1 == c2:
                continue
            for i in range(n):
                pool.append(("same", c1, truth[c1][i], c2, truth[c2][i]))
                for v in CATS[c2][:n]:
                    if v != truth[c2][i]:
                        pool.append(("diff", c1, truth[c1][i], c2, v))
    rng.shuffle(pool)
    # prefer indirect clues: at most one direct "is" clue
    direct = 0
    for cl in pool:
        if cl[0] == "is":
            if direct >= 1:
                continue
            direct += 1
        clues.append(cl)
        sols = _solve(n, clues)
        if len(sols) == 1:
            break
    # minimize: drop clues that are not needed for uniqueness
    for cl in list(clues):
        trial = [c for c in clues if c is not cl]
        if len(_solve(n, trial)) == 1:
            clues = trial
    assert len(_solve(n, clues)) == 1
    ask_i, ask_c = rng.randrange(n), rng.choice(cats)
    text = " ".join(_render(cl, names) for cl in clues)
    intro = (f"{n} people ({', '.join(names)}) each have one {cats[0]}, one {cats[1]}, and one {cats[2]}, "
             f"all different. Pets: {', '.join(CATS['pet'][:n])}. Drinks: {', '.join(CATS['drink'][:n])}. "
             f"Cities: {', '.join(CATS['city'][:n])}.")
    q = f"What is {names[ask_i]}'s {ask_c}?"
    pid = f"pz_{seed}_{idx:04d}"
    return {"id": pid, "family": "puzzles", "question": q, "answer": truth[ask_c][ask_i],
            "context": intro + "\n\nClues: " + text, "sha": hashlib.sha256((pid + text).encode()).hexdigest(),
            "n_clues": len(clues), "unique": True}


def score(pred: str, item) -> bool:
    from tasks.hotpot import normalize
    return normalize(pred) == normalize(item["answer"]) or normalize(item["answer"]) in normalize(pred).split()
