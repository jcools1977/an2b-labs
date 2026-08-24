#!/usr/bin/env python3
"""Record the HF commit hash of each downloaded model snapshot in
data/MANIFEST.json under "models" (DECISIONS.md D13).

mlx-community repos are updated in place, so a bare repo name is a moving
target; the snapshot commit turns "we used Qwen3-8B-4bit" into a
reproducible claim. Refuses to record a repo whose snapshot is absent or
ambiguous, and refuses to silently change an already-recorded pin.
"""
import json
import sys
from pathlib import Path

REPOS = [
    "mlx-community/Qwen3-8B-4bit",
    "mlx-community/Meta-Llama-3.1-8B-Instruct-8bit",
]

HUB = Path.home() / ".cache" / "huggingface" / "hub"
MANIFEST = Path(__file__).resolve().parents[1] / "data" / "MANIFEST.json"


def snapshot_commit(repo):
    snap_dir = HUB / ("models--" + repo.replace("/", "--")) / "snapshots"
    commits = [p.name for p in snap_dir.iterdir() if p.is_dir()] if snap_dir.is_dir() else []
    if len(commits) != 1:
        raise RuntimeError(
            f"{repo}: expected exactly one downloaded snapshot, found "
            f"{commits or 'none'}; download it (or prune stale ones) first"
        )
    return commits[0]


def main():
    with open(MANIFEST) as fh:
        manifest = json.load(fh)
    recorded = manifest.setdefault("models", {})

    for repo in REPOS:
        commit = snapshot_commit(repo)
        prior = recorded.get(repo, {}).get("hf_commit")
        if prior is not None and prior != commit:
            print(
                f"PIN CONFLICT: {repo} already recorded at {prior}, local "
                f"snapshot is {commit}; the repo changed upstream. Re-download "
                f"the pinned revision or record the change in DECISIONS.md "
                f"first. Not overwriting."
            )
            return 1
        recorded[repo] = {"hf_commit": commit}
        print(f"pinned {repo} @ {commit}")

    with open(MANIFEST, "w") as fh:
        json.dump(manifest, fh, indent=2)
    print(f"wrote {MANIFEST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
