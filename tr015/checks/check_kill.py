#!/usr/bin/env python3
"""TR-015 KILL gate (protocol; D6, D8).

Schema (results/kill.json):
{
  "residualizer_biteproof": {"topic_collapse": bool, "voice_survives": bool},
  "paraphrase": {"true_author_accuracy": f, "chance": f,
                 "invalid_paraphrases": int, "n": int},
  "killed": bool
}
"""
import json
import sys


def check(path):
    d = json.load(open(path))
    v = []
    bp = d.get("residualizer_biteproof", {})
    if not bp.get("topic_collapse"):
        v.append("D6 bite-proof: planted topic signal did not collapse; "
                 "the residualizer cannot be trusted")
    if not bp.get("voice_survives"):
        v.append("D6 bite-proof: planted voice signal did not survive; "
                 "the residualizer over-corrects")
    p = d.get("paraphrase", {})
    acc, chance = p.get("true_author_accuracy"), p.get("chance")
    if acc is None or chance is None:
        v.append("paraphrase KILL results missing")
    elif acc < 2 * chance:
        v.append(f"KILL (D8): paraphrased chunks attribute to their true "
                 f"author at {acc} < 2x chance ({2*chance:.3f}); the voice "
                 f"subspace is content in costume")
    if d.get("killed") is True and acc is not None and acc >= 2 * chance:
        v.append("killed flag inconsistent with paraphrase result")
    return v


def main():
    if len(sys.argv) != 2:
        return 2
    vs = check(sys.argv[1])
    for x in vs:
        print(f"VIOLATION [{sys.argv[1]}]: {x}")
    if not vs:
        print(f"KILL gate holds: {sys.argv[1]}")
    return 1 if vs else 0


if __name__ == "__main__":
    sys.exit(main())
