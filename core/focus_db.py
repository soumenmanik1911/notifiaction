"""SQLite storage for focus mode held items and session logs."""

import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "assistant.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS focus_held(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT,
  text TEXT,
  category TEXT,
  urgency REAL,
  created_at TEXT,
  status TEXT DEFAULT 'held',
  mode TEXT
);
CREATE TABLE IF NOT EXISTS focus_sessions(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  mode TEXT,
  started_at TEXT,
  ended_at TEXT,
  shown_count INTEGER,
  held_count INTEGER,
  silenced_count INTEGER
);
CREATE TABLE IF NOT EXISTS focus_signals(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT,
  category TEXT,
  mode TEXT,
  signaled_at TEXT
);
CREATE TABLE IF NOT EXISTS focus_allow_rules(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT,
  category TEXT,
  mode TEXT,
  created_at TEXT,
  UNIQUE(source, category, mode)
);
"""


def conn(path=None):
    path = path or DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    c = sqlite3.connect(path, check_same_thread=False, timeout=10)
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    _ensure_columns(c)
    return c


def _ensure_columns(c):
    cols = [r["name"] for r in c.execute("PRAGMA table_info(focus_held)").fetchall()]
    if "mode" not in cols:
        c.execute("ALTER TABLE focus_held ADD COLUMN mode TEXT")
        c.commit()
    _migrate_signals(c)
    _migrate_allow_rules(c)


def _migrate_signals(c):
    cols = [r["name"] for r in c.execute("PRAGMA table_info(focus_signals)").fetchall()]
    if "category" in cols:
        return
    c.execute("ALTER TABLE focus_signals RENAME TO focus_signals_old")
    c.execute(
        """CREATE TABLE focus_signals(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          source TEXT,
          category TEXT,
          mode TEXT,
          signaled_at TEXT
        )"""
    )
    c.execute(
        "INSERT INTO focus_signals(id,source,category,mode,signaled_at) SELECT id,source,'',mode,signaled_at FROM focus_signals_old"
    )
    c.execute("DROP TABLE focus_signals_old")
    c.commit()


def _migrate_allow_rules(c):
    cols = [r["name"] for r in c.execute("PRAGMA table_info(focus_allow_rules)").fetchall()]
    if "category" in cols:
        return
    c.execute("ALTER TABLE focus_allow_rules RENAME TO focus_allow_rules_old")
    c.execute(
        """CREATE TABLE focus_allow_rules(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          source TEXT,
          category TEXT,
          mode TEXT,
          created_at TEXT,
          UNIQUE(source, category, mode)
        )"""
    )
    c.execute(
        "INSERT OR IGNORE INTO focus_allow_rules(id,source,category,mode,created_at) SELECT id,source,'',mode,created_at FROM focus_allow_rules_old"
    )
    c.execute("DROP TABLE focus_allow_rules_old")
    c.commit()


def add_held(source, text, category, urgency, created_at=None, mode=None):
    c = conn()
    if created_at is None:
        ts = datetime.now().isoformat(timespec="seconds")
    elif isinstance(created_at, datetime):
        ts = created_at.isoformat(timespec="seconds")
    else:
        ts = str(created_at)
    cur = c.execute(
        "INSERT INTO focus_held(source,text,category,urgency,created_at,status,mode) VALUES(?,?,?,?,?,?,?)",
        (source, text, category, urgency, ts, "held", mode),
    )
    c.commit()
    item_id = cur.lastrowid
    c.close()
    return item_id


def get_held(item_id):
    c = conn()
    row = c.execute("SELECT * FROM focus_held WHERE id=?", (item_id,)).fetchone()
    c.close()
    return row


def list_held(status="held"):
    c = conn()
    if status is None:
        rows = c.execute("SELECT * FROM focus_held ORDER BY created_at DESC").fetchall()
    else:
        rows = c.execute(
            "SELECT * FROM focus_held WHERE status=? ORDER BY created_at DESC", (status,)
        ).fetchall()
    c.close()
    return rows


def release_all():
    c = conn()
    cur = c.execute("UPDATE focus_held SET status='released' WHERE status='held'")
    c.commit()
    count = cur.rowcount
    c.close()
    return count


def set_held_status(item_id, status):
    c = conn()
    c.execute("UPDATE focus_held SET status=? WHERE id=?", (status, item_id))
    c.commit()
    c.close()


def log_session(mode, started_at, ended_at, shown_count, held_count, silenced_count):
    c = conn()
    cur = c.execute(
        "INSERT INTO focus_sessions(mode,started_at,ended_at,shown_count,held_count,silenced_count) VALUES(?,?,?,?,?,?)",
        (mode, started_at, ended_at, shown_count, held_count, silenced_count),
    )
    c.commit()
    session_id = cur.lastrowid
    c.close()
    return session_id


def record_release_signal(item_id):
    """Count release signal; add always-allow after 3 signals."""
    c = conn()
    row = c.execute("SELECT source, category, mode FROM focus_held WHERE id=?", (item_id,)).fetchone()
    if row is None:
        c.close()
        return False
    source = row["source"] or ""
    category = (row["category"] or "").lower()
    mode = row["mode"] or "Off"
    now = datetime.now()
    c.execute(
        "INSERT INTO focus_signals(source,category,mode,signaled_at) VALUES(?,?,?,?)",
        (source, category, mode, now.isoformat(timespec="seconds")),
    )
    count = c.execute(
        "SELECT COUNT(*) AS n FROM focus_signals WHERE source=? AND category=? AND mode=?",
        (source, category, mode),
    ).fetchone()["n"]
    added = False
    if count >= 3:
        c.execute(
            "INSERT OR IGNORE INTO focus_allow_rules(source,category,mode,created_at) VALUES(?,?,?,?)",
            (source, category, mode, now.isoformat(timespec="seconds")),
        )
        added = c.execute(
            "SELECT 1 FROM focus_allow_rules WHERE source=? AND category=? AND mode=?",
            (source, category, mode),
        ).fetchone() is not None
    c.commit()
    c.close()
    return added


def is_always_allowed(source, category, mode):
    c = conn()
    row = c.execute(
        "SELECT 1 FROM focus_allow_rules WHERE source=? AND category=? AND mode=?",
        (source or "", (category or "").lower(), mode or ""),
    ).fetchone()
    c.close()
    return row is not None


def list_allow_rules():
    c = conn()
    rows = c.execute(
        "SELECT id, source, category, mode, created_at FROM focus_allow_rules ORDER BY created_at DESC"
    ).fetchall()
    c.close()
    return rows


def remove_allow_rule(rule_id):
    c = conn()
    c.execute("DELETE FROM focus_allow_rules WHERE id=?", (rule_id,))
    c.commit()
    c.close()
