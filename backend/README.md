# VibeHub Backend

## Tech Stack
- **Python**: 3.13
- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Database Migrations**: Alembic
- **Package Manager**: [uv](https://github.com/astral-sh/uv)

## Getting Started

1. Install `uv` if you haven't already.
2. Install dependencies:
   ```bash
   uv sync
   ```
3. Run the development server:
   ```bash
   uv run uvicorn app.main:app --reload
   ```

## Project Structure
- `app/`: Main application code.
  - `main.py`: FastAPI application entry point.
  - `models.py`: SQLAlchemy database models.
- `migrations/`: Alembic database migration scripts.
- `pyproject.toml`: Project metadata and dependencies.
