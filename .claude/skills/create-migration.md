---
name: create-migration
description: Create a new Alembic database migration
---

# Create Database Migration

## Steps

1. **Define/Update SQLAlchemy model** in `apps/api/src/infrastructure/database/models/`

Model template:
```python
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.sql import func
from uuid import uuid4
from datetime import datetime

from app.infrastructure.database.connection import Base

class {TableName}Model(Base):
    __tablename__ = "{table_names}"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    # ... columns
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
```

2. **Generate migration:**
```bash
cd apps/api && alembic revision --autogenerate -m "description_of_change"
```

3. **Review the generated migration** — check:
   - Correct table name (snake_case, plural)
   - All indexes created (especially on FKs)
   - Constraints are correct (NOT NULL, UNIQUE, CHECK)
   - No unwanted changes to existing tables

4. **Run migration:**
```bash
cd apps/api && alembic upgrade head
```

## Conventions
- Table names: snake_case, plural (`users`, `love_events`)
- Primary keys: UUID v7
- All tables: `created_at`, `updated_at`
- Soft delete: `deleted_at` (nullable)
- JSONB for flexible/dynamic fields
- Index all foreign keys
- Use `server_default` for database-level defaults
