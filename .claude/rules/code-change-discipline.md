---
name: code-change-discipline
description: Every code change MUST be accompanied by test updates and documentation updates — the Triangle of Change
---

# Code Change Discipline — Triangle of Change

## Core Principle

> **Mọi thay đổi code đều phải đi kèm với cập nhật test và tài liệu.**
> Không bao giờ sửa code mà không kiểm tra test và docs tương ứng.

```
        📝 Documentation
       /              \
      /   EVERY CODE   \
     /    CHANGE MUST    \
    /     TOUCH ALL 3     \
   /________________________\
  🧪 Tests          💻 Source Code
```

**Nếu sửa code mà không sửa test + docs → CHƯA HOÀN THÀNH.**

---

## Quy Trình Bắt Buộc Khi Sửa Code

### Bước 1: Hiểu Phạm Vi Thay Đổi (Impact Analysis)

Trước khi sửa bất kỳ dòng code nào, xác định:

1. **File nào bị ảnh hưởng trực tiếp?** (file bạn đang sửa)
2. **File nào bị ảnh hưởng gián tiếp?** (file import/depend vào file bạn sửa)
3. **Test nào cover file đó?** (tìm trong `tests/unit/`, `tests/integration/`)
4. **Tài liệu nào mô tả tính năng đó?** (tìm trong `docs/`, `CLAUDE.md`, `.claude/rules/`, `.claude/skills/`)

```bash
# Tìm test liên quan
grep -r "import.*{module_name}" apps/api/tests/
grep -r "{ClassName}" apps/api/tests/
grep -r "{function_name}" apps/api/tests/

# Tìm docs liên quan
grep -r "{feature_name}" docs/
grep -r "{feature_name}" .claude/
grep -r "{feature_name}" CLAUDE.md
```

### Bước 2: Sửa Code (Source Code)

Thực hiện thay đổi code theo yêu cầu.

### Bước 3: Cập Nhật Tests (BẮT BUỘC)

| Loại thay đổi code | Hành động test bắt buộc |
|---|---|
| **Thêm function/method mới** | Viết test mới cho function đó |
| **Sửa logic trong function** | Cập nhật test hiện tại + thêm test cho case mới |
| **Đổi signature (params, return)** | Cập nhật TẤT CẢ test gọi function đó |
| **Xóa function/method** | Xóa test tương ứng + kiểm tra không test nào gọi nó |
| **Thêm API endpoint** | Viết unit test cho use case + integration test cho route |
| **Sửa DTO/schema** | Cập nhật test data (factories, fixtures) |
| **Sửa database model** | Cập nhật factory + integration tests |
| **Sửa frontend component** | Cập nhật component test (render, interaction) |
| **Sửa hook** | Cập nhật hook test |
| **Fix bug** | Viết regression test để bug không tái diễn |

### Bước 4: Cập Nhật Tài Liệu (BẮT BUỘC)

| Loại thay đổi code | Tài liệu cần cập nhật |
|---|---|
| **Thêm/sửa API endpoint** | `docs/plan/api-design.md`, OpenAPI docstring |
| **Thêm/sửa database table** | `docs/plan/database-schema.md` |
| **Thay đổi kiến trúc** | `docs/plan/architecture.md`, `CLAUDE.md` |
| **Thêm tính năng mới** | `docs/plan/phase{N}.md` (roadmap tương ứng) |
| **Sửa domain logic** | Docstring trong entity/use case |
| **Thêm config/env var** | `CLAUDE.md` (Tech Stack / Settings) |
| **Thay đổi quy ước code** | `.claude/rules/` (rule tương ứng) |
| **Thêm pattern/skill mới** | `.claude/skills/` (skill tương ứng) |
| **Thay đổi UI component** | Comment/docstring trong component |
| **Thay đổi deploy process** | `.claude/skills/deploy.md` |

---

## Checklist Trước Khi Hoàn Thành

Mỗi code change PHẢI qua checklist này trước khi coi là hoàn thành:

### ✅ Source Code
- [ ] Code đã sửa đúng yêu cầu
- [ ] Code tuân thủ Clean Architecture (domain → application → infrastructure → presentation)
- [ ] Code tuân thủ coding conventions (naming, typing, async/await)
- [ ] Không có code thừa, console.log, print debug, TODO bị quên
- [ ] Import paths đúng layer (không vi phạm dependency rules)

### ✅ Tests
- [ ] Tất cả test hiện tại vẫn PASS (`pytest` / `vitest run`)
- [ ] Test mới đã viết cho code mới/sửa
- [ ] Regression test đã viết nếu đây là bug fix
- [ ] Test coverage không giảm (≥80% cho use cases)
- [ ] Test đặt tên đúng convention: `test_{what}_{scenario}_{expected}`
- [ ] Factory/fixture đã cập nhật nếu model/DTO thay đổi

### ✅ Documentation
- [ ] Docstring cập nhật cho function/class bị sửa
- [ ] API docs cập nhật nếu endpoint thay đổi
- [ ] Schema docs cập nhật nếu database thay đổi
- [ ] README/CLAUDE.md cập nhật nếu config/convention thay đổi
- [ ] Rules/Skills cập nhật nếu pattern thay đổi

---

## Ví Dụ Thực Tế

### Ví dụ 1: Thêm field `location` vào Event

