#!/usr/bin/env bash
# demo.sh — run the safe, deterministic parts of the workflow against synthetic
# data. No network requests are made to a real target.
#
#   1. scope check against examples/scope.md       (real checker, synthetic hosts)
#   2. URL classification                           (real cbh classifier)
#   3. engine mock run                              (mock recon, deterministic map)
#
# The engine mock uses a local lab fixture; it is labelled as mock in the output.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENGINE="${OPENCODE_RED_ENGINE:-$HOME/.config/opencode/bughunter/engine}"
CBH="${OPENCODE_RED_CBH:-$HOME/.config/opencode/bughunter/cbh/cli.py}"

if [ ! -f "$ENGINE/scope.py" ] || [ ! -f "$CBH" ]; then
  echo "opencode-red is not installed. Run ./install.sh first." >&2
  exit 1
fi

line() { printf '\n\033[1;35m$ %s\033[0m\n' "$*"; }

line "python3 engine/scope.py app.acme-lab.example admin.acme-lab.example --md examples/scope.md"
python3 "$ENGINE/scope.py" app.acme-lab.example admin.acme-lab.example --md "$REPO_DIR/examples/scope.md" || true

line "cbh classify 'https://api.acme-lab.example/v1/invoices/1042?next=https://evil.example'"
python3 "$CBH" classify "https://api.acme-lab.example/v1/invoices/1042?next=https://evil.example"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
line "engine.py --scope examples/engagement.json --mock --hunt"
python3 "$ENGINE/engine.py" --scope "$REPO_DIR/examples/engagement.json" --base "$TMP" --mock --hunt
