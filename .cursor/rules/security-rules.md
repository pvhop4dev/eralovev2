---
name: security-rules
description: Security requirements for Eralove application
---

# Security Rules

## Authentication

- JWT access tokens: 15 minute expiry, stored in memory (Zustand), never localStorage
- Refresh tokens: 7 day expiry, httpOnly + Secure + SameSite=Lax cookie
- Password hashing: bcrypt with cost factor 12
- OTP codes: 6 digits, 10 minute expiry, max 5 attempts
- Rate limit auth endpoints: 10 requests/minute per IP

## Authorization

- Every API endpoint that accesses couple data MUST verify the user belongs to that couple
- Use middleware to extract and validate JWT on every request
- Couple-scoped queries: always filter by `couple_id` derived from authenticated user
- Never trust client-provided `couple_id` or `user_id` — derive from JWT

## Data Privacy

- Couples can only see their own data (events, photos, messages, etc.)
- User search returns minimal info (id, username, display_name, avatar)
- Soft-deleted data is invisible to users but retained for recovery
- Full data deletion available on account delete (GDPR-like compliance)
- S3 presigned URLs expire in 1 hour

## Input Validation

- All inputs validated with Pydantic (backend) and Zod (frontend)
- Sanitize HTML in user-generated content (messages, notes, bios)
- File upload: validate MIME type and file size (max 10MB images, 100MB videos)
- SQL injection: prevented by SQLAlchemy parameterized queries (never raw SQL with string interpolation)
- XSS: React escapes by default, never use `dangerouslySetInnerHTML`

## API Security

- CORS: whitelist specific origins only
- Rate limiting: 100 req/min general, 10 req/min auth, 5 req/min AI
- Request size limit: 10MB
- No sensitive data in URL query parameters
- Use HTTPS only in production
- Disable OpenAPI docs in production (`docs_url=None` when not dev)

## Secrets

- Never commit `.env` files, API keys, or credentials
- Use environment variables for all secrets
- Rotate JWT secret periodically
- S3 credentials via IAM roles in production (not access keys)
