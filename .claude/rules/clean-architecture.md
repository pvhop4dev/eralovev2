---
name: clean-architecture
description: Enforce Clean Architecture rules for the Python backend
---

# Clean Architecture Rules

## Layer Dependencies (STRICT)

```
Presentation → Application → Domain ← Infrastructure
```

### Domain Layer (Innermost)

- **MUST NOT** import from application, infrastructure, or presentation
- **MUST NOT** import SQLAlchemy, FastAPI, Redis, boto3, or any framework
- Contains: Entities, Value Objects, Repository Interfaces (ABC), Domain Events, Domain Services
- Pure Python only — no external dependencies

### Application Layer

- **CAN** import from Domain
- **MUST NOT** import from Infrastructure or Presentation
- **MUST NOT** import SQLAlchemy models or FastAPI directly
- Contains: Use Cases, DTOs (Pydantic), Service Interfaces (ABC)
- Each Use Case is a single class with one `execute()` method

### Infrastructure Layer

- **CAN** import from Domain and Application (to implement interfaces)
- **MUST NOT** import from Presentation
- Contains: PostgreSQL repositories, Redis client, S3 client, external API clients
- Implements abstract interfaces from Domain and Application layers

### Presentation Layer

- **CAN** import from Application (use cases, DTOs)
- **SHOULD NOT** import from Domain directly (use DTOs as boundary)
- **MUST NOT** import from Infrastructure directly
- Contains: FastAPI routes, middleware, WebSocket handlers
- Uses dependency injection to get use cases

## Dependency Injection Pattern

```python
# In presentation layer
from typing import Annotated
from fastapi import Depends

def get_user_repository() -> UserRepository:
    # returns concrete PostgresUserRepository
    ...

def get_register_use_case(
    repo: Annotated[UserRepository, Depends(get_user_repository)]
) -> RegisterUserUseCase:
    return RegisterUserUseCase(repo)

@router.post("/register")
async def register(
    body: RegisterRequest,
    use_case: Annotated[RegisterUserUseCase, Depends(get_register_use_case)],
):
    return await use_case.execute(body)
```

## File Naming Convention

- One entity per file: `user.py`, `couple.py`
- One use case per file: `register.py`, `login.py`
- One router per feature: `auth.py`, `events.py`
- Repository interface and implementation same name, different directories
