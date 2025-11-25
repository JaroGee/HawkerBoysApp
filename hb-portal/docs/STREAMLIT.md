# Streamlit edition of Hawker Boys Portal

This repository now ships a Streamlit clone of the Next.js portal for rapid demos and data exploration.

## Run locally
1. `cd hb-portal`
2. `python -m venv .venv && source .venv/bin/activate` (or `.\.venv\Scripts\activate` on Windows)
3. `pip install -r requirements-streamlit.txt`
4. `streamlit run streamlit_app.py`

## Notes
- State lives in `streamlit_data.json` in the repo root. Delete it or hit **Reset sample data** in the sidebar to reseed.
- Uploaded files land in `streamlit_uploads/`. The metadata shows up in the **Uploads** page.
- One-page layout: dashboard shows announcements first, then progress/quests/badges, shifts/compliance/support, and recent feedback. A separate Uploads page handles documents.
- Sidebar has a lightweight role switcher (default USER). Switch to ADMIN to unlock counts and CSV export (demo admin: `admin@hawkerboys.com`).
