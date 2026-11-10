# Toolchain

`./install.sh --tools` installs the tools below into `~/go/bin` and
`~/.local/bin`. Nothing is installed system-wide.

## Core

| Tool | Use | Install |
|---|---|---|
| `subfinder` | passive subdomain enumeration | `go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest` |
| `dnsx` | DNS resolution and probing | `go install github.com/projectdiscovery/dnsx/cmd/dnsx@latest` |
| `httpx` (ProjectDiscovery) | HTTP probe, status, title, tech | `go install github.com/projectdiscovery/httpx/cmd/httpx@latest` |
| `katana` | active crawl | `go install github.com/projectdiscovery/katana/cmd/katana@latest` |
| `gau` | historical URLs | `go install github.com/lc/gau/v2/cmd/gau@latest` |
| `waybackurls` | Wayback URLs | `go install github.com/tomnomnom/waybackurls@latest` |
| `assetfinder` | passive subdomains | `go install github.com/tomnomnom/assetfinder@latest` |
| `chaos` | ProjectDiscovery Chaos API | `go install github.com/projectdiscovery/chaos-client/cmd/chaos@latest` |
| `anew` | append unique lines | `go install github.com/tomnomnom/anew@latest` |
| `gf` + patterns | classify URLs by bug class | `go install github.com/tomnomnom/gf@latest` then clone `1ndianl33t/Gf-Patterns` to `~/.gf` |

## Scanning & exploitation

| Tool | Use | Install |
|---|---|---|
| `nuclei` | CVE / misconfig templates | release binary or `go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest` |
| `ffuf` | content and parameter fuzzing | release / package manager |
| `feroxbuster` | recursive content discovery | release / package manager |
| `gobuster` | directory/DNS/vhost brute force | package manager |
| `dalfox` | XSS scanning | `go install github.com/hahwul/dalfox/v2@latest` |
| `sqlmap` | SQL injection | package manager |
| `ghauri` | blind/error SQLi | `pipx install git+https://github.com/r0oth3x49/ghauri` |
| `jwt_tool` | JWT analysis and forging | `pipx install jwt-tool` or clone the repo |

## Code and secrets

| Tool | Use | Install |
|---|---|---|
| `semgrep` | SAST | `pipx install semgrep` |
| `trufflehog` | verified secret scan over git history | release binary |
| `gitleaks` | secret scan | `go install github.com/zricethezav/gitleaks/v8@latest` |
| `trivy` | containers, IaC, dependencies | release / package manager |
| `osv-scanner` | dependency CVEs | `go install github.com/google/osv-scanner/cmd/osv-scanner@latest` |
| `checkov` | IaC misconfiguration | `pipx install checkov` |

The `security-audit` skill orchestrates these and has grep-based fallbacks for
anything missing. It never installs a tool without asking.

## Mobile

| Tool | Use |
|---|---|
| `jadx` | APK/DEX decompilation |
| `apktool` | APK unpack/repack |
| `frida` / `objection` | runtime instrumentation |
| `class-dump` / `Hopper` | iOS static analysis |

## Wordlists

Common locations:

```
/usr/share/seclists/
/usr/share/wordlists/rockyou.txt
```

If SecLists is not installed:

```bash
sudo apt install seclists
# or
git clone --depth 1 https://github.com/danielmiessler/SecLists.git ~/tools/SecLists
```

## The `httpx` collision

`httpx` is both a Python library and a ProjectDiscovery scanner. If the Python
package is installed, its CLI can shadow the scanner and fail with:

```
The httpx command line client could not run because the required dependencies were not installed.
```

Check which one you have:

```bash
httpx -version | grep -i projectdiscovery
```

The installer moves a broken Python wrapper to `httpx-python.bak` and links the
ProjectDiscovery binary. If you install Python `httpx` later, fix the symlink
again or put `~/go/bin` before `~/.local/bin` in `PATH`.

## Burp Suite

The skills assume a proxy at `127.0.0.1:8080` when one is needed, but none of the
core commands require Burp. Burp Community is still the best manual companion for
request tampering, Repeater and Collaborator (blind SSRF/XXE/OOB).

If you use the `browse` MCP, point the browser at Burp or keep Burp for manual
work and use `browse` for authenticated automation.

## Browser MCP

- `browse` — real Chrome with your sessions. Best for SPA, OAuth, DOM XSS and
  file upload flows.
- `browser` — headless Chromium for scripted checks.

Neither is required by the installer. Configure them in
`~/.config/opencode/opencode.jsonc`.

## PATH

If `~/go/bin` is not on `PATH`, add to your shell rc:

```bash
export PATH="$HOME/go/bin:$HOME/.local/bin:$PATH"
```

## Verify

```bash
./scripts/verify.sh
```

Missing optional tools are reported as warnings, not failures. The install still
works without them; the skills degrade to curl/grep fallbacks.
