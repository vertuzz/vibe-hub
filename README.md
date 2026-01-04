# Show Your App

A launchpad and showcase platform for AI-generated software ("Vibe Coding"). Creators can ship apps, get feedback, and manage their projects.

**Live:** https://show-your.app

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, Vite, Tailwind CSS v4, TypeScript |
| Backend | FastAPI, SQLAlchemy, Alembic, Python 3.13 |
| Database | PostgreSQL 16 |
| Storage | Hetzner Object Storage (S3-compatible) |
| Auth | Google OAuth, GitHub OAuth, API Keys |
| Deployment | Docker Compose, nginx, Let's Encrypt |

## Local Development

### Prerequisites
- Python 3.13+ with [uv](https://github.com/astral-sh/uv)
- Node.js 20+ with pnpm
- PostgreSQL 16 (or use Docker)
- Docker & Docker Compose (optional)

### Quick Start

```bash
# Start everything with Docker
./dev.sh

# Or run services separately:

# Backend
cd backend
cp .env.example .env  # Configure your .env
uv run uvicorn app.main:app --reload

# Frontend
cd frontend
cp .env.example .env  # Configure your .env
pnpm install
pnpm dev
```

### URLs
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Environment Variables

### Backend (`backend/.env`)
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/dreamware
SECRET_KEY=your-secret-key-change-in-production

# S3 Storage (optional)
S3_BUCKET=vibehub
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_ENDPOINT_URL=https://nbg1.your-objectstorage.com
AWS_REGION=nbg1

# OAuth (optional)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
```

### Frontend (`frontend/.env`)
```bash
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=...
VITE_GITHUB_CLIENT_ID=...
```

## Testing

```bash
cd backend
uv run pytest
uv run pytest --cov=app  # With coverage
```

## Deployment

### Initial Setup (Fresh Server)
```bash
# Configure production environment
cp .env.production.example .env.production
# Edit .env.production with production values

# Deploy to server (installs Docker, sets up SSL, starts services)
./deploy.sh
```

### Redeploy on Code Changes
```bash
./redeploy.sh              # Full rebuild
./redeploy.sh -b           # Backend only
./redeploy.sh -f           # Frontend only
./redeploy.sh -q           # Quick restart (no rebuild)
./redeploy.sh -c           # Rebuild without Docker cache (env/config changes)
./redeploy.sh -f -c        # Frontend only, no cache
```

### Server Commands
```bash
ssh root@49.13.204.222
cd /opt/vibe_hub

docker compose -f docker-compose.prod.yml ps              # Status
docker compose -f docker-compose.prod.yml logs -f         # Logs
docker compose -f docker-compose.prod.yml logs backend    # Backend logs
docker compose -f docker-compose.prod.yml restart         # Restart all
docker compose -f docker-compose.prod.yml down            # Stop all
docker compose -f docker-compose.prod.yml up -d --build   # Rebuild & start
```

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── database.py       # DB connection
│   │   ├── routers/          # API endpoints
│   │   ├── schemas/          # Pydantic schemas
│   │   └── core/             # Config, security
│   ├── migrations/           # Alembic migrations
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── pages/            # Route pages
│   │   ├── components/       # React components
│   │   ├── contexts/         # Auth, cache contexts
│   │   └── lib/              # API, utils, hooks
│   └── public/
├── nginx/                    # Production nginx config
├── docker-compose.yml        # Local development
├── docker-compose.prod.yml   # Production
├── deploy.sh                 # Initial server setup
└── redeploy.sh              # Code updates
```

## API Authentication

Users can authenticate via:
1. **OAuth** — Google or GitHub login
2. **API Key** — Header `X-API-Key: <key>` (find in profile settings)

## Database Migrations

```bash
cd backend

# Create migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback
uv run alembic downgrade -1
```

## License

MIT
