---
name: deploy
description: Deploy Eralove application (frontend and/or backend)
---

# Deploy Eralove

## Frontend (Next.js → Vercel)

### Prerequisites
- Vercel CLI installed: `npm i -g vercel`
- Project linked: `vercel link`

### Deploy
```bash
# Preview deployment
cd apps/web && vercel

# Production deployment
cd apps/web && vercel --prod
```

### Environment Variables (Vercel Dashboard)
```
NEXT_PUBLIC_API_URL=https://api-love.eraquix.com
NEXT_PUBLIC_WS_URL=wss://api-love.eraquix.com
NEXT_PUBLIC_APP_URL=https://love.eraquix.com
NEXT_PUBLIC_MAPBOX_TOKEN=pk.xxx
NEXT_PUBLIC_S3_BUCKET_URL=https://cdn-love.eraquix.com
```

## Backend (Python FastAPI)

### Docker Build
```bash
cd apps/api && docker build -t eralove-api -f Dockerfile .
```

### Railway/Render Deployment
```bash
# Railway
railway up

# Or use Dockerfile deployment on Render/Fly.io
```

### Environment Variables (Backend)
```
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/eralove
REDIS_URL=redis://host:6379/0
AWS_S3_BUCKET=eralove-media
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_REGION=ap-southeast-1
CLAUDE_API_KEY=sk-ant-xxx
JWT_SECRET_KEY=xxx
CORS_ORIGINS=https://love.eraquix.com
```

## Database Migration (Production)
```bash
# SSH into server or use Railway CLI
cd apps/api && alembic upgrade head
```

## Pre-deploy Checklist
- [ ] All tests passing: `turbo test`
- [ ] No lint errors: `turbo lint`
- [ ] Build succeeds: `turbo build`
- [ ] Environment variables set in hosting provider
- [ ] Database migrations reviewed and tested
- [ ] No secrets in code
- [ ] CORS configured correctly
- [ ] Rate limiting enabled
