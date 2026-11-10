#!/usr/bin/env bash
# verify.sh — check that the OpenCode Red arsenal is installed and usable.
set -uo pipefail

ok=0; fail=0; warn=0

check_bin() {
  local t="$1"
  if command -v "$t" >/dev/null 2>&1; then
    printf '  \033[32m✓\033[0m %-16s %s\n' "$t" "$(command -v "$t")"; ok=$((ok+1))
  else
    printf '  \033[31m✗\033[0m %-16s missing\n' "$t"; fail=$((fail+1))
  fi
}
check_opt() {
  local t="$1"
  if command -v "$t" >/dev/null 2>&1; then
    printf '  \033[32m✓\033[0m %-16s %s\n' "$t" "$(command -v "$t")"; ok=$((ok+1))
  else
    printf '  \033[33m–\033[0m %-16s optional\n' "$t"; warn=$((warn+1))
  fi
}
check() {
  local name="$1"; shift
  if "$@" >/dev/null 2>&1; then
    printf '  \033[32m✓\033[0m %s\n' "$name"; ok=$((ok+1))
  else
    printf '  \033[31m✗\033[0m %s\n' "$name"; fail=$((fail+1))
  fi
}

echo "== Core binaries =="
for t in git python3 jq curl; do check_bin "$t"; done

echo
echo "== Recon & hunting tools =="
for t in subfinder dnsx httpx katana gau waybackurls assetfinder anew gf chaos \
         nuclei ffuf feroxbuster gobuster nmap sqlmap dalfox; do check_opt "$t"; done

echo
echo "== Code & secret scanners =="
for t in semgrep trufflehog gitleaks; do check_opt "$t"; done

echo
echo "== Mobile / tooling (optional) =="
for t in jadx apktool jwt_tool ghauri; do check_opt "$t"; done

echo
echo "== Engine =="
check "scope.py self-test" python3 "$HOME/.config/opencode/bughunter/engine/scope.py" --selftest
check "agent.py self-test" python3 "$HOME/.config/opencode/bughunter/engine/agent.py"
check "cbh" cbh --help

echo
echo "== Skills & commands =="
python3 - <<'PY'
import collections, os, sys
try:
    import yaml
except Exception:
    yaml = None
roots = [os.path.expanduser("~/.claude/skills"),
         os.path.expanduser("~/.config/opencode/skills")]
ids = collections.Counter(); bad = []; total = 0
for root in roots:
    for dirpath, _, files in os.walk(root):
        if "SKILL.md" not in files:
            continue
        total += 1
        sid = os.path.basename(dirpath)
        ids[sid] += 1
        text = open(os.path.join(dirpath, "SKILL.md"), encoding="utf-8", errors="replace").read()
        if not text.startswith("---\n"):
            bad.append((sid, "no frontmatter")); continue
        end = text.find("\n---", 4)
        fm = None
        if yaml is not None:
            try:
                fm = yaml.safe_load(text[4:end])
            except Exception as exc:
                bad.append((sid, f"yaml: {exc}")); continue
        if isinstance(fm, dict) and not fm.get("description"):
            bad.append((sid, "no description"))
dups = [k for k, v in ids.items() if v > 1]
print(f"  skills: {total}  |  unique IDs: {len(ids)}")
print(f"  duplicate IDs: {dups or 'none'}")
print(f"  malformed: {bad or 'none'}")
cmd_dir = os.path.expanduser("~/.config/opencode/commands")
cmds = sorted(f[:-3] for f in os.listdir(cmd_dir) if f.endswith(".md")) if os.path.isdir(cmd_dir) else []
print(f"  commands: {len(cmds)} -> {', '.join(cmds) or 'none'}")
PY

echo
echo "== MCP (optional) =="
if command -v opencode >/dev/null 2>&1; then
  opencode mcp list 2>/dev/null || echo "  (could not query; run 'opencode mcp list')"
else
  echo "  opencode not on PATH"
fi

echo
echo "Result: $ok ok, $warn optional/missing, $fail failed."
[ "$fail" -eq 0 ]
