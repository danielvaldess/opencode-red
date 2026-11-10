#!/usr/bin/env bash
# install.sh — install the OpenCode Red arsenal.
#
#   ./install.sh                 # skills + commands + engine + workspace
#   ./install.sh --tools         # also install the external toolchain
#   ./install.sh --dry-run       # show the plan, change nothing
#
# Defaults (override with flags or environment):
#   skills    ~/.claude/skills
#   commands  ~/.config/opencode/commands
#   engine    ~/.config/opencode/bughunter
#   bin       ~/.local/bin
#   upstream  ~/.local/share/opencode-red/upstream
#   workspace ~/bounties
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UPSTREAM_DIR="${OPENCODE_RED_UPSTREAM:-$HOME/.local/share/opencode-red/upstream}"
SKILLS_DIR="${OPENCODE_RED_SKILLS:-$HOME/.claude/skills}"
COMMANDS_DIR="${OPENCODE_RED_COMMANDS:-$HOME/.config/opencode/commands}"
ENGINE_DIR="${OPENCODE_RED_ENGINE:-$HOME/.config/opencode/bughunter}"
BIN_DIR="${OPENCODE_RED_BIN:-$HOME/.local/bin}"
WORKSPACE="${OPENCODE_RED_WORKSPACE:-$HOME/bounties}"

TOOLS=0; DRY=0; INSTALL_COMMANDS=1

usage() {
  sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'
}

while [ $# -gt 0 ]; do
  case "$1" in
    --tools) TOOLS=1 ;;
    --no-commands) INSTALL_COMMANDS=0 ;;
    --dry-run) DRY=1 ;;
    --workspace) WORKSPACE="$2"; shift ;;
    --upstream) UPSTREAM_DIR="$2"; shift ;;
    --skills-dir) SKILLS_DIR="$2"; shift ;;
    --engine-dir) ENGINE_DIR="$2"; shift ;;
    --bin-dir) BIN_DIR="$2"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1 (try --help)" >&2; exit 2 ;;
  esac
  shift
done

say() { printf '\033[1m%s\033[0m\n' "$*"; }
ok()  { printf '  \033[32m✓\033[0m %s\n' "$*"; }
warn(){ printf '  \033[33m!\033[0m %s\n' "$*"; }

say "OpenCode Red installer"
echo "  repo       : $REPO_DIR"
echo "  upstream   : $UPSTREAM_DIR"
echo "  skills     : $SKILLS_DIR"
echo "  commands   : $COMMANDS_DIR"
echo "  engine     : $ENGINE_DIR"
echo "  bin        : $BIN_DIR"
echo "  workspace  : $WORKSPACE"
echo "  tools      : $([ "$TOOLS" -eq 1 ] && echo yes || echo no)"
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 is required" >&2
  exit 1
fi
if ! command -v git >/dev/null 2>&1 && [ ! -d "$UPSTREAM_DIR/Claude-BugHunter" ]; then
  echo "error: git is required for the first install" >&2
  exit 1
fi
if ! command -v opencode >/dev/null 2>&1; then
  warn "opencode is not on PATH; the files will be installed anyway"
fi

if [ "$DRY" -eq 1 ]; then
  say "Plan (dry-run)"
  echo "  1. clone/update upstream bundles into $UPSTREAM_DIR"
  echo "  2. install skills into $SKILLS_DIR"
  echo "  3. install commands into $COMMANDS_DIR"
  echo "  4. install engine + cbh into $ENGINE_DIR and $BIN_DIR/cbh"
  echo "  5. scaffold workspace $WORKSPACE"
  [ "$TOOLS" -eq 1 ] && echo "  6. install external tools"
  echo
  echo "No changes written."
  exit 0
fi

# --------------------------------------------------------------------------- #
# 1. upstream
# --------------------------------------------------------------------------- #
clone_or_update() {
  local url="$1" dir="$2"
  if [ -d "$dir" ] && [ ! -d "$dir/.git" ]; then
    echo "error: $dir exists but is not a git repository; move it away and re-run" >&2
    exit 1
  fi
  if [ -d "$dir/.git" ]; then
    echo "→ updating $(basename "$dir")"
    git -C "$dir" fetch --depth 1 origin >/dev/null 2>&1 || git -C "$dir" fetch origin >/dev/null 2>&1
    git -C "$dir" reset --hard FETCH_HEAD >/dev/null 2>&1
  else
    echo "→ cloning $(basename "$dir")"
    git clone --depth 1 "$url" "$dir"
  fi
}

mkdir -p "$UPSTREAM_DIR"
clone_or_update https://github.com/elementalsouls/Claude-BugHunter.git "$UPSTREAM_DIR/Claude-BugHunter"
clone_or_update https://github.com/SnailSploit/claude-red.git "$UPSTREAM_DIR/claude-red"
clone_or_update https://github.com/cdmx-in/security-review.git "$UPSTREAM_DIR/security-review"
ok "upstream bundles ready"

# --------------------------------------------------------------------------- #
# 2-4. skills, commands, engine
# --------------------------------------------------------------------------- #
ARGS=(
  --repo "$REPO_DIR"
  --bughunter "$UPSTREAM_DIR/Claude-BugHunter"
  --claude-red "$UPSTREAM_DIR/claude-red"
  --security-review "$UPSTREAM_DIR/security-review"
  --skills-dir "$SKILLS_DIR"
  --commands-dir "$COMMANDS_DIR"
  --engine-dir "$ENGINE_DIR"
  --bin-dir "$BIN_DIR"
)
if [ "$INSTALL_COMMANDS" -eq 0 ]; then
  ARGS+=(--skip-commands)
fi
python3 "$REPO_DIR/scripts/install_skills.py" "${ARGS[@]}"
ok "skills, commands and engine installed"

# --------------------------------------------------------------------------- #
# 5. workspace
# --------------------------------------------------------------------------- #
mkdir -p "$WORKSPACE"
if [ ! -f "$WORKSPACE/AGENTS.md" ]; then
  cp "$REPO_DIR/templates/workspace-AGENTS.md" "$WORKSPACE/AGENTS.md"
  ok "workspace rules -> $WORKSPACE/AGENTS.md"
else
  ok "workspace rules already present"
fi
if [ ! -f "$WORKSPACE/README.md" ]; then
  cp "$REPO_DIR/templates/workspace-README.md" "$WORKSPACE/README.md"
fi

# --------------------------------------------------------------------------- #
# 6. tools
# --------------------------------------------------------------------------- #
if [ "$TOOLS" -eq 1 ]; then
  echo
  bash "$REPO_DIR/scripts/install_tools.sh"
fi

echo
say "Installed"
echo "  next: cd $WORKSPACE && bbnew <program>"
echo "        then open OpenCode there and run /hunt <target>"
echo
echo "  verify: $REPO_DIR/scripts/verify.sh"
echo "  docs  : $REPO_DIR/docs/ARSENAL.md"
