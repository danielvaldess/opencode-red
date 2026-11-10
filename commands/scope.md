---
description: "Mandatory pre-flight scope check — verify an asset is in scope BEFORE any HTTP touch. Deterministic (deny-wins, default-deny) via engine/scope.py against the engagement's scope.md. Blocks out-of-scope testing. Usage: /scope <asset> [<asset> ...]"
---

Run **exactly** this command with the `shell` tool and return its output verbatim:

```bash
python3 "$HOME/.config/opencode/bughunter/engine/scope.py" $ARGUMENTS --md ./scope.md
```

Rules:
- Do not read or interpret `scope.md` yourself: the script is the source of truth.
- Do not run any other tool before this command.
- If it fails because `./scope.md` does not exist, say so and stop (do not invent scope).
- If the output contains `OUT-OF-SCOPE`, stop: do not touch that asset.
- Report `IN-SCOPE` / `OUT-OF-SCOPE <reason>` literally.
