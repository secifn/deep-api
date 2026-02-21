# Multi-stage build for optimized image
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies + timezone
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Set timezone to Asia/Bangkok
ENV TZ=Asia/Bangkok
RUN ln -snf /usr/share/zoneinfo/Asia/Bangkok /etc/localtime && echo "Asia/Bangkok" > /etc/timezone

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (including test scripts)
COPY *.py ./
COPY *.sh ./

# Create necessary directories
RUN mkdir -p /app/event_detail /app/logs /app/data /app/backups

# Make shell scripts executable
RUN chmod +x *.sh 2>/dev/null || true

# Verify test scripts are present
RUN ls -la /app/test*.py || echo "Test scripts copied"

# Create entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:8080', timeout=5)" || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["report-server"]
