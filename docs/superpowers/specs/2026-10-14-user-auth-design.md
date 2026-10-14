# User authentication design

## Scope

Backend-only login, logout, current session, user administration, and an idempotent superadmin seed. No public registration, no frontend changes. Passwords require at least 8 characters, an uppercase letter, a lowercase letter, and a special character. Password changes revoke all of the user's sessions. Sessions have a fixed absolute lifetime of 24 hours.

Ordinary users may log in, read their own account, and edit only their own username/password. Only superadmin may create, list, read other accounts, or delete users. All credential edits revoke the target user's sessions and self-edits require the current password. No API can grant, remove, or transfer superadmin privilege.

## Architecture

One table per model file: users, auth sessions, and login throttle buckets. One CRUD file per module contains only database operations. Business decisions and transactions live in separate operation files under `use_cases/users/` and `use_cases/auth/`. Routes adapt HTTP requests and responses. Schemas prohibit undeclared fields, including role changes.

Passwords use Argon2id. Session tokens are 256-bit random secrets; the database stores only their SHA-256 digest. Browser authentication uses a host-only HttpOnly cookie with SameSite=Strict and Secure in production. Login rotates the token. A CSRF token derived with HMAC from the session secret protects authenticated mutations; unsafe requests require a configured Origin. Development HTTP cookies require explicit APP_ENV=development.

Login attempts and self-edit current-password checks share persistent limits by both normalized username and client IP, with atomic database counters. Unknown usernames and wrong passwords return the same error and perform password verification. Application code reads the ASGI client address; direct-server deployments disable proxy headers and reverse-proxy deployments must explicitly restrict trusted proxies.

Superadmin privilege is an immutable database flag, independent of username. Public create/update schemas cannot grant that privilege. The reserved initial username cannot be assigned to an ordinary account. The superadmin account cannot be deleted. Editing one's own username/password requires the current password. PostgreSQL row locks serialize login and password changes so revoked credentials cannot create a new session in a concurrent login.

Tables use RLS and revoke access from Supabase Data API roles. SQLAlchemy accesses them through the backend database connection. No password hashes, session secrets, or submitted passwords are returned in API errors or user representations. Seed passwords come from a local environment value or a hidden prompt, not tracked source.

## Verification

Unit tests cover password rules, session expiry, throttling, and seed idempotency. Endpoint tests use an isolated database and exercise login, logout, CSRF, unauthenticated requests, user CRUD, password revocation, attempted role injection, and protection after the superadmin username changes. Migration SQL is reviewed before applying; then the requested superadmin is seeded and the deployed database is checked using non-destructive queries.
