---
name: feature-workflow
description: "MANDATORY: Every feature must follow Plan → Implement → Test → Docs workflow. No exceptions."
---

# Feature Development Workflow (BẮT BUỘC)

> **Rule này KHÔNG CÓ NGOẠI LỆ.** Mọi tính năng — dù nhỏ hay lớn — đều phải tuân theo quy trình dưới đây. Bỏ qua bất kỳ bước nào sẽ bị coi là vi phạm nghiêm trọng.

## Quy trình 4 bước

### Bước 1: Plan (Lên kế hoạch)

Trước khi viết bất kỳ dòng code nào, PHẢI:

- [ ] Xác định rõ scope: tính năng làm gì, không làm gì
- [ ] Liệt kê các file sẽ tạo mới / sửa đổi (backend + frontend)
- [ ] Xác định domain entities, use cases, DTOs cần thiết
- [ ] Xác định API endpoints (method, path, request/response schema)
- [ ] Xác định database changes (model mới, migration)
- [ ] Xác định UI components cần tạo/sửa
- [ ] Ghi ra edge cases và error handling
- [ ] Estimate effort (S/M/L)

**Output:** Một implementation plan rõ ràng, được user review và approve trước khi code.

### Bước 2: Implement (Triển khai)

Triển khai theo đúng Clean Architecture, thứ tự từ trong ra ngoài:

1. **Domain layer** — Entities, Value Objects, Repository interfaces
2. **Application layer** — Use Cases, DTOs, Service interfaces
3. **Infrastructure layer** — Repository implementations, external services
4. **Presentation layer** — API routes, WebSocket handlers
5. **Database** — Alembic migration
6. **Frontend** — Components, pages, stores, hooks

**Rules khi implement:**
- Mỗi file PHẢI có docstring/comment mô tả mục đích
- Mỗi Use Case PHẢI có single `execute()` method
- Mỗi route PHẢI dùng `Annotated[Depends()]` pattern
- DTOs PHẢI nằm trong `application/dtos/`, KHÔNG inline trong route
- Response PHẢI theo format `{ data, meta, error }`
- Frontend PHẢI dùng TanStack Query cho server state, Zustand cho client state
- Frontend PHẢI dùng API client (`lib/api-client.ts`), KHÔNG raw `fetch`

### Bước 3: Test (Kiểm thử)

SAU KHI implement xong, PHẢI viết và chạy test:

#### Backend tests (bắt buộc):
- [ ] Unit test cho mỗi domain entity mới/sửa
- [ ] Unit test cho mỗi use case (happy path + error cases)
- [ ] Unit test cho mỗi value object mới
- [ ] Chạy `pytest` và xác nhận PASS

```bash
# Chạy test cho feature cụ thể
cd apps/api
python -m pytest tests/unit/use_cases/{feature}/ -v

# Chạy toàn bộ test suite để đảm bảo không break
python -m pytest tests/ -v
```

#### Frontend tests (khuyến khích, bắt buộc cho components phức tạp):
- [ ] Component test cho UI components chính (Vitest + React Testing Library)
- [ ] Chạy `npm run test` và xác nhận PASS

#### Tiêu chí PASS:
- Tất cả test hiện tại vẫn pass (không regression)
- Test mới cover ≥80% logic của use case
- Edge cases được test (null input, unauthorized, not found, duplicate)

### Bước 4: Docs (Cập nhật tài liệu)

SAU KHI test pass, PHẢI cập nhật các file tài liệu sau:

#### Bắt buộc cập nhật:
- [ ] **`FEATURES.md`** — Đánh dấu ✅ cho các task đã hoàn thành, cập nhật % completion
- [ ] **`docs/plan/phase*.md`** — Check `[x]` cho các task đã xong trong plan tương ứng

#### Cập nhật nếu liên quan:
- [ ] **`docs/plan/api-design.md`** — Nếu thêm/sửa API endpoint
- [ ] **`docs/plan/database-schema.md`** — Nếu thêm/sửa model hoặc migration
- [ ] **`CLAUDE.md`** (= `AGENTS.md` = `.cursorrules`) — Nếu thay đổi conventions hoặc architecture

## Checklist tổng hợp (copy-paste cho mỗi feature)

```markdown
## Feature: [Tên tính năng]

### Plan
- [ ] Scope defined
- [ ] Files identified (new/modified)
- [ ] API design documented
- [ ] Plan approved by user

### Implement
- [ ] Domain layer (entities, VOs, repo interfaces)
- [ ] Application layer (use cases, DTOs)
- [ ] Infrastructure layer (repo implementations)
- [ ] Presentation layer (routes)
- [ ] Database migration (if needed)
- [ ] Frontend components/pages
- [ ] Code follows Clean Architecture rules

### Test
- [ ] Unit tests written for use cases
- [ ] Unit tests written for domain entities
- [ ] All existing tests still pass
- [ ] `pytest` run successfully
- [ ] Frontend tests (if applicable)

### Docs
- [ ] FEATURES.md updated
- [ ] Phase plan updated
- [ ] API docs updated (if applicable)
- [ ] DB schema docs updated (if applicable)
```

## Vi phạm phổ biến (KHÔNG ĐƯỢC LÀM)

1. ❌ Code trực tiếp mà không có plan
2. ❌ Implement xong mà không viết test
3. ❌ Test fail mà vẫn move on
4. ❌ Quên cập nhật FEATURES.md sau khi hoàn thành
5. ❌ Inline DTO trong route thay vì tạo file riêng
6. ❌ Dùng raw `fetch` trong frontend thay vì API client
7. ❌ Tạo migration mà không document trong database-schema.md
8. ❌ Bỏ qua error handling và edge cases
