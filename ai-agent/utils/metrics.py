"""
Metrics Calculator for Manta trading agent.
Calculates trading performance metrics.
"""

from typing import Dict, List
from datetime import datetime
from dataclasses import dataclass

from loguru import logger


@dataclass
class TradeRecord:
    """Trade record data structure."""
    symbol: str
    side: str  # "buy" or "sell"
    entry_price: float
    exit_price: float
    quantity: float
    entry_time: datetime
    exit_time: datetime
    pnl: float = 0.0
    pnl_pct: float = 0.0


class MetricsCalculator:
    """
    Calculates trading performance metrics.
    """

    def __init__(self):
        """Initialize metrics calculator."""
        self.trades: List[TradeRecord] = []
        self.initial_capital: float = 0
        self.current_capital: float = 0

        logger.info("Metrics calculator initialized")

    def add_trade(self, trade: TradeRecord):
        """Add a trade record."""
        self.trades.append(trade)
        logger.info("Trade added", symbol=trade.symbol, pnl=trade.pnl)

    def calculate_metrics(self) -> Dict:
        """
        Calculate all trading metrics.

        Returns:
            Dictionary with performance metrics
        """
        if not self.trades:
            return self._empty_metrics()

        # Basic metrics
        total_trades = len(self.trades)
        winning_trades = sum(1 for t in self.trades if t.pnl > 0)
        losing_trades = sum(1 for t in self.trades if t.pnl < 0)

        # P&L metrics
        total_pnl = sum(t.pnl for t in self.trades)
        avg_pnl = total_pnl / total_trades if total_trades > 0 else 0

        # Win rate
        win_rate = winning_trades / total_trades if total_trades > 0 else 0

        # Profit factor
        gross_profit = sum(t.pnl for t in self.trades if t.pnl > 0)
        gross_loss = abs(sum(t.pnl for t in self.trades if t.pnl < 0))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

        # Max drawdown
        max_drawdown = self._calculate_max_drawdown()

        # Sharpe ratio (simplified)
        sharpe_ratio = self._calculate_sharpe_ratio()

        return {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": win_rate,
            "total_pnl": total_pnl,
            "avg_pnl": avg_pnl,
            "profit_factor": profit_factor,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe_ratio,
            "gross_profit": gross_profit,
            "gross_loss": gross_loss
        }

    def _empty_metrics(self) -> Dict:
        """Return empty metrics."""
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0,
            "total_pnl": 0,
            "avg_pnl": 0,
            "profit_factor": 0,
            "max_drawdown": 0,
            "sharpe_ratio": 0,
            "gross_profit": 0,
            "gross_loss": 0
        }

    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown."""
        if not self.trades:
            return 0

        cumulative = 0
        peak = 0
        max_drawdown = 0

        for trade in self.trades:
            cumulative += trade.pnl
            if cumulative > peak:
                peak = cumulative
            drawdown = peak - cumulative
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        return max_drawdown

    def _calculate_sharpe_ratio(self, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio (simplified)."""
        if len(self.trades) < 2:
            return 0

        returns = [t.pnl_pct for t in self.trades]
        avg_return = sum(returns) / len(returns)
        std_return = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5

        if std_return == 0:
            return 0

        return (avg_return - risk_free_rate) / std_return

    def get_summary(self) -> str:
        """Get formatted summary of metrics."""
        metrics = self.calculate_metrics()

        summary = f"""
📊 Trading Performance Summary
{'='*40}
Total Trades: {metrics['total_trades']}
Winning Trades: {metrics['winning_trades']}
Losing Trades: {metrics['losing_trades']}
Win Rate: {metrics['win_rate']:.2%}

💰 P&L:
  Total: {metrics['total_pnl']:.2f}
  Average: {metrics['avg_pnl']:.2f}
  Gross Profit: {metrics['gross_profit']:.2f}
  Gross Loss: {metrics['gross_loss']:.2f}

📈 Metrics:
  Profit Factor: {metrics['profit_factor']:.2f}
  Max Drawdown: {metrics['max_drawdown']:.2f}
  Sharpe Ratio: {metrics['sharpe_ratio']:.2f}
{'='*40}
"""
        return summary
