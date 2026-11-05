# Base image with Python and Node.js runtime support
FROM node:20-slim AS node-base
FROM python:3.11-slim

# Copy Node.js binaries into Python runtime environment
COPY --from=node-base /usr/local/bin /usr/local/bin
COPY --from=node-base /usr/local/lib/node_modules /usr/local/lib/node_modules

WORKDIR /app

# Install system utilities & build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Node.js dependencies
COPY package*.json .
RUN npm ci

# Copy full application codebase
COPY . .

# Expose MCP Gateway Port
EXPOSE 5001

# Default execution entrypoint launches the Agent Gateway
CMD ["npx", "tsx", "mcp/agent_gateway.ts"]
