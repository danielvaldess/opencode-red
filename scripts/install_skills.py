#!/usr/bin/env python3
"""
install_skills.py — install the OpenCode Red arsenal from upstream bundles.

What it does
------------
1. Copies the 83 Claude-BugHunter skills into ~/.claude/skills/.
2. Copies the 79 claude-red skills into ~/.claude/skills/claude-red/<category>/.
   - Adds YAML frontmatter to skills that ship without it (OpenCode will not
     advertise a skill without a description).
   - Renames the one ID collision with Claude-BugHunter:
     offensive-osint -> offensive-osint-red.
3. Copies the security-review `security-audit` skill.
4. Installs the deterministic engine + `cbh` CLI under
   ~/.config/opencode/bughunter/ and patches it for OpenCode.
5. Writes a `cbh` wrapper into ~/.local/bin (or --bin-dir).

The script is idempotent and backs up anything it replaces to
$XDG_DATA_HOME/opencode-red/backups/<timestamp>/.

Usage
-----
    python3 install_skills.py \
      --bughunter  /path/to/Claude-BugHunter \
      --claude-red /path/to/claude-red \
      --security-review /path/to/security-review

Everything is configurable; see --help.
"""
from __future__ import annotations

import argparse
import filecmp
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

RENAME_COLLISION = {"offensive-osint": "offensive-osint-red"}
CLAUDE_RED_ROOT = "claude-red"
REQUIRED_SKILL = "SKILL.md"


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def split_frontmatter(text: str) -> tuple[str | None, str]:
    """Return (frontmatter, body) or (None, text)."""
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            after = end + 4
            if after < len(text) and text[after] == "\n":
                after += 1
            return text[4:end], text[after:]
    return None, text


def description_from_body(body: str) -> str:
    """Extract a description from the legacy claude-red body format."""
    m = re.search(r"^##\s+Description\s*$(.*?)(?=^##\s|\Z)", body, re.M | re.S)
    raw = m.group(1) if m else ""
    if not raw.strip():
        for block in re.split(r"\n\s*\n", body):
            b = block.strip()
            if b and not b.startswith(("#", "- **", "```")):
                raw = b
                break
    raw = re.sub(r"\s+", " ", raw).strip().replace("`", "")
    return raw[:600].rstrip()


def ensure_frontmatter(path: Path, skill_id: str) -> str:
    """Guarantee name+description frontmatter. Returns added|fixed|ok."""
    text = path.read_text(encoding="utf-8", errors="replace")
    fm, body = split_frontmatter(text)
    if fm is None:
        desc = description_from_body(body) or f"{skill_id} offensive-security skill."
        path.write_text(
            f"---\nname: {skill_id}\ndescription: >-\n  {desc}\n---\n\n{body}",
            encoding="utf-8",
        )
        return "added"
    if not re.search(r"^description:\s*\S", fm, re.M):
        desc = description_from_body(body) or f"{skill_id} offensive-security skill."
        path.write_text(
            f"---\n{fm.rstrip()}\ndescription: >-\n  {desc}\n---\n\n{body}",
            encoding="utf-8",
        )
        return "fixed"
    return "ok"


def dirs_equal(a: Path, b: Path) -> bool:
    """True when two directory trees are byte-identical (content, not mtime)."""
    if not a.is_dir() or not b.is_dir():
        return False
    cmp = filecmp.dircmp(a, b)
    if cmp.left_only or cmp.right_only:
        return False
    for name in cmp.common_files:
        if not filecmp.cmp(a / name, b / name, shallow=False):
            return False
    for name in cmp.common_dirs:
        if not dirs_equal(a / name, b / name):
            return False
    return True


