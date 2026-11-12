"""SQLite storage: notifications, user choices (training data), reminders."""
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "assistant.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS notifications(
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, app TEXT, sender TEXT,
  text TEXT, category TEXT, urgency REAL, status TEXT DEFAULT 'pending');
CREATE TABLE IF NOT EXISTS choices(
  id INTEGER PRIMARY KEY AUTOINCREMENT, notif_id INTEGER, ts TEXT,
  category TEXT, app TEXT, hour INTEGER, weekend INTEGER, urgency REAL,
  action TEXT, source TEXT);              -- source: 'user' or 'ai'
CREATE TABLE IF NOT EXISTS reminders(
  id INTEGER PRIMARY KEY AUTOINCREMENT, notif_id INTEGER, due_ts TEXT,
  text TEXT, done INTEGER DEFAULT 0);
"""


def conn(path=None):
    """Create a configured SQLite connection (caller must close)."""
    path = path or DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    c = sqlite3.connect(path, check_same_thread=False, timeout=10)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL;")
    c.execute("PRAGMA busy_timeout=5000;")
    c.executescript(SCHEMA)
    return c


@contextmanager
def get_conn(path=None):
    """Short-lived connection context manager."""
    c = conn(path)
    try:
        yield c
    finally:
        c.close()


def add_notification(app, sender, text, category, urgency, ts=None):
    ts = (ts or datetime.now()).isoformat(timespec="seconds")
    with get_conn() as c:
        cur = c.execute(
            "INSERT INTO notifications(ts,app,sender,text,category,urgency) VALUES(?,?,?,?,?,?)",
            (ts, app, sender, text, category, urgency),
        )
        c.commit()
        return cur.lastrowid


def pending():
    with get_conn() as c:
        return c.execute(
            "SELECT * FROM notifications WHERE status='pending' ORDER BY ts DESC"
        ).fetchall()


def set_status(nid, status):
    with get_conn() as c:
        c.execute("UPDATE notifications SET status=? WHERE id=?", (status, nid))
        c.commit()


def log_choice(notif_id, category, app, ts, urgency, action, source="user"):
    with get_conn() as c:
        c.execute(
            "INSERT INTO choices(notif_id,ts,category,app,hour,weekend,urgency,action,source) VALUES(?,?,?,?,?,?,?,?,?)",
            (
                notif_id,
                ts.isoformat(timespec="seconds"),
                category,
                app,
                ts.hour,
                int(ts.weekday() >= 5),
                urgency,
                action,
                source,
            ),
        )
        c.commit()


def add_reminder(notif_id, due, text):
    with get_conn() as c:
        c.execute(
            "INSERT INTO reminders(notif_id,due_ts,text) VALUES(?,?,?)",
            (notif_id, due.isoformat(timespec="seconds"), text),
        )
        c.commit()


def reminders(include_done=False):
    q = "SELECT * FROM reminders " + ("" if include_done else "WHERE done=0 ") + "ORDER BY due_ts"
    with get_conn() as c:
        return c.execute(q).fetchall()


def complete_reminder(rid):
    with get_conn() as c:
        c.execute("UPDATE reminders SET done=1 WHERE id=?", (rid,))
        c.commit()


def user_choices_df():
    import pandas as pd

    with get_conn() as c:
        return pd.read_sql_query("SELECT * FROM choices WHERE source='user'", c)


def reset():
    with get_conn() as c:
        for t in ("notifications", "choices", "reminders"):
            c.execute(f"DELETE FROM {t}")
        c.commit()
