"""The wild-four adapters (DECISIONS D5, D21, D22).

Each adapter runs its framework's canonical tutorial composition against
the local endpoint and exposes the framework's own named units as
maskable components. Every interception goes through base.apply_mask, so
the sabotage mode breaks all four adapters identically and the
bite-proof harness can watch each one fail red.

Component masking is the ONLY nonstandard behavior; everything else is
the framework's own machinery. All client configs: temperature 0 (the
seeded phase's greedy rule, inherited per the observational freeze),
caching disabled wherever a framework caches.
"""
import json
from pathlib import Path

from .base import (API_KEY, ENDPOINT, MODEL_ID, TR_ROOT, apply_mask,
                   load_probes, trace_dict)

PROBES_DIR = Path(__file__).resolve().parent / "probes"


class WildSystem:
    def __init__(self, system_id, components, runner):
        self.system_id = system_id
        self._components = components
        self._runner = runner

    def component_names(self):
        return list(self._components)

    def run(self, item, lm=None, mask=None, mask_fn=None):
        return self._runner(item, mask, mask_fn)


# --- w1: LlamaIndex starter RAG (retriever -> synthesizer) --------------
def build_w1():
    from llama_index.core import Document, Settings, VectorStoreIndex
    from llama_index.core.response_synthesizers import get_response_synthesizer
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from llama_index.llms.openai_like import OpenAILike

    Settings.llm = OpenAILike(model=MODEL_ID, api_base=ENDPOINT, api_key=API_KEY,
                              temperature=0, is_chat_model=True, max_tokens=200)
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    docs = [Document(text=json.loads(l)["text"], doc_id=json.loads(l)["doc_id"])
            for l in open(PROBES_DIR / "w1_corpus.jsonl")]
    index = VectorStoreIndex.from_documents(docs)
    retriever = index.as_retriever(similarity_top_k=2)
    synth = get_response_synthesizer(response_mode="compact")

    def runner(item, mask, mask_fn):
        events = []
        nodes = retriever.retrieve(item["question"])
        texts = [n.node.get_content() for n in nodes]
        masked_texts = apply_mask("retriever", texts, mask, mask_fn)
        for node, t in zip(nodes, masked_texts):
            node.node.set_content(t)
        events.append({"component": "retriever", "masked": masked_texts is not texts,
                       "output": masked_texts})
        answer = str(synth.synthesize(item["question"], nodes=nodes))
        answer = apply_mask("synthesizer", answer, mask, mask_fn)
        events.append({"component": "synthesizer", "masked": False, "output": answer})
        return answer, trace_dict("w1_llamaindex_rag", item, mask, events, answer)

    return WildSystem("w1_llamaindex_rag", ["retriever", "synthesizer"], runner)


# --- w2: LangChain create_agent with two local tools --------------------
def build_w2():
    from langchain.agents import create_agent
    from langchain.tools import tool
    from langchain_openai import ChatOpenAI

    facts = json.load(open(PROBES_DIR / "w2_facts.json"))
    state = {"mask": None, "mask_fn": None, "events": None}

    @tool
    def calculator(expression: str) -> str:
        """Evaluate an arithmetic expression like (3 * 4) + 5."""
        try:
            raw = str(eval(expression, {"__builtins__": {}}, {}))
        except Exception:
            raw = "error"
        out = apply_mask("tool_calculator", raw, state["mask"], state["mask_fn"])
        state["events"].append({"component": "tool_calculator",
                                "masked": out != raw, "output": out})
        return out

    @tool
    def lookup(place: str) -> str:
        """Look up the population of a named place."""
        raw = str(facts.get(place.strip(), "unknown"))
        out = apply_mask("tool_lookup", raw, state["mask"], state["mask_fn"])
        state["events"].append({"component": "tool_lookup",
                                "masked": out != raw, "output": out})
        return out

    model = ChatOpenAI(model=MODEL_ID, base_url=ENDPOINT, api_key=API_KEY,
                       temperature=0, max_tokens=300)
    agent = create_agent(model, [calculator, lookup])

    def runner(item, mask, mask_fn):
        state.update(mask=mask, mask_fn=mask_fn, events=[])
        result = agent.invoke(
            {"messages": [{"role": "user", "content": item["question"]}]}
        )
        answer = result["messages"][-1].content
        if isinstance(answer, list):  # content blocks
            answer = " ".join(str(b.get("text", b)) if isinstance(b, dict) else str(b)
                              for b in answer)
        return answer, trace_dict("w2_langchain_agent", item, mask,
                                  state["events"], answer)

    return WildSystem("w2_langchain_agent", ["tool_calculator", "tool_lookup"], runner)


