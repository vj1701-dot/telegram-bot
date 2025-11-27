# Multi-stage Dockerfile for Telegram Audio Bot
# Stage 1: Base image with dependencies
FROM python:3.9-slim as base

# Install FFmpeg and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Stage 2: Bot container
FROM base as bot

WORKDIR /app

# Copy application code
COPY bot /app/bot
COPY shared /app/shared

# Create data directory
RUN mkdir -p /app/data/logs /app/data/audio /app/data/.audio_cache

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run bot
CMD ["python", "-m", "bot.main"]

# Stage 3: Dashboard container
FROM base as dashboard

WORKDIR /app

# Copy application code
COPY dashboard /app/dashboard
COPY bot /app/bot
COPY shared /app/shared

# Copy Streamlit config
COPY dashboard/.streamlit /app/dashboard/.streamlit

# Create data directory
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose Streamlit port
EXPOSE 8501

# Run dashboard
CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
