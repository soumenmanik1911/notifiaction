from datetime import datetime
import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core import focus_db
from core.focus import auto_mode, gate


def _tmp_db(tmp_path):
    focus_db.DB_PATH = str(tmp_path / "focus.db")


def test_study_family_high_shows(tmp_path):
    _tmp_db(tmp_path)
    assert gate("Study", "family", 0.8) == "SHOW"


def test_study_shopping_low_silences(tmp_path):
    _tmp_db(tmp_path)
    assert gate("Study", "shopping", 0.1) == "SILENCE"


def test_study_work_medium_holds(tmp_path):
    _tmp_db(tmp_path)
    assert gate("Study", "work", 0.4) == "HOLD"


def test_sleep_family_high_shows(tmp_path):
    _tmp_db(tmp_path)
    assert gate("Sleep", "family", 0.9) == "SHOW"


def test_sleep_shopping_low_silences(tmp_path):
    _tmp_db(tmp_path)
    assert gate("Sleep", "shopping", 0.1) == "SILENCE"


def test_commute_work_medium_shows(tmp_path):
    _tmp_db(tmp_path)
    assert gate("Commute", "work", 0.4) == "SHOW"


def test_commute_family_high_shows(tmp_path):
    _tmp_db(tmp_path)
    assert gate("Commute", "family", 0.9) == "SHOW"


def test_urgent_high_always_shows(tmp_path):
    _tmp_db(tmp_path)
    assert gate("Sleep", "work", 0.7) == "SHOW"


def test_shopping_in_study_silences(tmp_path):
    _tmp_db(tmp_path)
    assert gate("Study", "shopping", 0.2) == "SILENCE"


def test_shopping_high_in_study_silences(tmp_path):
    _tmp_db(tmp_path)
    assert gate("Study", "shopping", 0.9) == "SILENCE"


def test_auto_mode_times(tmp_path):
    _tmp_db(tmp_path)
    assert auto_mode(datetime(2026, 11, 12, 2, 0, 0)) == "Sleep"
    assert auto_mode(datetime(2026, 11, 12, 10, 0, 0)) == "Study"
    assert auto_mode(datetime(2026, 11, 12, 20, 0, 0)) == "Off"


def test_always_allow_override_from_signals(tmp_path):
    _tmp_db(tmp_path)
    assert gate("Study", "work", 0.4, source="Slack") == "HOLD"
    for _ in range(3):
        hid = focus_db.add_held("Slack", "msg", "work", 0.4, created_at=datetime.now(), mode="Study")
        focus_db.record_release_signal(hid)
    assert focus_db.is_always_allowed("Slack", "work", "Study")
    assert gate("Study", "work", 0.4, source="Slack") == "SHOW"


def test_rule_keyed_by_category(tmp_path):
    _tmp_db(tmp_path)
    for _ in range(3):
        hid = focus_db.add_held("Slack", "msg", "work", 0.4, mode="Study")
        focus_db.record_release_signal(hid)
    assert gate("Study", "work", 0.4, source="Slack") == "SHOW"
    assert gate("Study", "social", 0.4, source="Slack") == "HOLD"


def test_remove_rule_restores_normal_gating(tmp_path):
    _tmp_db(tmp_path)
    for _ in range(3):
        hid = focus_db.add_held("Slack", "msg", "work", 0.4, mode="Study")
        focus_db.record_release_signal(hid)
    assert gate("Study", "work", 0.4, source="Slack") == "SHOW"
    rules = focus_db.list_allow_rules()
    assert rules
    focus_db.remove_allow_rule(rules[0]["id"])
    assert not focus_db.is_always_allowed("Slack", "work", "Study")
    assert gate("Study", "work", 0.4, source="Slack") == "HOLD"
