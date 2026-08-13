# DGW MI & Accelerate — working proof-of-concept

A single, self-contained app that runs **right now** on your laptop, shows **everything**,
and already stores data in a **real database** (SQLite) — so moving to MTN cloud later is easy.

## ▶️ Run it (2 steps)

**Windows:** double-click **`run_windows.bat`**
**Mac/Linux:** run **`./run_mac_linux.sh`**

…or manually:
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
Then open **http://localhost:8501**.

## What it does

- **📝 Submit update** — pick an OpCo + month, edit what changed, hit Submit.
  The submission is written to a local database file **`submissions.db`**, and you get an
  Excel copy to download.
- **📊 Dashboard** — reads the database and shows:
  - a **tracker** (e.g. “3 / 14 submissions received” + who's still missing),
  - metric cards, **RAG donut**, **Accelerate progress bars** (how far each initiative is),
  - **MI maturity** gauge + bars,
  - a **“Download combined report” Excel** for all OpCos.

Re-submitting the same OpCo for the same month **updates** its record (no duplicates).

## Files

| File | Purpose |
|------|---------|
| `streamlit_app.py` | App entry point (Submit + view switch) |
| `dashboard.py` | Dashboard (reads DB, shows everything) |
| `db.py` | **Database layer (SQLite now)** — the only file to change for MTN cloud |
| `common.py` | Shared helpers + parsing (impacts, RAG, maturity) |
| `excel_builder.py` | Styled Excel export |
| `data.json` | OpCo initiatives (sample: Ghana, Zambia, Cameroon, Rwanda) |

## ⚠️ Before showing it around

Replace the **sample `data.json`** (4 OpCos) with your full corrected **14-OpCo `data.json`**.
Just drop your file in next to `streamlit_app.py` — nothing else changes.

## 🔜 Moving to MTN cloud + a bigger database (later)

The app never touches SQL directly — it only calls `db.save_submission()` and
`db.load_submissions()`. To move to SQL Server / Postgres:

1. Open **`db.py`**.
2. Replace the `sqlite3` connection with your cloud DB (e.g. via SQLAlchemy / pyodbc).
3. Keep the same two functions. **No other file changes.**

The `submissions` table schema (opco, year, month, submitted_by, email, payload_json, …)
maps straight onto any relational database.
