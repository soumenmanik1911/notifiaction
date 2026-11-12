"""Focus mode engine: gate notifications between classifier and recommender."""

import logging
from datetime import datetime

from core import focus_db


MODES = {
    "Off": {"categories": None, "urgencies": None},
    "Study": {"categories": {"family", "education", "college"}, "urgencies": {"High"}},
    "Sleep": {"categories": {"family"}, "urgencies": {"High"}},
    "Commute": {"categories": {"family", "work"}, "urgencies": {"High", "Medium"}},
}


def _urgency_level(urgency):
    if urgency >= 0.6:
        return "High"
    if urgency >= 0.3:
        return "Medium"
    return "Low"


def gate(mode, category, urgency, source=None):
    """Return SHOW, HOLD, or SILENCE for a notification."""
    cat = (category or "").lower()
    if source is not None and mode != "Off":
        try:
            if focus_db.is_always_allowed(source, cat, mode):
                return "SHOW"
        except Exception as e:
            logging.warning("focus always-allow check failed: %s", e)
    if mode == "Off":
        return "SHOW"
    level = _urgency_level(urgency)
    allowed = MODES.get(mode, MODES["Off"])
    allowed_cats = allowed["categories"]
    allowed_levels = allowed["urgencies"]
    cat_ok = allowed_cats is None or cat in allowed_cats
    urg_ok = allowed_levels is None or level in allowed_levels
    if cat_ok and urg_ok:
        return "SHOW"
    if cat == "shopping":
        return "SILENCE"
    if level == "High":
        return "SHOW"
    return "HOLD"


def auto_mode(now=None):
    """Return mode name from time of day."""
    current = now or datetime.now()
    hour = current.hour
    if hour >= 23 or hour < 6:
        return "Sleep"
    if 9 <= hour < 16:
        return "Study"
    return "Off"
