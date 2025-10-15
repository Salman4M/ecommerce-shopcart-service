#!/usr/bin/env sh
set -e

echo "Starting FastAPI entrypoint..."

if [ "$CLOUD_SQL_CONNECTION_NAME" ]; then
  POSTGRES_HOST="/cloudsql/$CLOUD_SQL_CONNECTION_NAME"
else
  POSTGRES_HOST="${DB_HOST:-db}"
fi

# Wait for Postgres
for i in $(seq 1 30); do
  if pg_isready -h "$POSTGRES_HOST" -p "${DB_PORT:-5432}" -U "${DB_USER}" -d "${DB_NAME}"; then
    echo "Postgres is ready!"
    break
  fi
  echo "Waiting for Postgres... ($i/30)"
  sleep 2
done

# Run migrations
alembic upgrade head || { echo "Migration failed!"; exit 1; }

# Start FastAPI
if [ "$ENV" = "development" ]; then
  echo "Running in development mode with reload..."
  exec uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8080} --reload
else
  echo "Running in production mode..."
  exec uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8080} --proxy-headers
fi