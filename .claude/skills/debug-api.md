---
name: debug-api
description: Debug a backend API issue in the FastAPI application
---

# Debug API Issue

When debugging a backend issue, follow this systematic approach:

## 1. Identify the Problem
- What endpoint is affected? Check `apps/api/src/presentation/api/v1/`
- What error is returned? (status code, error message)
- Is it reproducible? What request triggers it?

## 2. Trace the Request Flow (Clean Architecture)
Follow the request through layers:

```
Route (presentation/) → Use Case (application/) → Repository (infrastructure/) → Database
```

1. **Presentation layer**: Check route definition, middleware, auth guard
2. **Application layer**: Check use case logic, DTO validation
3. **Domain layer**: Check entity business rules, value object validation
4. **Infrastructure layer**: Check repository queries, external API calls

## 3. Common Issues

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
- Check TTL on cached items

### S3
- Check presigned URL expiry
- Check bucket CORS configuration
- Check IAM permissions

## 4. Debugging Tools
```bash
# Check API logs
cd apps/api && python -m uvicorn src.presentation.main:app --reload --log-level debug

# Test endpoint directly
curl -X POST http://localhost:8000/api/v1/endpoint -H "Content-Type: application/json" -d '{}'

# Check database
docker exec -it eralove-postgres psql -U eralove -d eralove

# Check Redis
docker exec -it eralove-redis redis-cli
```

## 5. Fix Approach
- Fix in the correct architectural layer
- Domain errors → fix entity/value object
- Validation errors → fix DTO/use case
- Data errors → fix repository/migration
- Add or update test for the bug
