# Workflow

A repeatable loop for a bug-bounty program. It is deliberately boring: the
creative work happens inside each phase, not in inventing a new process.

```
scope → recon → surface → hunt → validate → evidence → report → track
```

## 0. Prepare

```bash
bbnew acme
cd ~/bounties/acme
```

Open OpenCode in that directory. It loads the workspace `AGENTS.md` and the
engagement `AGENTS.md`; the engagement is the unit of context. Do not mix two
programs in one session.

## 1. Scope

Fill `scope.md` from the program page **before any request**:

- in-scope assets (exact hosts, wildcards, CIDRs, mobile apps, APIs)
- out-of-scope assets and excluded bug classes
- rules: test accounts, rate limits, no-DoS, no social engineering, KYC
- bounty bands and accepted impact

Then verify an asset:

```
/scope api.acme.com
```

The checker is deterministic. If it says `OUT-OF-SCOPE`, stop. An empty in-scope
list denies everything by design.

## 2. Recon

```
/bb-recon acme.com
```

This stage is breadth, not depth:

- subdomains (Chaos, subfinder, assetfinder, certificate transparency)
- live hosts and tech fingerprint (dnsx + httpx)
- URLs (katana + waybackurls + gau)
- parameters, JS bundles, source maps, secrets
- `gf` classification into candidate buckets
- `nuclei` for known CVEs and misconfigurations

Keep the raw output in `recon/`. Do not start testing from a list you have not
read; rank first.

## 3. Surface

```
/surface acme.com
```

Prioritize:

| Signal | Why it matters |
|---|---|
| Authentication and session flows | ATO chains, reset poisoning, MFA gaps |
| Object IDs and API routes | IDOR / BOLA — the most reliable bounty class |
| File upload, import, export | RCE, XXE, stored XSS, path traversal |
| Redirects and URL fetchers | SSRF, open redirect → OAuth theft |
| GraphQL / undocumented APIs | Broken object-level authorization |
| Admin or internal-looking hosts | Access-control mistakes |
| Recent features / changelogs | New code, less tested |

Work P1/P2 first. Ignore a P5 surface until the high-value paths are exhausted.

## 4. Hunt

```
/hunt acme.com
```

The dispatcher asks **Red Team** vs **WAPT / Bug Bounty**, then loads the right
skills. For a single class:

```
/hunt acme.com --vuln-class idor
```

or load a skill directly:

```
@hunt-idor
@hunt-ssrf
@hunt-ato
```

Rules:

- One hypothesis at a time; write it in `notes.md`.
- Test with two accounts (A and B) whenever authorization is involved.
- Use the browser MCP (`browse`) for real authenticated flows.
- Stop and rotate after ~20 minutes without progress.
- Never leave the scope to "just check" a related host.

## 5. Validate

```
/triage
```

Quick go/no-go. If it passes:

```
/validate
```

The gates reject:

- findings you cannot reproduce from a clean session
- theoretical impact, scanner output, or "could potentially"
- behavior that is intended by design
- issues on out-of-scope assets
- duplicates of public reports

If validation fails, write why in `notes.md` and move on. A killed finding is a
good outcome; an N/A submission costs reputation.

## 6. Evidence

Load `@evidence-hygiene` **before** taking screenshots.

- Redact `Cookie`, `Authorization`, `Set-Cookie`.
- Redact third-party PII (names, emails, phones, IDs).
- Sanitize HARs; never attach the raw file.
- Capture the two-account proof, not just the response.
- Store raw files in `evidence/`, reference redacted paths in the finding.

## 7. Report

```
/report
```

A report is: title with impact, summary, exact reproduction, proof, impact,
remediation. Keep it short enough for a busy engineer.

On Bugcrowd also load `@bugcrowd-reporting` for VRT mapping, severity requests
and OOS rebuttals. On HackerOne, check the program's severity taxonomy.

Record the submission ID in `submissions.txt` so chains can cross-reference.

## 8. Track and learn

At the end of a session:

```
/remember
/pickup acme.com
```

`/remember` writes to the engagement ledger; `/pickup` shows what was tested and
what is still untested. `/memory-gc` rotates the ledger when it grows.

After the engagement, add one line to your own notes: what worked, what was a
dead end, which skill you would load first next time.

## Timebox

| Phase | Typical budget |
|---|---|
| Scope + rules | 20–30 min |
| Recon | 1–2 h |
| Surface ranking | 30 min |
| Hunting | 2–4 h per session |
| Validation | 30–60 min per finding |
| Report | 30–45 min |

Rotate when a path is flat: 20 minutes without a new signal is enough.

## Artifacts

| File | Owner |
|---|---|
| `scope.md` | you, before testing |
| `notes.md` | running log |
| `findings/finding-NN-*.md` | one per lead |
| `evidence/` | screenshots, HARs (gitignored) |
| `submissions.txt` | submission IDs |

## Anti-patterns

- Running every scanner before reading the program rules.
- Testing a wildcard because it resolves, without checking it is in scope.
- Reporting a header or a stack trace with no demonstrated impact.
- Writing the report before reproducing the bug from a fresh session.
- Mixing two targets in one session and leaking context between them.
