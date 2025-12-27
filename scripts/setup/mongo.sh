#!/usr/bin/env bash

# --- Config projet ---
PROJECT_DIR="$HOME/cryptobot"

# --- Config Mongo ---
MONGO_CONTAINER="my_mongo"
MONGO_USER="datascientest"
MONGO_PWD="dst123"
MONGO_AUTH_DB="admin"
MONGO_DB="cryptobot"

cd "$PROJECT_DIR" || exit 1

# Start Docker
docker compose up -d

# Open mongosh (interactive)
docker exec -it "$MONGO_CONTAINER" mongosh \
  -u "$MONGO_USER" -p "$MONGO_PWD" \
  --authenticationDatabase "$MONGO_AUTH_DB" \
  "$MONGO_DB"
