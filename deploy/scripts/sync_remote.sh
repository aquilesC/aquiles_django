#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <ssh-host> <remote-environment> [local-environment] [remote-project-path]" >&2
  echo "Example: $0 deploy@vps staging dev /srv/aquiles" >&2
  exit 1
fi

SSH_HOST="$1"
REMOTE_ENV="$2"
LOCAL_ENV="${3:-$REMOTE_ENV}"
REMOTE_ROOT="${4:-/srv/aquiles}"

PROJECT_ROOT=$(cd -- "$(dirname "$0")/../.." && pwd)
LOCAL_DATA_ROOT="${PROJECT_ROOT}/deploy/.data/${LOCAL_ENV}"
REMOTE_DATA_ROOT="${REMOTE_ROOT}/deploy/.data/${REMOTE_ENV}"

mkdir -p "${LOCAL_DATA_ROOT}/backups" "${LOCAL_DATA_ROOT}/media"

rsync -avz --delete "${SSH_HOST}:${REMOTE_DATA_ROOT}/backups/" "${LOCAL_DATA_ROOT}/backups/"
rsync -avz --delete "${SSH_HOST}:${REMOTE_DATA_ROOT}/media/" "${LOCAL_DATA_ROOT}/media/"

echo "Sync complete. Latest backups and media are available in deploy/.data/${LOCAL_ENV}."
