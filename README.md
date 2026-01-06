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

## App Submission Agent

An AI-powered agent that automatically creates app listings on Show Your App by visiting URLs, taking screenshots, and generating compelling descriptions.

### Setup

```bash
cd submit_app_agent
uv sync  # Install dependencies
```

### Configuration

Set your API key (find it in your Show Your App profile settings):

```bash
export SHOWAPP_API_KEY="your-api-key-here"
```

Or the agent will use the default key from `config.py`.

### Usage

```bash
cd submit_app_agent

# Submit an app from a URL
uv run python -m showapp "add this app https://example.com/my-app"

# With verbose output (shows tool calls)
uv run python -m showapp -v "submit https://cool-demo.vercel.app"

# Test bootstrap only (shows your user info, available tools/tags, existing apps)
uv run python -m showapp --bootstrap-only
```

### What It Does

1. **Navigates** to the app URL using Playwright browser
2. **Explores** the app and takes screenshots
3. **Creates** a listing with title, description, tags, and tools
4. **Uploads** screenshots to S3 and attaches them to the app

### Available Tools

| Tool | Description |
|------|-------------|
| `get_current_user` | Get authenticated user info |
| `list_my_apps` | List your existing apps |
| `get_tools` | Get available "How It Was Built" tools |
| `get_tags` | Get available "What It's About" tags |
| `create_app` | Create a new app listing |
| `update_app` | Update an existing app |
| `get_presigned_url` | Get S3 upload URL |
| `upload_file_to_s3` | Upload screenshot to S3 |
| `attach_media_to_app` | Attach media to app |

### Running Tests

```bash
cd submit_app_agent
uv run pytest tests/ -v
```
