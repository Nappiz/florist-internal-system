# User authentication verification — 14 October 2026

- Complete suite: **42 tests passed**, including **5 PostgreSQL concurrency tests** against isolated temporary schemas.
- Local endpoint tests cover access control, password requirements, generic login failures, persisted throttles, CSRF, cookie flags, expiry, logout, role injection, self-edit current-password checks, credential revocation, and superadmin protection after rename.
- PostgreSQL tests verify atomic account limits across workers, login during password changes, expired-counter cleanup under concurrent login, expiry while awaiting row locks, and logout during authentication.
- Independent read-only security review identified three issues: current-password brute force, stale expiry while waiting for locks, and cleanup deadlocks. Regression tests and implementation fixes resolved them; follow-up review found no new actionable issues in those changes.
- Applied Alembic revision: `20261014_01`.
- Live database checks verified RLS on all three authentication tables and no SELECT grants for `anon`, `authenticated`, or `service_role`.
- Requested superadmin exists, its supplied initial password matches the Argon2 hash, and repeated seeding preserves the same account and password hash.
- Real Uvicorn HTTP smoke against Supabase passed login, create user, deny staff changes to superadmin, password reset with session revocation, login using the new password, logout, and delete the temporary account.
- Temporary test users and PostgreSQL schemas were removed. The seed password was not written into tracked source or `.env`.

## Operational limits

These checks do not certify that every possible vulnerability is absent. The local smoke ran in explicit development mode with `--no-proxy-headers`. Production cookie/HTTPS behavior was checked with TestClient; real production TLS termination, reverse-proxy trust, network traffic controls, backups, and credential handling remain deployment responsibilities documented in README.md.
