#!/usr/bin/env python3
"""Committed probe sets for the wild four (D5 observational freeze: 150
items per system, matched to each system's task, deterministic at seed
21, committed as JSONL). Also emits the RAG corpus and the lookup-tool
fact table, committed alongside, since the probes reference them.
"""
import json
import random
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
OUT = TR_ROOT / "wild" / "probes"
SEED = 21
N = 150

PLACES = ["Novara", "Kestrel Bay", "Uld", "Port Halvern", "Meridian Valley",
          "Skenn", "Auberon", "Tarvis", "Lowland Reaches", "Quillmark",
          "Farrowdale", "Ombra Heights", "Ysel Flats", "Candelport", "Astern"]
CITIES = ["Varn", "Solace", "Kirith", "Ombra", "Telling", "Farrow", "Ysel",
          "Candel", "Mirebrook", "Astern", "Quill", "Halvern", "Skenholm",
          "Tarv", "Auber"]
NOUNS = ["lighthouses", "canals", "windmills", "aqueducts", "observatories",
         "tramways", "granaries", "clock towers", "ferries", "printing presses"]
THINGS = ["welcome letter", "product description", "safety notice",
          "meeting summary", "tour itinerary", "press blurb"]
TOPICS = ["a community garden", "a harbor festival", "a night market",
          "a bicycle cooperative", "a tidal observatory", "a seed library"]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)

    # Corpus for w1 (RAG): one fact doc per place, committed.
    docs = []
    for i, place in enumerate(PLACES):
        city = CITIES[(i * 7 + 3) % len(CITIES)]
        pop = 20000 + ((i * 13217) % 60000)
        noun = NOUNS[i % len(NOUNS)]
        docs.append({
            "doc_id": f"doc-{i:02d}",
            "text": (f"{place} is a region whose capital is {city}. "
                     f"The capital has a population of {pop}. "
                     f"{place} is known for its historic {noun}."),
            "place": place, "capital": city, "population": pop, "noun": noun,
        })
    with open(OUT / "w1_corpus.jsonl", "w") as fh:
        for d in docs:
            fh.write(json.dumps(d, ensure_ascii=False) + "\n")

    with open(OUT / "probes_w1_llamaindex_rag.jsonl", "w") as fh:
        for i in range(N):
            d = docs[rng.randrange(len(docs))]
            kind = rng.choice(["capital", "noun"])
            if kind == "capital":
                q, a = f"What is the capital of {d['place']}?", d["capital"]
            else:
                q, a = f"What is {d['place']} known for?", f"historic {d['noun']}"
            fh.write(json.dumps({"id": f"w1-{i:03d}", "question": q, "answer": a},
                                ensure_ascii=False) + "\n")

    # Fact table for w2's lookup tool, committed.
    facts = {d["place"]: d["population"] for d in docs}
    with open(OUT / "w2_facts.json", "w") as fh:
        json.dump(facts, fh, indent=2, sort_keys=True)

    with open(OUT / "probes_w2_langchain_agent.jsonl", "w") as fh:
        for i in range(N):
            if i % 2 == 0:
                a, b, c = rng.randint(3, 99), rng.randint(3, 99), rng.randint(3, 99)
                q = f"Use the calculator tool to compute ({a} * {b}) + {c} and report only the number."
                ans = str(a * b + c)
            else:
                place = rng.choice(PLACES)
                q = (f"Use the lookup tool to find the population of {place} "
                     f"and report only the number.")
                ans = str(facts[place])
            fh.write(json.dumps({"id": f"w2-{i:03d}", "question": q, "answer": ans},
                                ensure_ascii=False) + "\n")

    with open(OUT / "probes_w3_crewai_crew.jsonl", "w") as fh:
        for i in range(N):
            topic = f"{rng.choice(TOPICS)} in {rng.choice(PLACES)}"
            fh.write(json.dumps({"id": f"w3-{i:03d}", "topic": topic},
                                ensure_ascii=False) + "\n")

    with open(OUT / "probes_w4_autogen_planner.jsonl", "w") as fh:
        for i in range(N):
            thing = rng.choice(THINGS)
            topic = f"{rng.choice(TOPICS)} in {rng.choice(PLACES)}"
            fh.write(json.dumps({"id": f"w4-{i:03d}",
                                 "task": f"Write a two-sentence {thing} for {topic}."},
                                ensure_ascii=False) + "\n")

    print(f"wrote 4 probe sets ({N} each), corpus, and fact table at seed {SEED}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
