import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.categorize import CATEGORIES
from core import samples


def test_samples_count_and_fields():
    assert len(samples.SAMPLES) >= 120
    for s in samples.SAMPLES:
        for k in ("message", "app", "sender", "category", "urgency"):
            assert k in s
            assert str(s[k]).strip() != ""


def test_every_category_at_least_ten():
    for c in CATEGORIES:
        count = sum(1 for s in samples.SAMPLES if s["category"] == c)
        assert count >= 10


def test_no_repeats_until_exhausted():
    samples._bags.clear()
    samples._last.clear()
    pool = list(samples.SAMPLES)
    seen = set()
    last = None
    for _ in range(len(pool)):
        s = samples.next_sample(None, last)
        assert id(s) not in seen
        seen.add(id(s))
        last = s


def test_never_same_twice_in_row():
    samples._bags.clear()
    samples._last.clear()
    last = None
    for _ in range(len(samples.SAMPLES) * 2):
        s = samples.next_sample(None, last)
        if last is not None:
            assert s is not last
        last = s


def test_category_filter_only_returns_category():
    samples._bags.clear()
    samples._last.clear()
    for c in CATEGORIES:
        last = None
        for _ in range(30):
            s = samples.next_sample(c, last)
            assert s["category"] == c
            last = s
