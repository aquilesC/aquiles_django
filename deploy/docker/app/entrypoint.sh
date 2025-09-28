#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

: "${RUN_MIGRATIONS:=true}"
: "${COLLECT_STATIC:=true}"
: "${APP_COMMAND:=gunicorn aquiles_site.wsgi:application --bind 0.0.0.0:8000}"
: "${RUN_CHECKS:=true}"

if [ "$RUN_CHECKS" = "true" ]; then
  python manage.py check
fi

if [ "$RUN_MIGRATIONS" = "true" ]; then
  python manage.py migrate --noinput
fi

if [ "$COLLECT_STATIC" = "true" ]; then
  python manage.py collectstatic --noinput
fi

exec ${APP_COMMAND}
