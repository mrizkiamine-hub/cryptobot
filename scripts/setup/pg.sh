#!/usr/bin/env bash

# --- Config projet ---
PROJECT_DIR="$HOME/cryptobot"

# --- Config Postgres ---
PG_CONTAINER="pg_container"
PG_USER="daniel"
PG_DB="dst_db"

cd "$PROJECT_DIR" || exit 1

# Start Docker
docker compose up -d

# Open interactive psql
docker exec -it "$PG_CONTAINER" psql -U "$PG_USER" -d "$PG_DB"
