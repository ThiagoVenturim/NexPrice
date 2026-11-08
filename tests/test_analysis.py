"""Tests for the fake-discount detector."""

from datetime import datetime, timedelta

from nexprice.analysis import assess_discount
from nexprice.models import PriceObservation


def _series(prices, start_days_ago=120):
    now = datetime(2026, 11, 8, 12, 0, 0)
    obs = []
    n = len(prices)
    for i, p in enumerate(prices):
        days_ago = start_days_ago - int(start_days_ago * i / max(n - 1, 1))
        obs.append(PriceObservation("p1", "loja", float(p), now - timedelta(days=days_ago)))
    return obs


def test_real_discount():
    # Long stable at 100, then drops to 80 now.
    hist = _series([100] * 10 + [80])
    v = assess_discount(hist)
    assert v.is_real_discount
    assert not v.is_suspicious
    assert v.pct_vs_baseline > 0.1


def test_fake_black_friday_discount():
    # Stable at 100, inflated to 140 right before the sale, "discounted" back to 100.
    now = datetime(2026, 11, 8, 12, 0, 0)
    hist = [PriceObservation("p1", "loja", 100.0, now - timedelta(days=d)) for d in (90, 75, 60, 45, 30)]
    hist += [PriceObservation("p1", "loja", 140.0, now - timedelta(days=5))]
    hist += [PriceObservation("p1", "loja", 100.0, now)]
    v = assess_discount(hist)
    assert v.is_suspicious
    assert not v.is_real_discount


def test_no_discount():
    hist = _series([100] * 10 + [99])
    v = assess_discount(hist)
    assert not v.is_real_discount
    assert not v.is_suspicious


def test_empty_history_raises():
    try:
        assess_discount([])
    except ValueError:
        return
    raise AssertionError("expected ValueError")
