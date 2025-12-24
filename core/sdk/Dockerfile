FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy Shadow SDK
COPY . /app/shadow_sdk/

# Install Shadow SDK and dependencies
WORKDIR /app/shadow_sdk
RUN pip install --no-cache-dir -e .

# Install MCP SDK
RUN pip install --no-cache-dir mcp

WORKDIR /app

# Copy MCP server
COPY mcp_server.py /app/

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run MCP server
CMD ["python", "-m", "mcp_server"]

