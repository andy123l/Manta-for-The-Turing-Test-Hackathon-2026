"""
Macro-Driven Trading Strategy for Manta.
Core strategy that combines macro, sentiment, and technical analysis.
"""

from typing import Dict, Optional
from datetime import datetime

import pandas as pd
import numpy as np
from loguru import logger

from .base import BaseStrategy, Signal


class MacroDrivenStrategy(BaseStrategy):
    """
    Macro-Driven Trading Strategy.

    Combines:
    - Macroeconomic analysis (40% weight)
    - Market sentiment analysis (30% weight)
    - Technical analysis (30% weight)

    This strategy adjusts positions based on:
    - Economic cycle (inflationary, tightening, recessionary, recovery)
    - Market fear/greed
    - Price momentum and technical indicators
    """

    def __init__(
        self,
        macro_weight: float = 0.4,
        sentiment_weight: float = 0.3,
        technical_weight: float = 0.3,
        stop_loss_pct: float = 0.02,
        take_profit_pct: float = 0.04
    ):
        """
        Initialize macro-driven strategy.

        Args:
            macro_weight: Weight for macro signals (default: 0.4)
            sentiment_weight: Weight for sentiment signals (default: 0.3)
            technical_weight: Weight for technical signals (default: 0.3)
            stop_loss_pct: Stop loss percentage (default: 2%)
            take_profit_pct: Take profit percentage (default: 4%)
        """
        super().__init__("MacroDriven")

        # Signal weights
        self.macro_weight = macro_weight
        self.sentiment_weight = sentiment_weight
        self.technical_weight = technical_weight

        # Risk parameters
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct

        # Strategy parameters
        self.min_confidence = 0.6  # Minimum confidence to trade
        self.max_position_pct = 0.1  # Maximum 10% position

        logger.info(
            "Macro strategy initialized",
            weights={
                "macro": macro_weight,
                "sentiment": sentiment_weight,
                "technical": technical_weight
            }
        )

    def generate_signal(self, data: Dict) -> Signal:
        """
        Generate trading signal based on macro, sentiment, and technical data.

        Args:
            data: Dictionary containing:
                - macro: Macro sentiment data
                - sentiment: Market sentiment data
                - price: Current price data
                - indicators: Technical indicators

        Returns:
            Signal object with action and metadata
        """
        try:
            # Extract components
            macro_data = data.get("macro", {})
            sentiment_data = data.get("sentiment", {})
            price_data = data.get("price", {})
            indicators = data.get("indicators", {})

            # Generate individual signals
            macro_signal = self._generate_macro_signal(macro_data)
            sentiment_signal = self._generate_sentiment_signal(sentiment_data)
            technical_signal = self._generate_technical_signal(price_data, indicators)

            # Combine signals with weights
            combined_score = (
                macro_signal * self.macro_weight +
                sentiment_signal * self.sentiment_weight +
                technical_signal * self.technical_weight
            )

            # Determine action
            if combined_score > self.min_confidence:
                action = "buy"
                confidence = combined_score
                reason = f"Bullish: Macro={macro_signal:.2f}, Sent={sentiment_signal:.2f}, Tech={technical_signal:.2f}"
            elif combined_score < -self.min_confidence:
                action = "sell"
                confidence = abs(combined_score)
                reason = f"Bearish: Macro={macro_signal:.2f}, Sent={sentiment_signal:.2f}, Tech={technical_signal:.2f}"
            else:
                action = "hold"
                confidence = 1 - abs(combined_score)
                reason = f"Neutral: Combined score {combined_score:.2f} below threshold"

            # Get current price for SL/TP calculation
            current_price = price_data.get("last_price", 0)

            # Calculate stop loss and take profit
            stop_loss = self.calculate_stop_loss(current_price, action)
            take_profit = self.calculate_take_profit(current_price, action)

            signal = Signal(
                action=action,
                confidence=confidence,
                reason=reason,
                stop_loss=stop_loss,
                take_profit=take_profit
            )

            logger.info(
                "Signal generated",
                action=action,
                confidence=confidence,
                combined_score=combined_score
            )

            return signal

        except Exception as e:
            logger.error("Error generating signal", error=str(e))
            return Signal(action="hold", confidence=0, reason=f"Error: {str(e)}")

    def _generate_macro_signal(self, macro_data: Dict) -> float:
        """
        Generate signal from macroeconomic data.

        Args:
            macro_data: Macro sentiment data

        Returns:
            Signal score (-1 to 1)
        """
        if not macro_data:
            return 0.0

        # Get macro sentiment score
        score = macro_data.get("score", 0)

        # Get cycle information
        cycle = macro_data.get("cycle", "unknown")

        # Adjust based on cycle
        cycle_adjustments = {
            "recovery": 0.2,    # Bullish
            "inflationary": -0.1,
            "tightening": -0.2,
            "recessionary": -0.3
        }

        adjustment = cycle_adjustments.get(cycle, 0)
        adjusted_score = score + adjustment

        # Clamp to [-1, 1]
        return max(-1, min(1, adjusted_score))

    def _generate_sentiment_signal(self, sentiment_data: Dict) -> float:
        """
        Generate signal from market sentiment.

        Args:
            sentiment_data: Market sentiment data

        Returns:
            Signal score (-1 to 1)
        """
        if not sentiment_data:
            return 0.0

        # Get sentiment score
        score = sentiment_data.get("score", 0)

        # Get Fear & Greed Index if available
        fear_greed = sentiment_data.get("fear_greed", {})
        if fear_greed:
            fg_value = fear_greed.get("value", 50)
            # Extreme fear (< 25) = buy opportunity
            # Extreme greed (> 75) = sell signal
            fg_adjustment = (50 - fg_value) / 100  # -0.25 to 0.25
            score = (score + fg_adjustment) / 2

        # Clamp to [-1, 1]
        return max(-1, min(1, score))

    def _generate_technical_signal(self, price_data: Dict, indicators: Dict) -> float:
        """
        Generate signal from technical indicators.

        Args:
            price_data: Price data
            indicators: Technical indicators

        Returns:
            Signal score (-1 to 1)
        """
        if not price_data or not indicators:
            return 0.0

        signals = []

        # RSI signal
        rsi = indicators.get("rsi", 50)
        if rsi < 30:
            signals.append(0.5)  # Oversold = buy
        elif rsi > 70:
            signals.append(-0.5)  # Overbought = sell
        else:
            signals.append(0)

        # MACD signal
        macd = indicators.get("macd", 0)
        macd_signal = indicators.get("macd_signal", 0)
        if macd > macd_signal:
            signals.append(0.3)
        elif macd < macd_signal:
            signals.append(-0.3)
        else:
            signals.append(0)

        # Moving average signal
        price = price_data.get("last_price", 0)
        sma_20 = indicators.get("sma_20", price)
        sma_50 = indicators.get("sma_50", price)

        if price > sma_20 > sma_50:
            signals.append(0.4)  # Strong uptrend
        elif price < sma_20 < sma_50:
            signals.append(-0.4)  # Strong downtrend
        else:
            signals.append(0)

        # Volume signal (if available)
        volume = price_data.get("volume_24h", 0)
        avg_volume = indicators.get("avg_volume", volume)
        if volume > avg_volume * 1.5:
            # High volume confirms trend
            signals.append(signals[-1] * 0.2)
        else:
            signals.append(0)

        # Average all signals
        avg_signal = sum(signals) / len(signals) if signals else 0

        # Clamp to [-1, 1]
        return max(-1, min(1, avg_signal))

    def calculate_stop_loss(self, entry_price: float, direction: str) -> float:
        """
        Calculate stop loss price.

        Args:
            entry_price: Entry price
            direction: "buy" or "sell"

        Returns:
            Stop loss price
        """
        if direction == "buy":
            return entry_price * (1 - self.stop_loss_pct)
        else:
            return entry_price * (1 + self.stop_loss_pct)

    def calculate_take_profit(self, entry_price: float, direction: str) -> float:
        """
        Calculate take profit price.

        Args:
            entry_price: Entry price
            direction: "buy" or "sell"

        Returns:
            Take profit price
        """
        if direction == "buy":
            return entry_price * (1 + self.take_profit_pct)
        else:
            return entry_price * (1 - self.take_profit_pct)

    def calculate_optimal_position_size(
        self,
        capital: float,
        current_price: float,
        stop_loss_price: float
    ) -> float:
        """
        Calculate optimal position size based on risk management.

        Args:
            capital: Available capital
            current_price: Current market price
            stop_loss_price: Stop loss price

        Returns:
            Optimal position size
        """
        # Calculate risk per unit
        risk_per_unit = abs(current_price - stop_loss_price)
        risk_per_unit_pct = risk_per_unit / current_price

        # Calculate position size based on max risk
        max_risk_amount = capital * self.max_position_pct
        position_size = max_risk_amount / risk_per_unit_pct

        # Cap at maximum position
        max_position = capital * self.max_position_pct
        position_size = min(position_size, max_position)

        return position_size

    def should_exit(self, current_price: float, indicators: Dict) -> bool:
        """
        Check if position should be exited based on conditions.

        Args:
            current_price: Current market price
            indicators: Technical indicators

        Returns:
            True if should exit
        """
        if self.position == 0:
            return False

        # Check stop loss
        if self.position > 0:  # Long
            if current_price <= self.entry_price * (1 - self.stop_loss_pct):
                logger.info("Stop loss triggered", price=current_price)
                return True
        else:  # Short
            if current_price >= self.entry_price * (1 + self.stop_loss_pct):
                logger.info("Stop loss triggered", price=current_price)
                return True

        # Check take profit
        if self.position > 0:  # Long
            if current_price >= self.entry_price * (1 + self.take_profit_pct):
                logger.info("Take profit triggered", price=current_price)
                return True
        else:  # Short
            if current_price <= self.entry_price * (1 - self.take_profit_pct):
                logger.info("Take profit triggered", price=current_price)
                return True

        # Check RSI for exit
        rsi = indicators.get("rsi", 50)
        if self.position > 0 and rsi > 80:  # Overbought
            logger.info("RSI overbought exit", rsi=rsi)
            return True
        elif self.position < 0 and rsi < 20:  # Oversold
            logger.info("RSI oversold exit", rsi=rsi)
            return True

        return False

    def get_status(self) -> Dict:
        """Get strategy status with additional macro info."""
        base_status = super().get_status()
        base_status.update({
            "weights": {
                "macro": self.macro_weight,
                "sentiment": self.sentiment_weight,
                "technical": self.technical_weight
            },
            "risk_params": {
                "stop_loss_pct": self.stop_loss_pct,
                "take_profit_pct": self.take_profit_pct,
                "min_confidence": self.min_confidence
            }
        })
        return base_status
