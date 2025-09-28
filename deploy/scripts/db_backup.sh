#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <environment>" >&2
  echo "Examples: $0 dev | $0 staging | $0 prod" >&2
  exit 1
fi

ENVIRONMENT="$1"
PROJECT_ROOT=$(cd -- "$(dirname "$0")/../.." && pwd)
COMPOSE_BASE="${PROJECT_ROOT}/deploy/docker-compose.base.yml"
COMPOSE_ENV="${PROJECT_ROOT}/deploy/docker-compose.${ENVIRONMENT}.yml"
BACKUP_DIR="${PROJECT_ROOT}/deploy/.data/${ENVIRONMENT}/backups"

mkdir -p "${BACKUP_DIR}"

if [[ ! -f "${COMPOSE_ENV}" ]]; then
  echo "Compose override not found: ${COMPOSE_ENV}" >&2
  exit 1
fi

COMPOSE_CMD=(docker compose -f "${COMPOSE_BASE}" -f "${COMPOSE_ENV}")

DB_NAME=$("${COMPOSE_CMD[@]}" exec -T db printenv POSTGRES_DB | tr -d '\r')
DB_USER=$("${COMPOSE_CMD[@]}" exec -T db printenv POSTGRES_USER | tr -d '\r')

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql.gz"

echo "Creating backup ${OUTPUT_FILE}"
"${COMPOSE_CMD[@]}" exec -T db pg_dump -U "${DB_USER}" "${DB_NAME}" | gzip > "${OUTPUT_FILE}"

echo "Backup complete: ${OUTPUT_FILE}"
