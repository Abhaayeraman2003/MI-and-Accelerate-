"""
Database layer for the DGW MI & Accelerate app.

Uses SQLite now (a single local file, zero setup) so the proof-of-concept works
immediately AND already persists data in a real database.

MIGRATION LATER (MTN cloud):
  Only this file changes. Replace the sqlite3 connection with SQL Server / Postgres
  (e.g. via SQLAlchemy). The rest of the app calls save_submission() / load_submissions()
  and never touches SQL directly, so nothing else has to change.
"""

import os
import json
import sqlite3
import datetime

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "submissions.db"))


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the submissions table if it does not exist."""
    with _conn() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS submissions (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                opco          TEXT NOT NULL,
                year          TEXT NOT NULL,
                month         TEXT NOT NULL,
                reporting_month TEXT,
                submitted_by  TEXT,
                email         TEXT,
                items_updated INTEGER,
                submitted_at  TEXT,
                payload_json  TEXT NOT NULL
            )
            """
        )
        # one latest submission per OpCo+year+month (re-submitting overwrites)
        c.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS ux_opco_period "
            "ON submissions(opco, year, month)"
        )


def save_submission(payload, year, month):
    """Insert or replace the submission for this OpCo + period. Returns row id."""
    init_db()
    now = datetime.datetime.utcnow().isoformat() + "Z"
    with _conn() as c:
        cur = c.execute("SELECT id FROM submissions WHERE opco=? AND year=? AND month=?",
                        (payload.get("opco"), year, month))
        existing = cur.fetchone()
        data = (
            payload.get("opco"), year, month, payload.get("reportingMonth"),
            payload.get("submittedBy"), payload.get("email"),
            int(payload.get("itemsUpdated") or 0), payload.get("submittedAt", now),
            json.dumps(payload, ensure_ascii=False),
        )
        if existing:
            c.execute(
                "UPDATE submissions SET reporting_month=?, submitted_by=?, email=?, "
                "items_updated=?, submitted_at=?, payload_json=? WHERE id=?",
                (data[3], data[4], data[5], data[6], data[7], data[8], existing["id"]),
            )
            return existing["id"]
        cur = c.execute(
            "INSERT INTO submissions "
            "(opco, year, month, reporting_month, submitted_by, email, items_updated, submitted_at, payload_json) "
            "VALUES (?,?,?,?,?,?,?,?,?)", data,
        )
        return cur.lastrowid


def load_submissions(year=None, month=None):
    """Return a list of submission payload dicts, optionally filtered by period."""
    init_db()
    q = "SELECT payload_json FROM submissions"
    args = []
    conds = []
    if year:
        conds.append("year=?"); args.append(year)
    if month:
        conds.append("month=?"); args.append(month)
    if conds:
        q += " WHERE " + " AND ".join(conds)
    q += " ORDER BY opco"
    with _conn() as c:
        rows = c.execute(q, args).fetchall()
    out = []
    for r in rows:
        try:
            out.append(json.loads(r["payload_json"]))
        except Exception:
            pass
    return out


def list_meta():
    """Lightweight listing for an admin/status view."""
    init_db()
    with _conn() as c:
        rows = c.execute(
            "SELECT opco, year, month, submitted_by, items_updated, submitted_at "
            "FROM submissions ORDER BY submitted_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def periods_available():
    init_db()
    with _conn() as c:
        rows = c.execute("SELECT DISTINCT year, month FROM submissions").fetchall()
    return [(r["year"], r["month"]) for r in rows]
