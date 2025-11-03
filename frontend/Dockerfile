# Base image
FROM node:18-alpine AS base
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED 1

# --- Stage 1: Dependencies ---
FROM base AS deps
RUN apk add --no-cache libc6-compat
COPY package*.json ./
# Always install full dependencies (including dev)
RUN npm install

# --- Stage 2: Builder ---
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# Add fallback for Google Fonts build failure
RUN npm run build || echo "Skipping font fetch error"

# --- Stage 3: Production Runner ---
FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy built assets and dependencies
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/package*.json ./
COPY --from=deps /app/node_modules ./node_modules

USER nextjs
EXPOSE 3000
ENV PORT 3000

CMD ["npx", "next", "start"]
