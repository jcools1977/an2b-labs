"""The seven seeded systems (protocol ground-truth phase; DECISIONS D1).

Definitions only: wiring, prompts, and behavior. Expected verdicts live
in plants.py, which the runner and the auditor never import; only
scripts/build_seal.py reads it. Redundancy is implemented as consumer
robustness (validation-based selection), never mask detection: a
consumer of a redundant pair accepts the first input that passes a
content check, so a masked partner is skipped naturally and masking
both severs the value.

Every component runs on every probe (dead components still execute and
burn their cost; what they lack is causal influence, which is exactly
the quantity under audit).
"""
import re

from auditor.trace import Component, System

IRRELEVANT_RECIPES = [
    "Recipe: fold the egg whites gently before baking the sponge.",
    "Recipe: simmer the broth for two hours with bay leaves.",
    "Recipe: rest the dough overnight in a cold place.",
]

DISCLAIMER = "Disclaimer: this reply is informational and not a guarantee of service."


def _first_number(texts):
    for t in texts:
        m = re.search(r"-?\d+(\.\d+)?", str(t))
        if m:
            return m.group(0)
    return None


def build_systems():
    systems = {}

    # S1 research-brief: critic is appended-but-never-read (finalizer
    # reads the drafter only).
    systems["s1_research_brief"] = System(
        "s1_research_brief",
        [
            Component("searcher", lambda ctx, it, inp: ctx.generate(
                f"List three factual notes about {it['topic']}."), []),
            Component("drafter", lambda ctx, it, inp: ctx.generate(
                f"Draft a two-sentence brief on {it['topic']} from these notes: {inp['searcher']}"),
                ["searcher"]),
            Component("critic", lambda ctx, it, inp: ctx.generate(
                f"Critique this draft: {inp['drafter']}"), ["drafter"]),
            Component("finalizer", lambda ctx, it, inp: ctx.generate(
                f"Polish into a final brief: {inp['drafter']}"), ["drafter"]),
        ],
        final="finalizer",
    )

    # S2 rag-qa: one retrieval source returns only irrelevant recipes.
    systems["s2_rag_qa"] = System(
        "s2_rag_qa",
        [
            Component("retriever_encyclopedia",
                      lambda ctx, it, inp: list(it["docs_relevant"]), []),
            Component("retriever_recipes",
                      lambda ctx, it, inp: list(IRRELEVANT_RECIPES), []),
            Component("synthesizer", lambda ctx, it, inp: ctx.generate(
                "Summarize what these documents say that is relevant to the "
                f"question '{it['question']}': "
                + " | ".join(inp["retriever_encyclopedia"] + inp["retriever_recipes"])),
                ["retriever_encyclopedia", "retriever_recipes"]),
            Component("answerer", lambda ctx, it, inp: ctx.generate(
                f"Question: {it['question']}\nContext: {inp['synthesizer']}\n"
                "Answer with a short span only."), ["synthesizer"]),
        ],
        final="answerer",
    )

    # S3 math-tools: two identical calculators; the reconciler takes the
    # first input containing a parseable number.
    def _calc(ctx, it, inp):
        try:
            return str(eval(inp["parser"], {"__builtins__": {}}, {}))  # arithmetic only
        except Exception:
            return "error"

    systems["s3_math_tools"] = System(
        "s3_math_tools",
        [
            Component("parser", lambda ctx, it, inp: it["expression"], []),
            Component("calc_a", _calc, ["parser"]),
            Component("calc_b", _calc, ["parser"]),
            Component("reconciler", lambda ctx, it, inp: (
                _first_number([inp["calc_a"], inp["calc_b"]]) or "cannot compute"),
                ["calc_a", "calc_b"]),
        ],
        final="reconciler",
    )

    # S4 committee: the tangent debater is never aggregated.
    systems["s4_committee"] = System(
        "s4_committee",
        [
            Component("debater_pro", lambda ctx, it, inp: ctx.generate(
                f"Argue FOR: {it['question']}"), []),
            Component("debater_con", lambda ctx, it, inp: ctx.generate(
                f"Argue AGAINST: {it['question']}"), []),
            Component("debater_tangent", lambda ctx, it, inp: ctx.generate(
                f"Digress about the history of committees, apropos of {it['question']}"), []),
            Component("aggregator", lambda ctx, it, inp: ctx.generate(
                f"Weigh these arguments. FOR: {inp['debater_pro']} "
                f"AGAINST: {inp['debater_con']}"),
                ["debater_pro", "debater_con"]),
            Component("verdictor", lambda ctx, it, inp: ctx.generate(
                f"State a one-sentence verdict: {inp['aggregator']}"), ["aggregator"]),
        ],
        final="verdictor",
    )

    # S5 plan-exec: the executor follows a fixed procedure and never reads
    # the plan.
    systems["s5_plan_exec"] = System(
        "s5_plan_exec",
        [
            Component("planner", lambda ctx, it, inp: ctx.generate(
                f"Write a step-by-step plan to alphabetize: {it['words']}"), []),
            Component("executor", lambda ctx, it, inp: ", ".join(sorted(it["words"])), []),
            Component("verifier", lambda ctx, it, inp: ctx.generate(
                f"Confirm this list is alphabetized and restate it: {inp['executor']}"),
                ["executor"]),
        ],
        final="verifier",
    )

    # S6 support-triage: sentiment is computed and never read; two
    # identical disclaimer generators, assembler keeps the first VALID one.
    def _assemble(ctx, it, inp):
        disclaimers = [d for d in (inp["disclaimer_a"], inp["disclaimer_b"])
                       if str(d).startswith("Disclaimer:")]
        tail = disclaimers[0] if disclaimers else ""
        return f"{inp['responder']} {tail}".strip()

    systems["s6_support_triage"] = System(
        "s6_support_triage",
        [
            Component("classifier", lambda ctx, it, inp: ctx.generate(
                f"Classify this ticket into billing/technical/shipping: {it['ticket']}"), []),
            Component("sentiment", lambda ctx, it, inp: ctx.generate(
                f"Rate the sentiment of this ticket from 1-5: {it['ticket']}"), []),
            Component("responder", lambda ctx, it, inp: ctx.generate(
                f"Draft a two-sentence reply to this {inp['classifier']} ticket: {it['ticket']}"),
                ["classifier"]),
            Component("disclaimer_a", lambda ctx, it, inp: DISCLAIMER, []),
            Component("disclaimer_b", lambda ctx, it, inp: DISCLAIMER, []),
            Component("assembler", _assemble,
                      ["responder", "disclaimer_a", "disclaimer_b"]),
        ],
        final="assembler",
    )

    # S7 all-live control: every component is on the only causal path.
    systems["s7_all_live_qa"] = System(
        "s7_all_live_qa",
        [
            Component("retriever", lambda ctx, it, inp: list(it["docs_relevant"]), []),
            Component("reranker", lambda ctx, it, inp: ctx.generate(
                f"Pick the single document most relevant to '{it['question']}': "
                + " | ".join(inp["retriever"])), ["retriever"]),
            Component("answerer", lambda ctx, it, inp: ctx.generate(
                f"Question: {it['question']}\nEvidence: {inp['reranker']}\n"
                "Answer with a short span only."), ["reranker"]),
        ],
        final="answerer",
    )
    return systems
