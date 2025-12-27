# VibeHub Backend

The backend for VibeHub, a visual-first aggregation platform for AI-generated software concepts ("Vibe Coding").

## Tech Stack
- **Python**: 3.13
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
- **Database**: PostgreSQL (Production), SQLite (Development & Testing)
- **Security**: [JWT](https://pyjwt.readthedocs.io/) (via `python-jose`) & `bcrypt`
- **Package Manager**: [uv](https://github.com/astral-sh/uv)
- **Testing**: `pytest`

## Core Features
- **Auth**: Secure JWT-based authentication (Stable User IDs).
- **Vibes**: Full lifecycle of AI app concepts (Create, Feed, Fork, Status).
- **Social**: Comments, Vibe Checks (0-100% reviews), and Likes.
- **Collaboration**: Implementation submissions and Official status linking.
- **Social Graph**: User following and real-time-like notifications.
- **Content Management**: Dynamic Tools and Tags for masonry feed filtering.

## Getting Started

1. **Install uv**: Follow instructions at [astral.sh/uv](https://astral.sh/uv).
2. **Setup Project**:
   ```bash
   uv sync
   ```
3. **Environment**:
   Set `SECRET_KEY` for JWT signing. Default dev key is used if unset.
4. **Run Server**:
   ```bash
   uv run uvicorn app.main:app --reload
   ```
5. **Interactive Docs**:
   Navigate to [http://localhost:8000/docs](http://localhost:8000/docs) for the Swagger UI.

## Testing
Comprehensive integration tests cover 100% of the happy paths using an in-memory SQLite database.

```bash
uv run pytest tests/ -v
```

## Project Structure
- `app/`: Main application code.
  - `core/`: Security and JWT configuration.
  - `routers/`: 12 domain-specific API routers.
  - `schemas/`: Pydantic models for request/response validation.
  - `models.py`: SQLAlchemy database models.
  - `main.py`: App entry point and router registration.
  - `database.py`: DB engine and session management.
- `tests/`: Integration tests using `TestClient`.
- `migrations/`: Alembic database migration scripts.
- `pyproject.toml`: Project metadata and dependencies.

