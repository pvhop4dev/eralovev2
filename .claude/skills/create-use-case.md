---
name: create-use-case
description: Create a new application use case following Clean Architecture pattern
---

# Create Use Case

When asked to implement a business operation, follow this pattern:

## 1. Identify the Use Case Type

| Type | Pattern | Example |
|---|---|---|
| **Query** (Read) | Returns data | GetEventByIdUseCase, ListEventsUseCase |
| **Command** (Write) | Modifies state | CreateEventUseCase, DeleteEventUseCase |
| **Action** (Trigger) | Side effects | SendLoveTouchUseCase, AnalyzeSentimentUseCase |

## 2. Create the Use Case File

```python
# apps/api/src/application/use_cases/{feature}/{action}.py
from uuid import UUID
from domain.entities.{entity} import {Entity}
from domain.repositories.{entity}_repository import {Entity}Repository
from domain.repositories.couple_repository import CoupleRepository
from domain.exceptions import NotFoundError, ForbiddenError
from application.dtos.{feature}_dto import {Action}{Feature}Request, {Feature}Response
import structlog

logger = structlog.get_logger()


class {Action}{Feature}UseCase:
    """
    {Vietnamese description of what this use case does}.

    Flow:
    1. Verify user belongs to a couple
    2. {Step 2}
    3. {Step 3}

    Raises:
        CoupleNotFoundError: User is not matched with anyone.
        NotFoundError: {Entity} does not exist.
        ForbiddenError: {Entity} does not belong to this couple.
    """

    def __init__(
        self,
        {entity}_repo: {Entity}Repository,
        couple_repo: CoupleRepository,
    ):
        self.{entity}_repo = {entity}_repo
        self.couple_repo = couple_repo

    async def execute(
        self,
        dto: {Action}{Feature}Request,
        user_id: UUID,
    ) -> {Feature}Response:
        # 1. Verify user belongs to a couple
        couple = await self.couple_repo.get_by_user(user_id)
        if not couple:
            raise CoupleNotFoundError("You are not matched with anyone")

        # 2. Business logic
        entity = {Entity}(
            couple_id=couple.id,
            # ... map from DTO
        )

        # 3. Persist
        created = await self.{entity}_repo.create(entity)

        logger.info(
            "{entity}_created",
            {entity}_id=str(created.id),
            couple_id=str(couple.id),
            user_id=str(user_id),
        )

        # 4. Return response DTO
        return {Feature}Response.model_validate(created)
```

## 3. Create DTOs

```python
# apps/api/src/application/dtos/{feature}_dto.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from uuid import UUID

class {Action}{Feature}Request(BaseModel):
    """Request DTO for {action} {feature}."""
    title: str = Field(..., min_length=1, max_length=255)
    # ... required fields

class Update{Feature}Request(BaseModel):
    """Request DTO for updating {feature}. All fields optional."""
    title: str | None = Field(None, min_length=1, max_length=255)
    # ... optional fields

class {Feature}Response(BaseModel):
    """Response DTO for {feature}."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    # ... all response fields
    created_at: datetime
    updated_at: datetime | None = None
```

## 4. Wire Up Dependencies

```python
# apps/api/src/presentation/deps.py
from typing import Annotated
from fastapi import Depends

def get_{action}_{feature}_use_case(
    session: DbSession,
) -> {Action}{Feature}UseCase:
    return {Action}{Feature}UseCase(
        {entity}_repo=Postgres{Entity}Repository(session),
        couple_repo=PostgresCoupleRepository(session),
    )

# Type alias
{Action}{Feature}UC = Annotated[
    {Action}{Feature}UseCase,
    Depends(get_{action}_{feature}_use_case),
]
```

## 5. Connect to Route

```python
# apps/api/src/presentation/api/v1/{feature}.py
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_{feature}(
    body: {Action}{Feature}Request,
    current_user: CurrentUser,
    use_case: {Action}{Feature}UC,
) -> ApiResponse[{Feature}Response]:
    result = await use_case.execute(body, current_user.id)
    return ApiResponse(data=result)
```

## 6. Write Tests

```python
# apps/api/tests/unit/use_cases/{feature}/test_{action}.py
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from application.use_cases.{feature}.{action} import {Action}{Feature}UseCase
from application.dtos.{feature}_dto import {Action}{Feature}Request
from domain.exceptions import CoupleNotFoundError, ForbiddenError
from tests.factories.{entity}_factory import {Entity}Factory
from tests.factories.couple_factory import CoupleFactory


@pytest.fixture
def mock_{entity}_repo():
    return AsyncMock(spec={Entity}Repository)

@pytest.fixture
def mock_couple_repo():
    return AsyncMock(spec=CoupleRepository)

@pytest.fixture
def use_case(mock_{entity}_repo, mock_couple_repo):
    return {Action}{Feature}UseCase(
        {entity}_repo=mock_{entity}_repo,
        couple_repo=mock_couple_repo,
    )

@pytest.fixture
def valid_dto():
    return {Action}{Feature}Request(title="Test", ...)

@pytest.fixture
def fake_couple():
    return CoupleFactory.create()


class TestCreate{Feature}:
    @pytest.mark.asyncio
    async def test_success(self, use_case, valid_dto, fake_couple, mock_couple_repo, mock_{entity}_repo):
        # Arrange
        user_id = uuid4()
        mock_couple_repo.get_by_user.return_value = fake_couple
        mock_{entity}_repo.create.return_value = {Entity}Factory.create()

        # Act
        result = await use_case.execute(valid_dto, user_id)

        # Assert
        assert result is not None
        mock_couple_repo.get_by_user.assert_called_once_with(user_id)
        mock_{entity}_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_couple_raises_error(self, use_case, valid_dto, mock_couple_repo):
        mock_couple_repo.get_by_user.return_value = None

        with pytest.raises(CoupleNotFoundError):
            await use_case.execute(valid_dto, uuid4())
```

## Checklist
- [ ] Use case has single `execute()` method
- [ ] All dependencies injected via constructor
- [ ] Authorization check (user belongs to couple)
- [ ] Domain exceptions raised (not HTTP exceptions)
- [ ] Request/Response DTOs defined with Pydantic v2
- [ ] Structured logging for business events
- [ ] Dependency provider function in `deps.py`
- [ ] Route connected with proper status code
- [ ] Unit tests: happy path + error cases
- [ ] Docstring with flow description and exceptions
