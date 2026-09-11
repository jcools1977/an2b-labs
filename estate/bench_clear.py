#!/usr/bin/env python3
"""Bench clearance (estate/BENCH_CLEAR.md). Dry run by default.

  bench_clear.py tr002r tr004            # what would be swept
  bench_clear.py tr002r --execute        # sweep and write the disk line
  bench_clear.py --all-ratified          # every TR with report/RATIFIED
Options: --repo PATH (default: this repo), --hub PATH (HF cache),
--no-fetch (skip origin fetch), --execute.
Refuses unless report/RATIFIED exists, the TR's tracked files are
clean, and HEAD is contained in origin/main.
"""
import argparse
import datetime as dt
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

BULK_DIRS = ["corpus_store", "data/raw", "cache", "checkpoints", ".venv", "build", "dist", "adapters"]
BULK_GLOBS = ["*.egg-info", "*.log", "**/.venv", "**/__pycache__", "**/*.log"]


def sh(args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def du(path: Path) -> int:
    total = 0
    if path.is_file():
        return path.stat().st_size
    for p in path.rglob("*"):
        try:
            if p.is_file() and not p.is_symlink():
                total += p.stat().st_size
        except OSError:
            pass
    return total


def gb(n):
    return f"{n/1e9:6.2f} GB"


def read_keep(path: Path):
    if not path.exists():
        return []
    out = []
    for ln in path.read_text().splitlines():
        ln = ln.split("#", 1)[0].strip()
        if ln:
            out.append(ln.rstrip("/"))
    return out


def refuse(msg):
    print(f"REFUSED: {msg}")
    return 2


def check_gate(repo: Path, tr: str, fetch: bool):
    trd = repo / tr
    if not trd.is_dir():
        return f"{tr}: no such experiment directory"
    if not (trd / "report" / "RATIFIED").exists():
        return f"{tr}: report/RATIFIED absent; the report is not ratified, the bench stays"
    st = sh(["git", "status", "--porcelain", "--", tr], repo)
    if st.stdout.strip():
        return f"{tr}: tracked or untracked files not committed:\n" + st.stdout
    if fetch:
        sh(["git", "fetch", "-q", "origin"], repo)
    r = sh(["git", "merge-base", "--is-ancestor", "HEAD", "origin/main"], repo)
    if r.returncode != 0:
        return f"{tr}: HEAD is not on origin/main; push first"
    return None


def bulk_for(repo: Path, tr: str):
    trd = repo / tr
    keep = read_keep(trd / "KEEP")
    items = []
    seen = set()
    cands = [trd / d for d in BULK_DIRS]
    for g in BULK_GLOBS:
        cands.extend(trd.glob(g))
    cands = sorted({c for c in cands if c.exists()}, key=lambda c: len(c.parts))
    for p in cands:
        if p in seen or any(str(p).startswith(str(q) + os.sep) for q in seen):
            continue  # nested inside a directory already listed
        seen.add(p)
        rel = p.relative_to(trd).as_posix()
        if any(rel == k or rel.startswith(k + "/") for k in keep):
            items.append((p, rel, "KEEP (trXXX/KEEP)", du(p)))
        else:
            items.append((p, rel, "SWEEP", du(p)))
    return items


def model_refs(repo: Path, hub: Path):
    """model id -> set of TRs referencing it (by string in code/docs)."""
    refs = {}
    models = [d for d in hub.glob("models--*") if d.is_dir()] if hub.is_dir() else []
    trs = [d for d in repo.glob("tr[0-9]*") if d.is_dir()]
    texts = {}
    for trd in trs:
        buf = []
        for p in trd.rglob("*"):
            if p.is_file() and p.suffix in (".py", ".md", ".json", ".txt", ".sh", ".yaml") and \
               not any(part in ("corpus_store", ".venv", "cache", "adapters", "results") for part in p.parts):
                try:
                    buf.append(p.read_text(errors="ignore"))
                except OSError:
                    pass
        texts[trd.name] = "\n".join(buf)
    for m in models:
        mid = m.name[len("models--"):].replace("--", "/", 1)
        refs[mid] = {t for t, txt in texts.items() if mid in txt or mid.split("/")[-1] in txt}
    return refs, {m.name[len("models--"):].replace("--", "/", 1): m for m in models}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("trs", nargs="*")
    ap.add_argument("--all-ratified", action="store_true")
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--hub", default=os.path.expanduser("~/.cache/huggingface/hub"))
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--execute", action="store_true")
    a = ap.parse_args()
    repo, hub = Path(a.repo).resolve(), Path(a.hub).expanduser().resolve()
    trs = list(a.trs)
    if a.all_ratified:
        trs += [d.name for d in sorted(repo.glob("tr[0-9]*")) if (d / "report" / "RATIFIED").exists() and d.name not in trs]
    if not trs:
        return refuse("name at least one TR or pass --all-ratified")
    for tr in trs:
        err = check_gate(repo, tr, not a.no_fetch)
        if err:
            return refuse(err)
    ratified = {d.name for d in repo.glob("tr[0-9]*") if (d / "report" / "RATIFIED").exists()}
    open_trs = {d.name for d in repo.glob("tr[0-9]*") if d.is_dir()} - ratified
    plan = []
    for tr in trs:
        for p, rel, action, size in bulk_for(repo, tr):
            plan.append((tr, p, f"{tr}/{rel}", action, size))
    refs, mdirs = model_refs(repo, hub)
    hub_keep = read_keep(repo / "estate" / "KEEP")
    for mid, who in sorted(refs.items()):
        size = du(mdirs[mid])
        if mid in hub_keep:
            action = "KEEP (estate/KEEP)"
        elif not who:
            action = "REPORT ONLY (referenced by nothing; provenance unknown)"
        elif who & open_trs:
            action = f"KEEP (open: {', '.join(sorted(who & open_trs))})"
        elif who & set(trs):
            action = "SWEEP"
        else:
            action = f"KEEP (referenced by ratified {', '.join(sorted(who))}, not being cleared)"
        plan.append(("hub", mdirs[mid], f"hub/{mid}", action, size))
    host = platform.node()
    print(f"bench clearance on {host}: {'EXECUTE' if a.execute else 'DRY RUN'} for {', '.join(trs)}")
    total = 0
    for tr, p, label, action, size in plan:
        print(f"  {gb(size)}  {action:44} {label}")
        if action == "SWEEP":
            total += size
    print(f"  {gb(total)}  would be freed" if not a.execute else f"  {gb(total)}  to free")
    if not a.execute:
        return 0
    removed = []
    for tr, p, label, action, size in plan:
        if action != "SWEEP":
            continue
        rp = p.resolve()
        if not (str(rp).startswith(str(repo) + os.sep) or str(rp).startswith(str(hub) + os.sep)):
            print(f"  skip (outside repo and hub): {rp}")
            continue
        if rp.is_dir() and not rp.is_symlink():
            shutil.rmtree(rp)
        else:
            rp.unlink()
        removed.append((label, size))
    free = shutil.disk_usage(str(repo)).free
    stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    for tr in trs:
        mine = [(l, s) for l, s in removed if l.startswith(tr + "/") or l.startswith("hub/")]
        line = (f"\n\n## Bench cleared {stamp} on {host} (estate/BENCH_CLEAR.md)\n"
                f"Removed: " + (", ".join(f"{l} ({gb(s).strip()})" for l, s in mine) or "nothing") +
                f". Kept: evidence, KEEP entries, sealed plaintexts. Free after: {gb(free).strip()}.\n")
        with open(repo / tr / "DECISIONS.md", "a") as fh:
            fh.write(line)
    print(f"  removed {len(removed)} paths, {gb(sum(s for _, s in removed))} freed; disk lines appended (commit them)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
