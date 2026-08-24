"""Hard gates shared by TR-001 scripts (PHASE2_BRIEF, D13).

Every gate raises SystemExit on violation. Nothing downstream of a failed
gate runs; a mismatch is never excused or worked around.
"""
import hashlib
import json
from pathlib import Path

TR_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = TR_ROOT / "data" / "MANIFEST.json"
HUB = Path.home() / ".cache" / "huggingface" / "hub"

A_REPO = "mlx-community/Qwen3-8B-4bit"
# B at 4-bit per the D6 headroom rule: the 8-bit build measured 19.95 GB
# peak on a one-step training probe (adapter state is ~8.6 GB fp32 on its
# own) and engaged swap on the 16 GB machine.
B_REPO = "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"


def manifest():
    with open(MANIFEST_PATH) as fh:
        return json.load(fh)


def vocab_sha256(tokenizer):
    tok = getattr(tokenizer, "_tokenizer", tokenizer)  # mlx TokenizerWrapper
    return hashlib.sha256(
        json.dumps(tok.get_vocab(), sort_keys=True).encode("utf-8")
    ).hexdigest()


def assert_b_tokenizer(tokenizer):
    """The 200-400 filter was measured with the MANIFEST tokenizer; the
    production B build must be the same ruler, or the split rebuilds."""
    want = manifest()["tokenizer"]["vocab_sha256"]
    got = vocab_sha256(tokenizer)
    if got != want:
        raise SystemExit(
            f"TOKENIZER GATE: production B vocab hash {got[:16]}... != "
            f"MANIFEST {want[:16]}...; the split was measured with the wrong "
            f"ruler. Rebuild it (scripts/build_split.py, deterministic, "
            f"seed 7) instead of excusing this."
        )


def pinned_snapshot(repo):
    """Return (snapshot_path, commit) for the MANIFEST-pinned revision.
    Loading by this path makes floating to a newer upstream impossible."""
    pin = manifest()["models"][repo]["hf_commit"]
    snap = HUB / ("models--" + repo.replace("/", "--")) / "snapshots" / pin
    if not snap.is_dir():
        raise SystemExit(
            f"REVISION GATE: {repo} is pinned at {pin[:12]} (MANIFEST "
            f"models, D13) but that snapshot is not in the local HF cache. "
            f"Download the pinned revision; do not float to latest."
        )
    return snap, pin
