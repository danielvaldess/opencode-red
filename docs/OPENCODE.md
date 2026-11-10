# OpenCode compatibility notes

This repository exists because skill bundles written for Claude Code need a few
changes to work *well* in OpenCode. These are the details that matter.

## Skills

OpenCode discovers skills in:

| Scope | Path |
|---|---|
| Global | `~/.config/opencode/skills` |
| Global compatibility | `~/.claude/skills`, `~/.agents/skills` |
| Project | `.opencode/skills`, `.claude/skills`, `.agents/skills` |

`opencode-red` installs into `~/.claude/skills` because that is the compatibility
path both harnesses read. You can override it with `--skills-dir`.

Rules that actually bite:

1. **The ID is the directory name**, not the frontmatter `name`. A file at
   `~/.claude/skills/hunt-idor/SKILL.md` has ID `hunt-idor`.
2. **A skill without a `description` is not advertised.** It can still be loaded
   by ID, but the model will not discover it. One upstream bundle ships 28 such
   skills; `install_skills.py` adds valid frontmatter.
3. **Nesting is allowed** up to six levels. `claude-red/web/offensive-sqli/SKILL.md`
   is valid and has ID `offensive-sqli`.
4. **A directory containing `SKILL.md` is one skill**; OpenCode does not search
   inside it for more skills.
5. **Duplicate IDs** are resolved by source precedence. Avoid them; this repo
   renames the one upstream collision (`offensive-osint` → `offensive-osint-red`).

Load a skill explicitly with `@skill-id`, or let the model choose it from the
description.

### Hiding a skill

To keep a skill on disk but out of the automatic list:

```yaml
---
name: offensive-something
description: ...
metadata:
  opencode/autoinvoke: false
---
```

It remains loadable with `@offensive-something`. Use this for large categories you
do not want in the prompt on every step (wireless, IoT, internal AD, exploit-dev…).

### How many skills is too many?

Every advertised skill adds its ID, name and description to the model context at
each step. This repo installs 163; on a 2.x OpenCode build that is roughly 30–40k
input tokens before your first message, mostly cached after the first step. If
that is expensive for you, hide the categories you do not use.

## Commands

OpenCode reads Markdown commands from:

```
~/.config/opencode/commands/*.md
.opencode/commands/**/*.md
```

The filename is the command name (`bb-recon.md` → `/bb-recon`). Frontmatter
supports `description`, `agent`, `model`, `subagent`. The body is the prompt.

`$ARGUMENTS` expands to the full argument string; `$1`, `$2` are positional.
Commands with no placeholder receive the arguments appended after a blank line.

The commands in this repo are adapted from Claude-BugHunter:

- `recon` is renamed `bb-recon` so it does not collide with a CTF `/recon`.
- YAML descriptions are quoted; upstream had `: ` inside unquoted scalars.
- Engine paths point at `~/.config/opencode/bughunter/engine/`.
- `/scope` tells the model to run the deterministic checker instead of reasoning
  about the scope file itself.
- `Claude Code` references are replaced with OpenCode equivalents.

### Shell blocks

OpenCode executes `` !`command` `` blocks in a command template **before** the
prompt is submitted and inserts the output. This repo avoids them for scope
because argument interpolation into a shell is a sharp edge; `/scope` instead
instructs the model to run one exact command. If you add shell blocks, never put
untrusted text inside them.

## Workspace context

OpenCode reads `AGENTS.md` from the project. `bbnew` writes one per engagement,
and the installer writes one at the workspace root. This is the equivalent of the
upstream `CLAUDE.md` scaffold.

## Engine dispatch

The upstream engine shells out to `claude -p`. `config/agent.opencode.py` replaces
that with:

```bash
opencode run --format json --auto "<task>"
```

Backend selection:

| Variable | Effect |
|---|---|
| `BUGHUNTER_AGENT` | `auto` (default), `claude` or `opencode` |
| `BUGHUNTER_OPENCODE_MODEL` | `provider/model` passed to `opencode run -m` |
| `BUGHUNTER_OPENCODE_AGENT` | optional `--agent` id |
| `BUGHUNTER_MEMORY_DIR` | ledger directory (default `~/.claude/bughunter/memory`) |

`auto` uses the Claude CLI if present, otherwise OpenCode. The engine parses the
JSON event stream from `opencode run --format json` and extracts the final
`json` verdict block the agent is asked to produce.

> `--auto` auto-approves tool permissions. Only use `/autopilot` against
> authorized targets, and review the engine's rules of engagement first.

## Tool-name mapping

Skills and commands written for Claude Code mention Claude tools. In OpenCode:

| Claude Code | OpenCode |
|---|---|
| `Bash` | `shell` |
| `Read` | `read` |
| `Grep` | `grep` |
| `Glob` | `glob` |
| `Write` / `Edit` | `write` / `edit` |
| `WebFetch` / `WebSearch` | `webfetch` / `websearch` |
| `Task` / `Agent` | `subagent` |
| `TodoWrite` | the agent's task list |

The workspace `AGENTS.md` states this so loaded skills can be followed without
guessing.

## Models and permissions

Model selection stays in your `opencode.jsonc`; the repo does not pin a model.
For the engine backend, either let OpenCode use its default model or set
`BUGHUNTER_OPENCODE_MODEL=provider/model`.

Permissions are also yours. If you want the interactive agent to ask before shell
commands, keep the default. `/autopilot` uses `--auto` because it is a batch loop.

## Optional MCP servers

The workflow does not require MCP, but two are useful:

- **`browse`** — your real browser, with your logged-in sessions. Best for
  authenticated SPA/OAuth flows and DOM XSS.
- **`browser`** — a headless Chromium for scripted page checks.

Add them to `~/.config/opencode/opencode.jsonc` using the examples in each MCP
server's documentation. The `osint` and `radare2` servers are useful for image
geolocation and binary/mobile work but are unrelated to the core workflow.

## Adding your own skill

```
~/.claude/skills/my-skill/SKILL.md
```

```yaml
---
name: my-skill
description: What it does and when to use it. This line is what the model sees.
---

Instructions go here. Relative paths resolve from the skill directory, so keep
scripts and references beside `SKILL.md`.
```

Then restart the TUI or wait for the next model step. If it does not appear,
check that the file is `SKILL.md`, that it has a description, and that the ID is
not shadowed by a higher-precedence source.
