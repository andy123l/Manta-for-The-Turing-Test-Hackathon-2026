"""
Momentum Trading Strategy for Manta.
Rides price trends based on momentum indicators.
"""

from typing import Dict
from loguru import logger

from .base import BaseStrategy, Signal


class MomentumStrategy(BaseStrategy):
    """
    Momentum Trading Strategy.

    Uses:
    - RSI (Relative Strength Index)
    - MACD (Moving Average Convergence Divergence)
    - Moving Averages crossover
    """

    def __init__(
        self,
        rsi_period: int = 14,
        rsi_overbought: float = 70,
        rsi_oversold: float = 30,
        fast_ma: int = 12,
        slow_ma: int = 26
    ):
        """Initialize momentum strategy."""
        super().__init__("Momentum")

        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        self.fast_ma = fast_ma
        self.slow_ma = slow_ma

    def generate_signal(self, data: Dict) -> Signal:
        """Generate momentum-based signal."""
        indicators = data.get("indicators", {})
        price_data = data.get("price", {})

        rsi = indicators.get("rsi", 50)
        macd = indicators.get("macd", 0)
        macd_signal = indicators.get("macd_signal", 0)
        sma_fast = indicators.get("sma_fast", 0)
        sma_slow = indicators.get("sma_slow", 0)
        current_price = price_data.get("last_price", 0)

        score = 0
        reasons = []

        # RSI signal
        if rsi < self.rsi_oversold:
            score += 0.4
            reasons.append(f"RSI oversold ({rsi:.1f})")
        elif rsi > self.rsi_overbought:
            score -= 0.4
            reasons.append(f"RSI overbought ({rsi:.1f})")

        # MACD signal
        if macd > macd_signal:
            score += 0.3
            reasons.append("MACD bullish crossover")
        elif macd < macd_signal:
            score -= 0.3
            reasons.append("MACD bearish crossover")

        # Moving average crossover
        if sma_fast > sma_slow:
            score += 0.3
            reasons.append("Fast MA above Slow MA")
        elif sma_fast < sma_slow:
            score -= 0.3
            reasons.append("Fast MA below Slow MA")

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
            reason="; ".join(reasons) if reasons else "No clear momentum signal",
            stop_loss=self.calculate_stop_loss(current_price, action),
            take_profit=self.calculate_take_profit(current_price, action)
        )

    def calculate_stop_loss(self, entry_price: float, direction: str) -> float:
        """Calculate stop loss (2% default)."""
        if direction == "buy":
            return entry_price * 0.98
        else:
            return entry_price * 1.02

    def calculate_take_profit(self, entry_price: float, direction: str) -> float:
        """Calculate take profit (4% default)."""
        if direction == "buy":
            return entry_price * 1.04
        else:
            return entry_price * 0.96
