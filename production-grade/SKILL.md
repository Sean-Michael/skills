---
name: production-grade
description: >
  Apply production-grade standards when building or modifying web applications.
  Trigger on: "make it production ready", "add auth", "production grade",
  "harden this", or any time a user is building a web app with user accounts,
  an API, or a database and hasn't said it's a prototype. Standards are the
  default — not an add-on.
---

# Production-Grade Web Applications

If scope is ambiguous, ask once. If the user says prototype, relax these
standards. Otherwise, apply them without being asked.

## Non-Obvious Defaults

These are the things that get skipped without explicit instruction:

**Auth**
- All mutations check resource ownership server-side — never trust a
  client-supplied ID alone (IDOR).
- Session tokens in `httpOnly` cookies, not `localStorage`.
- Server-side logout invalidation.

**Rate limiting**
- Auth endpoints (login, register, password reset) rate limited per IP.
- Applied at middleware layer — not inside route handlers (handlers can be
  bypassed by concurrency).
- Returns `429` with `Retry-After`.

**Password reset tokens**
- Cryptographically random (`secrets.token_urlsafe` or equivalent).
- Expiry ≤ 1 hour. Single-use: invalidated on first use.
- Stored hashed. Endpoint returns identical response whether email exists or not.

**Observability**
- Structured JSON logging with request ID, user ID, timestamp on every error.
- Request ID propagated through middleware → logs → error responses.
- `/health` endpoint.
- No secrets, tokens, or PII in logs.