# --- w3: CrewAI researcher -> writer crew -------------------------------
def build_w3():
    from crewai import Agent, Crew, LLM, Task

    llm = LLM(model=f"openai/{MODEL_ID}", base_url=ENDPOINT, api_key=API_KEY,
              temperature=0, max_tokens=300)
    researcher = Agent(role="Researcher",
                       goal="Gather three concise factual notes on the topic",
                       backstory="A meticulous researcher.", llm=llm, verbose=False)
    writer = Agent(role="Writer",
                   goal="Write a two-sentence brief from the research notes",
                   backstory="A concise writer.", llm=llm, verbose=False)

    def runner(item, mask, mask_fn):
        events = []
        research = Task(description=f"Research: {item['topic']}. List three notes.",
                        expected_output="Three factual notes.", agent=researcher)
        notes = str(Crew(agents=[researcher], tasks=[research],
                         verbose=False).kickoff())
        masked_notes = apply_mask("researcher", notes, mask, mask_fn)
        events.append({"component": "researcher",
                       "masked": masked_notes != notes, "output": masked_notes})
        write = Task(description=(f"Using these research notes: {masked_notes}\n"
                                  f"Write a two-sentence brief on {item['topic']}."),
                     expected_output="A two-sentence brief.", agent=writer)
        answer = str(Crew(agents=[writer], tasks=[write], verbose=False).kickoff())
        answer2 = apply_mask("writer", answer, mask, mask_fn)
        events.append({"component": "writer", "masked": answer2 != answer,
                       "output": answer2})
        return answer2, trace_dict("w3_crewai_crew", item, mask, events, answer2)

    return WildSystem("w3_crewai_crew", ["researcher", "writer"], runner)


# --- w4: AutoGen planner -> executor ------------------------------------
def build_w4():
    from autogen import AssistantAgent

    llm_config = {
        "config_list": [{"model": MODEL_ID, "base_url": ENDPOINT,
                         "api_key": API_KEY, "price": [0.0, 0.0]}],
        "temperature": 0,
        "cache_seed": None,  # caching would fake determinism and hide masking
    }
    planner = AssistantAgent(
        "planner", llm_config=llm_config,
        system_message="You write short numbered plans. Plan only; never execute.")
    executor = AssistantAgent(
        "executor", llm_config=llm_config,
        system_message="You follow the given plan and produce the final text only.")

    def runner(item, mask, mask_fn):
        events = []
        plan = planner.generate_reply(
            messages=[{"role": "user", "content": f"Plan this task: {item['task']}"}])
        plan = plan if isinstance(plan, str) else str(plan)
        masked_plan = apply_mask("planner", plan, mask, mask_fn)
        events.append({"component": "planner", "masked": masked_plan != plan,
                       "output": masked_plan})
        answer = executor.generate_reply(
            messages=[{"role": "user",
                       "content": f"Task: {item['task']}\nPlan:\n{masked_plan}\n"
                                  f"Produce the final text."}])
        answer = answer if isinstance(answer, str) else str(answer)
        answer2 = apply_mask("executor", answer, mask, mask_fn)
        events.append({"component": "executor", "masked": answer2 != answer,
                       "output": answer2})
        return answer2, trace_dict("w4_autogen_planner", item, mask, events, answer2)

    return WildSystem("w4_autogen_planner", ["planner", "executor"], runner)


BUILDERS = {
    "w1_llamaindex_rag": build_w1,
    "w2_langchain_agent": build_w2,
    "w3_crewai_crew": build_w3,
    "w4_autogen_planner": build_w4,
}

# Bite-proof designations: (system, dependent component, probe id whose
# answer demonstrably depends on it).
BITE = {
    "w1_llamaindex_rag": ("retriever", 0),
    "w2_langchain_agent": ("tool_calculator", 0),
    "w3_crewai_crew": ("researcher", 0),
    "w4_autogen_planner": ("planner", 0),
}

FAMILY = {
    "w1_llamaindex_rag": "span",
    "w2_langchain_agent": "number",
    "w3_crewai_crew": "text",
    "w4_autogen_planner": "text",
}

TASK_OF = {
    "w1_llamaindex_rag": lambda it: f"Answer: {it['question']}",
    "w2_langchain_agent": lambda it: f"Answer: {it['question']}",
    "w3_crewai_crew": lambda it: f"Write a brief on {it['topic']}",
    "w4_autogen_planner": lambda it: it["task"],
}
