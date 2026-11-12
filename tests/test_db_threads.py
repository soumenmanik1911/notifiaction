import os
import sys
import threading

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core import db, focus_db


def test_db_operations_from_thread(tmp_path, monkeypatch):
    db_path = str(tmp_path / "thread.db")
    monkeypatch.setattr(db, "DB_PATH", db_path)
    monkeypatch.setattr(focus_db, "DB_PATH", db_path)
    c = db.conn(db_path)
    errors = []

    def worker():
        try:
            nid = db.add_notification(c, "Slack", "Tester", "hello from thread", "work", 0.5)
            hid = focus_db.add_held("Slack", "held from thread", "work", 0.4, mode="Study")
            worker.result = (nid, hid)
        except Exception as e:
            errors.append(e)

    t = threading.Thread(target=worker)
    t.start()
    t.join()

    assert not errors
    nid, hid = worker.result
    row = c.execute("SELECT id, text FROM notifications WHERE id=?", (nid,)).fetchone()
    assert row is not None and row["text"] == "hello from thread"
    held = focus_db.get_held(hid)
    assert held is not None and held["text"] == "held from thread"
    c.close()
