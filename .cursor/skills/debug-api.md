---
name: debug-api
description: Debug a backend API issue in the FastAPI application
---

# Debug API Issue

When debugging a backend issue, follow this systematic approach:

## 1. Identify the Problem

- What endpoint is affected? Check `apps/api/src/presentation/api/v1/`
- What error is returned? (status code, error message)
- **Get the `X-Trace-Id`** from the response header or `meta.trace_id` in error body
- Is it reproducible? What request triggers it?

## 2. Use Trace ID for Correlation

Every request has a unique `trace_id` that flows through the entire stack:

```bash
# Find all logs for a specific request
grep "trace_id=abc123" logs/app.log

# Frontend can read it from response header
# Response Header: X-Trace-Id: abc123def456
# Error Body: { "meta": { "trace_id": "abc123def456" } }
```

**Key files:**

- `infrastructure/trace_context.py` — `get_trace_id()` / `set_trace_id()`
- `presentation/middleware/trace_middleware.py` — generates + binds trace_id
- `presentation/middleware/error_handler.py` — includes trace_id in error responses

## 3. Trace the Request Flow (Clean Architecture)

Follow the request through layers:

```
TraceMiddleware (sets trace_id) → Route (presentation/) → Use Case (application/) → Repository (infrastructure/) → Database
```

1. **Middleware layer**: Check TraceMiddleware, auth middleware, CORS
2. **Presentation layer**: Check route definition, request validation
3. **Application layer**: Check use case logic, DTO validation
4. **Domain layer**: Check entity business rules, value object validation
5. **Infrastructure layer**: Check repository queries, external API calls

## 4. Common Issues

### Database

- Check SQLAlchemy query: enable `echo=True` on engine temporarily
- Check migration status: `alembic current` and `alembic history`
- Check connection pool: `pool_size`, `max_overflow` in connection config

### Auth

- Check JWT expiry: decode token at jwt.io
- Check refresh token flow
- Check middleware order in `main.py`

### Redis

- Check connection: `redis-cli ping`
- Check key patterns: `redis-cli keys "pattern*"`
- Check TTL on cached items (mood: 24h)

### Trace ID Issues

- If `X-Trace-Id` header is missing: check `TraceMiddleware` is registered in `main.py`
- If `meta.trace_id` is null in errors: check `get_trace_id()` import in error_handler
- If frontend can't read header: check `expose_headers=["X-Trace-Id"]` in CORS config

## 5. Debugging Tools

```bash
# Check API logs (trace_id auto-included in structlog output)
cd apps/api && python -m uvicorn src.presentation.main:app --reload --log-level debug

# Test endpoint directly — pass custom trace_id for easy grep
curl -X POST http://localhost:8000/api/v1/endpoint \
  -H "Content-Type: application/json" \
  -H "X-Trace-Id: debug-$(date +%s)" \
  -d '{}'

# Check database
docker exec -it eralove-postgres psql -U eralove -d eralove

# Check Redis
docker exec -it eralove-redis redis-cli
```

## 6. Fix Approach

- Fix in the correct architectural layer
- Domain errors → fix entity/value object
- Validation errors → fix DTO/use case
- Data errors → fix repository/migration
- **Add or update test for the bug** (Triangle of Change: code + test + doc)
