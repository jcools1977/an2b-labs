#!/usr/bin/env python3
"""Generate the committed probe sets (DECISIONS D12): 150 items per
system, synthetic, deterministic at seed 20. Re-running must reproduce
the committed files byte-for-byte.
"""
import json
import random
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
OUT = TR_ROOT / "seed_systems" / "probes"
SEED = 20
N = 150

NOUNS = ["lighthouses", "canals", "windmills", "aqueducts", "observatories",
         "printing presses", "tramways", "granaries", "clock towers", "ferries"]
PLACES = ["Novara", "Kestrel Bay", "Uld", "Port Halvern", "the Meridian Valley",
          "Skenn", "Auberon", "Tarvis", "the Lowland Reaches", "Quillmark"]
CITIES = ["Varn", "Solace", "Kirith", "Ombra", "Telling", "Farrow", "Ysel",
          "Candel", "Mirebrook", "Astern"]
ORGS = ["the city council", "a rural school district", "a shipping cooperative",
        "a public library system", "a regional hospital", "a transit authority"]
POLICIES = ["four-day work weeks", "open records by default", "congestion pricing",
            "volunteer boards", "algorithmic scheduling", "sunset clauses"]
WORDS = ["marble", "quince", "anchor", "delta", "harbor", "iris", "juniper",
         "kettle", "lantern", "meadow", "nectar", "orchid", "pillar", "quartz",
         "russet", "saffron", "thistle", "umber", "velvet", "willow"]
PRODUCTS = ["router", "standing desk", "coffee grinder", "rain jacket", "monitor"]
ISSUES = ["arrived with a cracked casing", "was billed twice", "never shipped",
          "stopped working after a week", "was missing the power cable"]


def facts(rng, n=3):
    """Invented-country capital facts; the last one answers the question."""
    picked = rng.sample(range(len(PLACES)), n)
    docs = [f"The capital of {PLACES[i]} is {CITIES[(i * 3 + 1) % len(CITIES)]}."
            for i in picked]
    q_i = picked[-1]
    question = f"What is the capital of {PLACES[q_i]}?"
    answer = CITIES[(q_i * 3 + 1) % len(CITIES)]
    return docs, question, answer


def main():
    OUT.mkdir(exist_ok=True)
    rng = random.Random(SEED)
    gens = {
        "s1_research_brief": lambda i: {
            "topic": f"the history of {rng.choice(NOUNS)} in {rng.choice(PLACES)}"},
        "s2_rag_qa": lambda i: dict(zip(
            ("docs_relevant", "question", "answer"), facts(rng))),
        "s3_math_tools": lambda i: {
            "expression": f"{rng.randint(2, 99)} {rng.choice(['+', '-', '*'])} "
                          f"{rng.randint(2, 99)} {rng.choice(['+', '-'])} {rng.randint(2, 99)}"},
        "s4_committee": lambda i: {
            "question": f"Should {rng.choice(ORGS)} adopt {rng.choice(POLICIES)}?"},
        "s5_plan_exec": lambda i: {"words": rng.sample(WORDS, 6)},
        "s6_support_triage": lambda i: {
            "ticket": f"My {rng.choice(PRODUCTS)} {rng.choice(ISSUES)}. "
                      f"Order number {rng.randint(10000, 99999)}."},
        "s7_all_live_qa": lambda i: dict(zip(
            ("docs_relevant", "question", "answer"), facts(rng))),
    }
    for sid, gen in gens.items():
        path = OUT / f"probes_{sid}.jsonl"
        with open(path, "w") as fh:
            for i in range(N):
                item = {"id": f"{sid}-{i:03d}"}
                item.update(gen(i))
                fh.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"wrote {path.name} ({N} items)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
