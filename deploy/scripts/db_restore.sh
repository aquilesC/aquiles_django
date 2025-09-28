#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <environment> <backup-file>" >&2
  echo "Example: $0 dev deploy/.data/dev/backups/aquiles_dev_20240101_120000.sql.gz" >&2
  exit 1
fi

ENVIRONMENT="$1"
BACKUP_FILE="$2"

if [[ ! -f "${BACKUP_FILE}" ]]; then
  echo "Backup file not found: ${BACKUP_FILE}" >&2
  exit 1
fi

PROJECT_ROOT=$(cd -- "$(dirname "$0")/../.." && pwd)
COMPOSE_BASE="${PROJECT_ROOT}/deploy/docker-compose.base.yml"
COMPOSE_ENV="${PROJECT_ROOT}/deploy/docker-compose.${ENVIRONMENT}.yml"
COMPOSE_CMD=(docker compose -f "${COMPOSE_BASE}" -f "${COMPOSE_ENV}")

if [[ ! -f "${COMPOSE_ENV}" ]]; then
  echo "Compose override not found: ${COMPOSE_ENV}" >&2
  exit 1
fi

DB_NAME=$("${COMPOSE_CMD[@]}" exec -T db printenv POSTGRES_DB | tr -d '\r')
DB_USER=$("${COMPOSE_CMD[@]}" exec -T db printenv POSTGRES_USER | tr -d '\r')

read -rp "This will overwrite the ${DB_NAME} database in ${ENVIRONMENT}. Continue? [y/N] " confirm
if [[ "${confirm}" != "y" && "${confirm}" != "Y" ]]; then
  echo "Restore aborted"
  exit 0
fi

echo "Restoring ${BACKUP_FILE} into ${DB_NAME}" >&2
if [[ "${BACKUP_FILE}" == *.gz ]]; then
  gunzip -c "${BACKUP_FILE}" | "${COMPOSE_CMD[@]}" exec -T db psql -U "${DB_USER}" "${DB_NAME}"
else
  "${COMPOSE_CMD[@]}" exec -T db psql -U "${DB_USER}" "${DB_NAME}" < "${BACKUP_FILE}"
fi

echo "Restore complete"