**Code changes:**
```python
# 1. Domain entity — thêm field
# apps/api/src/domain/entities/event.py
@dataclass
class Event:
    ...
    location: str | None = None  # NEW

# 2. DTO — thêm field
# apps/api/src/application/dtos/event_dto.py
class CreateEventRequest(BaseModel):
    ...
    location: str | None = Field(None, max_length=500)  # NEW

class EventResponse(BaseModel):
    ...
    location: str | None = None  # NEW

# 3. DB model — thêm column
# apps/api/src/infrastructure/database/models/event_model.py
class EventModel(Base):
    ...
    location: Mapped[str | None] = mapped_column(String(500), nullable=True)  # NEW

# 4. Migration
# alembic revision --autogenerate -m "add location to events"
```

**Test changes (BẮT BUỘC):**
```python
# 5. Factory — thêm field
class EventFactory:
    @staticmethod
    def create(..., location="Hà Nội", **overrides):
        defaults = {..., "location": location}
        ...

# 6. Unit test — test new field
async def test_create_event_with_location_stores_location():
    dto = CreateEventRequest(title="Date", ..., location="Café Cộng")
    result = await use_case.execute(dto, user_id)
    assert result.location == "Café Cộng"

async def test_create_event_without_location_defaults_none():
    dto = CreateEventRequest(title="Date", ...)  # no location
    result = await use_case.execute(dto, user_id)
    assert result.location is None

# 7. Integration test — test API response includes location
async def test_get_event_returns_location(client, auth_headers):
    resp = await client.get(f"/api/v1/events/{event_id}", headers=auth_headers)
    assert resp.json()["data"]["location"] == "Hà Nội"
```

**Doc changes (BẮT BUỘC):**
```markdown
# 8. docs/plan/database-schema.md — thêm column description
| location | varchar(500) | nullable | Địa điểm sự kiện |

# 9. docs/plan/api-design.md — thêm field vào request/response
POST /api/v1/events body: { ..., "location": "Café Cộng" }
GET  /api/v1/events/{id} response.data: { ..., "location": "Café Cộng" }
```

### Ví dụ 2: Fix bug — tin nhắn không hiển thị emoji

**Code change:**
```python
# Fix: sanitize content was stripping emojis
def sanitize_content(text: str) -> str:
    # OLD: re.sub(r'[^\w\s]', '', text)  — strips emojis!
    # NEW: only strip dangerous HTML
    return bleach.clean(text, strip=True)
```

**Test change (BẮT BUỘC):**
```python
# Regression test — ensure this specific bug never returns
def test_sanitize_content_preserves_emojis():
    """Regression: emojis were stripped by old regex. See bug #42."""
    result = sanitize_content("Yêu em 💕🥰")
    assert "💕" in result
    assert "🥰" in result

def test_sanitize_content_strips_html():
    result = sanitize_content("<script>alert('xss')</script>Hello")
    assert "<script>" not in result
    assert "Hello" in result
```

**Doc change (BẮT BUỘC):**
```python
# Docstring updated
def sanitize_content(text: str) -> str:
    """Sanitize user-generated text content.

    Strips dangerous HTML tags while preserving Unicode characters
    including emojis. Uses bleach for safe HTML cleaning.

    Note: Previous regex-based approach incorrectly stripped emojis.
    See regression test test_sanitize_content_preserves_emojis.
    """
```

---

## Quy Tắc Đặc Biệt

### Khi Refactor (không thay đổi behavior)
- Tests PHẢI vẫn pass mà KHÔNG sửa assertions
- Nếu phải sửa test assertions → đây không phải refactor, đây là behavior change
- Docs: chỉ cần cập nhật nếu file path/structure thay đổi

### Khi Xóa Code
- Xóa tests tương ứng
- Xóa docs tương ứng
- Kiểm tra không có dead references (imports, links) bị sót
- `grep -r "{deleted_function}" .` để tìm references còn sót

### Khi Sửa Bug
- **BẮT BUỘC** viết regression test (test tái hiện bug trước khi fix)
- Comment trong test mô tả bug gốc
- Nếu bug do thiếu validation → thêm validation + test cho case đó

### Khi Thêm Dependency Mới
- Cập nhật `requirements.txt` / `package.json`
- Cập nhật `CLAUDE.md` Tech Stack nếu là dependency quan trọng
- Cập nhật `.gitignore` nếu dependency tạo files mới
- Cập nhật Docker config nếu cần system package

### Khi Thay Đổi Environment Variables
- Cập nhật `.env.example`
- Cập nhật `CLAUDE.md` (Domains / Settings)
- Cập nhật `deploy.md` skill (environment variables section)
- Cập nhật Docker Compose / deployment configs

---

## Xác Minh (Verification)

Sau khi hoàn thành cả 3 phần (code + test + docs), chạy:

```bash
# Backend
cd apps/api && ruff check src/                    # Lint
cd apps/api && pytest tests/ -v                   # All tests pass
cd apps/api && pytest --cov=src --cov-fail-under=80  # Coverage OK

# Frontend
cd apps/web && npx eslint src/                    # Lint
cd apps/web && npx vitest run                     # All tests pass

# Verify no broken references
grep -r "TODO" apps/ --include="*.py" --include="*.ts" --include="*.tsx"
```

## Tóm Tắt

| ❌ KHÔNG chấp nhận | ✅ BẮT BUỘC |
|---|---|
| Sửa code, quên sửa test | Code + Test + Docs luôn đi cùng nhau |
| Test pass nhưng không cover case mới | Viết test cho mọi case mới |
| Docs cũ mô tả behavior cũ | Docs luôn phản ánh trạng thái hiện tại |
| Fix bug mà không có regression test | Mọi bug fix đều kèm regression test |
| Refactor mà test phải sửa assertion | Refactor = behavior giữ nguyên |
| Thêm env var mà không ghi docs | Mọi config change đều được document |
