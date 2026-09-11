#!/usr/bin/env bash
# Negative controls for bench clearance. Builds a fixture repo with a
# bare origin and a fake model cache; every refusal must fire, KEEP
# must hold, and a model an open TR references must survive execute.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
T="$(mktemp -d "${TMPDIR:-/tmp}/bench.XXXXXX")"
fails=0; legs=0
pass() { legs=$((legs+1)); echo "  PASS  $1"; }
fail() { legs=$((legs+1)); fails=$((fails+1)); echo "  FAIL  $1"; }
BC="python3 $HERE/bench_clear.py --repo $T/repo --hub $T/hub --no-fetch"
git init -q -b main "$T/repo"; git init -q --bare "$T/origin.git"
cd "$T/repo"; git remote add origin "$T/origin.git"
mkdir -p tr900/report tr900/corpus_store tr900/.venv tr900/results tr901/report tr901/results
echo "x" > tr900/report/TR900_report.md; echo "r" > tr900/results/analysis.json; echo "big" > tr900/corpus_store/blob; echo "v" > tr900/.venv/bin
echo 'model = "org/model-a"' > tr900/extract.py
echo 'model = "org/model-b"' > tr901/extract.py; echo "open" > tr901/report/TR901_report.md
mkdir -p "$T/hub/models--org--model-a/snapshots/x" "$T/hub/models--org--model-b/snapshots/x" "$T/hub/models--org--orphan/snapshots/x"
echo w > "$T/hub/models--org--model-a/snapshots/x/w"; echo w > "$T/hub/models--org--model-b/snapshots/x/w"; echo w > "$T/hub/models--org--orphan/snapshots/x/w"
printf 'corpus_store/\n.venv/\n' > .gitignore
git add -A >/dev/null; git -c user.name=t -c user.email=t@t commit -q -m fixture; git push -q origin main
echo "[1] refusals"
$BC tr900 >/dev/null 2>&1 && fail "swept without RATIFIED" || pass "refuses without report/RATIFIED"
echo "2026-09-11 fixture" > tr900/report/RATIFIED
$BC tr900 >/dev/null 2>&1 && fail "swept with uncommitted marker" || pass "refuses while the marker is uncommitted"
git add -A >/dev/null; git -c user.name=t -c user.email=t@t commit -q -m ratified
$BC tr900 >/dev/null 2>&1 && fail "swept before push" || pass "refuses while HEAD is not on origin"
git push -q origin main
$BC tr901 >/dev/null 2>&1 && fail "swept an open TR" || pass "refuses an open TR (no marker)"
echo "[2] dry run lists the right things"
out="$($BC tr900 2>&1)"
echo "$out" | grep -q "SWEEP.*tr900/corpus_store" && pass "corpus_store listed for sweep" || fail "corpus_store not listed"
echo "$out" | grep -q "SWEEP.*hub/org/model-a" && pass "model referenced only by the cleared TR listed" || fail "model-a not listed"
echo "$out" | grep -q "KEEP (open: tr901).*hub/org/model-b" && pass "model referenced by an open TR kept" || fail "model-b not kept"
echo "$out" | grep -q "REPORT ONLY.*hub/org/orphan" && pass "unreferenced model reported, not swept" || fail "orphan handling wrong"
[ -d tr900/corpus_store ] && pass "dry run deleted nothing" || fail "dry run deleted"
echo "[3] KEEP and execute"
printf 'corpus_store  # PI word, fixture\n' > tr900/KEEP; git add -A >/dev/null; git -c user.name=t -c user.email=t@t commit -q -m keep; git push -q origin main
$BC tr900 --execute >/dev/null 2>&1 || fail "execute refused unexpectedly"
[ -d tr900/corpus_store ] && pass "KEEP path survived execute" || fail "KEEP path deleted"
[ -d tr900/.venv ] && fail ".venv survived execute" || pass ".venv swept"
[ -d "$T/hub/models--org--model-a" ] && fail "model-a survived" || pass "model-a swept"
[ -d "$T/hub/models--org--model-b" ] && pass "model-b (open TR) survived" || fail "model-b deleted"
[ -d "$T/hub/models--org--orphan" ] && pass "orphan model survived" || fail "orphan deleted"
[ -f tr900/results/analysis.json ] && pass "evidence untouched" || fail "evidence deleted"
grep -q "Bench cleared" tr900/DECISIONS.md && pass "disk line appended to DECISIONS" || fail "no disk line"
echo; echo "bench clearance verify: $((legs-fails))/$legs legs green; $fails failing"
rm -rf "$T"; [ $fails -eq 0 ]
