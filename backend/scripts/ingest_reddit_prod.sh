#!/bin/bash
# Run Reddit ingestion locally but connected to production database via SSH tunnel
# This avoids Reddit's IP blocking of cloud servers while using prod data
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

SERVER="root@49.13.204.222"
LOCAL_PORT=54321

# Parse arguments (pass through to Python script)
PYTHON_ARGS="$@"
if [ -z "$PYTHON_ARGS" ]; then
    PYTHON_ARGS="--limit 50"
fi

echo "=== Reddit Ingestion (Local -> Prod DB) ==="
echo "Args: $PYTHON_ARGS"

# Get the Docker container's IP for the database
echo "Getting DB container IP..."
DB_CONTAINER_IP=$(ssh $SERVER "docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' vibe-hub-db")
echo "DB container IP: $DB_CONTAINER_IP"

# Check if tunnel already exists on this port
if lsof -i :$LOCAL_PORT >/dev/null 2>&1; then
    echo "Port $LOCAL_PORT already in use, killing existing process..."
    kill $(lsof -t -i :$LOCAL_PORT) 2>/dev/null || true
    sleep 1
fi

# Start SSH tunnel to prod database (through Docker container IP)
echo "Starting SSH tunnel to prod database..."
ssh -f -N -L $LOCAL_PORT:$DB_CONTAINER_IP:5432 $SERVER
TUNNEL_PID=$(lsof -t -i :$LOCAL_PORT 2>/dev/null || echo "")
echo "SSH tunnel established (PID: $TUNNEL_PID)"

# Cleanup function
cleanup() {
    if [ -n "$TUNNEL_PID" ]; then
        echo "Closing SSH tunnel..."
        kill $TUNNEL_PID 2>/dev/null || true
    fi
}
trap cleanup EXIT

# Get prod database credentials from .env.production
if [ -f "$BACKEND_DIR/../.env.production" ]; then
    # Extract Postgres credentials
    POSTGRES_USER=$(grep "^POSTGRES_USER=" "$BACKEND_DIR/../.env.production" | cut -d'=' -f2-)
    POSTGRES_PASSWORD=$(grep "^POSTGRES_PASSWORD=" "$BACKEND_DIR/../.env.production" | cut -d'=' -f2-)
    POSTGRES_DB=$(grep "^POSTGRES_DB=" "$BACKEND_DIR/../.env.production" | cut -d'=' -f2-)
    
    # Build DATABASE_URL with tunneled connection
    LOCAL_DB_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:${LOCAL_PORT}/${POSTGRES_DB}"
    
    echo "Using tunneled connection to prod database"
else
    echo "ERROR: .env.production not found"
    exit 1
fi

# Also get other required env vars from .env.production
export AGENT_API_KEY=$(grep "^AGENT_API_KEY=" "$BACKEND_DIR/../.env.production" | cut -d'=' -f2-)
export AGENT_API_BASE=$(grep "^AGENT_API_BASE=" "$BACKEND_DIR/../.env.production" | cut -d'=' -f2-)
export AGENT_MODEL=$(grep "^AGENT_MODEL=" "$BACKEND_DIR/../.env.production" | cut -d'=' -f2- || echo "gpt-4o")
export S3_BUCKET=$(grep "^S3_BUCKET=" "$BACKEND_DIR/../.env.production" | cut -d'=' -f2-)
export AWS_ACCESS_KEY_ID=$(grep "^AWS_ACCESS_KEY_ID=" "$BACKEND_DIR/../.env.production" | cut -d'=' -f2-)
export AWS_SECRET_ACCESS_KEY=$(grep "^AWS_SECRET_ACCESS_KEY=" "$BACKEND_DIR/../.env.production" | cut -d'=' -f2-)
export AWS_REGION=$(grep "^AWS_REGION=" "$BACKEND_DIR/../.env.production" | cut -d'=' -f2- || echo "us-east-1")
export LOGFIRE_TOKEN=$(grep "^LOGFIRE_TOKEN=" "$BACKEND_DIR/../.env.production" | cut -d'=' -f2-)

# Set the tunneled database URL
export DATABASE_URL="$LOCAL_DB_URL"

echo ""
echo "Running ingestion script..."
echo ""

# Run the ingestion script
cd "$BACKEND_DIR"
uv run python scripts/ingest_reddit_posts.py $PYTHON_ARGS

echo ""
echo "=== Ingestion complete ==="
