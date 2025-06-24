# Stage 1: Build the Next.js application
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Install build dependencies for native modules (if any)
RUN apk add --no-cache python3 make g++

# Copy package.json and package-lock.json for dependency caching
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy the rest of the application
COPY . .

# Build the Next.js application
RUN npm run build

# Stage 2: Run the application
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy built assets from builder stage
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/public ./public

# Expose port for Next.js
EXPOSE 3000

# Environment variable for production
ENV NODE_ENV=production

# Start the Next.js application
CMD ["npm", "start"]