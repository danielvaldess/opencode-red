# Cheat sheet

What to load first for a given surface, and the signal that tells you it is worth
continuing. The skill is the methodology; this table is the entry point.

> Everything below is for authorized testing only. Confirm the asset is in scope
> before sending a request.

## Access control & identity

| Surface | Load | First moves | Signal |
|---|---|---|---|
| Object IDs, API routes | `@hunt-idor` | Swap IDs across two accounts; try numeric, UUID, GraphQL `node()` | Account B's data or action |
| Login, reset, email change | `@hunt-ato` | Reset poisoning, token reuse, email change without re-auth, MFA skip | Takeover of a test account |
| Auth protocols | `@hunt-auth-bypass` | SAML XSW, signature stripping, JWT trust, legacy endpoints | Authenticated as another user |
| JWT | `@hunt-jwt-crypto` | `alg:none`, RS256→HS256, weak secret, `kid`/`jku` | Forged token accepted |
| OAuth / OIDC | `@hunt-oauth` | `redirect_uri` bypass, missing `state`, code replay, open redirect | Code/token theft |
| SAML | `@hunt-saml` | XSW, comment injection, signature stripping, audience | Assertion for another identity |
| Sessions | `@hunt-session` | Fixation, no rotation on login, logout not invalidating | Persistent session |
| MFA / OTP | `@hunt-mfa-bypass` | Step skip, code replay, brute force, recovery-code leak | Post-MFA access |
| Password reset | `@hunt-forgot-password` | Enumeration, token in response, replay, no expiry | Reset another account |

## Injection

| Surface | Load | First moves | Signal |
|---|---|---|---|
| Reflected input | `@hunt-xss` | Context break, polyglot, DOM sinks, CSP bypass | Script execution in a browser |
| SQL-backed params | `@hunt-sqli` | Error/UNION, boolean/time blind, ORM edges | Data or boolean oracle |
| NoSQL | `@hunt-nosqli` | `$ne`, `$regex`, `$where`, JSON operator injection | Auth bypass or data dump |
| Templates | `@hunt-ssti` | `{{7*7}}`, `${7*7}`, engine fingerprint | Evaluated expression |
| File includes | `@hunt-lfi` | Traversal, wrappers, log poisoning, filter chains | File read / RCE |
| XML | `@hunt-xxe` | External entity, SVG/DOCX upload, OOB DTD | OOB callback / file read |
| Commands | `@hunt-rce` | Command separators, argument injection, deserialization | Command output |
| Deserialization | `@hunt-deserialization` | Magic methods, gadget chains, signed blobs | Code execution |

## Request-layer

| Surface | Load | First moves | Signal |
|---|---|---|---|
| Redirect params | `@hunt-open-redirect` | Protocol-relative, encoded, CRLF, `@` tricks | Off-domain redirect |
| SSRF-capable fetchers | `@hunt-ssrf` | Internal IPs, metadata, DNS rebinding, redirects | Internal response / OOB |
| Host header | `@hunt-host-header` | Reset poisoning, cache key, routing override | Poisoned link or internal route |
| Cache | `@hunt-cache-poison` | Unkeyed headers, parameter cloaking, deception | Poisoned response served to others |
| Proxies | `@hunt-http-smuggling` | CL.TE, TE.CL, H2.CL, timing probe | Desync / next-user request |
| CORS | `@hunt-cors` | Reflect origin, `null`, regex bypass, credentials | Cross-origin credentialed read |
| CSRF | `@hunt-csrf` | SameSite, Origin omission, JSON CSRF, WebSocket | State change cross-site |
| WebSockets | `@hunt-websocket` | Origin check, per-message auth, room takeover | Cross-site socket actions |
| Clickjacking | `@hunt-clickjacking` | Frame-ancestors, sensitive action framing | Real click on a sensitive action |

## Logic, data & APIs

| Surface | Load | First moves | Signal |
|---|---|---|---|
| Checkout, coupons, refunds | `@hunt-business-logic` | Negative quantity, stacking, currency, TOCTOU | Financial gain |
| Concurrent actions | `@hunt-race-condition` | Single-packet attack, parallel redeem | Double spend / extra entitlement |
| GraphQL | `@hunt-graphql` | Introspection, `node()`, batching, alias DoS | Cross-object read / auth bypass |
| Fintech GraphQL | `@hunt-fintech-graphql` | Ledger mutations, idempotency, decimal precision | Money movement |
| Undocumented APIs | `@hunt-shadow-api`, `@hunt-spa-api` | JS bundle routes, old versions, specs | Missing auth on a live route |
| Mass assignment | `@hunt-api-misconfig` | Add `role`, `is_admin`, `verified` | Privilege change |
| Uploads | `@hunt-file-upload` | Extension/MIME/magic, SVG, ZIP slip, path traversal | Execution or stored XSS |
| Source maps / bundles | `@hunt-source-leak` | `.map`, `.env`, `.git`, webpack chunks | Secret or route map |
| Cloud storage | `@hunt-cloud-misconfig`, `@cloud-iam-deep` | Public bucket, permissive ACL, leaked key | Data read/write |
| Subdomains | `@hunt-subdomain` | Dangling CNAME, provider fingerprints | Takeover |
| TLS / DNS | `@hunt-tls-network` | HSTS, DMARC, AXFR, weak ciphers | Spoof or zone leak |
| Mobile | `@apk-redteam-pipeline`, `@ios-redteam-pipeline` | Hardcoded secrets, pinning, exported components | Secret / bypass / deep link |
| AI / LLM | `@hunt-llm-ai`, `@hunt-rag-vector` | Direct/indirect injection, exfil, cross-tenant retrieval | Prompt/system leak, data exfil |
| Source code in scope | `@security-audit` | Semgrep, gitleaks, TruffleHog, dependency scan | Verified finding in source |

## Before you submit

1. Reproduce from a clean session.
2. Prove impact with two accounts (A attacks B) when authorization is involved.
3. Confirm the asset is in scope.
4. Redact cookies, tokens and third-party PII.
5. Run `/triage`, then `/validate`.
6. Write the report with `/report`.

If the signal column is empty, the finding is not ready.
