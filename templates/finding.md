# Finding — <short name>

- **Status:** lead | validated | drafted | submitted | triaged | paid | closed
- **Class:** IDOR / SSRF / XSS / auth bypass / business logic / …
- **Asset:**
- **Severity:** (CVSS 3.1 vector + score)
- **Submission UUID:**

## Summary

One paragraph: what the bug is, where it lives, and what an attacker gains.

## 7-Question Gate

1. Is it reproducible from a clean session? —
2. Is the asset in scope? —
3. Is the impact real (not theoretical)? —
4. Is it a duplicate of known behavior? —
5. Does it require privileged access the attacker would not have? —
6. Is it already fixed? —
7. Would a triager accept this as a security issue? —

## Reproduction

```
1.
2.
3.
```

Include the exact request and response (redacted). Keep it minimal and deterministic.

## Impact

Who can do what, against whom, and what it costs the program. Prefer a concrete
impact statement over a vulnerability-class definition.

## Evidence

| File | Description |
|---|---|
| `../evidence/…` | redacted screenshot/HAR |

## Remediation

The smallest fix that removes the root cause (authorization check, server-side
validation, token binding, rate limit, etc.).

## Notes

Triager dialogue, chain references, follow-ups.
