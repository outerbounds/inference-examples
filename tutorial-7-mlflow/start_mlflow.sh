#!/bin/bash
# Start MLflow Tracking Server with PostgreSQL backend from Outerbounds persistence.
set -e

echo "============================================================"
echo "Starting MLflow Tracking Server"
echo "============================================================"

# Build the PostgreSQL URI from Metaflow credentials
BACKEND_STORE_URI=$(python generate_pg_url.py)

echo "Backend store: PostgreSQL (localhost:5432)"
echo "Default artifact root: ./mlartifacts"
echo "Host: 0.0.0.0"
echo "Port: 5000"
echo "============================================================"

mlflow server \
    --backend-store-uri "$BACKEND_STORE_URI" \
    --default-artifact-root ./mlartifacts \
    --host 0.0.0.0 \
    --port 5000
