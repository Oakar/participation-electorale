FROM mcr.microsoft.com/devcontainers/python:3.12

# Install Node.js 20 for TypeScript
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install TypeScript and Claude Code globally
RUN npm install -g typescript @anthropic-ai/claude-code
