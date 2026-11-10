---
description: "Run autonomous hunt loop on a target — scope check → recon → rank surface → hunt → validate → report with configurable checkpoints. Usage: /autopilot target.com [--paranoid|--normal|--yolo]"
---

> **OpenCode adaptation:** where the flow says `question:` / `header:` / `options:`, call the `question` tool with that prompt and options; where it says "invoke `<skill>`", use the `skill` tool with the ID; `Bash` means `shell`. You cannot run slash commands (`/scope`, `/chain`, …) from inside a prompt — execute their logic yourself. For scope run `python3 "$HOME/.config/opencode/bughunter/engine/scope.py" <asset> --md ./scope.md`; the rest are described in `~/.config/opencode/commands/`.


# /autopilot

Autonomous hunt loop with deterministic scope safety and configurable checkpoints.

## Usage

```
/autopilot target.com                    # default: --paranoid mode
/autopilot target.com --normal           # batch checkpoint after validation
/autopilot target.com --yolo             # minimal checkpoints (still requires report approval)
/autopilot target.com --quick            # fast surface scan, fewer checks, lower token use
/autopilot targets.txt                   # multiple targets — one domain per line in the file
```

## Session Isolation (Important)

**Start a fresh OpenCode session per target.** OpenCode acumula context across a session —
testing multiple targets in one session causes cross-contamination where findings, payloads,
and tech stack assumptions from target A bleed into target B.

Best practice:
```bash
# Terminal 1: target A
opencode  →  /autopilot targetA.com

# Terminal 2: target B (separate process)
opencode  →  /autopilot targetB.com
```

If you must test multiple targets in one session, run `/pickup target.com` at the start of
each target switch to reload the correct context.

## Token Optimization

Use `--quick` for faster, lower-cost scans (skips deep fuzzing and extended nuclei templates):
```
/autopilot target.com --quick    # ~40% fewer tokens, covers main attack surface
/hunt target.com --vuln-class idor   # single bug class — lowest token use
```

For long hunts, start a fresh thread when the context grows; save findings in `notes.md` before restarting.

## What This Does

Runs the full hunt cycle without stopping for approval at each step:

```
1. SCOPE     Load and confirm program scope
2. RECON     Run recon (or use cached if < 7 days old)
3. RANK      Prioritize attack surface (/surface o `cbh surface`)
4. HUNT      Test P1 endpoints systematically
5. VALIDATE  7-Question Gate on findings
6. REPORT    Draft reports for validated findings
7. CHECKPOINT  Present to human for review
```

## Safety Guarantees

- **Every URL** is checked against the scope allowlist before any request
- **Reports are NEVER auto-submitted** — always requires explicit approval
- **PUT/DELETE/PATCH** require human approval in --yolo mode (safe methods only)
- **Circuit breaker** stops hammering if 5 consecutive 403/429/timeout on same host
- **Rate limited** at 1 req/sec (testing) and 10 req/sec (recon)

## Checkpoint Modes

| Mode | When it stops | Best for |
|---|---|---|
| `--paranoid` | Every finding + partial signal | New targets, learning the surface |
| `--normal` | After validation batch | Systematic coverage |
| `--yolo` | After full surface exhausted | Familiar targets, experienced hunters |

## Ledger memory (token saving)

The autonomous loop can consult the **autopilot ledger** to skip provably-wasteful agent
calls — an item already **confirmed** on a prior run (carried forward, not re-tested) or a
vuln_class with strong **negative** history on this tech stack (`dead-class`).

- **`--paranoid` (default) / `--normal`:** memory is **off** — full coverage, no skips.
- **`--quick` / `--yolo`:** the command passes `--use-memory` to the engine — skips on.
- A vuln_class never hunted on this stack is **never** skipped, and every skip is logged
  (`hunt: skipped via ledger (...)`). Coverage is never silently reduced.
- Capture is automatic; the ledger fills itself as you run. Manage size with `/memory-gc`.

## After Autopilot

- Run `/remember` to log successful patterns to hunt memory
- Run `/pickup target.com` next time to pick up where you left off
- Check the ledger (`~/.claude/bughunter/memory/findings.jsonl`) or run `/memory-gc` for its size
