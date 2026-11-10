# Notice and attribution

`opencode-red` is an installer and orchestration layer. It does **not** vendor the
upstream skill texts; `install.sh` fetches them at install time. The following
projects are used under the MIT license:

## Claude-BugHunter

- Repository: <https://github.com/elementalsouls/Claude-BugHunter>
- Author: Sachin Sharma
- License: MIT — see [`licenses/Claude-BugHunter-MIT.txt`](licenses/Claude-BugHunter-MIT.txt)
- Used for: the 83-skill bug-bounty bundle, the 15 slash commands, the
  engagement engine and the `cbh` CLI.

Files in this repository derived from Claude-BugHunter:

- `commands/*.md` — adapted for OpenCode (filename-based command names, quoted
  YAML descriptions, engine paths, `/recon` → `/bb-recon`, `/scope` deterministic
  execution, Claude Code references replaced).
- `config/agent.opencode.py` — based on `engine/agent.py`; adds an OpenCode
  backend (`opencode run --format json --auto`) and keeps the original interface.
- `scripts/install_skills.py` — installs the upstream engine and applies the
  `osint.py` httpx detection patch and CLI wording patch.

## claude-red

- Repository: <https://github.com/SnailSploit/claude-red>
- Author: SnailSploit
- License: MIT — see [`licenses/claude-red-MIT.txt`](licenses/claude-red-MIT.txt)
- Used for: the 79-skill red-team library.

Compatibility changes applied at install time (not redistributed here):

- YAML frontmatter is added to skills that ship without it.
- The `offensive-osint` skill is installed as `offensive-osint-red` to avoid an
  ID collision with Claude-BugHunter.

## security-review

- Repository: <https://github.com/cdmx-in/security-review>
- Author: Codemax IT Solutions Pvt. Ltd.
- License: MIT — see [`licenses/security-review-MIT.txt`](licenses/security-review-MIT.txt)
- Used for: the `security-audit` skill.

## Original work

The following are original to this repository and MIT-licensed under
[`LICENSE`](LICENSE):

- `install.sh`, `scripts/install_skills.py`, `scripts/install_tools.sh`,
  `scripts/new-engagement.sh`, `scripts/verify.sh`, `scripts/generate_arsenal.py`
- `templates/*`
- `docs/*`
- the README, CI configuration and repository structure

## Trademarks

Product names, logos and trademarks are the property of their respective owners.
Reference to a tool or project does not imply endorsement.
