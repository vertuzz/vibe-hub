# Backend Implementation TODOs

Based on the review of `README.md`, `prd.md`, and the codebase, here are the missing pieces required before switching to frontend development.

## 🚨 Critical: Infrastructure & Database
- [x] **Fix Alembic Migrations config**: `migrations/env.py` has `target_metadata = None`. It needs to point to `app.models.Base.metadata` so tables are actually created in Postgres.
- [x] **Dockerize Database**: Create a `docker-compose.yml` file to spin up a local PostgreSQL instance for testing (matching production database type).
- [x] **Verify Migrations**: Run `alembic revision --autogenerate` and `alembic upgrade head` against the local Postgres container.

## 🔐 Authentication (PRD: "Auth: google + github")
- [ ] **Add OAuth2 Dependencies**: `httpx` and `authlib` (or manual implementation).
- [ ] **Social Login Endpoints**:
    - [ ] `POST /auth/google` (Exchange code for token).
    - [ ] `POST /auth/github` (Exchange code for token).
- [ ] **Update User Model Usage**: Ensure `google_id` and `github_id` are correctly populated during social login.

## 🖼️ Media Handling
- [ ] **Image Upload Strategy**:
    - Current implementation expects `image_url` string.
    - [ ] **Decision**: Do we implement a backend upload endpoint (e.g., `POST /upload` -> S3/Local) or does Frontend upload directly to a cloud provider (Cloudinary/S3 Presigned URLs)?
    - [ ] **Implement**: If backend handling is chosen, add `app/routers/media.py`.


## 🚀 Deployment Prep
- [ ] **Seed Data**: Create a script to seed initial Tools (Cursor, Replit, v0) and Tags so the DB isn't empty on first run.
