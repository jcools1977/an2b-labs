#!/usr/bin/env python3
"""Plumbing smoke: a synthetic corpus_store with two fake spaces
('bge' as a random clustered space, 'minilm' as its rotation plus
noise), the real store JSON schema, then run_grid + assemble_gates +
the three checkers. On this world the PASS gate must hold and every
control must hold; on a second world where 'minilm' is unrelated,
the PASS gate must FAIL and the KILL must fire. Exit nonzero if either
side misbehaves.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

TR = Path(__file__).resolve().parents[1]
N_STORE, N_Q, D, POOL = 1200, 120, 48, 2048


def make_world(root, seed, structured):
    rng = np.random.default_rng(seed)
    n_text = N_STORE + POOL + 2 * N_Q + 3 * 1024  # store, pool, q1, q2, scrambled
    centers = rng.standard_normal((40, D)) * 3
    lab = rng.integers(0, 40, n_text)
    A = centers[lab] + rng.standard_normal((n_text, D))
    R, _ = np.linalg.qr(rng.standard_normal((D, D)))
    B = A @ R + 0.15 * rng.standard_normal(A.shape) if structured else rng.standard_normal(A.shape)
    ids = []
    store = [f"w{i//100:02d}__{i%100:04d}" for i in range(N_STORE)]
    pool = [f"p{i//128:02d}__{i%128:04d}" for i in range(POOL)]
    ids += store + pool
    q1 = [f"q1_{seed}_{store[i]}" for i in range(N_Q)]
    q2 = [f"q2_{seed}_{store[i]}" for i in range(N_Q, 2 * N_Q)]
    ids += q1 + q2
    scr = {str(k): [f"scr_{seed}_{k}_{i:04d}" for i in range(k)] for k in (64, 256, 1024)}
    ids += scr["64"] + scr["256"] + scr["1024"]
    assert len(ids) <= n_text
    # queries: noisy copies of their targets; q2 cue = the successor (noisy)
    off = N_STORE + POOL
    A[off:off + N_Q] = A[:N_Q] + 0.1 * rng.standard_normal((N_Q, D))
    B[off:off + N_Q] = B[:N_Q] + 0.1 * rng.standard_normal((N_Q, D))
    A[off + N_Q:off + 2 * N_Q] = A[N_Q + 1:2 * N_Q + 1] + 0.1 * rng.standard_normal((N_Q, D))
    B[off + N_Q:off + 2 * N_Q] = B[N_Q + 1:2 * N_Q + 1] + 0.1 * rng.standard_normal((N_Q, D))
    # scrambled anchors: far-off random vectors, paired consistently
    soff = off + 2 * N_Q
    A[soff:soff + 1344] = rng.standard_normal((1344, D)) * 6 + 20
    B[soff:soff + 1344] = A[soff:soff + 1344] @ R if structured else rng.standard_normal((1344, D))
    emb = root / "emb"
    emb.mkdir(parents=True)
    np.savez(emb / "bge.npz", ids=np.array(ids), X=A[:len(ids)].astype(np.float32))
    np.savez(emb / "minilm.npz", ids=np.array(ids), X=B[:len(ids)].astype(np.float32))
    st = {"seed": seed, "store": store,
          "store_meta": {c: {"work": c.split("__")[0], "pos": int(c.split("__")[1])} for c in store},
          "q1": [{"qid": q1[i], "target": store[i], "work": store[i].split("__")[0]} for i in range(N_Q)],
          "q2": [{"qid": q2[i - N_Q], "target": store[i], "work": store[i].split("__")[0], "cue_source": store[i + 1]} for i in range(N_Q, 2 * N_Q)],
          "anchor_pool": pool,
          "anchors_random": {str(k): list(rng.choice(pool, k, replace=False)) for k in (64, 256, 1024)},
          "anchors_mismatched": {str(k): {"A": list(rng.choice(pool[:1024], k, replace=False)),
                                          "B": list(rng.choice(pool[1024:], k, replace=False))} for k in (64, 256, 1024)},
          "anchors_scrambled": scr}
    json.dump(st, open(root / f"store_{seed}.json", "w"))


def run_world(structured):
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "corpus_store"
        for seed in (41, 43):
            pass
        root.mkdir()
        # both seeds share embeddings but have their own store json (same ids)
        make_world(root, 41, structured)
        st = json.load(open(root / "store_41.json"))
        st["seed"] = 43
        json.dump(st, open(root / "store_43.json", "w"))
        res = Path(td) / "results"
        res.mkdir()
        man = {"disjointness": {"store_vs_anchor_pool": True, "query_sources_vs_anchor_pool": True,
                                "anchors_vs_queries_all_seed_pairs": True, "works_partition_global": True}}
        json.dump(man, open(Path(td) / "manifest.json", "w"))
        for cmd in ([sys.executable, str(TR / "scripts" / "run_grid.py"), "--root", str(root),
                     "--spaces", "bge,minilm", "--out", str(res / "grid.jsonl")],
                    [sys.executable, str(TR / "scripts" / "assemble_gates.py"), "--grid", str(res / "grid.jsonl"),
                     "--manifest", str(Path(td) / "manifest.json"), "--outdir", str(res)]):
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0:
                print("  step failed:", " ".join(Path(c).name for c in cmd[:2]))
                print("  " + "\n  ".join(r.stderr.strip().splitlines()[-6:]))
                raise SystemExit(1)
        rc = {}
        for name, f in (("pass", "analysis.json"), ("kill", "kill.json"), ("controls", "controls.json")):
            r = subprocess.run([sys.executable, str(TR / "checks" / f"check_{name}.py"), str(res / f)],
                               capture_output=True, text=True)
            rc[name] = (r.returncode, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "")
        return rc


def main():
    bad = 0
    print("recoverable world (rotation): PASS and controls must hold, KILL must not fire")
    rc = run_world(True)
    for k, (code, line) in rc.items():
        ok = code == 0
        print(f"  {'ok ' if ok else 'FAIL'} {k}: {line}")
        bad += 0 if ok else 1
    print("unrelated world: PASS must FAIL and KILL must fire (the red side)")
    rc = run_world(False)
    for k, want_fail in (("pass", True), ("kill", True)):
        code, line = rc[k]
        ok = (code != 0) == want_fail
        print(f"  {'ok ' if ok else 'FAIL'} {k}: {line}")
        bad += 0 if ok else 1
    print(f"grid smoke: {'PASS' if bad == 0 else str(bad) + ' failing'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
