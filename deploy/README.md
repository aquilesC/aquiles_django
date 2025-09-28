# Deployment and environment operations

This directory contains the infrastructure as code required to run the project
consistently across development, staging, and production. The stack is based on
Docker, PostgreSQL, and Nginx, with optional Redis support.

## Directory overview

| Path | Purpose |
| --- | --- |
| `docker-compose.base.yml` | Shared compose definition for all environments. |
| `docker-compose.<env>.yml` | Environment-specific overrides (`dev`, `staging`, `prod`). |
| `docker/app/` | Dockerfile and entrypoint for the Django application image. |
| `docker/nginx/` | Reverse proxy configuration shared by all environments. |
| `env/` | Example `.env` files documenting required settings. Copy per environment. |
| `.data/` | Host bind mounts for media, static assets, and backups per environment. |
| `scripts/` | Helper scripts for common workflows (bootstrap, backup, restore, sync). |

## Environment variables

1. Copy the example files to concrete `.env` files and edit the secrets:

```bash
cp deploy/env/.env.dev.example deploy/env/.env.dev
cp deploy/env/.env.staging.example deploy/env/.env.staging
cp deploy/env/.env.prod.example deploy/env/.env.prod
```

2. Review `deploy/env/.env.base` for shared defaults. Override values in the
environment-specific files as needed.

## Local development

```bash
./deploy/scripts/bootstrap_dev.sh
```

The script builds the containers, ensures an `.env.dev` exists, and tails logs.
Hot reloading works by bind-mounting the repository into the `web` container.
Static files are rebuilt during the Docker image build; run `npm run watch:css`
locally for faster Tailwind feedback if desired.

To stop the stack:

```bash
docker compose -f deploy/docker-compose.base.yml -f deploy/docker-compose.dev.yml down
```

## Staging

1. Provision a droplet with Docker installed and clone the repository to a
   location such as `/srv/aquiles`.
2. Copy `deploy/env/.env.staging.example` to `.env.staging` and fill the
   secrets.
3. Start the stack:

```bash
docker compose \
  -f deploy/docker-compose.base.yml \
  -f deploy/docker-compose.staging.yml \
  up -d --build
```

Backups, collected static files, and media live under
`deploy/.data/staging/`. These directories are bind-mounted so they can be
archived or synchronised easily.

## Production

The production workflow mirrors staging. After staging validation passes, deploy
with the production overrides and environment file:

```bash
docker compose \
  -f deploy/docker-compose.base.yml \
  -f deploy/docker-compose.prod.yml \
  up -d --build
```

TLS termination is handled by the Nginx container; obtain certificates with your
preferred ACME client (for example, `certbot`) and mount them into the
container. The configuration leaves room to expand to a CDN later—static and
media assets are served via Nginx from bind-mounted directories.

## Database operations

Create a backup (writes to `deploy/.data/<env>/backups`):

```bash
./deploy/scripts/db_backup.sh <env>
```

Restore a backup:

```bash
./deploy/scripts/db_restore.sh <env> path/to/backup.sql.gz
```

Synchronise remote backups and media to your local machine:

```bash
./deploy/scripts/sync_remote.sh deploy@vps staging dev /srv/aquiles
```

This enables the “masked staging → local” workflow: refresh staging from
production, then pull the staging assets locally to reproduce issues.

## Health checks

The application exposes `GET /healthz/`, which probes database and cache
connectivity. Nginx forwards `/healthz/` to Django and returns a JSON payload,
allowing load balancers or uptime monitors to guard deployments.

## Release checklist

1. Run the local quality gates (migrations, visual inspection, tests).
2. Build and push a tagged image or use `docker compose ... up --build` on
   staging.
3. Execute database migrations on staging, run smoke tests, and validate the
   component gallery.
4. Promote the release to production using the same compose files.
5. Monitor `/healthz/`, logs, and alerts for at least 15 minutes.
6. Keep a rolling set of backups (`db_backup.sh`) and verify restores monthly.

Document any environment-specific overrides in `deploy/env/` so the three
workflows stay in sync.
