#!/usr/bin/env bash
# Cockpit side. Reads the OpenRouter key from 1Password and pipes it over
# ssh into the panel runner's stdin on legion. The key is never written
# to disk on either machine and never enters a shell environment: the
# runner reads it from fd 0 and holds it in process memory only.
#
#   oracle/panel/inject_key.sh exam
#   oracle/panel/inject_key.sh seal TR-003r TR003r_....md
#
# Requires: `op signin` completed in this terminal; the item at
# $OP_OPENROUTER_ITEM (default op://Private/OpenRouter/credential).
set -euo pipefail
ITEM="${OP_OPENROUTER_ITEM:-op://Private/OpenRouter/credential}"
HOST="${PANEL_HOST:-legion}"
LAB="${PANEL_LAB_DIR:-\$HOME/an2b-labs}"
PY="${PANEL_PY:-\$HOME/clawtex-env/bin/python}"
op whoami >/dev/null 2>&1 || { echo "1Password CLI is not signed in; run: op signin" >&2; exit 3; }
op read "$ITEM" | ssh "$HOST" "cd $LAB && $PY oracle/panel/panel.py $*"
