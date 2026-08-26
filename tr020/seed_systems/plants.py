"""Expected verdicts for the seeded systems (DECISIONS D1, D6).

Imported ONLY by scripts/build_seal.py and the recovery scorer, never by
the runner or the auditor package. Finding these is an act of
measurement, not file access.
"""

EXPECTED = {
    "s1_research_brief": {
        "searcher": "live",
        "drafter": "live",
        "critic": "dead",        # archetype: appended-but-never-read
        "finalizer": "live",
    },
    "s2_rag_qa": {
        "retriever_encyclopedia": "live",
        "retriever_recipes": "dead",  # archetype: irrelevant-only retrieval
        "synthesizer": "live",
        "answerer": "live",
    },
    "s3_math_tools": {
        "parser": "live",
        "calc_a": "redundant",   # archetype: duplicate tool (pair)
        "calc_b": "redundant",
        "reconciler": "live",
    },
    "s4_committee": {
        "debater_pro": "live",
        "debater_con": "live",
        "debater_tangent": "dead",  # appended-but-never-aggregated
        "aggregator": "live",
        "verdictor": "live",
    },
    "s5_plan_exec": {
        "planner": "dead",       # produced and never read
        "executor": "live",
        "verifier": "live",
    },
    "s6_support_triage": {
        "classifier": "live",
        "sentiment": "dead",     # computed and never read
        "responder": "live",
        "disclaimer_a": "redundant",  # duplicate pair, validation-selected
        "disclaimer_b": "redundant",
        "assembler": "live",
    },
    "s7_all_live_qa": {          # negative control 1: zero plants
        "retriever": "live",
        "reranker": "live",
        "answerer": "live",
    },
}

REDUNDANT_PAIRS = [
    ("s3_math_tools", "calc_a", "calc_b"),
    ("s6_support_triage", "disclaimer_a", "disclaimer_b"),
]
