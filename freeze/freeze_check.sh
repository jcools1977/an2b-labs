#!/usr/bin/env bash
# Frozen-protocol freeze check (ARENA rule 3, review B4).
# BB4C rule 1 says frozen protocol files are never modified. This is
# its negative control: the check FAILS on any byte change, deletion,
# or unlisted addition among the frozen TRxxx protocol files.
#
#   freeze/freeze_check.sh            check the working tree (default root)
#   FREEZE_ROOT=/dir freeze_check.sh  check another directory holding copies
#   freeze/freeze_check.sh --reissue  rewrite MANIFEST (a logged, approved act)
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${FREEZE_ROOT:-$(cd "$HERE/.." && pwd)}"
MANIFEST="${FREEZE_MANIFEST:-$HERE/MANIFEST.sha256}"

frozen_files() {
  # Protocol files only: TRnnn or TRnnnx followed by an underscore.
  # Kickoff-gate packages are adjudication documents, not protocols.
  (cd "$ROOT" && ls TR[0-9][0-9][0-9]_*.md TR[0-9][0-9][0-9][a-z]_*.md 2>/dev/null \
     | grep -v KICKOFF_GATE | sort)
}

if [[ "${1:-}" == "--reissue" ]]; then
  {
    echo "# Frozen protocol manifest. Reissued $(date -u +%Y-%m-%dT%H:%M:%SZ) at commit $(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)."
    echo "# Any reissue is a logged act approved through a channel other than the seat it constrains."
    (cd "$ROOT" && frozen_files | xargs shasum -a 256)
  } > "$MANIFEST"
  echo "manifest reissued: $(grep -c '^[0-9a-f]' "$MANIFEST") files"
  exit 0
fi

fail=0
[[ -f "$MANIFEST" ]] || { echo "FREEZE: manifest missing at $MANIFEST"; exit 1; }
listed="$(grep '^[0-9a-f]' "$MANIFEST" | awk '{print $2}' | sort)"
present="$(frozen_files)"
if [[ "$listed" != "$present" ]]; then
  echo "FREEZE: file set differs from manifest"
  diff <(echo "$listed") <(echo "$present") | sed 's/^/  /'
  fail=1
fi
out="$(cd "$ROOT" && grep '^[0-9a-f]' "$MANIFEST" | shasum -a 256 -c 2>&1)"
if echo "$out" | grep -qv ': OK$'; then
  echo "FREEZE: content differs from manifest"
  echo "$out" | grep -v ': OK$' | sed 's/^/  /'
  fail=1
fi
if [[ $fail -eq 0 ]]; then
  echo "FREEZE: OK, $(echo "$present" | wc -l | tr -d ' ') frozen protocol files match the manifest"
fi
exit $fail
