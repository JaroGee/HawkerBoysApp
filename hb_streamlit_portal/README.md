# HB Portal

A trainee-facing Streamlit app for Hawker Boys to track missions, progress, and support needs. The default storage is in-memory for development and can be replaced with a persistent backend later.

## Runbook

1. Create a virtual environment:

```zsh
[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```zsh
pip install -r requirements.txt
```

3. Launch Streamlit:

```zsh
cd hb_streamlit_portal
streamlit run app.py
```

Environment variables:

- `ADMIN_PASSWORD`: shared admin password for the simple admin view (default `change-me`).
- `DATABASE_URL`: reserved for future Postgres backend.
- `HB_LOGO_PATH`: path to logo asset (defaults to `static/assets/images/hb_logo.png`).

Authentication is intentionally minimal for internal testing only. Do not deploy without a proper auth solution.

## Storage

The `InMemoryStorage` backend seeds demo data and persists only for the running process. The storage interface in `core/storage.py` is designed to be swapped for a database-backed repository later.

## Testing

Run the test suite from the project root:

```zsh
cd hb_streamlit_portal
pytest
```

## Project structure

- `app.py` – Streamlit entrypoint with mode selection and session state setup.
- `pages/` – Streamlit multipage views for home, missions, progress, support, and admin.
- `core/` – Data models, storage abstraction, and gamification helpers.
- `config/` – Settings loaded from environment.
- `assets/` – Styling and placeholder logo assets.
- `tests/` – Pytest-based unit and smoke tests.

## Notes

- Language and visuals aim to respect adult learners with encouraging, neutral tone.
- No public leaderboards or shaming mechanics are included.
- Badges and XP logic are intentionally simple and can be extended.
