#!/usr/bin/env bash
# install_tools.sh — install the external tools used by the arsenal.
#
# This is opt-in: `./install.sh --tools` runs it. It installs into
# $HOME/go/bin and $HOME/.local/bin, and never touches system packages.
#
# Usage:
#   ./scripts/install_tools.sh [--minimal] [--skip-go] [--skip-python] [--dry-run]
#
# Requires: go (for the Go tools) and pipx (for semgrep/ghauri). Missing
# prerequisites are reported, not fatal.
set -uo pipefail

GOBIN="${GOBIN:-$HOME/go/bin}"
BIN="${HOME}/.local/bin"
MINIMAL=0; SKIP_GO=0; SKIP_PY=0; DRY=0

for arg in "$@"; do
  case "$arg" in
    --minimal) MINIMAL=1 ;;
    --skip-go) SKIP_GO=1 ;;
    --skip-python) SKIP_PY=1 ;;
    --dry-run) DRY=1 ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

run() {
  if [ "$DRY" -eq 1 ]; then echo "[dry-run] $*"; else "$@"; fi
}

link() {
  local name="$1"
  [ -x "$GOBIN/$name" ] || return 0
  run ln -sf "$GOBIN/$name" "$BIN/$name"
}

mkdir -p "$GOBIN" "$BIN"

# --------------------------------------------------------------------------- #
# Go tools
# --------------------------------------------------------------------------- #
if [ "$SKIP_GO" -eq 0 ]; then
  if ! command -v go >/dev/null 2>&1; then
    echo "!! go not found; skipping Go tools (install Go 1.21+ and re-run)" >&2
  else
    GO_TOOLS=(
      "subfinder|github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
      "dnsx|github.com/projectdiscovery/dnsx/cmd/dnsx@latest"
      "httpx|github.com/projectdiscovery/httpx/cmd/httpx@latest"
      "katana|github.com/projectdiscovery/katana/cmd/katana@latest"
      "chaos|github.com/projectdiscovery/chaos-client/cmd/chaos@latest"
      "assetfinder|github.com/tomnomnom/assetfinder@latest"
      "anew|github.com/tomnomnom/anew@latest"
      "waybackurls|github.com/tomnomnom/waybackurls@latest"
      "gf|github.com/tomnomnom/gf@latest"
      "gau|github.com/lc/gau/v2/cmd/gau@latest"
    )
    [ "$MINIMAL" -eq 1 ] || GO_TOOLS+=(
      "dalfox|github.com/hahwul/dalfox/v2@latest"
      "gitleaks|github.com/zricethezav/gitleaks/v8@latest"
    )
    for entry in "${GO_TOOLS[@]}"; do
      name="${entry%%|*}"
      pkg="${entry#*|}"
      if [ -x "$GOBIN/$name" ]; then
        echo "✓ $name already installed"
        link "$name"
        continue
      fi
      echo "→ go install $pkg"
      if [ "$DRY" -eq 1 ]; then
        echo "[dry-run] GOBIN=$GOBIN go install $pkg"
      elif GOBIN="$GOBIN" go install "$pkg"; then
        link "$name"
      else
        echo "!! failed: $pkg" >&2
      fi
    done

    # ProjectDiscovery httpx is named `httpx`, which often collides with the
    # Python library's CLI. Replace the Python wrapper only if it is broken.
    if [ -x "$GOBIN/httpx" ]; then
      if [ -f "$BIN/httpx" ] && [ ! -L "$BIN/httpx" ]; then
        if ! "$BIN/httpx" -version 2>&1 | grep -qi projectdiscovery; then
          echo "→ moving Python httpx CLI to $BIN/httpx-python.bak"
          run mv "$BIN/httpx" "$BIN/httpx-python.bak"
        fi
      fi
      link httpx
    fi

    # trufflehog's module has replace directives; use the release binary.
    if [ ! -x "$GOBIN/trufflehog" ] && [ "$MINIMAL" -eq 0 ]; then
      ver="$(curl -fsSL https://api.github.com/repos/trufflesecurity/trufflehog/releases/latest 2>/dev/null | jq -r .tag_name 2>/dev/null || true)"
      if [ -n "${ver:-}" ] && [ "$ver" != "null" ]; then
        url="https://github.com/trufflesecurity/trufflehog/releases/latest/download/trufflehog_${ver#v}_linux_amd64.tar.gz"
        tmp="$(mktemp -d)"
        echo "→ trufflehog $ver"
        if [ "$DRY" -eq 1 ]; then
          echo "[dry-run] curl $url | tar -> $GOBIN/trufflehog"
        elif curl -fsSL "$url" -o "$tmp/th.tgz" && tar -xzf "$tmp/th.tgz" -C "$tmp"; then
          install -m755 "$tmp/trufflehog" "$GOBIN/trufflehog" && link trufflehog
        else
          echo "!! could not download trufflehog (install it manually)" >&2
        fi
        rm -rf "$tmp"
      fi
    fi

    # gf patterns
    if [ ! -d "$HOME/.gf" ]; then
      echo "→ cloning gf patterns"
      run git clone --depth 1 https://github.com/1ndianl33t/Gf-Patterns "$HOME/.gf"
    else
      echo "✓ gf patterns present"
    fi
  fi
fi

# --------------------------------------------------------------------------- #
# Python tools
# --------------------------------------------------------------------------- #
if [ "$SKIP_PY" -eq 0 ]; then
  if ! command -v pipx >/dev/null 2>&1; then
    echo "!! pipx not found; skipping semgrep/ghauri (install pipx and re-run)" >&2
  else
    if ! command -v semgrep >/dev/null 2>&1; then
      echo "→ pipx install semgrep"
      run pipx install semgrep
    else
      echo "✓ semgrep already installed"
    fi
    if ! command -v ghauri >/dev/null 2>&1; then
      echo "→ pipx install ghauri (from git)"
      py="$(command -v python3.13 || command -v python3 || true)"
      if [ "$DRY" -eq 1 ]; then
        echo "[dry-run] pipx install --python $py git+https://github.com/r0oth3x49/ghauri"
      elif [ -n "$py" ]; then
        pipx install --python "$py" "git+https://github.com/r0oth3x49/ghauri" || \
          echo "!! ghauri install failed; sqlmap is still available" >&2
      fi
    else
      echo "✓ ghauri already installed"
    fi
  fi
fi

# --------------------------------------------------------------------------- #
# Optional: SecretFinder
# --------------------------------------------------------------------------- #
if [ ! -d "$HOME/tools/SecretFinder" ]; then
  echo "→ cloning SecretFinder"
  run git clone --depth 1 https://github.com/m4ll0k/SecretFinder "$HOME/tools/SecretFinder" || true
  if [ "$DRY" -eq 0 ] && command -v python3 >/dev/null 2>&1; then
    python3 -m pip install --user --break-system-packages jsbeautifier >/dev/null 2>&1 || true
  fi
else
  echo "✓ SecretFinder present"
fi

echo
echo "Done."
echo "If ~/go/bin or ~/.local/bin is not on PATH, add this to your shell rc:"
# shellcheck disable=SC2016  # print the literal line, do not expand it
echo '  export PATH="$HOME/go/bin:$HOME/.local/bin:$PATH"'