class Installer:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        self.backup_root = Path(
            os.environ.get(
                "XDG_DATA_HOME", Path.home() / ".local/share"
            )
        ) / "opencode-red" / "backups" / self.stamp
        self.stats = {
            "bughunter": 0,
            "claude_red": 0,
            "security_audit": 0,
            "frontmatter_added": 0,
            "renamed": 0,
            "commands": 0,
        }

    # -- filesystem ---------------------------------------------------------
    def backup(self, path: Path) -> None:
        if not path.exists():
            return
        if self.args.dry_run:
            print(f"[dry-run] backup {path}")
            return
        rel = path.relative_to(Path.home()) if path.is_relative_to(Path.home()) else Path(path.name)
        dest = self.backup_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            shutil.rmtree(dest) if dest.is_dir() else dest.unlink()
        shutil.move(str(path), str(dest))

    def replace_dir(self, src: Path, dest: Path) -> None:
        if dest.exists() and dirs_equal(src, dest):
            if self.args.dry_run:
                print(f"[dry-run] unchanged {dest}")
            return
        if dest.exists():
            self.backup(dest)
        if self.args.dry_run:
            print(f"[dry-run] copy {src} -> {dest}")
            return
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    def copy_skill(self, src: Path, dest: Path) -> None:
        self.replace_dir(src, dest)

    # -- validation ---------------------------------------------------------
    def require(self, path: Path, label: str) -> None:
        if not path.exists():
            raise SystemExit(f"error: {label} not found at {path}")

    # -- steps --------------------------------------------------------------
    def install_bughunter(self) -> None:
        root = self.args.bughunter / "skills"
        self.require(root, "Claude-BugHunter skills")
        for src in sorted(p for p in root.iterdir() if p.is_dir()):
            self.copy_skill(src, self.args.skills_dir / src.name)
            self.stats["bughunter"] += 1

    def install_claude_red(self) -> None:
        root = self.args.claude_red / "Skills"
        self.require(root, "claude-red Skills")
        for src in sorted(p for p in root.glob("*/*") if p.is_dir()):
            if not (src / REQUIRED_SKILL).is_file():
                continue
            category, name = src.parent.name, src.name
            dest_name = RENAME_COLLISION.get(name, name)
            dest = self.args.skills_dir / CLAUDE_RED_ROOT / category / dest_name
            self.copy_skill(src, dest)
            self.stats["claude_red"] += 1
            if dest_name != name:
                self.stats["renamed"] += 1
            if not self.args.dry_run:
                result = ensure_frontmatter(dest / REQUIRED_SKILL, dest_name)
                if result == "added":
                    self.stats["frontmatter_added"] += 1

    def install_security_review(self) -> None:
        src = self.args.security_review / "security-audit"
        self.require(src, "security-review security-audit skill")
        self.copy_skill(src, self.args.skills_dir / "security-audit")
        self.stats["security_audit"] = 1

    def install_engine(self) -> None:
        src_engine = self.args.bughunter / "engine"
        src_cbh = self.args.bughunter / "cbh"
        self.require(src_engine, "Claude-BugHunter engine")
        self.require(src_cbh, "Claude-BugHunter cbh")
        self.replace_dir(src_engine, self.args.engine_dir / "engine")
        self.replace_dir(src_cbh, self.args.engine_dir / "cbh")

        # OpenCode dispatch overlay (uses `opencode run` when the Claude CLI is absent).
        overlay = self.args.repo / "config" / "agent.opencode.py"
        if overlay.is_file() and not self.args.dry_run:
            shutil.copy2(overlay, self.args.engine_dir / "engine" / "agent.py")

        # Accept a ProjectDiscovery httpx binary named `httpx` as well as
        # `httpx-toolkit`; the engine verifies the version before trusting it.
        osint = self.args.engine_dir / "engine" / "osint.py"
        if osint.is_file() and not self.args.dry_run:
            t = osint.read_text(encoding="utf-8")
            t = t.replace('for cand in ("httpx-toolkit",):', 'for cand in ("httpx-toolkit", "httpx"):')
            osint.write_text(t, encoding="utf-8")

        # Cosmetics: the CLI help should not claim Claude Code is the primary UI.
        cli = self.args.engine_dir / "cbh" / "cli.py"
        if cli.is_file() and not self.args.dry_run:
            t = cli.read_text(encoding="utf-8")
            t = t.replace("in Claude Code are PRIMARY", "in OpenCode are PRIMARY")
            t = t.replace("/hunt, /recon, /triage", "/hunt, /bb-recon, /triage")
            t = t.replace("when not in a Claude Code session", "when not in an OpenCode session")
            t = t.replace("Need richer context? In a Claude Code conversation:", "Need richer context? In OpenCode, run:")
            cli.write_text(t, encoding="utf-8")

        wrapper = self.args.bin_dir / "cbh"
        if self.args.dry_run:
            print(f"[dry-run] write wrapper {wrapper}")
            return
        self.args.bin_dir.mkdir(parents=True, exist_ok=True)
        wrapper.write_text(
            "#!/usr/bin/env bash\n"
            'exec python3 "$HOME/.config/opencode/bughunter/cbh/cli.py" "$@"\n',
            encoding="utf-8",
        )
        wrapper.chmod(0o755)

    def install_commands(self) -> None:
        src = self.args.repo / "commands"
        self.require(src, "commands directory")
        dest = self.args.commands_dir
        if not self.args.dry_run:
            dest.mkdir(parents=True, exist_ok=True)
        for f in sorted(src.glob("*.md")):
            target = dest / f.name
            if self.args.dry_run:
                print(f"[dry-run] copy {f} -> {target}")
                continue
            if target.exists():
                self.backup(target)
            shutil.copy2(f, target)
            self.stats["commands"] += 1

    def install_scaffolder(self) -> None:
        src = self.args.repo / "scripts" / "new-engagement.sh"
        if self.args.dry_run:
            print(f"[dry-run] install scaffolder from {src}")
            return
        self.args.bin_dir.mkdir(parents=True, exist_ok=True)
        dest = self.args.bin_dir / "bbnew"
        if dest.exists() or dest.is_symlink():
            dest.unlink()
        shutil.copy2(src, dest)
        dest.chmod(0o755)

    def run(self) -> int:
        self.install_bughunter()
        self.install_claude_red()
        self.install_security_review()
        self.install_engine()
        if not self.args.skip_commands:
            self.install_commands()
        self.install_scaffolder()
        if self.args.dry_run:
            print("\n[dry-run] no changes written")
            return 0
        print()
        print(f"  Claude-BugHunter skills : {self.stats['bughunter']}")
        print(f"  claude-red skills       : {self.stats['claude_red']} "
              f"({self.stats['renamed']} renamed, "
              f"{self.stats['frontmatter_added']} frontmatter added)")
        print(f"  security-audit          : {self.stats['security_audit']}")
        print(f"  OpenCode commands       : {self.stats['commands']}")
        print(f"  engine + cbh            : {self.args.engine_dir}")
        print(f"  backups (if any)        : {self.backup_root}")
        return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    home = Path.home()
    p = argparse.ArgumentParser(description="Install the OpenCode Red skill arsenal.")
    p.add_argument("--repo", type=Path, default=Path(__file__).resolve().parent.parent)
    p.add_argument("--bughunter", type=Path, required=True)
    p.add_argument("--claude-red", type=Path, required=True)
    p.add_argument("--security-review", type=Path, required=True)
    p.add_argument("--skills-dir", type=Path, default=home / ".claude/skills")
    p.add_argument("--commands-dir", type=Path, default=home / ".config/opencode/commands")
    p.add_argument("--engine-dir", type=Path, default=home / ".config/opencode/bughunter")
    p.add_argument("--bin-dir", type=Path, default=home / ".local/bin")
    p.add_argument("--skip-commands", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args(argv)


if __name__ == "__main__":
    try:
        sys.exit(Installer(parse_args()).run())
    except KeyboardInterrupt:
        eprint("\ninterrupted")
        sys.exit(130)
