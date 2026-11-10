# Workspace rules — OpenCode Red

This workspace is for **authorized** security testing only. Every engagement must
have a program policy, signed scope, or explicit written permission.

## The one rule

Test only assets that are **explicitly in scope** for the engagement. If an asset,
bug class or technique is not clearly permitted, stop and document it — do not widen
the scope. Bug bounty is legal because of the permission, not despite it.

## Layout

```
<workspace>/
├── AGENTS.md                 # this file
└── <engagement>/
    ├── AGENTS.md             # engagement-specific context
    ├── scope.md              # in/out of scope — the source of truth
    ├── notes.md              # leads, hypotheses, dead ends
    ├── submissions.txt       # submission IDs
    ├── findings/             # one markdown file per finding
    ├── evidence/             # screenshots/HARs (gitignored)
    └── recon/                # recon output
```

Create one with:

```bash
bbnew <program>
cd <program>
```

## Workflow

1. **Scope** — fill `scope.md` from the program page before any request.
2. **Recon** — `/bb-recon <target>` or `cbh recon <target>`.
3. **Surface** — `/surface <target>`; work P1/P2 first.
4. **Hunt** — `/hunt <target>`, or `@hunt-<class>` for one vulnerability class.
5. **Validate** — `/triage`, then `/validate`. No reproducible PoC, no report.
6. **Evidence** — load `@evidence-hygiene` before capturing anything.
7. **Report** — `/report`; on Bugcrowd also load `@bugcrowd-reporting`.

## Before each active phase

```bash
python3 "$HOME/.config/opencode/bughunter/engine/scope.py" <asset> --md ./scope.md
```

or simply:

```
/scope <asset>
```

Scope semantics (deny-wins, default-deny):

| Pattern | Matches |
|---|---|
| `acme.com` | apex **and any subdomain** |
| `*.acme.com` | subdomains, **not** the bare apex |
| `10.0.0.0/8` | any IP in the CIDR |
| `re:^lab[0-9]+\.acme\.io$` | explicit regex |

An empty in-scope list denies everything. If an asset matches both lists, out wins.

## Commands

| Command | Purpose |
|---|---|
| `/hunt <target>` | Main dispatcher: red team vs WAPT/bug bounty |
| `/bb-recon <target>` | Subdomains, live hosts, crawl, params, nuclei |
| `/scope <asset>` | Deterministic scope check |
| `/surface <target>` | Ranked attack surface |
| `/triage` | Quick 7-Question Gate |
| `/validate` | Full validation gates |
| `/report` | Submission-ready draft |
| `/chain` | Build an A→B→C exploit chain |
| `/intel <target>` | CVEs, disclosed reports, target memory |
| `/pickup <target>` | Resume from the ledger |
| `/remember` | Manual note in the ledger |
| `/memory-gc` | Rotate/clean the ledger |
| `/autopilot <target>` | Autonomous loop with checkpoints |
| `/token-scan <dir>` | Token/contract rug-pull audit |
| `/web3-audit <file>` | Smart-contract audit |

## Tool-name mapping

Skills were written for Claude Code. In OpenCode:

`Bash` → `shell` · `Read` → `read` · `Grep` → `grep` · `Glob` → `glob` ·
`Write`/`Edit` → `write`/`edit` · `WebFetch`/`WebSearch` → `webfetch`/`websearch` ·
`Task`/`Agent` → `subagent` · `TodoWrite` → the agent's task list.

## Evidence hygiene

- Capture only after confirming the finding.
- Redact `Cookie`, `Authorization` and `Set-Cookie` before sharing.
- Redact third-party PII (names, emails, phones, IDs).
- Sanitize HARs before attaching them.
- Keep raw evidence in `evidence/` (gitignored); reference redacted paths in findings.
- Rotate test credentials when the engagement ends.

## Prohibited

- No DoS, mass brute force, spam or social engineering unless explicitly allowed.
- No access to other users' data beyond the minimum needed to demonstrate the flaw.
- No public disclosure without program approval.
- No testing production when the program requires QA/staging.

## Maintenance

```bash
python3 ~/path/to/opencode-red/scripts/generate_arsenal.py   # refresh catalogue
~/path/to/opencode-red/scripts/verify.sh                     # health check
```

Skills live in `~/.claude/skills`; OpenCode discovers them recursively. The skill
ID is the directory name (not the frontmatter `name`). Load one with `@<id>`.
