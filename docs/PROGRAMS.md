# Choosing a program

There is no "best" program, only programs that match your current skill and the
time you can invest. This page is a decision framework, not a list of guaranteed
targets — programs, scopes and payout tables change constantly.

## Program types

| Type | What it is | Best for |
|---|---|---|
| **VDP** (vulnerability disclosure) | No bounty, but legal safe harbor and credit | First reports, learning the workflow |
| **Public bounty** | Open to everyone, scoped, paid | Building a track record |
| **Private / invite** | Invitation only, less competition | Better payouts once you have valid reports |
| **Open source** | Internet Bug Bounty, project-run programs | Code-level bugs, supply chain |
| **Web3** | Smart contracts, wallets, bridges | Solidity/Rust skills |

## Platforms

| Platform | Strengths | Watch out for |
|---|---|---|
| **Intigriti** | Less crowded, responsive triage, strong EU programs | Smaller catalogue |
| **Bugcrowd** | Managed triage, University, VRT taxonomy | Some programs are invite-only |
| **HackerOne** | Largest catalogue, Hacktivity for learning | Very high competition on famous programs |
| **YesWeHack** | Growing EU/Asia catalogue, less saturated | Smaller programme volume |
| **Open Bug Bounty** | No payout pressure, open disclosure | No money, reputation only |
| **Immunefi** | Web3 bounties | Requires smart-contract skills |
| **huntr** | AI/ML and open-source bounties | Niche scope |

Directories:

- <https://hackerone.com/directory/programs>
- <https://bugcrowd.com/programs>
- <https://app.intigriti.com/programs>
- <https://yeswehack.com/programs>
- <https://www.openbugbounty.org>
- <https://immunefi.com>
- <https://huntr.com>

## Selection criteria

Start with a program that has:

1. **A small, readable scope** — two or three applications, not `*.bigcorp.com`.
2. **Fast first response** — under a week; check the program's stats.
3. **Accepts low/medium** — even small payouts teach the workflow.
4. **Safe harbor** — explicit permission and disclosure rules.
5. **No ban on the techniques you need** — some forbid automated scanning, some
   exclude rate-limit findings, some require a specific test account.
6. **Recently active** — resolved reports in the last 90 days.

Avoid for your first program:

- household-name targets with thousands of researchers
- programs with a 6-month median response time
- programs whose scope is only "the whole internet" with no asset list
- programs that pay only for critical RCE on a marketing site

## Read the scope twice

Before touching anything, extract:

- **In scope:** exact hosts, wildcards, mobile apps, APIs, source repos, IP ranges.
- **Out of scope:** subsidiaries, staging, third-party services, specific bug
  classes (self-XSS, missing headers, rate limits on non-auth endpoints, etc.).
- **Rules:** test accounts, no DoS, no social engineering, data-retention limits,
  KYC, disclosure embargo.
- **Bounty table:** what the program actually pays; a P4 on one program can be a
  P2 on another.
- **Safe harbor:** the paragraph that makes your testing legal. If it is missing,
  ask before testing.

Write it into `scope.md`. The deterministic checker is only as good as that file.

## A realistic first month

**Week 1 — learn the format.**
Read 20 disclosed reports for the program or its technology. Complete a few
PortSwigger Academy labs and Hacker101. Write down how good reports frame impact.

**Week 2 — map one target.**
Pick one program with a small scope. Fill `scope.md`, run `/bb-recon`, read the
JS bundles, map authentication and the main object IDs. Do not test yet.

**Week 3 — one bug class.**
Choose a class that matches the surface (IDOR/BOLA, auth bypass, business logic,
XSS). Load the corresponding `hunt-*` skill and go deep. Depth beats breadth.

**Week 4 — validate and submit.**
Reproduce from a clean session, capture redacted evidence, run `/triage` and
`/validate`, write the report, submit. Then review the triage feedback.

## What gets rejected

Common reasons a report is closed as N/A or informative:

- no demonstrable impact ("an attacker could potentially…")
- the asset is out of scope or a third party
- intended behavior (e.g. a feature that is supposed to be public)
- scanner output with no manual confirmation
- missing reproduction steps or a PoC that only works with privileged access
- already-known issue / duplicate
- rate limiting, missing headers, self-XSS, clickjacking on a non-sensitive page
  when the program excludes them explicitly
- social engineering or physical access

Run `/triage` before writing. It is cheaper than an N/A.

## Private invitations

Private programs are earned, not applied for on most platforms. The path is:

1. Submit valid, well-written reports on public programs.
2. Keep your signal high; avoid speculative submissions.
3. Fill your profile with the classes you actually test.
4. Accept invitations to smaller private programs first.

A single confirmed medium with a clean report is worth more than ten rushed
low-severity submissions.

## Ethics and law

Bug bounty is legal **because** of the permission. Stay inside scope, respect the
rules, do not access other users' data beyond the minimum, do not disclose before
the program allows it. If something is ambiguous, ask the program before testing.
An out-of-scope request can be a crime even if the intention was good.

## Practice before you hunt

- PortSwigger Web Security Academy — <https://portswigger.net/web-security>
- Hacker101 and CTF — <https://hacker101.com>
- YesWeHack Dojo
- Bugcrowd University
- OWASP Juice Shop and DVWA locally

Practice targets let you make mistakes without burning reputation.
