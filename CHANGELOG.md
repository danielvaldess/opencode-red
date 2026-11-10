# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [0.1.0] — 2026-11-10

### Added

- One-command installer for OpenCode 2.x: skills, commands, engine and workspace.
- 163 skills: 84 bug-bounty core (Claude-BugHunter + security-review) and 79
  red-team skills (claude-red).
- 15 OpenCode slash commands, including `/hunt`, `/bb-recon`, `/scope`,
  `/triage`, `/validate`, `/report`, `/chain` and `/autopilot`.
- Deterministic scope checker (`engine/scope.py`) with deny-wins, default-deny
  semantics and `/scope` integration.
- `bbnew` engagement scaffolder with `scope.md`, `AGENTS.md`, findings, evidence
  and a submissions tracker.
- OpenCode dispatch overlay for the upstream engine
  (`opencode run --format json --auto`).
- Optional toolchain bootstrap: subfinder, dnsx, httpx (ProjectDiscovery),
  katana, gau, waybackurls, assetfinder, chaos, anew, gf, dalfox, gitleaks,
  trufflehog, semgrep, ghauri and SecretFinder.
- Generated skill catalogue (`docs/ARSENAL.md`).
- Terminal demo and a real, repeatable example (`examples/demo.sh`).
- Documentation: workflow, OpenCode compatibility, tools, program selection,
  troubleshooting, architecture and a task-oriented cheat sheet.
- CI: ShellCheck, Python compilation, command-frontmatter validation and an
  installer dry-run.
- MIT license and upstream attribution.
