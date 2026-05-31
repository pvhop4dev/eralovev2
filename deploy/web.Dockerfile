# Eralove Web — Production Dockerfile
FROM node:20-alpine AS base

# Install libc6-compat for process compatibility
RUN apk add --no-cache libc6-compat
WORKDIR /app

# ── 1. Install Dependencies Stage ───────────────────────
FROM base AS deps

# Copy monorepo metadata and lockfile
COPY package.json package-lock.json turbo.json ./
COPY apps/web/package.json ./apps/web/package.json
COPY packages/shared/package.json ./packages/shared/package.json

# Install dependencies using clean install
RUN npm ci

# ── 2. Build Stage ──────────────────────────────────────
FROM base AS builder

COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/package-lock.json ./package-lock.json
COPY . .

# Environment variables must be present at build time
ENV NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=production

# Build the Next.js app inside the monorepo workspace
RUN npx turbo run build --filter=@eralove/web

# ── 3. Production Runner Stage ──────────────────────────
FROM base AS runner

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME="0.0.0.0"

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Pre-create directory for caching purposes
RUN mkdir .next && chown nextjs:nodejs .next

# Copy Next.js standalone folder output
COPY --from=builder --chown=nextjs:nodejs /app/apps/web/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/apps/web/.next/static ./apps/web/.next/static
COPY --from=builder --chown=nextjs:nodejs /app/apps/web/public ./apps/web/public

USER nextjs

EXPOSE 3000

# Next.js standalone entrypoint
CMD ["node", "apps/web/server.js"]
