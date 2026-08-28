#!/usr/bin/env python3
"""Surrogate stage B (D23): score the frozen tracer against the
ablation verdicts. Refuses to run without a green re-run certificate.

Runs in the wild venv (needs the bge-small embedder). Writes
results/surrogate.json with both kappas (primary dead-vs-not gated,
secondary flagged-vs-live reported).
"""
import json
import re
import sys
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TR_ROOT))

from seed_systems.systems import build_systems  # noqa: E402

SPAN_CONTAINMENT = 0.2
SHORT_OUTPUT_WORDS = 5
EMBED_COS = 0.60
DEAD_RATE = 0.05


def flatten(output):
    if isinstance(output, str):
        return output
    if isinstance(output, list):
        return " ".join(flatten(x) for x in output)
    if isinstance(output, dict):
        return " ".join(flatten(v) for k, v in sorted(output.items()))
    return str(output)


def words(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def span_hit(src, dst):
    sw = words(src)
    if not sw:
        return True  # empty output trivially "contained"; cannot be traced
    if len(sw) <= SHORT_OUTPUT_WORDS:
        return " ".join(sw) in " ".join(words(dst))
    grams = {tuple(sw[i:i + 3]) for i in range(len(sw) - 2)}
    dw = words(dst)
    dgrams = {tuple(dw[i:i + 3]) for i in range(len(dw) - 2)}
    return len(grams & dgrams) / len(grams) >= SPAN_CONTAINMENT


def transitive_readers(system):
    direct = {c.name: set() for c in system.components}
    for c in system.components:
        for r in c.reads:
            direct[r].add(c.name)
    closure = {}
    for name in direct:
        seen, stack = set(), list(direct[name])
        while stack:
            n = stack.pop()
            if n not in seen:
                seen.add(n)
                stack.extend(direct[n])
        closure[name] = seen
    return closure


def kappa(pairs):
    n = len(pairs)
    po = sum(1 for a, b in pairs if a == b) / n
    pa = sum(1 for a, _ in pairs if a) / n
    pb = sum(1 for _, b in pairs if b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return 1.0 if pe == 1.0 else (po - pe) / (1 - pe)


def main():
    cert = json.load(open(TR_ROOT / "results" / "surrogate_cert.json"))
    if not cert.get("all_match"):
        raise SystemExit("CERT GUARD (D23): re-run certificate is not green")

    traces = {}
    for line in open(TR_ROOT / "cache" / "seeded_traces_pass1.jsonl"):
        t = json.loads(line)
        traces.setdefault(t["system"], []).append(t)

    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    embedder = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    def embed_hit(src, dst):
        import numpy as np
        a = np.array(embedder.get_text_embedding(src[:2000]))
        b = np.array(embedder.get_text_embedding(dst[:2000]))
        cos = float(a @ b / ((a @ a) ** 0.5 * (b @ b) ** 0.5))
        return cos >= EMBED_COS

    systems = build_systems()
    recovery = json.load(open(TR_ROOT / "results" / "seeded_recovery.json"))
    ablation = {(r["system"], r["component"]): r["verdict"]
                for r in recovery["per_component"]}

    per_component = []
    for sid, system in systems.items():
        readers = transitive_readers(system)
        for comp in system.component_names():
            hits = 0
            for t in traces[sid]:
                outs = {e["component"]: flatten(e["output"]) for e in t["events"]}
                src = outs[comp]
                downstream = [outs[d] for d in readers[comp]] + [flatten(t["answer"])]
                item_hit = any(span_hit(src, d) for d in downstream)
                if not item_hit:
                    item_hit = any(embed_hit(src, d) for d in downstream)
                hits += item_hit
            rate = hits / len(traces[sid])
            per_component.append({
                "system": sid, "component": comp,
                "influence_rate": round(rate, 4),
                "surrogate_dead": rate < DEAD_RATE,
                "ablation_verdict": ablation[(sid, comp)],
            })
            print(f"[{sid}] {comp}: influence {rate:.3f} "
                  f"surrogate_dead={rate < DEAD_RATE} ablation={ablation[(sid, comp)]}",
                  flush=True)

    primary = kappa([(r["surrogate_dead"], r["ablation_verdict"] == "dead")
                     for r in per_component])
    secondary = kappa([(r["surrogate_dead"],
                        r["ablation_verdict"] in ("dead", "redundant"))
                       for r in per_component])
    out = {
        "thresholds": {"span_containment": SPAN_CONTAINMENT,
                       "short_output_words": SHORT_OUTPUT_WORDS,
                       "embed_cos": EMBED_COS, "dead_rate": DEAD_RATE,
                       "frozen_in": "D23, before any trace existed"},
        "kappa_primary_dead_vs_not": round(primary, 4),
        "kappa_secondary_flagged_vs_live": round(secondary, 4),
        "per_component": per_component,
    }
    with open(TR_ROOT / "results" / "surrogate.json", "w") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps({k: v for k, v in out.items() if k != "per_component"}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
