import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core import db, focus_db
from ui.components import focus_table_rows, get_home_stats


def _use_tmp_db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "home.db")
    monkeypatch.setattr(db, "DB_PATH", db_path)
    monkeypatch.setattr(focus_db, "DB_PATH", db_path)
    return db_path


def test_get_home_stats_empty(tmp_path, monkeypatch):
    _use_tmp_db(tmp_path, monkeypatch)
    stats = get_home_stats()
    assert stats == {
        "notifications_handled": 0,
        "held_during_focus": 0,
        "learned_rules": 0,
        "choices_learned": 0,
    }


def test_get_home_stats_populated(tmp_path, monkeypatch):
    db_path = _use_tmp_db(tmp_path, monkeypatch)
    c = db.conn(db_path)
    nid = db.add_notification(c, "Slack", "s", "msg1", "work", 0.5)
    db.log_choice(c, nid, "work", "Slack", __import__("datetime").datetime.now(), 0.5, "1h", "user")
    db.add_notification(c, "Gmail", "s", "msg2", "family", 0.2)
    c.close()
    focus_db.add_held("Slack", "held msg", "work", 0.4, mode="Study")
    # create allow rule
    hid1 = focus_db.add_held("A", "m", "work", 0.4, mode="Study")
    hid2 = focus_db.add_held("A", "m", "work", 0.4, mode="Study")
    hid3 = focus_db.add_held("A", "m", "work", 0.4, mode="Study")
    focus_db.record_release_signal(hid1)
    focus_db.record_release_signal(hid2)
    focus_db.record_release_signal(hid3)
    stats = get_home_stats()
    assert stats["notifications_handled"] == 2
    assert stats["held_during_focus"] == 4  # 1 + 3 held items (status held)
    assert stats["learned_rules"] == 1
    assert stats["choices_learned"] == 1


def test_focus_table_rows_structure():
    rows = focus_table_rows()
    assert len(rows) == 4
    modes = [r["mode"] for r in rows]
    assert modes == ["Off", "Study", "Sleep", "Commute"]
    for r in rows:
        assert set(r.keys()) == {"mode", "allows", "urgency", "note"}
        assert all(isinstance(r[k], str) and r[k] for k in r)
