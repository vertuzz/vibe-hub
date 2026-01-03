#!/bin/bash
set -e

# Wait for database to be ready
echo "Waiting for database..."
while ! python -c "
import asyncio
import asyncpg
import os

async def check():
    try:
        url = os.environ.get('DATABASE_URL', '')
        # Parse connection string
        conn = await asyncpg.connect(url)
        await conn.close()
        return True
    except Exception as e:
        return False

exit(0 if asyncio.run(check()) else 1)
" 2>/dev/null; do
    echo "Database not ready, waiting..."
    sleep 2
done

echo "Database is ready!"

# Run migrations
echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec "$@"
