"""Structure-preserving neutral masking (protocol: "replace with neutral
placeholder, preserving structure").

The mask must remove content while leaving shape intact, so a masked
component's downstream consumers see the same types, lengths, and keys.
The placebo control (paraphrase instead of placeholder) is Phase 2.
"""


def neutral_mask(output):
    if isinstance(output, str):
        return "[MASKED OUTPUT]"
    if isinstance(output, list):
        return [f"[MASKED ITEM {i}]" for i in range(len(output))]
    if isinstance(output, dict):
        return {k: "[MASKED]" for k in output}
    raise TypeError(f"unmaskable output type {type(output).__name__}")
