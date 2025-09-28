#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT=$(cd -- "$(dirname "$0")/../.." && pwd)
COMPOSE_BASE="${PROJECT_ROOT}/deploy/docker-compose.base.yml"
COMPOSE_DEV="${PROJECT_ROOT}/deploy/docker-compose.dev.yml"
ENV_FILE="${PROJECT_ROOT}/deploy/env/.env.dev"

if [[ ! -f "${ENV_FILE}" ]]; then
  cp "${PROJECT_ROOT}/deploy/env/.env.dev.example" "${ENV_FILE}"
  echo "Created ${ENV_FILE}. Update credentials before continuing."
fi

mkdir -p "${PROJECT_ROOT}/deploy/.data/dev/backups"

DOCKER_COMPOSE="docker compose -f ${COMPOSE_BASE} -f ${COMPOSE_DEV}"

${DOCKER_COMPOSE} build
${DOCKER_COMPOSE} up -d

${DOCKER_COMPOSE} logs -f
