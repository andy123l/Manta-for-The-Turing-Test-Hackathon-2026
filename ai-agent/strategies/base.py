"""
Base Strategy class for Manta trading agent.
All strategies inherit from this base class.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from datetime import datetime
from dataclasses import dataclass

from loguru import logger


@dataclass
class Signal:
    """Trading signal data structure."""
    action: str  # "buy", "sell", "hold"
    confidence: float  # 0.0 to 1.0
    reason: str
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.

    All strategies must implement:
    - generate_signal(): Generate trading signals
    - calculate_stop_loss(): Calculate stop loss price
    - calculate_take_profit(): Calculate take profit price
    """

    def __init__(self, name: str):
        """
        Initialize strategy.

        Args:
            name: Strategy name
        """
        self.name = name
        self.position = 0  # Current position size
        self.entry_price = 0  # Entry price of current position
        self.is_active = True

        logger.info("Strategy initialized", name=name)

    @abstractmethod
    def generate_signal(self, data: Dict) -> Signal:
        """
        Generate trading signal based on input data.

        Args:
            data: Dictionary containing market data, indicators, etc.

        Returns:
            Signal object with action, confidence, and metadata
        """
        pass

    @abstractmethod
    def calculate_stop_loss(self, entry_price: float, direction: str) -> float:
        """
        Calculate stop loss price.

        Args:
            entry_price: Entry price
            direction: "long" or "short"

        Returns:
            Stop loss price
        """
        pass

    @abstractmethod
    def calculate_take_profit(self, entry_price: float, direction: str) -> float:
        """
        Calculate take profit price.

        Args:
            entry_price: Entry price
            direction: "long" or "short"

        Returns:
            Take profit price
        """
        pass

    def update_position(self, size: float, entry_price: float):
        """
        Update current position.

        Args:
            size: New position size (positive for long, negative for short)
            entry_price: Entry price
        """
        self.position = size
        self.entry_price = entry_price

        logger.info(
            "Position updated",
            strategy=self.name,
            size=size,
            entry_price=entry_price
        )

    def calculate_position_pnl(self, current_price: float) -> float:
        """
        Calculate unrealized P&L for current position.

        Args:
            current_price: Current market price

        Returns:
            Unrealized P&L as percentage
        """
        if self.position == 0 or self.entry_price == 0:
            return 0.0

        if self.position > 0:  # Long position
            pnl_pct = (current_price - self.entry_price) / self.entry_price
        else:  # Short position
            pnl_pct = (self.entry_price - current_price) / self.entry_price

        return pnl_pct * abs(self.position)

    def should_exit(self, current_price: float, indicators: Dict) -> bool:
        """
        Check if position should be exited.

        Args:
            current_price: Current market price
            indicators: Technical indicators

        Returns:
            True if should exit, False otherwise
        """
        # Base implementation - override for custom exit logic
        return False

    def get_status(self) -> Dict:
        """
        Get current strategy status.

        Returns:
            Dictionary with strategy status
        """
        return {
            "name": self.name,
            "is_active": self.is_active,
            "position": self.position,
            "entry_price": self.entry_price,
            "timestamp": datetime.now()
        }
