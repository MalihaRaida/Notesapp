# agents.md

## Project Overview
This repository contains a simple full-stack Notes application.

- **Backend**: Python, FastAPI, PostgreSQL
- **Frontend**: React (Vite)
- **Architecture**: REST API with a local PostgreSQL database
- **Environment**: Local development only (no Docker)

The backend exposes CRUD endpoints for notes, and the frontend consumes them.

---

## Agent Expectations

AI agents working on this repository should:

- Follow the existing project structure
- Avoid introducing Docker or container-based workflows
- Use modern FastAPI patterns (lifespan instead of deprecated `on_event`)
- Keep changes minimal, readable, and well-scoped
- Prefer clarity over abstraction

---

## Backend Guidelines

### Tech Stack
- Python 3.11+
- FastAPI
- psycopg (v3)
- PostgreSQL
- Pydantic v2

### Database
- Connection string is provided via `DATABASE_URL` in `.env`
- PostgreSQL runs locally on `localhost:5432`
- Schema initialization is handled automatically on app startup

⚠️ **Do not hardcode credentials or connection info**

---

### Database Initialization
- All schema definitions live in `app/schema.py`
- Schema is executed during application startup using FastAPI `lifespan`
- Agents should NOT embed `CREATE TABLE` statements inside route handlers

If schema changes are required:
- Modify `schema.py`
- Ensure changes are idempotent (`IF NOT EXISTS` where applicable)

---

### Backend Code Rules
- Use `get_conn()` from `db.py` for all database access
- Use context managers for DB connections and cursors
- Do not keep global DB connections
- Do not introduce ORMs unless explicitly requested

---

### API Design Rules
- RESTful endpoints only
- Use appropriate HTTP status codes
- Return JSON responses
- Avoid breaking existing endpoints unless instructed

Existing routes include:
- `GET /notes`
- `POST /notes`
- `PATCH /notes/{id}`
- `DELETE /notes/{id}`
- `GET /health`

---

## Frontend Guidelines

### Tech Stack
- React
- Vite
- Plain CSS / inline styles (no UI frameworks unless requested)

### Rules
- Keep frontend simple and readable
- Use `fetch()` for API calls
- API base URL is `http://localhost:8000`
- No authentication unless explicitly added

Agents should avoid:
- Adding Redux / complex state management
- Adding unnecessary dependencies
- Over-engineering UI components

---

## Environment Configuration

Required `.env` variables (backend):

```
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/<db>
CORS_ORIGINS=http://localhost:5173

AUTO_INIT_DB=true
```

Agents must NOT commit `.env` files.

---

## Testing

- No automated test framework is currently configured
- Agents may add tests using unittest framework only if explicitly requested 
- Any added tests must not modify production data

---

## What NOT to Do

Agents should NOT:
- Add Dockerfiles or docker-compose
- Change database credentials or ports
- Replace psycopg with any other package
- Introduce authentication unless requested
- Refactor large sections without instruction

---

## Common Tasks Agents May Perform

Allowed:
- Add new note fields
- Improve validation
- Add search/filtering
- Improve frontend UX
- Fix bugs
- Add comments or documentation

Ask before:
- Introducing migrations
- Adding auth/user accounts
- Changing database schema significantly

---

## Agent Output Expectations

When making changes:
- Explain what was changed and why
- Keep diffs small
- Ensure the app still runs locally
- Prefer incremental improvements

