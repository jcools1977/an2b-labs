"""Canonical answer forms per task family (DECISIONS D15).

Answer-change rate is measured on canonicalized final answers. The
canonicalizer must match its human-ratified fixture pairs 100% (D3,
D13) before any rate it produces counts.
"""
import re
import string

_PUNC = set(string.punctuation)

FAMILY_OF_SYSTEM = {
    "s1_research_brief": "text",
    "s2_rag_qa": "span",
    "s3_math_tools": "number",
    "s4_committee": "text",
    "s5_plan_exec": "list",
    "s6_support_triage": "text",
    "s7_all_live_qa": "span",
}


def canon_number(ans):
    # Full sequence of normalized numbers, not first-only (ratification
    # correction #36, D17): "12 + 1" and "12" are different answers.
    nums = []
    for m in re.finditer(r"-?\d+(\.\d+)?", str(ans)):
        v = float(m.group(0))
        nums.append(str(int(v)) if v == int(v) else str(v))
    return ",".join(nums) if nums else "<no-number>"


def canon_list(ans):
    # Commas, semicolons, and " and " all read as separators to a human
    # (ratification corrections #48, #59, D17). Order is preserved:
    # list-family tasks are alphabetize-style, so order IS the answer.
    parts = [p.strip().lower()
             for p in re.split(r",|;|\band\b", str(ans)) if p.strip()]
    return "|".join(parts)


def canon_span(ans):
    s = "".join(ch for ch in str(ans).lower() if ch not in _PUNC)
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    return " ".join(s.split())


def canon_text(ans):
    return " ".join(str(ans).lower().split())


CANON = {
    "number": canon_number,
    "list": canon_list,
    "span": canon_span,
    "text": canon_text,
}


def changed(family, a, b):
    fn = CANON[family]
    return fn(a) != fn(b)
