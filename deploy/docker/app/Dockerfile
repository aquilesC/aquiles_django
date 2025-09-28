# syntax=docker/dockerfile:1.6

ARG PYTHON_VERSION=3.12-slim

FROM node:20-bullseye-slim AS node_builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --include=dev
COPY static ./static
RUN npm run build:css

FROM python:${PYTHON_VERSION} AS python_base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

COPY --from=node_builder /app/static/css/tailwind.css static/css/tailwind.css

COPY deploy/docker/app/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN useradd --create-home --shell /bin/bash django \
    && chown -R django:django /app

USER django

ENTRYPOINT ["/entrypoint.sh"]
