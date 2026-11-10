# Contributing

Thanks for considering a contribution. This project is a compatibility layer and
an installer, so the most valuable contributions are small, testable and honest
about provenance.

## Before you start

- Read `README.md`, `docs/ARCHITECTURE.md` and `NOTICE.md`.
- This project is for **authorized** security testing. Do not contribute
  payloads or techniques aimed at systems you do not own or have permission to
  test.
- Do not include real targets, customer data, credentials, tokens or private
  program details.

## Development setup

```bash
git clone https://github.com/danielvaldess/opencode-red.git
cd opencode-red
./install.sh --dry-run
./install.sh
./scripts/verify.sh
```

Useful targets:

```bash
make lint       # shellcheck + python compile
make verify     # environment health check
make catalog    # regenerate docs/ARSENAL.md
```

## What to contribute

| Area | Examples |
|---|---|
| Compatibility | A new OpenCode change that breaks skill/command discovery |
| Installer | Better idempotency, new package managers, macOS fixes |
| Commands | A command that fills a real gap in the workflow |
| Documentation | Clearer workflow, program selection, troubleshooting |
| Templates | Better finding/report/scope templates |
| Toolchain | New tool with a reproducible install path |

Please **do not** open PRs that:

- vendor large third-party skill texts (the installer fetches them);
- remove attribution or relicense upstream work;
- add a dependency that requires an account or a paid license;
- add offensive automation that runs without a scope check.

## Adding a skill

User skills do not need a repo change: put them in
`~/.claude/skills/<id>/SKILL.md`. If you want to ship one in this repo:

1. Add it under `skills/<id>/SKILL.md` (create the folder if needed).
2. Include YAML frontmatter with `name` and `description`.
3. Keep supporting files beside `SKILL.md`.
4. Add an install step in `scripts/install_skills.py`.
5. Regenerate the catalogue.

## Adding a command

1. Add `commands/<name>.md`.
2. Use valid YAML frontmatter with a quoted `description`.
3. Use `$ARGUMENTS` or `$1` for arguments.
4. Avoid shell blocks with untrusted interpolation.
5. Test it in OpenCode and mention the manual test in the PR.

## Style

- Shell: `set -euo pipefail`, quote variables, no GNU-only flags where possible.
- Python: 3.9+, standard library first, no network calls at import time.
- Markdown: one sentence per line is fine; keep tables readable.
- Commits: imperative mood, one logical change per commit.

## Pull request checklist

- [ ] `bash -n` passes for every shell script.
- [ ] `python3 -m py_compile scripts/*.py config/*.py` passes.
- [ ] `./scripts/verify.sh` passes on your machine.
- [ ] `./install.sh --dry-run` works without network access.
- [ ] New commands have valid frontmatter and a description.
- [ ] `docs/ARSENAL.md` is regenerated if skills changed.
- [ ] Attribution and licenses are intact.
- [ ] No secrets, real targets or personal data.

## License

By contributing you agree that your contribution is licensed under the MIT
license of this repository. Upstream-derived work keeps its original license and
attribution.
