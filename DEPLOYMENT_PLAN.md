## Deployment Plan: Render.com with Docker and Scheduled Jobs

### Overview
Deploy the AI news aggregator to Render.com with:
- PostgreSQL database (managed service)
- Docker container for the application
- Scheduled cron job to run `main.py` every 24 hours
- Environment variables configuration

### Architecture
```
Render Services:
├─ PostgreSQL Database (Managed Service)
├─ Web Service (Docker) - Optional for health checks
└─ Cron Job (Scheduled) - Runs main.py daily
```

Goal: Deploy the AI news aggregator on Render.com with a managed PostgreSQL database, Dockerized app, and a daily scheduled run of the pipeline.

### Phase 0 — Account Setup
1. Create a free Render.com account (sign up with GitHub or email).
2. Connect your GitHub repo to Render (authorize access to the repo).

### Phase 1 — Preparation
1. Confirm required env vars and secrets (e.g., `OPENAI_API_KEY`, `DATABASE_URL`, `GMAIL_USER`, `GMAIL_APP_PASSWORD`, `EMAIL_TO`).
2. Ensure `main.py` runs the full pipeline and exits cleanly (required for cron jobs).

### Phase 2 — Dockerization
1. Add a `Dockerfile` to build the app image from the repo.
2. Add `.dockerignore` to keep builds small and fast.
3. Confirm the container entrypoint can run `python -m app.services.daily_runner` (or `python main.py`).

### Phase 3 — Render Services
1. Create a **Render PostgreSQL** instance.
2. Create a **Render Cron Job** service:
   - Source: Git repo (Docker build from repo).
   - Command: `python -m app.services.daily_runner --hours 24 --limit 10`.
   - Schedule: daily cron (UTC).
3. Configure env vars for the cron job (including the internal `DATABASE_URL` from Render Postgres).
4. (Optional) Define a `render.yaml` in the repo root to:
   - Define PostgreSQL database service
   - Define scheduled cron job service
   - Configure environment variables
   - Set up health checks if needed

### Phase 4 — Initialization
1. Run one-off DB setup (e.g., `python -m app.database.create_tables`) as a Render one-off job or local script.
2. Trigger the cron job manually to verify end-to-end execution.

### Phase 5 — Operations
1. Check Render logs for each run and confirm email delivery.
2. Add alerting or a simple log-check if runs fail.

### Phase 6 — Additional Repo Updates (Optional)
1. Update database connection handling (if needed) to ensure `DATABASE_URL` is honored for Render.
2. Create a `requirements.txt` in repo root (export from `pyproject.toml`) if your Docker build prefers it.
3. Add an optional entrypoint script `scripts/run_daily.sh` to wrap cron execution with logging.
