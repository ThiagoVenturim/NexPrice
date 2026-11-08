"""Decide whether a current price is a real discount or a fake one.

The trick NexPrice fights: a store raises the price shortly before a sale and then
"discounts" it back to the usual level. The advertised drop looks big against the
inflated recent price, but the current price is not actually below the historical
norm. We judge the current price against the median of the period BEFORE the recent
run-up, not against the inflated peak.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from datetime import timedelta

from nexprice.models import PriceObservation


@dataclass(frozen=True)
class DiscountVerdict:
    current: float
    baseline_median: float
    window_low: float
    window_high: float
    pct_vs_baseline: float  # positive = cheaper than baseline
    pct_vs_recent_high: float  # what the store can advertise
    is_real_discount: bool
    is_suspicious: bool
    reason: str  # pt-BR, human readable
    sample_size: int


def assess_discount(
    history: list[PriceObservation],
    current_price: float | None = None,
    *,
    window_days: int = 90,
    spike_days: int = 14,
    min_drop: float = 0.05,
) -> DiscountVerdict:
    """Classify the current price against the product's own price history.

    - window_days: how far back to look.
    - spike_days: prices newer than this are the possibly-inflated "recent" period;
      the baseline is everything older, within the window.
    - min_drop: fraction below baseline that counts as a real discount (0.05 = 5%).
    """
    if not history:
        raise ValueError("history is empty")

    ordered = sorted(history, key=lambda o: o.at)
    latest = ordered[-1]
    current = latest.price if current_price is None else current_price

    window_start = latest.at - timedelta(days=window_days)
    window = [o for o in ordered if o.at >= window_start]
    prices = [o.price for o in window]

    window_low = min(prices)
    window_high = max(prices)

    spike_start = latest.at - timedelta(days=spike_days)
    baseline = [o.price for o in window if o.at < spike_start]
    baseline_median = statistics.median(baseline) if baseline else statistics.median(prices)

    pct_vs_baseline = (baseline_median - current) / baseline_median if baseline_median else 0.0
    pct_vs_recent_high = (window_high - current) / window_high if window_high else 0.0

    is_real_discount = current <= baseline_median * (1 - min_drop)
    # Big advertised drop versus the recent peak, but the price is essentially back to
    # (or above) the historical baseline: the discount is not real.
    is_suspicious = pct_vs_recent_high >= min_drop and current >= baseline_median * (1 - 0.01)

    if is_real_discount:
        reason = (
            f"Desconto real: {current:.2f} esta {pct_vs_baseline * 100:.0f}% abaixo da "
            f"mediana historica ({baseline_median:.2f})."
        )
    elif is_suspicious:
        reason = (
            f"Desconto suspeito: a loja anuncia {pct_vs_recent_high * 100:.0f}% de queda "
            f"sobre o pico recente ({window_high:.2f}), mas {current:.2f} esta na faixa da "
            f"mediana historica ({baseline_median:.2f}). Provavel preco inflado antes da promocao."
        )
    else:
        reason = (
            f"Sem desconto relevante: {current:.2f} esta proximo da mediana historica "
            f"({baseline_median:.2f})."
        )

    return DiscountVerdict(
        current=current,
        baseline_median=baseline_median,
        window_low=window_low,
        window_high=window_high,
        pct_vs_baseline=pct_vs_baseline,
        pct_vs_recent_high=pct_vs_recent_high,
        is_real_discount=is_real_discount,
        is_suspicious=is_suspicious,
        reason=reason,
        sample_size=len(window),
    )
