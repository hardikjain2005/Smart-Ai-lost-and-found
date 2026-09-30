# CampusFind AI — Smart Campus Lost & Found

Monorepo: `frontend/` (React + TS + Vite + Tailwind), `backend/` (FastAPI + SQLAlchemy + PostgreSQL),
`ml/` (matching/embeddings, not yet implemented), `database/` (Postgres init scripts),
`tests/` (backend tests), `docs/`.

## What works (MVP)

Register/login (JWT + bcrypt) · report lost/found items with image upload · search & filter ·
AI match suggestions (TF-IDF + weighted attributes, shown as a *Match Score*) · ownership claims ·
admin review of reports and claims · mark returned · item timeline · admin statistics.

Private identifying details are only returned to the reporter and admins. Admin APIs are enforced on
the backend (`require_admin`), not just by frontend routing.

## Demo accounts (seed data, development only)

Seeded on first start when `SEED_DEMO_DATA=true` and the database is empty. Passwords come from
`SEED_ADMIN_PASSWORD` / `SEED_DEMO_PASSWORD` in your `.env`.

| Role | Email |
| --- | --- |
| ADMIN | admin@campusfind.edu |
| STUDENT | aarav@campusfind.edu, diya@campusfind.edu, rohan@campusfind.edu |
| FACULTY | meera@campusfind.edu |

Demo flow: log in as Aarav → open "Black Dell Laptop" (lost) → see the ~89% match → open the found
report → "This is my item" → log in as admin → `/admin` → approve claim → Mark Returned.

## Quick start (Docker)

```bash
cp .env.example .env
# Edit .env: set POSTGRES_PASSWORD, put the same password in DATABASE_URL, and set JWT_SECRET_KEY
# (python3 -c "import secrets; print(secrets.token_urlsafe(48))")
docker compose up --build
```

- Frontend: http://localhost:5173
- API: http://localhost:8000/api/health (docs at http://localhost:8000/docs)

`VITE_API_BASE_URL` is baked into the frontend at build time; rebuild the frontend image after changing it.

## Local development (no Docker for app code)

```bash
docker compose up -d db            # Postgres only
# backend (set DATABASE_URL host to localhost in .env)
cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
PYTHONPATH=../ml .venv/bin/uvicorn app.main:app --reload
# frontend
cd frontend && npm install && npm run dev
```

## Tests

```bash
backend/.venv/bin/pytest tests        # backend
cd frontend && npm test               # frontend
```

## Configuration

All settings come from environment variables; see `.env.example`. `.env` is git-ignored.
Uploaded images are stored in `UPLOAD_DIR` (a Docker volume in compose). Tables are created on
startup (no migrations yet). The frontend reads `VITE_API_BASE_URL` from the repo-root `.env`.
Errors from the API use the envelope `{"error": {"code", "message", "details"}}`; the frontend
normalises them in `src/services/errors.ts`, and `ErrorBoundary` catches render errors.

<p align="center">
  <img src="./readmebg.png" alt="Lost & Found" width="100%">
</p>
