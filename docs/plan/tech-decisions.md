# Eralove - Technical Decisions Log

## TD-001: Next.js App Router (thay vi Pages Router)
- **Quyet dinh:** Dung App Router (Next.js 15)
- **Ly do:** Server Components giam JS bundle, streaming SSR, nested layouts, route groups phu hop voi cau truc app phuc tap
- **Trade-off:** Learning curve cao hon, mot so thu vien chua ho tro day du

## TD-002: Python FastAPI (thay vi Node.js/NestJS)
- **Quyet dinh:** Backend dung Python + FastAPI
- **Ly do:** User yeu cau Python. FastAPI async-first, auto OpenAPI docs, Pydantic validation tot, ecosystem AI/ML phong phu (Claude SDK, sentiment analysis)
- **Trade-off:** Khong share code giua FE/BE (khac ngon ngu), can Docker cho deployment

## TD-003: Clean Architecture cho Backend
- **Quyet dinh:** 4 layers: Domain → Application → Infrastructure → Presentation
- **Ly do:** Tach biet business logic khoi framework, de test, de thay doi database/external service
- **Trade-off:** Nhieu file hon, boilerplate ban dau

## TD-004: Turborepo cho Monorepo
- **Quyet dinh:** Dung Turborepo (khong phai Nx hay Lerna)
- **Ly do:** Nhe, nhanh, config don gian, tich hop tot voi Next.js (cung Vercel)
- **Trade-off:** It tinh nang hon Nx (khong co code generation built-in)

## TD-005: Zustand + TanStack Query (thay vi Redux)
- **Quyet dinh:** Zustand cho UI state, TanStack Query cho server state
- **Ly do:** Nhe hon Redux, it boilerplate, TQ co cache + invalidation + optimistic updates built-in
- **Trade-off:** Zustand stores nho, can quan ly nhieu store

## TD-006: S3 Presigned URLs cho upload
- **Quyet dinh:** Client upload truc tiep len S3 qua presigned URL
- **Ly do:** Khong bottleneck backend, khong can proxy file qua server, tiet kiem bandwidth
- **Trade-off:** Can CloudFront/CDN phia truoc, CORS config can chinh xac

## TD-007: Redis Pub/Sub cho WebSocket scaling
- **Quyet dinh:** WebSocket events qua Redis Pub/Sub
- **Ly do:** Khi scale nhieu backend instances, messages van broadcast dung
- **Trade-off:** Them dependency (Redis), phuc tap hon direct WebSocket

## TD-008: UUID v7 cho Primary Keys
- **Quyet dinh:** UUID v7 thay vi auto-increment integer
- **Ly do:** Time-sortable (khong can ORDER BY created_at), an toan khi expose ra API, khong lo trung khi distributed
- **Trade-off:** 16 bytes thay vi 4/8 bytes, index lon hon

## TD-009: Cursor-based Pagination cho Chat
- **Quyet dinh:** Chat messages dung cursor pagination, events dung offset
- **Ly do:** Chat la infinite scroll (cursor hieu qua hon), events la calendar view (offset phu hop)
- **Trade-off:** Cursor phuc tap hon implement

## TD-010: Claude API cho AI Ari
- **Quyet dinh:** Dung Claude API (Anthropic) truc tiep
- **Ly do:** Ho tro tieng Viet tot, conversation context dai, personality engineering tot
- **Trade-off:** Chi phi API, can cache responses khi co the
