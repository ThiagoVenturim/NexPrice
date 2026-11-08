"""NexPrice: track prices across sites and expose fake discounts through real price history."""

from nexprice.analysis import DiscountVerdict, assess_discount
from nexprice.models import Offer, PriceObservation, Product

__all__ = ["Offer", "PriceObservation", "Product", "DiscountVerdict", "assess_discount"]
