import os
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core import db, focus_db
from core.chat import generate_reply, daytime_label


def _use_tmp_db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "chat.db")
    monkeypatch.setattr(db, "DB_PATH", db_path)
    monkeypatch.setattr(focus_db, "DB_PATH", db_path)
    return db_path


def test_daytime_labels():
    assert daytime_label(9) == "morning"
    assert daytime_label(14) == "afternoon"
    assert daytime_label(19) == "evening"
    assert daytime_label(2) == "night"
    assert daytime_label(23) == "night"
    assert daytime_label(5) == "morning"
    assert daytime_label(12) == "afternoon"
    assert daytime_label(17) == "evening"
    assert daytime_label(4) == "night"


def test_reply_empty_db_includes_daytime_without_crashing(tmp_path, monkeypatch):
    _use_tmp_db(tmp_path, monkeypatch)
    now = datetime(2026, 11, 12, 10, 30, 0)
    for msg in ("hello", "help", "how many pending notifications", "anything at all"):
        reply = generate_reply(msg, now=now)
        assert isinstance(reply, str) and len(reply) > 0
        assert "morning" in reply.lower() and "hour 10" in reply


def test_reply_populated_data(tmp_path, monkeypatch):
    _use_tmp_db(tmp_path, monkeypatch)
    c = db.conn()
    now = datetime(2026, 11, 12, 10, 30, 0)
    nid = db.add_notification(c, "Slack", "lead", "send the report", "work", 0.8, ts=now)
    db.add_notification(c, "Gmail", "mom", "call me when free", "family", 0.2, ts=now)
    db.add_reminder(c, nid, now, "follow up on report")
    db.log_choice(c, nid, "work", "Slack", now, 0.8, "1h", "user")
    c.close()
    focus_db.add_held("Slack", "held msg", "work", 0.4, created_at=now, mode="Study")

    r1 = generate_reply("how many pending notifications", now=now)
    assert "morning" in r1.lower()
    assert "2 pending" in r1
    assert "work" in r1 and "family" in r1

    r2 = generate_reply("any reminders due now", now=now)
    assert "reminder" in r2.lower()
    assert "due now" in r2.lower()

    r3 = generate_reply("what held items do i have", now=now)
    assert "1 held" in r3

    r4 = generate_reply("what is focus mode", now=now)
    assert "Study" in r4

    r5 = generate_reply("how many choices have i learned from", now=now)
    assert "1" in r5

    r6 = generate_reply("tell me about work", now=now)
    assert "work:" in r6.lower() or "work " in r6.lower()

    r7 = generate_reply("goodbye", now=now)
    assert "morning" in r7.lower()
