---
name: unit-testing
description: Comprehensive unit testing rules for backend (pytest) and frontend (Vitest)
---

# Unit Testing Rules

## Core Principles

- Every use case MUST have unit tests
- Tests are isolated — mock ALL external dependencies (DB, Redis, S3, APIs)
- One assertion per test when possible, multiple related assertions OK
- Tests must be deterministic — no dependency on time, random, network
- Tests must be fast — unit test suite < 30 seconds

## Backend (pytest + pytest-asyncio)

### Test Structure

```
apps/api/tests/
├── conftest.py                    # Shared fixtures
├── factories/                     # Test data factories
│   ├── user_factory.py
│   ├── couple_factory.py
│   └── event_factory.py
├── unit/
│   ├── domain/
│   │   ├── test_user_entity.py
│   │   ├── test_email_value_object.py
│   │   └── test_match_service.py
│   └── use_cases/
│       ├── auth/
│       │   ├── test_register.py
│       │   └── test_login.py
│       ├── calendar/
│       │   ├── test_create_event.py
│       │   └── test_delete_event.py
│       └── chat/
│           └── test_send_message.py
└── integration/
    ├── conftest.py                # DB fixtures, test client
    └── test_auth_api.py
```

### Test File Naming

- File: `test_{module_name}.py`
- Function: `test_{action}_{scenario}_{expected_result}`
- Examples:
  - `test_register_with_valid_data_creates_user`
  - `test_register_with_existing_email_raises_conflict`
  - `test_login_with_wrong_password_raises_unauthorized`
  - `test_create_event_by_non_couple_member_raises_forbidden`

### Test Pattern: Arrange-Act-Assert (AAA)

```python
@pytest.mark.asyncio
async def test_create_event_with_valid_data_returns_event():
    # Arrange — setup mocks and test data
    mock_event_repo = AsyncMock(spec=EventRepository)
    mock_couple_repo = AsyncMock(spec=CoupleRepository)
    mock_couple_repo.get_by_user.return_value = fake_couple
    mock_event_repo.create.return_value = fake_event

    use_case = CreateEventUseCase(
        event_repo=mock_event_repo,
        couple_repo=mock_couple_repo,
    )
    dto = CreateEventRequest(
        title="Date Night",
        event_type="date",
        event_date="2026-05-01",
    )

    # Act — execute the action under test
    result = await use_case.execute(dto, user_id=fake_user.id)

    # Assert — verify expected outcome
    assert result.title == "Date Night"
    assert result.event_type == "date"
    mock_event_repo.create.assert_called_once()
    mock_couple_repo.get_by_user.assert_called_once_with(fake_user.id)
```

### Test Pattern: Exception Tests

```python
@pytest.mark.asyncio
async def test_create_event_without_couple_raises_not_found():
    mock_couple_repo = AsyncMock(spec=CoupleRepository)
    mock_couple_repo.get_by_user.return_value = None  # No couple

    use_case = CreateEventUseCase(
        event_repo=AsyncMock(),
        couple_repo=mock_couple_repo,
    )

    with pytest.raises(CoupleNotFoundError):
        await use_case.execute(dto, user_id=fake_user.id)
```

### Factory Pattern for Test Data

```python
# tests/factories/user_factory.py
from uuid import uuid4
from datetime import date
from app.domain.entities.user import User

class UserFactory:
    @staticmethod
    def create(
        id=None,
        email="test@example.com",
        display_name="Test User",
        **overrides,
    ) -> User:
        defaults = {
            "id": id or uuid4(),
            "email": email,
            "display_name": display_name,
            "date_of_birth": date(2000, 1, 15),
            "is_onboarded": True,
        }
        defaults.update(overrides)
        return User(**defaults)
```

### What to Test per Layer

#### Domain Entities & Value Objects

- Validation rules (Email format, Password strength)
- Business logic methods
- State transitions
- Edge cases (empty strings, boundary values)

