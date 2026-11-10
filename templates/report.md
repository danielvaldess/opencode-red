# <Title: impact in one line>

**Program:** <program>
**Asset:** <in-scope asset>
**Severity:** <CVSS 3.1 score> — `<vector>`
**Class:** <CWE / VRT>

## Summary

Two or three sentences: what the issue is, where it is, and the concrete impact.
Write for an engineer who has 60 seconds.

## Steps to reproduce

1. Sign in as a test user (account A).
2. Send the following request:

```http
POST /api/... HTTP/1.1
Host: ...
Cookie: <redacted>
Content-Type: application/json

{ ... }
```

3. Observe the response:

```http
HTTP/1.1 200 OK
...
```

4. The same request returns account B's data / performs the action without
   authorization / leaks the token.

## Proof of concept

- Minimal script or curl command:
- Evidence (redacted screenshots / HAR):
- Two-account proof: attacker account A → victim account B.

## Impact

An unauthenticated/authenticated attacker can <read/modify/delete/take over>
<whose data> at <scale>. This violates <security property> and enables
<next step in the chain>.

## Affected users / scope

- Environment: production/QA
- Number of affected accounts (if known):
- Preconditions:

## Remediation

Specific, testable fix. If the fix needs a migration or rollout, say so.

## References

- CWE:
- Similar disclosed report / advisory:
- Timeline:
