#!/usr/bin/env bash
# new-engagement.sh — scaffold a per-program bug-bounty workspace.
#
# Usage:
#   bbnew <slug> [base]
#   OPENCODE_RED_WORKSPACE=~/bounties bbnew acme
#
# Creates ~/bounties/<slug>/ with AGENTS.md, scope.md, notes.md, a submissions
# tracker, findings/, evidence/ (gitignored) and recon/.
set -euo pipefail

slug="${1:-}"
base="${2:-${OPENCODE_RED_WORKSPACE:-${BB_BASE:-$HOME/bounties}}}"

if [ -z "$slug" ]; then
  echo "Usage: $0 <slug> [base]" >&2
  echo "Example: $0 acme" >&2
  exit 2
fi
if ! [[ "$slug" =~ ^[a-z0-9][a-z0-9._-]*$ ]]; then
  echo "Invalid slug: '$slug' (use lowercase letters, digits, dot, dash)." >&2
  exit 2
fi

dir="$base/$slug"
if [ -d "$dir" ]; then
  echo "Already exists: $dir"
  echo "cd $dir"
  exit 0
fi

mkdir -p "$dir"/{findings,evidence,recon}

# ---------------------------------------------------------------- AGENTS.md
cat > "$dir/AGENTS.md" <<EOF
# Engagement: $slug

> Workspace rules: \`../../AGENTS.md\`.
> **Read \`scope.md\` before sending any request.**

- **Platform:** [HackerOne / Bugcrowd / Intigriti / YesWeHack / private]
- **Program URL:** [paste]
- **Started:** $(date -u +%Y-%m-%d)
- **Phase:** recon

## Scope rule

Only assets listed as **in scope** in \`scope.md\` may be tested.
If a host or action is not explicitly permitted, stop and document it — never widen the scope.
Before each active phase run: \`/scope <asset>\`.

## Workflow

1. **Scope** — fill \`scope.md\` from the program page (in/out of scope, rules, bands).
2. **Recon** — \`/bb-recon <target>\` (or \`cbh recon <target>\`).
3. **Surface** — \`/surface <target>\`; prioritize P1/P2.
4. **Hunt** — \`/hunt <target>\`, or \`@hunt-<class>\` for one bug class.
5. **Validate** — \`/triage\`, then \`/validate\`. No reproducible PoC, no report.
6. **Evidence** — load \`@evidence-hygiene\` before any screenshot/HAR; redact cookies/PII.
7. **Report** — \`/report\` (plus \`@bugcrowd-reporting\` on Bugcrowd).

## Files

- \`findings/finding-NN-<name>.md\` — one finding per file.
- \`evidence/\` — screenshots, HARs, raw responses (never share unredacted).
- \`notes.md\` — leads, hypotheses, dead ends.
- \`submissions.txt\` — submission IDs, used to cross-reference chains.

## Prohibited

- No DoS, mass brute force, spam or social engineering unless the program explicitly allows it.
- Do not access other users' data beyond the minimum needed to demonstrate the flaw.
- No public disclosure without program approval.
- Do not test production if the program requires QA/staging.
EOF

# ---------------------------------------------------------------- scope.md
cat > "$dir/scope.md" <<'EOF'
# Scope — <target>

> Fill this from the program page BEFORE any active testing.
> `/scope <asset>` checks an asset against this file (deny-wins, default-deny).
> Semantics: `acme.com` covers the apex and all subdomains; `*.acme.io` does NOT
> cover the apex; `10.0.0.0/8` is a CIDR; `re:...` is a regex. If an asset matches
> both an in-scope and an out-of-scope rule, out-of-scope wins.

## In scope

- (paste the in-scope asset list)

## Out of scope

- (paste OOS, including excluded bug classes)

## Focus areas / accepted impact

- (what the program values most — this is where the money is)

## Bounty bands

| Severity | Range |
|---|---|
| P1 / Critical | |
| P2 / High | |
| P3 / Medium | |
| P4 / Low | |
| P5 / Info | (usually unpaid) |

## Rules / safe harbor

- (test accounts, rate limits, no-DoS, KYC, contact email)

## Test accounts

- **Email:** (`alias@bugcrowdninja.com` on Bugcrowd)
- **UID:**
- **Production vs QA:**
- **Mobile builds (APK/IPA):**
- **Auth / SSO / MFA:**

## OOS clauses to pre-empt

- (e.g. "rate limiting on non-authentication endpoints")
- (e.g. "user enumeration with low-risk information")
EOF

# ---------------------------------------------------------------- notes.md
cat > "$dir/notes.md" <<'EOF'
# Notes — <target>

## Leads

- [ ]

## Hypotheses

-

## Ruled out (and why)

-
EOF

# ---------------------------------------------------------------- submissions.txt
cat > "$dir/submissions.txt" <<'EOF'
# Submissions — <target>
# Format (tabs): <UUID>	<severity>	<VRT/class>	<one-line title>
EOF

# ---------------------------------------------------------------- findings/README.md
cat > "$dir/findings/README.md" <<'EOF'
# Findings — <target>

One file per lead: `finding-NN-<name>.md`.

Each file should contain:
1. Status (lead / validated / drafted / submitted / triaged / paid / closed)
2. Summary + 7-Question Gate
3. Reproduction steps with exact requests/responses
4. Evidence inventory (redacted paths under `../evidence/`)
5. Severity + justification (CVSS 3.1 / VRT)
6. Submission UUID
7. Triager dialogue
EOF

# ---------------------------------------------------------------- evidence/.gitignore
cat > "$dir/evidence/.gitignore" <<'EOF'
*
!.gitignore
!.gitkeep
EOF
touch "$dir/evidence/.gitkeep"

# ---------------------------------------------------------------- .gitignore
cat > "$dir/.gitignore" <<'EOF'
# Evidence is never committed unredacted
evidence/*
!evidence/.gitignore
!evidence/.gitkeep
recon/*
!recon/.gitkeep
*.har
*.pcap
.env
EOF
touch "$dir/recon/.gitkeep"

echo "Created: $dir"
echo
echo "Next:"
echo "  1) cd $dir"
echo "  2) fill scope.md from the program page"
echo "  3) open OpenCode there and run /hunt <target>"