```python
def test_email_value_object_rejects_invalid_format():
    with pytest.raises(InvalidEmailError):
        Email("not-an-email")

def test_email_value_object_normalizes_case():
    email = Email("Test@Example.COM")
    assert email.value == "test@example.com"

def test_couple_days_together_calculates_correctly():
    couple = CoupleFactory.create(start_date=date(2025, 1, 1))
    # Freeze time to 2026-01-01
    assert couple.days_together(today=date(2026, 1, 1)) == 365
```

#### Use Cases

- Happy path (valid input → expected output)
- Authorization checks (user belongs to couple)
- Validation errors (invalid input → domain exception)
- Not found scenarios (entity doesn't exist)
- Business rule violations (already matched, event in past, etc.)
- Side effects verified (repo methods called with correct args)

#### NEVER Test in Unit Tests

- Database queries (that's integration tests)
- HTTP endpoints (that's integration tests)
- External API calls (that's integration tests)
- File I/O

### Fixtures (conftest.py)

```python
# tests/conftest.py
import pytest
from tests.factories.user_factory import UserFactory
from tests.factories.couple_factory import CoupleFactory

@pytest.fixture
def fake_user():
    return UserFactory.create()

@pytest.fixture
def fake_partner():
    return UserFactory.create(email="partner@example.com", display_name="Partner")

@pytest.fixture
def fake_couple(fake_user, fake_partner):
    return CoupleFactory.create(user1=fake_user, user2=fake_partner)
```

### Mocking Rules

- Use `AsyncMock(spec=InterfaceClass)` to enforce interface contract
- Mock at the boundary (repository interfaces, service interfaces)
- NEVER mock domain entities or value objects — use factories
- NEVER mock the use case itself — that's what you're testing
- Verify mock calls: `assert_called_once()`, `assert_called_with()`

---

## Frontend (Vitest + React Testing Library)

### Test Structure

```
apps/web/src/
├── features/calendar/
│   ├── components/
│   │   ├── event-card.tsx
│   │   └── __tests__/
│   │       └── event-card.test.tsx
│   ├── hooks/
│   │   ├── use-events.ts
│   │   └── __tests__/
│   │       └── use-events.test.ts
│   └── __tests__/
│       └── api.test.ts
```

### Component Test Rules

- Test behavior, NOT implementation details
- Query by role/text/label, NOT by class/id/test-id
- Prefer `getByRole` > `getByText` > `getByLabelText` > `getByTestId`
- Test user interactions (`userEvent` over `fireEvent`)
- Test what the user sees, not internal state

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

test("submit button is disabled when form is empty", () => {
  render(<EventForm />);
  const submitBtn = screen.getByRole("button", { name: /tao su kien/i });
  expect(submitBtn).toBeDisabled();
});

test("calls onSubmit with form data when filled and submitted", async () => {
  const user = userEvent.setup();
  const onSubmit = vi.fn();
  render(<EventForm onSubmit={onSubmit} />);

  await user.type(screen.getByLabelText(/tieu de/i), "Date Night");
  await user.click(screen.getByRole("button", { name: /tao su kien/i }));

  expect(onSubmit).toHaveBeenCalledWith(
    expect.objectContaining({ title: "Date Night" }),
  );
});
```

### Hook Test Rules

- Wrap hooks that use context in test providers
- Use `renderHook` from `@testing-library/react`
- Mock API client for hooks using TanStack Query

### What NOT to Test

- Third-party libraries (Framer Motion animations, TanStack Query internals)
- CSS/styling (use visual regression tests if needed)
- Next.js routing internals

---

## Coverage Requirements

| Layer                           | Target           | Enforced              |
| ------------------------------- | ---------------- | --------------------- |
| Domain entities & value objects | >90%             | Yes (CI blocks below) |
| Application use cases           | >80%             | Yes (CI blocks below) |
| Infrastructure repos            | >60%             | Integration tests     |
| Presentation routes             | >60%             | Integration tests     |
| Frontend components             | Key interactions | No hard target        |
| Frontend hooks                  | Data flow tested | No hard target        |

## Running Tests

```bash
# Backend unit tests only
cd apps/api && pytest tests/unit -v

# Backend with coverage
cd apps/api && pytest tests/unit --cov=src --cov-report=html

# Frontend tests
cd apps/web && npx vitest run

# All tests (Turborepo)
turbo test
```
