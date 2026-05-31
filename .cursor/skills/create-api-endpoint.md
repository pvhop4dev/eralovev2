---
name: create-api-endpoint
description: Create a new API endpoint following Clean Architecture pattern
---

# Create API Endpoint

When asked to create a new API endpoint, follow this exact pattern:

## 1. Define the DTO (Request/Response Schema)

```python
# apps/api/src/application/dtos/{feature}_dto.py
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class Create{Feature}Request(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    # ... fields with validation

class {Feature}Response(BaseModel):
    id: UUID
    # ... fields
    created_at: datetime

    model_config = {"from_attributes": True}
```

## 2. Create/Update the Use Case

```python
# apps/api/src/application/use_cases/{feature}/{action}.py
from app.domain.repositories.{feature}_repository import {Feature}Repository
from app.application.dtos.{feature}_dto import Create{Feature}Request, {Feature}Response

class {Action}{Feature}UseCase:
    def __init__(self, repo: {Feature}Repository):
        self.repo = repo

    async def execute(self, dto: Create{Feature}Request, user_id: UUID) -> {Feature}Response:
        # business logic here
        entity = await self.repo.create(...)
        return {Feature}Response.model_validate(entity)
```

## 3. Create the Route

```python
# apps/api/src/presentation/api/v1/{feature}.py
from fastapi import APIRouter, Depends, status
from typing import Annotated

router = APIRouter(prefix="/{feature}s", tags=["{Feature}s"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_{feature}(
    body: Create{Feature}Request,
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[{Action}{Feature}UseCase, Depends(get_{action}_{feature}_use_case)],
) -> ApiResponse[{Feature}Response]:
    result = await use_case.execute(body, current_user.id)
    return ApiResponse(data=result)
```

## 4. Register the Router

Add to `apps/api/src/presentation/main.py`:
```python
app.include_router({feature}_router, prefix="/api/v1")
```

## Rules
- Always use `Annotated[..., Depends()]` pattern
- Always validate input with Pydantic
- Return proper HTTP status codes (201 for create, 204 for delete)
- Use `ApiResponse` wrapper for consistent response format
- Add route to OpenAPI tags
- Write a test for the endpoint
