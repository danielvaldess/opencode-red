# Troubleshooting

## A skill does not appear

1. The file must be `~/.claude/skills/<id>/SKILL.md` (or a nested path no deeper
   than six levels).
2. It must have YAML frontmatter with a `description`. Skills without one are not
   advertised.
3. The ID is the **directory name**. `@hunt-idor` loads
   `~/.claude/skills/hunt-idor/SKILL.md`, regardless of the frontmatter `name`.
4. It may be hidden by `metadata.opencode/autoinvoke: false`.
5. A higher-precedence source may define the same ID. Check
   `~/.config/opencode/skills` and the project `.opencode/skills`.

Diagnose:

```bash
find ~/.claude/skills -name SKILL.md | sed 's|/SKILL.md||' | sort | head
python3 - <<'PY'
import os, yaml
root = os.path.expanduser("~/.claude/skills")
for d in os.listdir(root):
    p = os.path.join(root, d, "SKILL.md")
    if os.path.isfile(p):
        t = open(p).read()
        if not t.startswith("---"):
            print("no frontmatter:", d)
PY
```

After install, OpenCode picks new skills up on the next model step; if the TUI
looks stale, restart it.

## A command does not appear

- Commands live in `~/.config/opencode/commands/*.md` or project
  `.opencode/commands/`.
- The filename is the command name: `bb-recon.md` → `/bb-recon`.
- The frontmatter must be valid YAML. A `description` containing `: ` must be
  quoted:

  ```yaml
  description: "Recon: subdomains, hosts, URLs"
  ```

- Commands reload automatically when the file changes; restart the TUI if not.

## `/scope` says everything is out of scope

That is the safe default: an empty in-scope list denies everything. Fill
`scope.md` from the program page first. Check the semantics:

- `acme.com` covers the apex **and subdomains**.
- `*.acme.com` covers subdomains but **not** `acme.com`.
- `re:...` is a regex; escape dots.
- If an asset matches both in and out, out wins.

Run the checker directly to see the reason:

```bash
python3 "$HOME/.config/opencode/bughunter/engine/scope.py" api.acme.com --md ./scope.md
```

## `httpx` fails with a Python dependency error

The Python `httpx` CLI is shadowing the ProjectDiscovery scanner. Check:

```bash
httpx -version | grep -i projectdiscovery
```

Fix:

```bash
mv ~/.local/bin/httpx ~/.local/bin/httpx-python.bak
ln -sf ~/go/bin/httpx ~/.local/bin/httpx
```

Or put `~/go/bin` before `~/.local/bin` in `PATH`.

## `cbh: command not found`

The installer writes `~/.local/bin/cbh`. Ensure that directory is on `PATH`:

```bash
export PATH="$HOME/.local/bin:$HOME/go/bin:$PATH"
cbh --help
```

If the engine was installed elsewhere, edit the wrapper or pass
`--engine-dir` when reinstalling.

## The engine cannot find its files

The default layout is:

```
~/.config/opencode/bughunter/engine/
~/.config/opencode/bughunter/cbh/
```

Commands call `$HOME/.config/opencode/bughunter/engine/...`. If you used a custom
`--engine-dir`, update the commands or reinstall with the default path.

Self-tests:

```bash
python3 ~/.config/opencode/bughunter/engine/scope.py --selftest
python3 ~/.config/opencode/bughunter/engine/agent.py
```

## `/autopilot` fails or hangs

- It uses `opencode run --format json --auto`. Test it manually:

  ```bash
  opencode run --format json --auto "Reply with OK"
  ```

- If the Claude CLI is installed and you want OpenCode anyway, set
  `BUGHUNTER_AGENT=opencode`.
- If the engine cannot find a model, set
  `BUGHUNTER_OPENCODE_MODEL=provider/model`.
- `--auto` auto-approves tools. Do not run it on an unauthorized target.

## Install fails cloning upstream

The first install clones three GitHub repositories into
`~/.local/share/opencode-red/upstream`. If you are behind a proxy or offline:

```bash
OPENCODE_RED_UPSTREAM=/path/to/upstream ./install.sh
```

The directory must contain `Claude-BugHunter/`, `claude-red/` and
`security-review/`.

## Duplicate skill IDs

Only one skill per ID is loaded. Rename the directory of the one you do not want,
or remove it. This repo already renames the one upstream collision
(`offensive-osint` → `offensive-osint-red`).

## macOS notes

- The scripts target bash 3.2+ and POSIX tools; GNU-specific flags are avoided
  where possible.
- `ghead`/`gsed` are not required.
- If `pipx` is not installed: `brew install pipx && pipx ensurepath`.

## WSL notes

- Install OpenCode, Go and pipx inside WSL, not on the Windows side, so the
  binaries and `PATH` are consistent.
- Windows browsers are reachable but a Linux Chromium is simpler for headless
  MCP servers.

## Everything is installed but the model ignores the skill

- Load it explicitly with `@skill-id`.
- Skills are instructions, not tools: the model still has to follow them.
- If the prompt is huge, the model may pick a competing skill. For web bounty,
  prefer `hunt-*` over the overlapping `offensive-*` skill.
- Hiding unused categories reduces noise and cost.

## Reset

The installer backs up replaced files under
`~/.local/share/opencode-red/backups/<timestamp>/`. To start clean:

```bash
rm -rf ~/.claude/skills/claude-red ~/.claude/skills/security-audit
rm -rf ~/.config/opencode/bughunter
./install.sh
```

Do not delete skills you added yourself without checking them first.
