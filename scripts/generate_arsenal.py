#!/usr/bin/env python3
"""
generate_arsenal.py — build docs/ARSENAL.md from the installed skills.

The catalogue is generated, never hand-maintained: run it after `install.sh`
(or after updating an upstream bundle) and commit the result.

    python3 scripts/generate_arsenal.py
    python3 scripts/generate_arsenal.py --check   # fail if the file is stale
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:  # PyYAML is optional; the fallback parser handles our frontmatter shapes.
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


GROUPS_BUGHUNTER = {
    "Core methodology & tradecraft": {
        "bb-methodology", "redteam-mindset", "redteam-report-template",
        "recon-scope-triage", "mid-engagement-ir-detection", "security-arsenal",
    },
    "Recon & OSINT": {
        "offensive-osint", "osint-methodology", "web2-recon", "hunt-source-leak",
        "hunt-spa-api", "hunt-shadow-api", "supply-chain-attack-recon",
    },
    "Validation & reporting": {
        "triage-validation", "report-writing", "bugcrowd-reporting", "evidence-hygiene",
    },
    "Enterprise platforms & identity": {
        "m365-entra-attack", "okta-attack", "enterprise-vpn-attack",
        "vmware-vcenter-attack", "hunt-sharepoint", "hunt-ntlm-info",
        "hunt-auth-bypass", "hunt-saml",
    },
    "Cloud, containers & CI/CD": {
        "cloud-iam-deep", "hunt-cloud-misconfig", "hunt-k8s", "hunt-cicd",
    },
    "Mobile applications": {"apk-redteam-pipeline", "ios-redteam-pipeline"},
    "AI / LLM security": {"hunt-llm-ai", "hunt-rag-vector"},
    "Web3 & fintech": {"meme-coin-audit", "web3-audit", "hunt-fintech-graphql"},
}

CLAUDE_RED_CATEGORIES = {
    "active-directory": "Active Directory",
    "ai": "AI security",
    "api": "API security",
    "auth": "Auth & identity",
    "cicd": "CI/CD",
    "cloud": "Cloud",
    "container": "Containers & Kubernetes",
    "crypto": "Cryptography & TLS",
    "exploit-dev": "Exploit development",
    "forensics": "Forensics & anti-forensics",
    "fuzzing": "Fuzzing",
    "infrastructure": "Red-team infrastructure",
    "iot": "IoT & embedded",
    "mobile": "Mobile",
    "network": "Network",
    "post-exploitation": "Post-exploitation",
    "privesc": "Privilege escalation",
    "recon": "Recon & OSINT",
    "social-engineering": "Social engineering",
    "supply-chain": "Supply chain",
    "utility": "Utility",
    "web": "Web application",
    "wireless": "Wireless",
}

UPSTREAM = {
    "BugHunter": ("Claude-BugHunter", "https://github.com/elementalsouls/Claude-BugHunter"),
    "claude-red": ("claude-red", "https://github.com/SnailSploit/claude-red"),
    "security-review": ("security-review", "https://github.com/cdmx-in/security-review"),
}


def split_frontmatter(text: str) -> tuple[str | None, str]:
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            after = end + 4
            if after < len(text) and text[after] == "\n":
                after += 1
            return text[4:end], text[after:]
    return None, text


def fallback_parse(fm: str) -> dict[str, str]:
    out: dict[str, str] = {}
    lines = fm.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if val in (">", ">-", "|", "|-"):
            block = []
            i += 1
            while i < len(lines) and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
                block.append(lines[i].strip())
                i += 1
            out[key] = " ".join(x for x in block if x).strip()
            continue
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        out[key] = val
        i += 1
    return out


def read_meta(skill_md: Path) -> tuple[str, str, str]:
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    fm, _ = split_frontmatter(text)
    data: dict[str, str] = {}
    if fm:
        if yaml is not None:
            try:
                loaded = yaml.safe_load(fm)
                if isinstance(loaded, dict):
                    data = {str(k): "" if v is None else str(v) for k, v in loaded.items()}
            except Exception:
                data = fallback_parse(fm)
        else:
            data = fallback_parse(fm)
    return (
        data.get("name", skill_md.parent.name),
        data.get("description", ""),
        skill_md.parent.name,
    )


def clean_desc(desc: str, limit: int = 170) -> str:
    desc = re.sub(r"\s+", " ", desc).strip()
    desc = desc.replace("|", "\\|")
    if len(desc) <= limit:
        return desc
    cut = desc[:limit]
    for sep in (". ", "; ", ", "):
        idx = cut.rfind(sep)
        if idx > limit * 0.55:
            return cut[: idx + 1].rstrip() + " …"
    idx = cut.rfind(" ")
    if idx > limit * 0.6:
        cut = cut[:idx]
    return cut.rstrip(" ,;:—-") + " …"


def discover(skills_dir: Path) -> dict[str, list[tuple[str, str, str]]]:
    groups: dict[str, list[tuple[str, str, str]]] = {}
    seen: set[str] = set()

    def add(group: str, sid: str, name: str, desc: str, source: str) -> None:
        if sid in seen:
            return
        seen.add(sid)
        groups.setdefault(group, []).append((sid, name, clean_desc(desc), source))  # type: ignore[arg-type]

    # Claude-BugHunter (top-level folders only)
    if skills_dir.is_dir():
        for d in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
            if d.name in {"claude-red", "synced"} or d.name.startswith("."):
                continue
            md = d / "SKILL.md"
            if not md.is_file():
                continue
            name, desc, sid = read_meta(md)
            if sid == "security-audit":
                add("Source-code audit", sid, name, desc, "security-review")
                continue
            group = next((g for g, ids in GROUPS_BUGHUNTER.items() if sid in ids), None)
            if group is None:
                group = "Web, API & application classes"
            add(group, sid, name, desc, "BugHunter")

        red_root = skills_dir / "claude-red"
        if red_root.is_dir():
            for md in sorted(red_root.glob("*/*/SKILL.md")):
                name, desc, sid = read_meta(md)
                cat = md.parent.parent.name
                add("red::" + CLAUDE_RED_CATEGORIES.get(cat, cat.title()), sid, name, desc, "claude-red")

    return groups


def render_table(rows: list[tuple[str, str, str]]) -> list[str]:
    out = ["| Skill | Focus | Source |", "|---|---|---|"]
    for sid, _name, desc, source in sorted(rows, key=lambda r: r[0]):
        label, url = UPSTREAM[source]
        out.append(f"| `{sid}` | {desc or '—'} | [{label}]({url}) |")
    return out


def render(groups: dict[str, list[tuple[str, str, str]]]) -> str:
    core = {g: v for g, v in groups.items() if not g.startswith("red::")}
    red = {g: v for g, v in groups.items() if g.startswith("red::")}
    core_total = sum(len(v) for v in core.values())
    red_total = sum(len(v) for v in red.values())

    order = [
        "Core methodology & tradecraft", "Recon & OSINT",
        "Web, API & application classes", "Validation & reporting",
        "Enterprise platforms & identity", "Cloud, containers & CI/CD",
        "Mobile applications", "AI / LLM security", "Web3 & fintech",
        "Source-code audit",
    ]
    ordered = [g for g in order if g in core]
    ordered += sorted(g for g in core if g not in order)

    out = [
        "# Arsenal",
        "",
        f"**{core_total + red_total} skills** in two layers: a bug-bounty core and a",
        "red-team library. This file is generated by `scripts/generate_arsenal.py`",
        "from the installed bundles — do not edit it by hand.",
        "",
        "Load a skill by ID with `@<skill>` in OpenCode, or let the model pick it from",
        "the description. The **Source** column points at the upstream project; the",
        "full text lives in `~/.claude/skills/` after installation.",
        "",
        "For a task-oriented index (surface → skill → first move) see",
        "[`CHEATSHEET.md`](CHEATSHEET.md).",
        "",
        "> Only test systems you are authorized to test. A skill is knowledge, not permission.",
        "",
        "---",
        "",
        f"## Part 1 — Bug bounty core ({core_total})",
        "",
        "The engagement workflow: methodology, recon, per-class hunting, validation,",
        "reporting, enterprise platforms, cloud and source-code audit.",
        "",
    ]
    for group in ordered:
        out += [f"### {group}", ""] + render_table(core[group]) + [""]

    out += [
        "---",
        "",
        f"## Part 2 — Red-team library ({red_total})",
        "",
        "`claude-red` adds deeper material for internal red team, mobile, cloud,",
        "CI/CD, exploit development, wireless and embedded engagements. Some of it",
        "overlaps the core library; for web bug bounty prefer the `hunt-*` skills.",
        "",
    ]
    for group in sorted(red):
        title = group.split("::", 1)[1]
        out += [f"### {title}", ""] + render_table(red[group]) + [""]

    out += [
        "---",
        "",
        "## Attribution",
        "",
        "The skill texts are authored by the upstream projects and redistributed/installed",
        "under their MIT licenses; see `NOTICE.md` and `licenses/`. This repository's own",
        "code (installer, command adaptations, engine overlay, scaffolding, docs) is MIT.",
        "",
    ]
    return "\n".join(out)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--skills-dir", type=Path, default=Path.home() / ".claude/skills")
    p.add_argument("--out", type=Path, default=Path(__file__).resolve().parent.parent / "docs/ARSENAL.md")
    p.add_argument("--check", action="store_true", help="exit 1 if the committed file is stale")
    args = p.parse_args()

    text = render(discover(args.skills_dir))
    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        if current != text:
            print(f"error: {args.out} is stale; run scripts/generate_arsenal.py", file=sys.stderr)
            return 1
        print(f"{args.out} is up to date")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out} ({text.count('| `')} skills)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
