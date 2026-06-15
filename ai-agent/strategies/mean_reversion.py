"""
Mean Reversion Trading Strategy for Manta.
Trades price reversions to the mean.
"""

from typing import Dict
from loguru import logger

from .base import BaseStrategy, Signal


class MeanReversionStrategy(BaseStrategy):
    """
    Mean Reversion Strategy.

    Uses:
    - Bollinger Bands
    - RSI
    - Standard deviation
    """

    def __init__(
        self,
        bb_period: int = 20,
        bb_std: float = 2.0,
        rsi_period: int = 14
    ):
        """Initialize mean reversion strategy."""
        super().__init__("MeanReversion")

        self.bb_period = bb_period
        self.bb_std = bb_std
        self.rsi_period = rsi_period

    def generate_signal(self, data: Dict) -> Signal:
        """Generate mean reversion signal."""
        indicators = data.get("indicators", {})
        price_data = data.get("price", {})

        current_price = price_data.get("last_price", 0)
        bb_upper = indicators.get("bb_upper", current_price * 1.02)
        bb_lower = indicators.get("bb_lower", current_price * 0.98)
        bb_middle = indicators.get("bb_middle", current_price)
        rsi = indicators.get("rsi", 50)

        score = 0
        reasons = []

        # Bollinger Band signal
        if current_price < bb_lower:
            # Price below lower band - buy signal
            distance = (bb_lower - current_price) / (bb_upper - bb_lower)
            score += 0.4 + (distance * 0.2)
            reasons.append("Price below lower Bollinger Band")
        elif current_price > bb_upper:
            # Price above upper band - sell signal
            distance = (current_price - bb_upper) / (bb_upper - bb_lower)
            score -= 0.4 + (distance * 0.2)
            reasons.append("Price above upper Bollinger Band")

        # RSI confirmation
        if rsi < 30:
            score += 0.3
            reasons.append(f"RSI oversold ({rsi:.1f})")
        elif rsi > 70:
            score -= 0.3
            reasons.append(f"RSI overbought ({rsi:.1f})")

        # Distance from mean
        if bb_middle > 0:
            distance_from_mean = (current_price - bb_middle) / bb_middle
            if abs(distance_from_mean) > 0.02:
                score -= distance_from_mean * 2
                reasons.append(f"Distance from mean: {distance_from_mean:.2%}")

        # Determine action
        if score > 0.5:
            action = "buy"
            confidence = min(score, 1.0)
        elif score < -0.5:
            action = "sell"
            confidence = min(abs(score), 1.0)
        else:
            action = "hold"
            confidence = 1 - abs(score)

        return Signal(
            action=action,
            confidence=confidence,
            reason="; ".join(reasons) if reasons else "No clear reversion signal",
            stop_loss=self.calculate_stop_loss(current_price, action),
            take_profit=self.calculate_take_profit(current_price, action)
        )

    def calculate_stop_loss(self, entry_price: float, direction: str) -> float:
        """Calculate stop loss (2.5% default)."""
        if direction == "buy":
            return entry_price * 0.975
        else:
            return entry_price * 1.025

    def calculate_take_profit(self, entry_price: float, direction: str) -> float:
        """Calculate take profit (3% default)."""
        if direction == "buy":
            return entry_price * 1.03
        else:
            return entry_price * 0.97
