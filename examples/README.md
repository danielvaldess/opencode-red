# Examples

Synthetic data for trying the workflow without touching a real target.

| File | Purpose |
|---|---|
| `scope.md` | Reserved `.example` hosts; one in scope, one out of scope |
| `engagement.json` | Scope file for the engine's mock mode (localhost lab fixture) |
| `demo.sh` | Runs the real scope checker, the real URL classifier and the engine mock |

```bash
./install.sh          # installs the engine and cbh
./examples/demo.sh
```

`demo.sh` makes no network requests to the synthetic hosts. The engine mock uses a
local lab fixture and labels its output as mock. The terminal GIF in the README is
an abridged recording of this run.

This directory is intentionally small: it exists to demonstrate the deterministic
parts of the workflow, not to be a full lab. For practice targets, use OWASP Juice
Shop, DVWA or PortSwigger Academy.
