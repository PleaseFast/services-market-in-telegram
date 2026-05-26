FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install the backend package first (provides app.*)
COPY backend /app/backend
RUN pip install --upgrade pip && pip install -e /app/backend

# Then bots — installed as aiogram deps only; the `bots` package is reachable via PYTHONPATH=/app
COPY bots /app/bots
RUN pip install aiogram>=3.10

ENV PYTHONPATH=/app:/app/backend
WORKDIR /app/bots
